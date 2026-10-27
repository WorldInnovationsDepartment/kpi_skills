"""brick_common.py -- shared loading/parsing for the brick-writer-121 scripts.

A «brick» is the dissertation. This module loads one part of it (or the whole
text) from .md / .txt / .docx, splits it into blocks (headings, paragraphs, list
items, table rows, captions), detects the kind of the part (анотація, вступ,
розділ N, висновки, список джерел, додатки) and extracts the objects the checks
need: headings, sentences, figure/table captions and references, formula numbers,
citations, numbers with units, abbreviations.

Public API (used by check_chapter.py and brick_status.py):
    load_text(path) -> (text, fmt)          fmt in {"md", "txt", "docx"}
    parse_blocks(text, fmt) -> [block]
    make_parts(blocks, name, fmt, kind=None, chapter=None, split=True) -> [Part]
    load_parts(path, kind=None, chapter=None, split=True) -> [Part]
    Part: .kind .chapter .label .paras .headings .sentences .fig_caps .tab_caps
          .fig_refs .tab_refs .formulas .citations .blocks() .pages() ...
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

CHARS_PER_PAGE = 1800  # TNR 14, 1.5 spacing, A4, 20-25 mm margins: ~1800-2000 chars with spaces per page


class BrickError(Exception):
    pass


# ---------------------------------------------------------------- shared rules data
# The regexes below are copied from skills/phd-seminar-review/scripts/check_deck.py
# (GRADATION_RE ... PLACEHOLDER_RE, LANG_CHECKS, KNOWN_ABBR) so that the talk and the
# dissertation are judged by the same vocabulary; the calque list is extended.

GRADATION_RE = r"вперше|уперше|удосконал|покращен|набу\w*\s+(подальш|дальш)\w*\s+розвит|дістал\w*\s+подальш|отрима\w*\s+подальш|розвинуто|first(ly)?\s+(proposed|developed)|improved|further developed"
DISTINCT_RE = r"відрізня|на відміну|полягає|новизна .{0,20}(у|в)\b|за рахунок|which differs|unlike"
EFFECT_RE = r"дозвол|забезпеч|підвищ|зменш|скорот|зниз|покращ|прискор|збільш|allows|reduce|increase|improve"
QUANT_RE = r"\d+[.,]?\d*\s*(%|відсот|раз|раз(и|ів)|мс|ms|с\b|сек|хв|мб|гб|kb|mb|gb|times|x\b)|в\s+\d+[.,]?\d*\s+раз"
ARCH_RE = r"архітектур|architecture"
SE_RE = (r"програмн\w*\s+(забезпеч|систем|компонент|продукт|комплекс|засоб)|архітектур|мікросервіс|компонент"
         r"|модул\w+ (систем|програм)|uml|вимог\w* до (пз|програм)|software|супровод|експлуатац\w* (пз|програм|систем)"
         r"|тестуванн|верифікац|валідац\w* (пз|програм)|якост\w* (пз|програм)|моніторинг|субд|баз\w* даних")
INFINITIVE_RE = r"^[«\"]?[\w'’ʼ-]+(ти|тись|тися)\b"
PLACEHOLDER_RE = r"\bTODO\b|lorem ipsum|\bXXX+\b|click to (add|edit)|клацніть|натисніть, щоб|введіть текст|заголовок слайда|\[\s*(тут|вставити|todo)"
# Extra placeholders typical for a dissertation draft (case-sensitive ones are kept apart).
PLACEHOLDER_EXTRA_RE = (r"\[\s*N\s*%?\s*\]|\[\s*\d*\s*%\s*\]|\[\s*назва[^\]]{0,40}\]|\[\s*число\s*\]|\?\?\?"
                        r"|(?:…|\.\.\.)\s*TODO|\bFIXME\b|\bTBD\b|\[\s*цитата\s*\]")
PLACEHOLDER_CASE_RE = r"\bXX\b(?!\s*(?:ст\b|століт|-))"

# (pattern, suggestion[, severity]); matched on normtext(). Severity defaults to WARN;
# "INFO" marks stylistic items that are common in the genre.
LANG_CHECKS = [
    (r"\bявля(є|ю)ть?ся\b", "«являється» -> «є», «становить»"),
    (r"\bявляє собою\b", "«являє собою» -> «є», «становить»"),
    (r"\bприйма\w* участь", "«приймати участь» -> «брати участь»"),
    (r"\bна протязі\b", "«на протязі» -> «протягом»"),
    (r"\bу відповідності (з|до)\b|\bв відповідності", "«у відповідності з» -> «відповідно до»"),
    (r"\bв залежності від\b|\bу залежності від\b", "«в залежності від» -> «залежно від»"),
    (r"\bслідуюч\w+", "«слідуючий» -> «наступний»"),
    (r"\bспівпада\w*", "«співпадає» -> «збігається»"),
    (r"\bоб'єм\w*", "«об'єм» (даних, інформації) -> «обсяг»"),
    (r"\bпроцент\w*", "«процент» -> «відсоток»"),
    (r"\bдан(ий|ого|ому|им|ій|ої|ою)\s+(метод|модел|підх|алгоритм|систем|робот|дослідж|програм|архітектур|запит)",
     "«даний метод/дана робота» -> «цей метод», «запропонований метод»"),
    (r"\bна (сьогоднішній|даний) (день|час|момент)\b", "«на даний час» -> «нині», «сьогодні»"),
    (r"\bтак як\b", "«так як» (причина) -> «оскільки», «бо»"),
    (r"\bв якості\b|\bу якості\b", "«в якості» -> «як»"),
    (r"\bз точки зору\b", "«з точки зору» -> «з погляду», «щодо»"),
    (r"\b(рішенн\w+|вирішенн\w+|виріш\w+)\s+(задач|систем\w* рівнянь)", "задачі «розв'язують», а не «вирішують»"),
    (r"\bміроприємств\w*", "«міроприємства» -> «заходи»"),
    (r"\bполуч\w+", "«получити» -> «отримати»"),
    (r"\bвідмічен\w+|\bвідмітити\b", "«відмітити» -> «зазначити», «відзначити»"),
    (r"\bпо відношенню до\b", "«по відношенню до» -> «щодо»"),
    (r"\bприймаюч\w+ до уваги\b", "«приймаючи до уваги» -> «зважаючи на»"),
    (r"\bв повній мірі\b|\bу повній мірі\b", "«в повній мірі» -> «повною мірою»"),
    (r"\bпри присутності\b", "«при присутності» -> «за наявності»"),
    (r"\b(рішенн\w*|заход\w*|пропозиці\w*) по\s", "«рішення по …» -> «рішення щодо …»"),
    (r"\bвирахов\w+", "«вираховувати» -> «обчислювати»"),
    (r"\bпроект(ув|н|увал)\w*", "«проектування» -> «проєктування» (правопис 2019)"),
    (r"\bрезультуюч\w+", "«результуючий» -> «підсумковий», «вихідний»"),
    (r"\bрозробк(а|и|у|ою)\s+(модел|метод|архітектур|програмн)", "«розробка моделі/методу» -> «розроблення моделі/методу»"),
    # --- extensions for the dissertation genre
    (r"\bпредставля\w*\s+собою\b", "«представляє собою» -> «є», «становить»"),
    (r"\bіснуюч\w+", "«існуючий» -> «наявний» (поширено в жанрі)", "INFO"),
    (r"\bне дивлячись на\b", "«не дивлячись на» -> «незважаючи на»"),
    (r"\bвиключенн\w+", "«виключення» -> «виняток» (якщо йдеться не про вилучення)"),
    (r"\bлюб(ий|а|е|і|ого|ому|им|их|ої|ій|ою|ими)\b", "«любий» -> «будь-який»"),
    (r"\bвірн(ий|а|е|і|ого|ому|им|их|ою|ій|ої)\b|\bвірніст\w*", "«вірний/вірність» -> «правильний/правильність»"),
    (r"\bпідтверджу\w*\s+вірніст\w*", "«підтверджують вірність» -> «підтверджують правильність»"),
    (r"\bобласт(ь|і|и|ю|ей)\b", "«область» -> «галузь», «сфера» (якщо не математична область)", "INFO"),
    (r"\bоточенн\w+", "«оточення» -> «середовище»", "INFO"),
    (r"\bзгідно\s+(?!з\b|із\b|зі\b)\w+", "«згідно вимог» -> «згідно з вимогами»"),
    (r"\bвідповідно\s+(вимог\w*|стандарт\w*|норм\w*)", "«відповідно вимогам» -> «відповідно до вимог»"),
    (r"\bпри допомозі\b", "«при допомозі» -> «за допомогою»"),
    (r"\bна рахунок\b", "«на рахунок» -> «щодо»"),
]

# Abbreviations nobody needs to expand.
KNOWN_ABBR = {
    "КПІ", "МОН", "ТЕФ", "ІПЗЕ", "ФІОТ", "НТУУ", "ПЗ", "ІТ", "ЗВО", "НДР", "ОНП", "ДСТУ", "ISO", "IEC", "IEEE",
    "UML", "API", "REST", "SQL", "NOSQL", "HTTP", "HTTPS", "JSON", "XML", "CPU", "GPU", "RAM", "CRUD",
    "ID", "IT", "AI", "ML", "OS", "PC", "URL", "UI", "UX", "ACM", "DOI", "PDF", "WOS", "PHD", "ORCID",
    "SCOPUS", "СУБД", "БД", "ISSN", "ISBN", "Q1", "Q2", "Q3", "Q4", "МО", "ТОВ", "ДП", "АТ", "ПАТ", "НАН", "США", "ЄС", "ЗСУ", "РНБО",
    "ООН", "НАТО", "ЕОМ", "ІКТ", "PYTHON", "JAVA", "C", "SI", "UTC", "IOT", "КТН", "ДТН", "ТОМ", "ЧАСТИНА",
    "ЗМІСТ", "ВИСНОВКИ", "ДЯКУЮ", "УВАГУ", "ТА", "І", "Й", "В", "У", "НА", "ДО", "ЗА", "ПРО", "ЩО", "ЯК",
}

PART_KINDS = {"anotatsiia", "vstup", "rozdil", "vysnovky", "spysok", "dodatky", "poznachennia", "zmist"}
KIND_NAMES = {"anotatsiia": "анотація", "vstup": "вступ", "rozdil": "розділ", "vysnovky": "загальні висновки",
              "spysok": "список джерел", "dodatky": "додатки", "poznachennia": "перелік позначень",
              "zmist": "зміст", "tytul": "титульні сторінки", None: "невизначена частина"}
RUS_LETTERS = "ыэъёЫЭЪЁ"
APOS = "'’ʼ`´"
NUM = r"(?:\d+(?:\.\d+)*|[А-ЯA-Z]\.\d+)"


# ---------------------------------------------------------------- text utils

def norm(s: str) -> str:
    """Lower-case, unify apostrophes/quotes/dashes, squeeze whitespace."""
    s = unicodedata.normalize("NFC", s or "")
    for a in APOS:
        s = s.replace(a, "'")
    s = re.sub(r"[«»“”„\"]", '"', s)
    s = re.sub(r"[–—−]", "-", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def normtext(s: str) -> str:
    """Like norm() but keeps quotes/dashes: lower-case, apostrophes unified, NBSP -> space."""
    s = unicodedata.normalize("NFC", s or "").replace("\u00a0", " ").replace("\u00ad", "")
    for a in "’ʼ`´":
        s = s.replace(a, "'")
    return s.lower()


def words(s: str) -> list[str]:
    return re.findall(r"[^\W\d_][\w'’ʼ-]*", s or "")


def is_mostly_upper(s: str) -> bool:
    letters = [c for c in s if c.isalpha()]
    return bool(letters) and sum(c.isupper() for c in letters) / len(letters) > 0.7


def short(s: str, n: int = 80) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def to_float(tok: str) -> float | None:
    try:
        return float(tok.replace(",", "."))
    except ValueError:
        return None


def number_tokens(text: str) -> set[float]:
    """All numbers in `text` as floats (so «27,0» == «27» and «1,8» == «1.8»)."""
    out = set()
    for m in re.finditer(r"(?<![\d.,])\d+(?:[.,]\d+)?(?![\d])", text):
        v = to_float(m.group(0))
        if v is not None:
            out.add(v)
    return out


def quantities(text: str) -> list[tuple[str, float]]:
    """[(matched text, numeric value)] for every number with a unit (QUANT_RE)."""
    out = []
    for m in re.finditer(QUANT_RE, normtext(text)):
        n = re.search(r"\d+(?:[.,]\d+)?", m.group(0))
        v = to_float(n.group(0)) if n else None
        if v is not None:
            out.append((m.group(0).strip(), v))
    return out


# Abbreviations that must not end a sentence.
_ABBR_DOT = re.compile(
    r"(?i)(?<![\w])(рис|табл|с|сс|р|рр|т|д|п|пп|ст|ч|ім|див|напр|пор|вул|тис|млн|млрд|грн|ін|пр|ред|авт|проф|доц|акад|"
    r"канд|докт|м|к|н|о|док|абз|рос|укр|англ|fig|eq|tab|et al|al|vol|no|pp|p|dr|prof|ca|etc|vs|e\.g|i\.e)\.(?=\s)")
_INITIAL = re.compile(r"(?<![\w])([А-ЯІЇЄҐA-Z])\.(?=\s*[А-ЯІЇЄҐA-Z]\.|\s+[А-ЯІЇЄҐA-Z][а-яіїєґa-z'’ʼ-]+)")
_SENT_END = re.compile(r"[.!?…]+[\"»”)\]]*\s+(?=[«\"“(\[]?[А-ЯІЇЄҐA-Z])")
_DOT = "\u2024"


def split_sentences(text: str) -> list[str]:
    t = _ABBR_DOT.sub(lambda m: m.group(0).replace(".", _DOT), text)
    t = _INITIAL.sub(lambda m: m.group(0).replace(".", _DOT), t)
    out, pos = [], 0
    for m in _SENT_END.finditer(t):
        out.append(t[pos:m.end()])
        pos = m.end()
    out.append(t[pos:])
    return [s.replace(_DOT, ".").strip() for s in out if s.strip()]


# ---------------------------------------------------------------- loading

def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "cp1251"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _load_docx(path: Path) -> str:
    try:
        from docx import Document
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError as e:  # pragma: no cover
        raise BrickError(f"{path.name}: для .docx потрібен python-docx ({e}); запускайте через `uv run`") from e
    try:
        doc = Document(str(path))
    except Exception as e:
        raise BrickError(f"{path.name}: не вдалося відкрити .docx ({e})") from e
    out: list[str] = []
    for el in doc.element.body.iterchildren():
        tag = el.tag.rsplit("}", 1)[-1]
        if tag == "p":
            p = Paragraph(el, doc)
            t = p.text.strip()
            if not t:
                out.append("")
                continue
            sname = (p.style.name if p.style is not None else "") or ""
            m = re.match(r"(?i)(?:heading|заголовок)\s*(\d)", sname)
            if m:
                out.append("#" * int(m.group(1)) + " " + t)
            elif sname.lower() in ("title", "назва"):
                out.append("# " + t)
            elif el.pPr is not None and el.pPr.numPr is not None:
                out.append("- " + t)  # auto-numbered list item: the number itself is not stored in the text
            else:
                out.append(t)
        elif tag == "tbl":
            out.append("")
            tbl = Table(el, doc)
            for row in tbl.rows:
                cells, prev = [], None
                for c in row.cells:
                    if prev is not None and c._tc is prev:
                        continue  # merged cell repeated by python-docx
                    prev = c._tc
                    cells.append(re.sub(r"\s+", " ", c.text).strip())
                out.append("| " + " | ".join(cells) + " |")
            out.append("")
    return "\n\n".join(out)


def load_text(path: Path) -> tuple[str, str]:
    path = Path(path)
    if not path.is_file():
        raise BrickError(f"{path}: файл не знайдено")
    ext = path.suffix.lower()
    if ext == ".pdf":
        raise BrickError(f"{path.name}: PDF не читається напряму. Перетворіть: `pdftotext -layout {path.name} out.txt` "
                         "і запустіть перевірку на out.txt")
    if ext in (".md", ".markdown"):
        return _read_text(path), "md"
    if ext in (".txt", ".text"):
        return _read_text(path), "txt"
    if ext == ".docx":
        return _load_docx(path), "docx"
    if ext in (".doc", ".odt", ".rtf"):
        raise BrickError(f"{path.name}: формат {ext} не підтримується; збережіть як .docx "
                         "(або `soffice --headless --convert-to docx`)")
    raise BrickError(f"{path.name}: непідтримуваний формат {ext!r} (потрібні .md, .txt або .docx)")


# ---------------------------------------------------------------- headings

def _is_toc_tail(s: str) -> bool:
    return bool(re.search(r"(\.{3,}|…{2,}|(?:\.\s){3,})\s*\d*\s*$", s) or re.search(r"\s\d{1,3}\s*$", s))


def _strip_inline(s: str) -> str:
    s = re.sub(r"<span[^>]*>(.*?)</span>", r"\1", s)
    s = re.sub(r"<span[^>]*/?>", "", s)
    s = s.replace("**", "").replace("__", "").replace("\u00a0", " ").replace("\u00ad", "")
    s = re.sub(r"\s*\{#[^}]*\}\s*$", "", s)
    return s


def classify_heading(text: str, hashes: int | None) -> dict | None:
    """Return {level, number, title, hkind, chapter} if `text` is a heading, else None.
    hashes = number of leading '#' for a Markdown heading (None for a plain line)."""
    t = re.sub(r"\s+", " ", text).strip()
    if not t:
        return None
    plain = hashes is None
    low = norm(t).rstrip(".:").strip()
    m = re.match(r"(?i)^розділ\s+(\d+)\s*[.:)]?\s*(.*)$", t)
    if m:
        rest = m.group(2).strip()
        if plain and rest and (not is_mostly_upper(rest[:80]) or _is_toc_tail(rest)):
            return None
        return dict(level=1, number=m.group(1), title=rest, hkind="rozdil", chapter=int(m.group(1)))
    m = re.match(r"^(?:висновки|висновок)\s+до\s+розділу(?:\s+(\d+))?$", low)
    if m:
        return dict(level=2, number=None, title=t, hkind="concl", chapter=int(m.group(1)) if m.group(1) else None)
    if re.match(r"^(загальні\s+)?висновки$", low):
        return dict(level=1, number=None, title=t, hkind="vysnovky", chapter=None)
    if low == "вступ":
        return dict(level=1, number=None, title=t, hkind="vstup", chapter=None)
    if re.match(r"^(анотація|annotation|abstract|анотація/abstract)$", low):
        return dict(level=1, number=None, title=t, hkind="anotatsiia", chapter=None)
    if re.match(r"^(список використаних джерел|список літератури|перелік використаних джерел|перелік посилань|"
                r"використані джерела|references|література|bibliography)$", low):
        return dict(level=1, number=None, title=t, hkind="spysok", chapter=None)
    if low in ("зміст", "contents", "table of contents"):
        return dict(level=1, number=None, title=t, hkind="zmist", chapter=None)
    if re.match(r"^(перелік умовних позначень|перелік скорочень|список скорочень|умовні позначення|"
                r"перелік умовних скорочень)", low) and len(t) < 90 and (not plain or not _is_toc_tail(t)):
        return dict(level=1, number=None, title=t, hkind="poznachennia", chapter=None)
    if re.match(r"(?i)^додат(ок|ки)(\s+[А-ЯA-ZІЇЄҐ0-9])?(\s|$)", t) and len(t) <= 150:
        rest = re.sub(r"(?i)^додат(ок|ки)(\s+[А-ЯA-ZІЇЄҐ0-9])?\s*", "", t)
        if not plain or (is_mostly_upper(t[:80]) and (not rest or is_mostly_upper(rest[:80])) and not _is_toc_tail(t)):
            return dict(level=1, number=None, title=t, hkind="dodatky", chapter=None)
    m = re.match(r"^(\d+(?:\.\d+){1,3})\.?\s+(\S.*)$", t)
    if m:
        title = m.group(2).strip()
        ok = bool(re.match(r"[А-ЯІЇЄҐA-Z«\"“(]", title)) and len(title) >= 5
        if ok and plain:
            ok = (len(title.split()) <= 40 and not title.endswith((".", ";", ",")) and not _is_toc_tail(title)
                  and not (len(title.split()) == 1 and is_mostly_upper(title) and len(title) <= 4))
        if ok:
            comps = m.group(1).split(".")
            hk = "concl" if re.match(r"^(висновки|висновок)(\s+до\s+розділу(\s+\d+)?)?$", norm(title).rstrip(".:")) else "sub"
            return dict(level=len(comps), number=m.group(1), title=title, hkind=hk, chapter=int(comps[0]))
        return None
    if hashes == 1:
        m = re.match(r"^(\d+)\.?\s+([А-ЯІЇЄҐA-Z].*)$", t)
        if m and len(m.group(2)) >= 5:
            return dict(level=1, number=m.group(1), title=m.group(2), hkind="rozdil", chapter=int(m.group(1)))
    if hashes:
        return dict(level=hashes, number=None, title=t, hkind="other", chapter=None)
    return None


# ---------------------------------------------------------------- blocks

LIST_RE = re.compile(r"^\s*(?:[-*•–—]|\d{1,3}[.)]|[а-яіїєґa-z][.)])\s+(\S.*)$")
LIST2_RE = re.compile(r"^\s*\d{1,3}[.)](?=[^\W\d_])(\S.*)$")  # «10.Автор …» (no space; typical of reference lists)
IMG_ONLY_RE = re.compile(r"^(?:!\[[^\]]*\]\([^)]*\)\s*)+(?:\{[^}]*\})?$")
_TOCISH_RE = re.compile(r"\.{4,}\s*\d+\s*$|…{3,}\s*\d+\s*$|\]\(#")


def _find_toc(lines: list[str]) -> tuple[int, int] | None:
    """(start, end) line indexes of the table of contents (the «ЗМІСТ» line .. last entry), or None."""
    for i, ln in enumerate(lines):
        s = _strip_inline(ln).strip().lstrip("#").strip().rstrip(".:").lower()
        if s in ("зміст", "contents", "table of contents"):
            window = range(i + 1, min(len(lines), i + 900))
            hits = [j for j in window if _TOCISH_RE.search(lines[j])]
            if len(hits) >= 3:
                end = hits[-1]
                # entries wrapped over several lines may precede the last leader; include page-number-only tail
                return i, end
    return None


def _join_wrapped(a: str, b: str, fmt: str) -> str:
    if fmt == "txt" and re.search(r"[A-Za-zА-Яа-яІіЇїЄєҐґ]-$", a) and re.match(r"[а-яіїєґa-z]", b):
        return a[:-1] + b
    return a + " " + b


def parse_blocks(text: str, fmt: str = "md") -> list[dict]:
    """Split text into blocks: {text, kind, heading|None, marker, line}. kind in
    body | list | table | image | formula | code | heading."""
    lines = text.replace("\r", "").replace("\x0c", "\n").split("\n")
    toc = _find_toc(lines)
    blocks: list[dict] = []
    cur: list[str] = []
    cur_line = 0

    def flush():
        nonlocal cur, list_idx
        list_idx = None
        if cur:
            t = cur[0]
            for nxt in cur[1:]:
                t = _join_wrapped(t, nxt, fmt)  # hyphenation at a line break (pdftotext) is repaired
            blocks.append(dict(text=re.sub(r"[ \t]+", " ", t).strip(), kind="body", heading=None, marker=None,
                               line=cur_line))
            cur = []

    def push(kind, t, marker=None, heading=None):
        nonlocal list_idx
        flush()
        blocks.append(dict(text=t, kind=kind, heading=heading, marker=marker, line=i + 1))
        list_idx = len(blocks) - 1 if kind == "list" else None

    in_code = in_math = False
    math_buf: list[str] = []
    i = -1
    list_idx = None  # index in `blocks` of the list item that wrapped lines continue
    base = 0
    if fmt == "txt":
        from collections import Counter
        ind = Counter(len(l) - len(l.lstrip(" ")) for l in lines if len(l.strip()) > 70)
        base = ind.most_common(1)[0][0] if ind else 0
    END_RE = re.compile(r"[.!?:;»)\"”]$")
    for i, raw in enumerate(lines):
        if toc and toc[0] < i <= toc[1]:
            continue
        if raw.strip().startswith("```"):
            flush()
            in_code = not in_code
            continue
        if in_code:
            continue
        if in_math:
            math_buf.append(raw)
            if "$$" in raw or "\\end{equation" in raw or "\\end{align" in raw:
                in_math = False
                push("formula", " ".join(x.strip() for x in math_buf))
                math_buf = []
            continue
        s0 = raw.strip()
        if s0.startswith("$$") or re.match(r"\\begin\{(equation|align|eqnarray)", s0):
            closed = (s0.count("$$") >= 2) or "\\end{" in s0
            if closed:
                push("formula", s0)
            else:
                in_math, math_buf = True, [raw]
            continue
        s = _strip_inline(raw)
        s = re.sub(r"\\([\[\]()_*#<>.!|{}$-])", r"\1", s)
        st = s.strip()
        if not st:
            flush()
            list_idx = None
            continue
        if fmt == "txt" and re.fullmatch(r"\d{1,3}", st):
            continue  # page number
        if st.startswith("[") and "](#" in st:
            flush()
            continue  # leftover TOC link
        if re.fullmatch(r"[+|:\-=\s]+", st) and ("-" in st or "=" in st):
            flush()
            continue  # table border / separator row
        mh = re.match(r"^(#{1,6})\s*(.*)$", st)
        if mh:
            title = mh.group(2).strip()
            if not title:
                flush()
                continue
            h = classify_heading(title, len(mh.group(1)))
            push("heading", title, heading=h)
            continue
        if st.startswith("|"):
            cells = [c.strip() for c in st.strip("|").split("|")]
            push("table", " | ".join(c for c in cells))
            continue
        if IMG_ONLY_RE.match(st):
            alts = re.findall(r"!\[([^\]]*)\]\(([^)]*)\)", st)
            if all(re.search(r"\.(wmf|emf)\s*$", u, re.I) for _, u in alts):
                cur_text = "▣"
                flush()
                cur.append(cur_text)
                cur_line = i + 1
                continue
            push("image", " ".join(a for a, _ in alts if a).strip())
            continue
        st_img = re.sub(r"!\[[^\]]*\]\([^)]*\.(?:wmf|emf)\)", "▣", st)
        st_img = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", st_img).strip() or st_img
        st = st_img
        h = classify_heading(st, None)
        if h:
            # wrapped ALL-CAPS chapter titles (pdftotext): absorb the following upper-case lines
            if fmt == "txt" and h["hkind"] == "rozdil":
                j = i + 1
                extra = []
                while j < len(lines) and lines[j].strip() and is_mostly_upper(lines[j]) and len(lines[j].strip()) > 3 \
                        and not _TOCISH_RE.search(lines[j]):
                    extra.append(lines[j].strip())
                    j += 1
                # (lines are consumed lazily: mark them by replacing with empty strings)
                for k, e in enumerate(extra):
                    lines[i + 1 + k] = ""
                if extra:
                    st = st + " " + " ".join(extra)
                    h = classify_heading(st, None) or h
            push("heading", re.sub(r"\s+", " ", st), heading=h)
            continue
        ml = LIST_RE.match(st) or LIST2_RE.match(st)
        if ml:
            marker = st[:len(st) - len(ml.group(1))].strip()
            push("list", ml.group(1).strip(), marker=marker)
            continue
        indent = len(s) - len(s.lstrip(" "))
        if fmt == "txt":
            if indent - base >= 10 and len(st) < 160:  # centred line (caption, title): a block of its own
                push("body", st)
                continue
            newpar = indent - base >= 2
            if list_idx is not None:
                if newpar and END_RE.search(blocks[list_idx]["text"]):
                    list_idx = None
                else:
                    blocks[list_idx]["text"] = _join_wrapped(blocks[list_idx]["text"], st, fmt)
                    continue
            elif cur and newpar and END_RE.search(cur[-1]):
                flush()
        elif list_idx is not None:
            blocks[list_idx]["text"] = _join_wrapped(blocks[list_idx]["text"], st, fmt)
            continue
        if not cur:
            cur_line = i + 1
        cur.append(st)
    flush()
    if fmt == "txt":  # a page break splits a sentence into two blocks: glue them
        merged: list[dict] = []
        for b in blocks:
            if (merged and b["kind"] == "body" and merged[-1]["kind"] == "body" and re.match(r"[а-яіїєґa-z]", b["text"])
                    and not END_RE.search(merged[-1]["text"])):
                merged[-1]["text"] += " " + b["text"]
            else:
                merged.append(b)
        blocks = merged
    return blocks


# ---------------------------------------------------------------- Part

FIG_CAP_RE = re.compile(r"(?i)^(рисунок|рис\.)\s*(" + NUM + r")(?:\s*([–—−-])\s*|\s*[.:]\s*|\s*$)(.*)$")
TAB_CAP_RE = re.compile(r"(?i)^(таблиця|табл\.)\s*(" + NUM + r")(?:\s*([–—−-])\s*|\s*[.:]\s*|\s*$)(.*)$")
FIG_REF_RE = re.compile(r"(?i)(?<![\w])(?:рис\.|рисун\w*|figure|fig\.)\s*(" + NUM + r")")
TAB_REF_RE = re.compile(r"(?i)(?<![\w])(?:табл\.|таблиц\w*|table)\s*(" + NUM + r")")
_REF_TAIL_RE = re.compile(r"^(?:\s*(?:,|і|та|й|и|і\s+також)\s*(" + NUM + r"))+")
FORMULA_NUM_RE = re.compile(r"\((\d+(?:\.\d+)+)\)\s*$")
TAG_RE = re.compile(r"\\tag\*?\{\(?(\d+(?:\.\d+)+)\)?\}")
AUTHOR_YEAR_RE = re.compile(r"\([A-ZА-ЯІЇЄҐ][\w'’ʼ-]+(?:\s+(?:et al\.|та ін\.|і\s+[A-ZА-ЯІЇЄҐ][\w'’ʼ-]+|and\s+\w+))?,?\s+(?:19|20)\d\d[a-z]?\)")
PROSE_RE = re.compile(r"(?:[А-Яа-яІіЇїЄєҐґ]{4,}\s+){4}")  # four long Cyrillic words in a row = prose, not a formula
_MATH_CHARS = re.compile(r"[=≈≤≥<>∑∏∫√+*/^_\\$▣]")

# Keyword labels of the blocks of a «вступ» (matched at the start of a paragraph or sentence).
BLOCK_PATTERNS = [
    ("novelty", r"^наукова\s+новизна"),
    ("practical", r"^практичн\w+\s+(значення|використання|цінність)"),
    ("personal", r"^особист\w+\s+внесок"),
    ("approbation", r"^апробація"),
    ("publications", r"^(публікації|опубліковано|за\s+темою\s+дисертації\s+опубліковано|основні\s+результати\s+.{0,40}опубліковано)"),
    ("structure", r"^(структура\s+(та|і|й)\s+обсяг|структура\s+дисертац|обсяг\s+та\s+структура|обсяг\s+і\s+структура)"),
    ("relevance", r"^актуальність"),
    ("link", r"^зв'язок"),
    ("object", r"^об'єкт"),
    ("subject", r"^предмет"),
    ("methods", r"^(методи\s+(дослідження|дисертаційного)|методи\s+та\s+засоби\s+дослідження|методологі|методи\b)"),
    ("tasks", r"^((основні\s+)?(наукові\s+)?завданн|для\s+(досягнення|реалізації)\s+(поставленої\s+|сформульованої\s+|цієї\s+)?мети.{0,120}завданн|"
              r"для\s+досягнення\s+мети.{0,80}(задач|завданн)|мета\s+(і|та)\s+завданн)"),
    ("aim", r"^мет(а|ою|и)\b"),
]
BLOCK_LABELS = {
    "relevance": "актуальність", "link": "зв'язок роботи з науковими програмами, планами, темами (НДР)",
    "aim": "мета", "tasks": "завдання", "object": "об'єкт", "subject": "предмет", "methods": "методи дослідження",
    "novelty": "наукова новизна", "practical": "практичне значення", "personal": "особистий внесок",
    "approbation": "апробація", "publications": "публікації", "structure": "структура та обсяг",
}


def block_label(text: str) -> str | None:
    t = normtext(re.sub(r"^[\s*_#\d.)(–—-]+", "", text.strip()))
    t = re.sub(r"^[*_]+", "", t).strip()
    for key, pat in BLOCK_PATTERNS:
        if re.search(pat, t):
            return key
    return None


def _expand_refs(text: str, rx: re.Pattern) -> list[str]:
    out = []
    for m in rx.finditer(text):
        nums = [m.group(1)]
        tail = _REF_TAIL_RE.match(text[m.end():])
        if tail:
            nums += re.findall(NUM, tail.group(0))
        rng = re.match(r"\s*[–—−-]\s*(" + NUM + r")", text[m.end():])
        if rng and "." in m.group(1) and "." in rng.group(1):
            a, b = m.group(1).split("."), rng.group(1).split(".")
            if len(a) == len(b) == 2 and a[0] == b[0] and a[1].isdigit() and b[1].isdigit() and 0 < int(b[1]) - int(a[1]) < 30:
                nums = [f"{a[0]}.{k}" for k in range(int(a[1]), int(b[1]) + 1)]
        out += nums
    return out


def parse_citation(inner: str) -> list[int] | None:
    """Numbers cited inside [...]; None when the brackets are not a citation."""
    inner = inner.strip()
    if not re.match(r"^\d", inner):
        return None
    if not re.fullmatch(r"[\d\s,;–—−\-]*(?:[,;]\s*(?:с|c|p|pp|т|т\.|стор)\.?\s*[\d\s,–—−\-]+)*[\d\s,;–—−\-]*", inner, re.I):
        # allow «12, с. 40» and «3, 7–9, с. 14»
        if not re.fullmatch(r"[\d\s,;–—−\-]+(?:[,;]\s*[сcpТт]{1,2}\.?\s*[\d\s,–—−\-]+)*", inner):
            return None
    nums: list[int] = []
    for seg in re.split(r"[;,]", inner):
        seg = seg.strip()
        if not seg or re.match(r"(?i)^(с|c|p|pp|т|стор)\b", seg):
            continue
        m = re.fullmatch(r"(\d+)\s*[–—−-]\s*(\d+)", seg)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a <= b <= a + 200:
                nums += list(range(a, b + 1))
            else:
                nums += [a, b]
        elif re.fullmatch(r"\d+", seg):
            nums.append(int(seg))
        else:
            return None
    return nums or None


class Part:
    def __init__(self, blocks: list[dict], name: str = "", fmt: str = "md", kind: str | None = None,
                 chapter: int | None = None, cpp: int = CHARS_PER_PAGE):
        self.name, self.fmt, self.cpp = name, fmt, cpp
        self.paras: list[dict] = []
        for b in blocks:
            if not b["text"].strip():
                continue
            h = b["heading"]
            self.paras.append(dict(
                i=len(self.paras) + 1, text=b["text"], kind=b["kind"], marker=b["marker"], line=b.get("line"),
                level=h["level"] if h else None, hnum=h["number"] if h else None, htitle=h["title"] if h else None,
                hkind=h["hkind"] if h else None, hchapter=h["chapter"] if h else None, path=""))
        self.kind, self.chapter = kind, chapter
        self._detect(kind, chapter)
        self._paths()
        self._classify_paras()
        self._sentences()
        self._extract()

    # -- detection
    def _detect(self, kind, chapter):
        hs = [p for p in self.paras if p["kind"] == "heading" and p["hkind"]]
        first = next((p for p in hs if p["hkind"] in PART_KINDS), None)
        dk, dch = None, None
        if first:
            dk, dch = first["hkind"], first["hchapter"]
        else:
            cc = next((p for p in hs if p["hkind"] == "concl"), None)
            nums = [p for p in hs if p["hkind"] == "sub" and p["level"] == 2]
            if cc and cc["hchapter"]:
                dk, dch = "rozdil", cc["hchapter"]
            elif nums:
                dk, dch = "rozdil", nums[0]["hchapter"]
        if dk is None and not kind:
            hint = Path(self.name.split(":")[0]).stem.lower() if self.name else ""
            for k, rx in (("anotatsiia", r"anotat|annot|abstract|анотац"), ("vstup", r"vstup|вступ"),
                          ("vysnovky", r"vysnov|висновк|conclusion"), ("spysok", r"spysok|dzherel|literatur|references|список"),
                          ("dodatky", r"dodat|appendi|додат"), ("rozdil", r"rozd|розд|chapter|ch\d")):
                if re.search(rx, hint):
                    dk = k
                    mm = re.search(r"(?:rozd\w*|розд\w*|chapter|ch)[-_ ]*(\d+)", hint)
                    dch = int(mm.group(1)) if mm else None
                    break
        self.kind = kind or dk
        self.chapter = chapter if chapter else (dch if (self.kind == "rozdil") else None)
        if self.kind == "rozdil" and self.chapter is None:
            for p in hs:
                if p["hnum"]:
                    self.chapter = int(p["hnum"].split(".")[0])
                    break
        if self.kind == "rozdil":
            seen_first = False
            for p in self.paras:
                if p["kind"] == "heading":
                    if seen_first and p["hkind"] == "vysnovky":
                        p["hkind"], p["hchapter"], p["loose"] = "concl", self.chapter, True
                    seen_first = True

    @property
    def label(self) -> str:
        if self.kind == "rozdil":
            return f"розділ {self.chapter}" if self.chapter else "розділ"
        return KIND_NAMES.get(self.kind, str(self.kind))

    def _paths(self):
        cur = self.label
        for p in self.paras:
            if p["kind"] == "heading":
                if p["hnum"] and p["hkind"] == "sub":
                    cur = p["hnum"]
                elif p["hkind"] == "concl":
                    cur = p["hnum"] or f"висновки до розділу {p['hchapter'] or ''}".strip()
                elif p["hkind"] == "rozdil":
                    cur = self.label
                else:
                    cur = short(p["text"], 40)
            p["path"] = cur

    # -- paragraph kinds
    def _classify_paras(self):
        self.concl_index = None
        for k, p in enumerate(self.paras):
            t = p["text"]
            if p["kind"] == "heading":
                if p["hkind"] == "concl" and self.concl_index is None:
                    self.concl_index = p["i"]
                continue
            if p["kind"] in ("list", "table"):
                continue
            if p["kind"] == "image":
                p["alt_caption"] = bool(FIG_CAP_RE.match(t))
                continue
            if p["kind"] == "body":
                if FIG_CAP_RE.match(t):
                    p["kind"] = "caption_fig"
                elif TAB_CAP_RE.match(t):
                    p["kind"] = "caption_tab"
                else:
                    fm = FORMULA_NUM_RE.search(t)
                    pre = t[:fm.start()] if fm else ""
                    if fm and (len(t) <= 40 or _MATH_CHARS.search(pre)) and not PROSE_RE.search(pre):
                        p["kind"] = "formula"
                        p["fnum"] = fm.group(1)
            if p["kind"] == "formula" and "fnum" not in p:
                tg = TAG_RE.search(t) or FORMULA_NUM_RE.search(t)
                p["fnum"] = tg.group(1) if tg else None
        # images: caption in alt text or in the neighbouring paragraph
        for k, p in enumerate(self.paras):
            if p["kind"] == "image":
                nb = [self.paras[j] for j in (k - 1, k + 1) if 0 <= j < len(self.paras)]
                p["has_caption"] = p["alt_caption"] or any(q["kind"] == "caption_fig" for q in nb)
        for p in self.paras:
            if p["kind"] == "image" and p.get("alt_caption"):
                p["kind"] = "caption_fig"

    def _sentences(self):
        self.sentences: list[dict] = []
        for p in self.paras:
            if p["kind"] in ("body", "list"):
                for s in split_sentences(p["text"]):
                    self.sentences.append(dict(text=s, para=p["i"], path=p["path"]))

    def _extract(self):
        self.fig_caps, self.tab_caps, self.fig_refs, self.tab_refs = [], [], [], []
        self.formulas, self.citations = [], []
        self.images_no_caption = 0
        canon_f = re.compile(r"^(Рисунок)\s+\d+(?:\.\d+)+ – \S.*(?<![.])$")
        canon_t = re.compile(r"^(Таблиця)\s+\d+(?:\.\d+)+ – \S.*(?<![.])$")
        for p in self.paras:
            t = p["text"]
            k = p["kind"]
            if k == "caption_fig":
                m = FIG_CAP_RE.match(t)
                self.fig_caps.append(dict(num=m.group(2), para=p["i"], text=t, canonical=bool(canon_f.match(t))))
            elif k == "caption_tab":
                m = TAB_CAP_RE.match(t)
                self.tab_caps.append(dict(num=m.group(2), para=p["i"], text=t, canonical=bool(canon_t.match(t))))
            elif k == "image" and not p.get("has_caption"):
                self.images_no_caption += 1
            if k == "formula" and p.get("fnum"):
                self.formulas.append(dict(num=p["fnum"], para=p["i"]))
            if k in ("body", "list", "table"):
                for n in _expand_refs(t, FIG_REF_RE):
                    self.fig_refs.append(dict(num=n, para=p["i"]))
                for n in _expand_refs(t, TAB_REF_RE):
                    self.tab_refs.append(dict(num=n, para=p["i"]))
            if k in ("body", "list", "table", "caption_fig", "caption_tab") and self.kind != "spysok":
                for m in re.finditer(r"\[([^\[\]]{1,80})\]", t):
                    nums = parse_citation(m.group(1))
                    if nums:
                        self.citations.append(dict(nums=nums, para=p["i"], raw=m.group(0)))
        self.fmt_author_year = sum(len(AUTHOR_YEAR_RE.findall(p["text"])) for p in self.paras if p["kind"] in ("body", "list"))

    # -- queries
    @property
    def headings(self) -> list[dict]:
        return [p for p in self.paras if p["kind"] == "heading"]

    def loc(self, para_i: int | None = None, path: str | None = None) -> str:
        if para_i is None:
            return self.label
        p = self.paras[para_i - 1]
        return f"{path or p['path']}, п.{p['i']}: «{short(p['text'], 80)}»"

    def chars(self) -> int:
        return sum(len(p["text"]) + 1 for p in self.paras)

    def pages(self, cpp: int | None = None) -> float:
        return self.chars() / (cpp or self.cpp)

    def main_paras(self) -> list[dict]:
        """Paragraphs outside the conclusions (for a chapter: before «Висновки до розділу»)."""
        if self.kind == "vysnovky":
            return []
        if self.concl_index:
            return [p for p in self.paras if p["i"] < self.concl_index]
        return list(self.paras)

    def concl_paras(self) -> list[dict]:
        if self.kind == "vysnovky":
            return [p for p in self.paras if p["kind"] != "heading"]
        if self.concl_index:
            return [p for p in self.paras if p["i"] > self.concl_index and p["kind"] != "heading"]
        return []

    def body_text(self, paras=None) -> str:
        return "\n".join(p["text"] for p in (paras if paras is not None else self.paras) if p["kind"] != "heading")

    def blocks(self) -> dict:
        """Keyword-labelled blocks of a вступ: key -> {first_para, units:[{text, para, list, marker}]}.
        A unit is a paragraph or a list item; labels are detected at the start of a paragraph or of a sentence."""
        out: dict[str, dict] = {}
        cur = None
        for p in self.paras:
            if p["kind"] in ("table", "formula", "image", "caption_fig", "caption_tab"):
                continue
            if p["kind"] == "heading":
                lab = block_label(p["text"])
                if lab:
                    cur = lab
                    out.setdefault(lab, dict(first_para=p["i"], units=[]))
                elif p["level"] and p["level"] <= 2 or p["hkind"] in PART_KINDS:
                    cur = None
                continue
            if p["kind"] == "body":
                # a label can start the paragraph or a later sentence of it: split into segments per label
                segs: list[tuple[str | None, list[str]]] = [(cur, [])]
                for sent in split_sentences(p["text"]):
                    lab = block_label(sent)
                    if lab:
                        cur = lab
                        segs.append((lab, []))
                    segs[-1][1].append(sent)
                for lab, ss in segs:
                    if not ss:
                        continue
                    if lab:
                        out.setdefault(lab, dict(first_para=p["i"], units=[]))["units"].append(
                            dict(text=" ".join(ss), para=p["i"], list=False, marker=None))
            elif cur:
                out[cur]["units"].append(dict(text=p["text"], para=p["i"], list=True, marker=p["marker"]))
        return out

    def stats(self) -> dict:
        return dict(headings=len(self.headings), pages=round(self.pages(), 1),
                    figures=len(self.fig_caps), tables=len(self.tab_caps), formulas=len(self.formulas),
                    citations=len(self.citations), has_conclusions=bool(self.concl_index) or self.kind == "vysnovky")

    def to_dict(self) -> dict:
        return dict(name=self.name, kind=self.kind, chapter=self.chapter, label=self.label,
                    format=self.fmt, **self.stats(),
                    headings_list=[dict(level=h["level"], number=h["hnum"], text=h["text"], para=h["i"]) for h in self.headings])


# ---------------------------------------------------------------- enumerations / novelty

def enumerate_items(units: list[dict]) -> list[str]:
    """List items of a block; if there are none, split an inline enumeration «1) …; 2) …» / «: …; …»."""
    items = [u["text"] for u in units if u["list"]]
    if items:
        return items
    for u in units:
        t = u["text"]
        if re.search(r"(?:^|\s)\(?\d{1,2}[.)]\s+\S", t) and len(re.findall(r"(?:^|[\s:;,])\(?\d{1,2}\)\s+", t)) >= 2:
            parts = re.split(r"(?:^|[\s:;,])\(?\d{1,2}\)\s+", t)[1:]
            return [x.strip(" ;.,") for x in parts if x.strip(" ;.,")]
        if ":" in t and t.count(";") >= 1:
            parts = re.split(r";\s*", t.split(":", 1)[1])
            return [x.strip(" .") for x in parts if x.strip(" .")]
    return []


def novelty_items(part: Part) -> tuple[bool, list[dict]]:
    """(block_found, items[{text, para}]) of the «наукова новизна» block of a part. Items are list items or,
    for prose, the sentences / «;»-separated pieces after the label."""
    blk = part.blocks().get("novelty")
    if not blk:
        return False, []
    units = blk["units"]
    lst = [u for u in units if u["list"]]
    if lst:
        return True, [dict(text=u["text"], para=u["para"]) for u in lst]
    items = []
    keep = []
    for k, u in enumerate(units):  # prose: the label paragraph and the following paragraphs that still carry a marker
        if k == 0 or re.search(GRADATION_RE, normtext(u["text"])):
            keep.append(u)
        else:
            break
    for u in keep:
        for s in split_sentences(u["text"]):
            pieces = [x.strip() for x in re.split(r";\s+", s)]
            if sum(bool(re.search(GRADATION_RE, normtext(x))) for x in pieces) >= 2:
                items += [dict(text=x, para=u["para"]) for x in pieces if x]
            else:
                items.append(dict(text=s, para=u["para"]))
    # drop the label sentence itself («Наукова новизна … полягає в тому, що:»)
    items = [it for it in items if not (len(it["text"]) < 140 and it["text"].rstrip().endswith(":"))
             and not re.fullmatch(r"(?i)наукова новизна[^.]{0,60}\.?", it["text"].strip())]
    # a sentence without a marker continues the previous item (elaboration of the same result)
    merged: list[dict] = []
    for it in items:
        if merged and not re.search(GRADATION_RE, normtext(it["text"])):
            merged[-1]["text"] += " " + it["text"]
        else:
            merged.append(dict(it))
    items = merged
    return True, items


# ---------------------------------------------------------------- building parts

def make_parts(blocks: list[dict], name: str, fmt: str, kind: str | None = None, chapter: int | None = None,
               split: bool = True, cpp: int = CHARS_PER_PAGE) -> list[Part]:
    """Build Part objects; a file that contains several top-level part headings is split into parts."""
    if split and kind is None and chapter is None:
        cuts, cur_kind = [], None
        for k, b in enumerate(blocks):
            h = b["heading"]
            if b["kind"] == "heading" and h and h["hkind"] in PART_KINDS and h["level"] == 1:
                key = (h["hkind"], h["chapter"])
                if cur_kind and cur_kind[0] == h["hkind"] and h["hkind"] in ("anotatsiia", "dodatky"):
                    continue
                if cur_kind and key == cur_kind and h["hkind"] == "rozdil":
                    continue
                cuts.append(k)
                cur_kind = key
        if len(cuts) >= 2:
            parts = []
            pre = blocks[:cuts[0]]
            if len([b for b in pre if b["text"].strip()]) >= 3:
                parts.append(Part(pre, f"{name}:tytul", fmt, kind="tytul", cpp=cpp))
            for a, b in zip(cuts, cuts[1:] + [len(blocks)]):
                seg = blocks[a:b]
                h = seg[0]["heading"]
                parts.append(Part(seg, f"{name}:{h['hkind']}{h['chapter'] or ''}", fmt, cpp=cpp))
            return parts
    return [Part(blocks, name, fmt, kind=kind, chapter=chapter, cpp=cpp)]


def load_parts(path: Path, kind: str | None = None, chapter: int | None = None, split: bool = True,
               cpp: int = CHARS_PER_PAGE) -> list[Part]:
    text, fmt = load_text(path)
    blocks = parse_blocks(text, fmt)
    if not any(b["text"].strip() for b in blocks):
        raise BrickError(f"{Path(path).name}: порожній документ")
    return make_parts(blocks, Path(path).name, fmt, kind, chapter, split, cpp)


# ---------------------------------------------------------------- reporting

class Report:
    SEV = ("ERROR", "WARN", "INFO")

    def __init__(self):
        self.items: list[dict] = []
        self.prefix = ""

    def add(self, severity: str, code: str, message: str, location: str = ""):
        loc = f"{self.prefix} · {location}" if self.prefix and location and location != self.prefix else (location or self.prefix)
        self.items.append({"severity": severity, "code": code, "message": message, "location": loc})

    def counts(self) -> dict:
        return {lv: sum(1 for i in self.items if i["severity"] == lv) for lv in self.SEV}

    def print_lines(self):
        order = {s: k for k, s in enumerate(self.SEV)}
        for it in sorted(self.items, key=lambda x: (order[x["severity"]], x["code"])):
            loc = f" [{it['location']}]" if it["location"] else ""
            print(f"{it['severity']:<5} {it['code']}{loc} {it['message']}")

    def summary_line(self) -> str:
        c = self.counts()
        return f"SUMMARY: {c['ERROR']} error(s), {c['WARN']} warning(s), {c['INFO']} info"
