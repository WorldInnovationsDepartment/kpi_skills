# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-pptx>=1.0",
#     "python-docx>=1.1",
#     "pymupdf>=1.24",
# ]
# ///
"""check_deck.py -- automatic content checks of a PhD seminar / defence talk for
specialty 121 «Інженерія програмного забезпечення» (F2) at Igor Sikorsky KPI.

    uv run check_deck.py talk.pptx
    uv run check_deck.py talk.ppt --minutes 20 --candidate Барабаш
    uv run check_deck.py talk.pdf --dissertation dissertation.docx --json findings.json

Accepts .pptx, .ppt/.odp/.key (converted with LibreOffice) and .pdf. Prints one
line per finding:

    ERROR <code> [слайд N]: ...   a requirement is violated -> fix before the seminar
    WARN  <code> [слайд N]: ...   a likely problem / typical reviewer objection
    INFO  <code>: ...             facts and reminders for the manual review

then the extracted structure and `SUMMARY: E error(s), W warning(s), I info`.
Exits 1 if there is any ERROR, 2 if the deck cannot be read, 0 otherwise.
Every rule, its severity and its source are listed in references/rules.md.
These are heuristics: the content review in SKILL.md decides, not this script.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deck_common import (  # noqa: E402
    SECTIONS,
    DeckError,
    classify_slide,
    is_mostly_upper,
    labelled_statement,
    load_deck,
    load_text,
    norm,
    numbered_items,
    section_map,
    translit,
    words,
)

SPECIALTY_RE = r"\b121\b|\bF2\b|\bF\s?2\b|інженері\w*\s+програмн\w+\s+забезпеч|software engineering"
OTHER_SPECIALTY_RE = r"\b(12[2-6]|151|141|144|F[13-7]|G\d{1,2})\s*[«\"(]"
UNIVERSITY_RE = r"кпі|київськ\w+ політехнічн|сікорськ|igor sikorsky|kyiv polytechnic"
DEGREE_RE = r"доктор\w*\s+філософ|ступен\w+|phd"
SUPERVISOR_RE = r"науков\w+\s+керівник|supervisor"
SUP_DEGREE_RE = r"д\.\s?т\.\s?н|к\.\s?т\.\s?н|д\.\s?ф\.-м|к\.\s?ф\.-м|доктор\w*\s+(технічн|фізико|економ|наук)|кандидат\w*\s+\w+\s+наук|професор|доцент|phd|dr\.?\s?sc"
YEAR_RE = r"\b20[2-3]\d\b"

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

# Russianisms / calques that councils and reviewers routinely flag.
# (pattern, suggestion). Patterns are matched on the lower-cased text.
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

DEFAULT_MINUTES = 20
MIN_PUBLICATIONS = 3     # Порядок присудження ступеня доктора філософії (КМУ №44), п. 8 -- requirements.md §1
MAX_WORDS_PER_SLIDE = 160
MIN_FONT_PT_WIDESCREEN = 14  # on a 13.33" wide slide; scaled for other sizes


class Report:
    def __init__(self):
        self.items: list[dict] = []

    def add(self, level: str, code: str, msg: str, slide: int | None = None):
        self.items.append({"level": level, "code": code, "slide": slide, "message": msg})

    def counts(self):
        return {lv: sum(1 for i in self.items if i["level"] == lv) for lv in ("ERROR", "WARN", "INFO")}


def short(s: str, n: int = 110) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


# ---------------------------------------------------------------- title slide

NAME_RE = re.compile(
    r"\b([А-ЯІЇЄҐ][А-ЯІЇЄҐ'’ʼ-]{1,})\s+([А-ЯІЇЄҐ][а-яіїєґ'’ʼ-]+)\s+([А-ЯІЇЄҐ][а-яіїєґ'’ʼ-]+)"  # ПРІЗВИЩЕ Ім'я По батькові
    r"|\b([А-ЯІЇЄҐ][а-яіїєґ'’ʼ-]+)\s+([А-ЯІЇЄҐ][а-яіїєґ'’ʼ-]+)\s+([А-ЯІЇЄҐ][а-яіїєґ'’ʼ-]+(ович|івна|ївна|евич|овна))\b"
    r"|\b([А-ЯІЇЄҐ'’ʼ-]{2,})\s+[А-ЯІЇЄҐ'’ʼ-]{2,}\s+[А-ЯІЇЄҐ'’ʼ-]+(ОВИЧ|ІВНА|ЇВНА|ЕВИЧ|ОВНА)\b"  # ПРІЗВИЩЕ ІМ'Я ПО БАТЬКОВІ
)


def title_info(deck: dict) -> dict:
    s = deck["slides"][0]
    paras = s["paragraphs"]
    info = {"topic": "", "candidate": "", "supervisor_lines": []}
    sup_i = None
    for i, p in enumerate(paras):
        if re.search(SUPERVISOR_RE, norm(p)):
            sup_i = i
            info["supervisor_lines"] = paras[i: i + 6]
            break
    excluded = UNIVERSITY_RE + r"|міністерств|ministry|спеціальн|specialty|дисертац|dissertation|керівник|supervisor|" \
        + SUP_DEGREE_RE + r"|київ\s*[-–—]?\s*20|^\s*20\d\d\s*$|науков\w+ семінар|кафедр|факультет|інститут|здобувач|аспірант"
    for i, p in enumerate(paras):
        if sup_i is not None and i >= sup_i:
            break
        m = NAME_RE.search(p)
        if m and len(words(p)) <= 6:
            g = m.groups()
            # Surname first ("БАРАБАШ Андрій Олегович", "Барабаш Андрій Олегович", all caps).
            surname = g[0] or g[3] or g[7] or ""
            info["candidate"] = surname.strip().capitalize() if surname.isupper() else surname.strip()
            break
    cands = [p for p in paras if len(p) > 20 and not re.search(excluded, norm(p)) and not NAME_RE.fullmatch(p.strip())]
    if cands:
        info["topic"] = max(cands, key=len).strip()
    return info


def check_title(deck, rep: Report, args) -> dict:
    s = deck["slides"][0]
    t = norm(s["text"])
    info = title_info(deck)
    if not re.search(UNIVERSITY_RE, t):
        rep.add("ERROR", "T01", "на титульному слайді немає назви закладу (КПІ ім. Ігоря Сікорського)", 1)
    full = norm("\n".join(x["text"] for x in deck["slides"][:2]))
    if not re.search(SPECIALTY_RE, full, re.I):
        rep.add("ERROR", "T02", "на титульному слайді немає спеціальності «121 Інженерія програмного забезпечення» (F2)", 1)
    other = re.search(OTHER_SPECIALTY_RE, s["text"])
    if other and not re.search(SPECIALTY_RE, t, re.I):
        rep.add("ERROR", "T02", f"вказано іншу спеціальність ({other.group(1)}); ця перевірка лише для 121 / F2", 1)
    if not re.search(DEGREE_RE, t):
        rep.add("WARN", "T03", "не вказано, що це дисертація на здобуття ступеня доктора філософії", 1)
    if not re.search(SUPERVISOR_RE, t):
        rep.add("ERROR", "T04", "на титульному слайді немає наукового керівника", 1)
    elif not re.search(SUP_DEGREE_RE, norm(" ".join(info["supervisor_lines"]))):
        rep.add("WARN", "T05", "у наукового керівника не вказано науковий ступінь і вчене звання (д.т.н., професор ...)", 1)
    if args.candidate:
        info["candidate"] = args.candidate
    if not info["candidate"]:
        rep.add("WARN", "T06", "не вдалося знайти ПІБ здобувача на титульному слайді (ПРІЗВИЩЕ Ім'я По батькові); "
                "передайте --candidate, щоб перевірити авторство публікацій", 1)
    if not re.search(YEAR_RE, s["text"]):
        rep.add("WARN", "T07", "на титульному слайді немає міста й року (наприклад, «Київ – 2026»)", 1)
    if not info["topic"]:
        rep.add("WARN", "T08", "не вдалося визначити тему дисертації на титульному слайді", 1)
    elif len(info["topic"]) > 300:
        rep.add("WARN", "T08", f"тема дуже довга ({len(info['topic'])} символів) — перевірте, чи збігається з затвердженою", 1)
    return info


# ---------------------------------------------------------------- structure

REQUIRED = ["relevance", "object", "subject", "aim", "tasks", "novelty", "conclusions", "publications"]
RECOMMENDED = ["methods", "practical", "approbation"]
OPTIONAL = ["analysis", "contribution", "connection", "thanks"]


def check_structure(deck, sm, rep: Report):
    for k in REQUIRED:
        if not sm[k]:
            rep.add("ERROR", "S01", f"немає обов'язкового елемента: {SECTIONS[k][2]}")
    for k in RECOMMENDED:
        if not sm[k]:
            rep.add("WARN", "S02", f"немає рекомендованого елемента: {SECTIONS[k][2]}")
    for k in OPTIONAL:
        if not sm[k]:
            rep.add("INFO", "S03", f"немає слайда/пункту: {SECTIONS[k][2]}")
    n = deck["slide_count"]
    first = {k: min(v) for k, v in sm.items() if v}
    order = ["relevance", "aim", "tasks", "novelty", "conclusions"]
    present = [k for k in order if k in first]
    for a, b in zip(present, present[1:]):
        if first[a] > first[b]:
            rep.add("WARN", "S04", f"порядок: «{SECTIONS[a][2]}» (слайд {first[a]}) іде після "
                    f"«{SECTIONS[b][2]}» (слайд {first[b]})", first[a])
    if "relevance" in first and first["relevance"] > max(3, n // 3):
        rep.add("WARN", "S04", "актуальність має бути на початку доповіді", first["relevance"])
    if "conclusions" in first and first["conclusions"] < n * 0.5:
        rep.add("WARN", "S04", "висновки стоять у першій половині доповіді", first["conclusions"])


# ---------------------------------------------------------------- statements

def check_statements(deck, rep: Report) -> dict:
    st = {k: labelled_statement(deck, k) for k in ("object", "subject", "aim", "methods")}
    obj, subj, aim = st["object"], st["subject"], st["aim"]
    if obj and subj:
        o, s = norm(obj[1]), norm(subj[1])
        if difflib.SequenceMatcher(None, o, s).ratio() > 0.9:
            rep.add("ERROR", "O01", "предмет дослідження збігається з об'єктом", subj[0])
        ow = {w[:5] for w in words(o) if len(w) > 4}
        sw = {w[:5] for w in words(s) if len(w) > 4}
        if ow and len(ow & sw) / len(ow) < 0.25:
            rep.add("WARN", "O02", "предмет майже не має спільних понять з об'єктом — предмет має бути частиною "
                    "(аспектом) об'єкта", subj[0])
        if re.match(r"\s*(процес|процеси)\b", s) and not re.match(r"\s*(процес|процеси)\b", o):
            rep.add("WARN", "O03", "предмет сформульовано як процес, а об'єкт — ні: зазвичай об'єкт — процес/явище, "
                    "предмет — моделі, методи, засоби", subj[0])
    if aim:
        a = norm(aim[1])
        if re.match(r"\s*(розроб|дослід|створ|вивч|аналіз)\w*", a) and not re.search(r"шляхом|за рахунок|для\b", a):
            rep.add("WARN", "O04", "мета сформульована як дія («розробити…»), а не як результат (наприклад, «підвищення "
                    "ефективності … шляхом розроблення …»)", aim[0])
    return {k: (v[1] if v else None) for k, v in st.items()}


def check_tasks_novelty_conclusions(deck, rep: Report) -> dict:
    tasks = numbered_items(deck, "tasks")
    novelty = numbered_items(deck, "novelty", min_len=40)
    concl = numbered_items(deck, "conclusions", min_len=30)

    for i, t in tasks:
        if not re.match(INFINITIVE_RE, norm(t)):
            rep.add("WARN", "K01", f"завдання не сформульоване інфінітивом («провести», «розробити»…): «{short(t, 70)}»", i)
    if tasks and concl and len(concl) < len(tasks):
        rep.add("WARN", "K02", f"висновків ({len(concl)}) менше, ніж завдань ({len(tasks)}): кожне завдання має "
                "отримати висновок")
    if tasks and novelty and len(novelty) > len(tasks):
        rep.add("WARN", "K03", f"пунктів новизни ({len(novelty)}) більше, ніж завдань ({len(tasks)})")

    for i, t in novelty:
        n = norm(t)
        if not re.search(GRADATION_RE, n):
            rep.add("WARN", "N01", f"пункт новизни без ступеня новизни («вперше», «удосконалено», «набуло подальшого "
                    f"розвитку»): «{short(t, 70)}»", i)
        if not re.search(DISTINCT_RE, n):
            rep.add("WARN", "N02", f"пункт новизни не каже, чим відрізняється від відомих («який відрізняється тим, "
                    f"що…»): «{short(t, 70)}»", i)
        if not re.search(EFFECT_RE, n):
            rep.add("WARN", "N03", f"пункт новизни не називає ефекту («що дозволило…»): «{short(t, 70)}»", i)
        if re.search(r"програмн\w*\s+(забезпеч|застосун|додат|продукт|комплекс)", n) and not re.search(ARCH_RE, n):
            rep.add("WARN", "N06", f"«розроблено програмне забезпечення» без архітектурної новизни — це практичне значення; "
                    f"сформулюйте як архітектуру або перенесіть: «{short(t, 70)}»", i)
        if not re.search(QUANT_RE, n):
            rep.add("INFO", "N07", f"у пункті новизни ефект без числа: «{short(t, 70)}»", i)
        if re.search(r"вперше", n) and re.search(r"удоскона|подальш", n):
            rep.add("WARN", "N04", f"в одному пункті змішано «вперше» та «удосконалено/подальшого розвитку»", i)
    if novelty and not (2 <= len(novelty) <= 5):
        rep.add("INFO", "N05", f"пунктів наукової новизни: {len(novelty)} (типово 2–4)")

    # 121-specific: one scientific result must be a software architecture.
    arch_items = [(i, t) for i, t in novelty if re.search(ARCH_RE, norm(t))]
    arch_slides = [s for s in deck["slides"] if re.search(ARCH_RE, norm(s["title"] + " " + s["text"]))]
    if novelty and not arch_items:
        where = f" (архітектура згадується на слайдах {', '.join(str(s['index']) for s in arch_slides[:6])}, але не як " \
                "науковий результат)" if arch_slides else ""
        rep.add("ERROR", "A01", "серед наукових результатів немає архітектури програмного забезпечення — для 121 у КПІ "
                "один із результатів має бути архітектурою (напр., «удосконалено архітектуру … системи, яка "
                "відрізняється …»)" + where, min(i for i, _ in novelty))
    for i, t in arch_items:
        if not re.search(DISTINCT_RE, norm(t)):
            rep.add("WARN", "A02", "архітектурний результат не каже, чим ця архітектура відрізняється від відомих "
                    "(компоненти, зв'язки, принцип взаємодії)", i)
    has_diagram = [s for s in arch_slides if s["index"] != 1 and (s["pictures"] or s["shapes"] >= 6)]
    titled = [s for s in has_diagram if re.search(ARCH_RE, norm(s["title"]))]
    captioned = [s for s in has_diagram
                 if re.search(r"(рис\.?|рисунок|fig\.?)\s*[\d.]*\s*[.:–-]?\s*.{0,60}" + ARCH_RE, norm(s["text"]))]
    if not titled:
        hint = (f" (на слайдах {', '.join(str(s['index']) for s in captioned)} є рисунок з підписом про архітектуру — "
                "винесіть «Архітектура …» у заголовок)") if captioned else ""
        rep.add("WARN", "A03", "немає слайда з діаграмою архітектури, де заголовок називає її архітектурою (схема "
                "компонентів/розгортання/потоків даних)" + hint, captioned[0]["index"] if captioned else None)
    se_items = [t for _, t in novelty if re.search(SE_RE, norm(t))]
    if novelty and len(se_items) < max(1, len(novelty) // 2):
        rep.add("WARN", "A04", f"лише {len(se_items)} з {len(novelty)} пунктів новизни прямо стосуються розроблення ПЗ — "
                "ризик питання про відповідність спеціальності 121")

    if concl and not re.search(r"подальш\w*\s+(дослідж|робот|розвит)|перспектив|future work", norm(" ".join(t for _, t in concl))):
        rep.add("WARN", "C01", "у висновках немає напрямів подальших досліджень (наказ МОН № 40, п. 10)",
                concl[-1][0])
    copies = [(ci, ct) for ci, ct in concl
              if any(difflib.SequenceMatcher(None, norm(ct)[:200], norm(nt)[:200]).ratio() > 0.85 for _, nt in novelty)]
    if copies:
        rep.add("INFO", "C02", f"{len(copies)} висновків майже дослівно повторюють пункти новизни — висновки мають "
                "давати результати з числами", copies[0][0])
    quant_scope = " ".join(t for _, t in novelty + concl)
    if (novelty or concl) and not re.search(QUANT_RE, norm(quant_scope)):
        rep.add("WARN", "Q01", "у новизні та висновках немає жодного кількісного результату (%, «у N разів», мс …)")
    elif concl and not re.search(QUANT_RE, norm(" ".join(t for _, t in concl))):
        rep.add("WARN", "Q02", "у висновках немає кількісних показників ефекту")
    return {"tasks": [t for _, t in tasks], "novelty": [t for _, t in novelty], "conclusions": [t for _, t in concl]}


# ---------------------------------------------------------------- publications

PUB_ENTRY_RE = re.compile(r"(\b(19|20)\d\d\b).*(\b[СC]\.\s*\d|\bP\.\s*\d|\bpp\.|\bс\.\s*\d|№|Vol|Т\.\s*\d|DOI|ISSN)", re.I)


def check_publications(deck, sm, info, rep: Report) -> dict:
    entries = []
    for i in sm["publications"]:
        for p in deck["slides"][i - 1]["paragraphs"]:
            if len(p) > 40 and PUB_ENTRY_RE.search(p):
                entries.append((i, p))
    # PDF lines may be split from their bibliographic tail; still count numbered items.
    if not entries:
        for i in sm["publications"]:
            for p in deck["slides"][i - 1]["paragraphs"]:
                if re.match(r"^\s*\d{1,2}[.)]\s", p) and len(p) > 40:
                    entries.append((i, p))
    out = {"entries": [p for _, p in entries], "summary_line": None}
    if not sm["publications"]:
        return out
    summary = None
    for i in sm["publications"]:
        for p in deck["slides"][i - 1]["paragraphs"]:
            if re.search(r"за темою дисертації|опубліковано|publications", norm(p)) and re.search(r"\d", p):
                summary = p
    out["summary_line"] = summary
    if not summary:
        rep.add("WARN", "P01", "немає підсумкового рядка «За темою дисертації опубліковано N статей (з них …), M тез …»",
                sm["publications"][0])
    credits = [(i, p, *pub_credit(p)) for i, p in entries]
    total = sum(c for *_, c in credits)
    out["credits"] = [{"slide": i, "kind": k, "authors": a, "credit": c, "entry": short(p, 140)}
                      for i, p, k, a, c in credits]
    out["credit_total"] = total
    if len(entries) < MIN_PUBLICATIONS or total < MIN_PUBLICATIONS:
        rep.add("WARN", "P02", f"за п. 8 Порядку №44 потрібно ≥ {MIN_PUBLICATIONS} зарахованих публікацій; за оцінкою "
                f"скрипта на слайдах {total:g} ({len(entries)} записів; > 2 авторів у фаховому — 0,5, Q1–Q3 — 2, "
                "тези — 0). Перевірте вручну", sm["publications"][0])
    rep.add("INFO", "P07", "оцінка зарахування: " + "; ".join(f"{k} ({a} авт.) = {c:g}" for _, _, k, a, c in credits)
            + f"; разом {total:g}" if credits else "бібліографічних записів не розпізнано")
    seen_issue: dict[tuple, int] = {}
    for i, p, k, *_ in credits:
        key = issue_key(p)
        if k != "тези" and key:
            if key in seen_issue:
                rep.add("WARN", "P08", f"дві статті в одному випуску ({key[0]}, {key[1]} № {key[2]}) — п. 9 Порядку №44 "
                        "зараховує лише одну", i)
            seen_issue[key] = i
    no_doi = [p for _, p, k, *_ in credits if k not in ("тези", "патент") and "doi" not in norm(p)]
    if no_doi:
        rep.add("INFO", "P09", f"статей без DOI на слайді: {len(no_doi)} — п. 9 Порядку №44 зараховує статті лише з "
                "активним DOI (дату, з якої це діє для старих статей, уточніть на кафедрі); перевірте, що DOI є")
    cand = info.get("candidate")
    if cand:
        # Surname stem in Cyrillic or in its Latin transliteration (English-language papers).
        stems = {norm(cand)[: max(4, len(cand) - 2)], translit(cand)[: max(4, len(translit(cand)) - 2)]}
        for i, p in entries:
            if not any(st in norm(p) for st in stems):
                rep.add("WARN", "P03", f"у записі немає прізвища здобувача ({cand}) — неповний список авторів або чужа "
                        f"праця: «{short(p, 80)}»", i)
    idx = [p for _, p in entries if re.search(r"scopus|web of science|\bwos\b|\bq[1-4]\b", norm(p))]
    rep.add("INFO", "P04", f"записів з позначкою Scopus/WoS/Q: {len(idx)} з {len(entries)}")
    whole = norm(" ".join(s["text"] for s in deck["slides"]))
    if not re.search(r"акт\w*\s+(впровадж|реаліза|використ)|довідк\w*\s+про\s+(впровадж|використ)", whole):
        rep.add("WARN", "P05", "немає актів/довідок впровадження — для 121 рада майже завжди питає про практичне "
                "використання ПЗ")
    if not re.search(r"конференц|conference|семінар|форум|симпозіум", whole):
        rep.add("WARN", "P06", "не показано апробацію на конференціях")
    return out


AUTHOR_RE = re.compile(r"[A-ZА-ЯІЇЄҐ][a-zа-яіїєґ'’ʼ-]+,?\s+(?:[A-ZА-ЯІЇЄҐ]\.\s?){1,2}"
                       r"|(?:[A-ZА-ЯІЇЄҐ]\.\s?){1,2}[A-ZА-ЯІЇЄҐ][a-zа-яіїєґ'’ʼ-]+")


def count_authors(entry: str) -> int:
    """Authors at the head of a DSTU/APA-style entry: «Іваненко П.П., Petrenko O. …»."""
    body = re.sub(r"^\s*\d{1,2}[.)]\s*", "", entry)
    n, pos = 0, 0
    for m in AUTHOR_RE.finditer(body):
        if body[pos:m.start()].strip(" ,;&та and") and n:
            break
        n, pos = n + 1, m.end()
    return max(n, 1)


def pub_credit(entry: str) -> tuple[str, int, float]:
    """(kind, authors, credit) under п. 8 Порядку №44. Heuristic: an unmarked article is taken as a фахова one."""
    e, authors = norm(entry), count_authors(entry)
    if re.search(r"патент", e):
        return ("патент", authors, 1.0 if re.search(r"винах", e) else 0.0)
    if re.search(r"конференц|conference|proceedings|symposium|workshop|тез[иа]|матеріали\s+\w*\s*(міжнар|всеукр|науков)|форум", e):
        return ("тези", authors, 0.0)
    if re.search(r"\bq[1-3]\b", e):
        return ("Q1–Q3", authors, 2.0)
    if re.search(r"scopus|web of science|\bwos\b|\bq4\b", e):
        return ("Scopus/WoS", authors, 1.0)
    return ("фахова", authors, 0.5 if authors > 2 else 1.0)


def issue_key(entry: str) -> tuple | None:
    m = re.search(r"([^.]{3,80})\.\s*\(?((?:19|20)\d\d)\)?[.,]?\s*(?:(?:Т|Том|Vol)\.?\s*\d+[.,]?\s*)?(?:№|No\.?|Iss(?:ue)?\.?)\s*(\d+)", entry)
    return (norm(m.group(1))[:30], m.group(2), m.group(3)) if m else None


# ---------------------------------------------------------------- form & language

def check_form(deck, rep: Report, minutes: int):
    n = deck["slide_count"]
    if n > minutes * 1.5:
        rep.add("WARN", "F01", f"{n} слайдів на {minutes} хв доповіді — забагато (орієнтир ≈ 1 слайд/хв)")
    elif n < minutes * 0.5:
        rep.add("WARN", "F01", f"{n} слайдів на {minutes} хв доповіді — замало для повного викладу результатів")
    min_pt = MIN_FONT_PT_WIDESCREEN * (deck["slide_width_in"] or 13.33) / 13.33
    for s in deck["slides"]:
        if s["words"] > MAX_WORDS_PER_SLIDE:
            rep.add("WARN", "F02", f"{s['words']} слів на слайді — суцільний текст, з проєктора не прочитати", s["index"])
        small = [f for f in s["font_sizes"] if f < min_pt - 0.1]
        if small and s["words"] > 15:
            rep.add("WARN", "F03", f"шрифт {min(small):g} pt (менше ≈{min_pt:.0f} pt для цього розміру слайда)", s["index"])
        if re.search(PLACEHOLDER_RE, s["text"], re.I):
            rep.add("ERROR", "F05", f"залишився шаблонний/незаповнений текст: «{short(re.search(PLACEHOLDER_RE, s['text'], re.I).group(0), 40)}»",
                    s["index"])
    numbered = sum(1 for s in deck["slides"][1:] if s["has_slide_number"])
    if n > 1 and numbered < (n - 1) / 2:
        rep.add("WARN", "F04", "слайди не пронумеровані — члени ради посилаються на номер слайда в запитаннях")
    missing_title = [s["index"] for s in deck["slides"][1:] if not s["title"] and s["words"] > 10]
    if missing_title:
        rep.add("WARN", "F06", f"слайди без заголовка: {', '.join(map(str, missing_title))}")
    figs: dict[str, list[int]] = {}
    for s in deck["slides"]:
        for m in re.finditer(r"\b(?:рис|fig)\.?\s*(\d+(?:\.\d+)?)", s["text"], re.I):
            figs.setdefault(m.group(1), []).append(s["index"])
    dup = {k: sorted(set(v)) for k, v in figs.items() if len(set(v)) > 1}
    if dup:
        rep.add("WARN", "F08", "однаковий номер рисунка на різних слайдах: " + "; ".join(
            f"Рис. {k} — слайди {', '.join(map(str, v))}" for k, v in list(dup.items())[:6]))
    # A decimal point, not a date (16.01.2024), a figure number or a volume/page reference.
    dec_point = r"(?<![\d.])(?<!рис\.)(?<!рис\. )\d+\.\d+(?![\d.])(?!\.\d)"
    seps = {s["index"] for s in deck["slides"] if re.search(dec_point, norm(s["text"]))}
    if seps and any(re.search(r"(?<![\d,])\d+,\d+(?![\d,])", s["text"]) for s in deck["slides"]):
        rep.add("INFO", "L03", f"десяткова крапка і кома вперемішку (крапка на слайдах {', '.join(map(str, sorted(seps)[:8]))})")
    if not any(s["notes"] for s in deck["slides"]) and deck["format"] == "pptx":
        rep.add("INFO", "F07", "немає нотаток доповідача — текст доповіді варто тримати в нотатках")


def check_language(deck, rep: Report):
    hits: dict[str, tuple[str, list[int]]] = {}
    for s in deck["slides"]:
        t = norm(s["text"])
        for pat, tip in LANG_CHECKS:
            m = re.search(pat, t)
            if m:
                hits.setdefault(tip, (m.group(0), []))[1].append(s["index"])
    for tip, (example, slides) in hits.items():
        more = f" (також слайди {', '.join(map(str, slides[1:]))})" if len(slides) > 1 else ""
        rep.add("WARN", "L01", f"«{example}»: {tip}{more}", slides[0])
    # Abbreviations: uppercase tokens in normal (non-caps) sentences that are never expanded.
    defined, used = set(), {}
    for s in deck["slides"]:
        for p in s["paragraphs"]:
            for m in re.finditer(r"\(([A-ZА-ЯІЇЄҐ]{2,8})\)|\b([A-ZА-ЯІЇЄҐ]{2,8})\s*[–—-]\s+[а-яіїєґa-z]", p):
                defined.add(m.group(1) or m.group(2))
            if s["index"] == 1 or is_mostly_upper(p) or len(words(p)) < 6:
                continue  # title slide, headings and diagram labels
            for m in re.finditer(r"\b[A-ZА-ЯІЇЄҐ]{2,8}\b", p):
                tok = m.group(0)
                after = p[m.end():m.end() + 3]
                if tok in KNOWN_ABBR or re.fullmatch(r"[IVXLCІ]+", tok) or re.match(r"\s[А-ЯІЇЄҐ][а-яіїєґ]", after) \
                        or re.match(r"\s?[=(\[_]|\s?[a-zа-я]{1,2}\(", after) or s["shapes"] > 40:
                    continue  # known, roman numeral, surname, or an identifier in a formula/flowchart
                used.setdefault(tok, s["index"])
    undefined = {k: v for k, v in used.items() if k not in defined}
    for tok, i in sorted(undefined.items(), key=lambda kv: kv[1])[:15]:
        rep.add("WARN", "L02", f"абревіатура «{tok}» ніде не розшифрована", i)


# ---------------------------------------------------------------- cross-check with the dissertation

def diss_statement(text: str, key: str) -> str | None:
    pats = {
        "object": r"об['’ʼ]єкт\w*\s+дослідж\w*\s*[:–—-]?\s*(?:[–—-]\s*)?([^\n]+)",
        "subject": r"предмет\w*\s+дослідж\w*\s*[:–—-]?\s*(?:[–—-]\s*)?([^\n]+)",
        "aim": r"мет(а|ою)\s+(дисертаційної\s+)?(роботи|дослідж\w*)\s*(є\s*)?[:–—-]?\s*([^\n]+)",
    }
    m = re.search(pats[key], text, re.I)
    if not m:
        return None
    return m.group(m.lastindex).strip()


def check_against_dissertation(deck, info, stmts, struct, diss_path: Path, rep: Report):
    try:
        text = load_text(diss_path)
    except DeckError as e:
        rep.add("WARN", "X00", f"не вдалося прочитати дисертацію: {e}")
        return
    nt = norm(text)
    if info.get("topic"):
        topic = norm(info["topic"]).strip(' ."')
        if topic not in nt:
            best = max((difflib.SequenceMatcher(None, topic, nt[i:i + len(topic)]).ratio()
                        for i in range(0, max(1, min(len(nt), 20000) - len(topic)), 40)), default=0)
            lvl = "ERROR" if best < 0.9 else "WARN"
            rep.add(lvl, "X01", f"тема на титульному слайді не збігається дослівно з темою в дисертації "
                    f"(схожість {best:.0%}) — тема має бути точно як у затвердженому наказі", 1)
    for key, label in (("object", "об'єкт"), ("subject", "предмет"), ("aim", "мета")):
        d, s = diss_statement(text, key), stmts.get(key)
        if d and s:
            r = difflib.SequenceMatcher(None, norm(s), norm(d)[: len(s) + 40]).ratio()
            if r < 0.85:
                rep.add("WARN", "X02", f"{label} у презентації відрізняється від дисертації ({r:.0%}): "
                        f"«{short(s, 60)}» vs «{short(d, 60)}»")
    m = re.search(r"наукова новизна[^\n]*\n(.+?)(практичне значення|особистий внесок|апробац)", text, re.I | re.S)
    if m and struct["novelty"]:
        dn = norm(m.group(1))
        for t in struct["novelty"]:
            head = norm(t)[:120]
            best = max((difflib.SequenceMatcher(None, head, dn[i:i + len(head)]).ratio()
                        for i in range(0, max(1, len(dn) - len(head)), 25)), default=0)
            if best < 0.6:
                rep.add("WARN", "X03", f"пункт новизни не знайдено в розділі «Наукова новизна» дисертації: «{short(t, 70)}»")
    elif struct["novelty"]:
        rep.add("INFO", "X03", "у дисертації не знайдено розділ «Наукова новизна» для звірки")


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck", type=Path, help=".pptx / .ppt / .odp / .key / .pdf")
    ap.add_argument("--minutes", type=int, default=DEFAULT_MINUTES, help=f"тривалість доповіді, хв (default {DEFAULT_MINUTES})")
    ap.add_argument("--candidate", help="прізвище здобувача (якщо не розпізнано з титульного слайда)")
    ap.add_argument("--dissertation", type=Path, help="текст дисертації (.docx/.pdf/.md/.txt) для звірки")
    ap.add_argument("--json", type=Path, help="записати знахідки та витягнуту структуру в JSON")
    args = ap.parse_args(argv)

    try:
        deck = load_deck(args.deck)
    except DeckError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if not deck["slides"]:
        print(f"error: {args.deck.name}: no slides", file=sys.stderr)
        return 2

    rep = Report()
    sm = section_map(deck)
    info = check_title(deck, rep, args)
    check_structure(deck, sm, rep)
    stmts = check_statements(deck, rep)
    struct = check_tasks_novelty_conclusions(deck, rep)
    pubs = check_publications(deck, sm, info, rep)
    check_form(deck, rep, args.minutes)
    check_language(deck, rep)
    if args.dissertation:
        check_against_dissertation(deck, info, stmts, struct, args.dissertation, rep)

    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    for it in sorted(rep.items, key=lambda x: (order[x["level"]], x["slide"] or 0)):
        where = f" [слайд {it['slide']}]" if it["slide"] else ""
        print(f"{it['level']:<5} {it['code']}{where}: {it['message']}")

    print("\nSTRUCTURE:")
    print(f"  slides: {deck['slide_count']}  format: {deck['converted_from'] or deck['format']}  "
          f"size: {deck['slide_width_in']}x{deck['slide_height_in']} in")
    print(f"  candidate: {info.get('candidate') or '?'}")
    print(f"  topic: {short(info.get('topic') or '?', 160)}")
    for k, v in sm.items():
        print(f"  {k:<13} {', '.join(map(str, v)) if v else '—'}")
    for k in ("tasks", "novelty", "conclusions"):
        print(f"  {k}: {len(struct[k])}")
    print(f"  publication entries: {len(pubs['entries'])}")
    c = rep.counts()
    print(f"\nSUMMARY: {c['ERROR']} error(s), {c['WARN']} warning(s), {c['INFO']} info")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps({
            "deck": {k: deck[k] for k in ("source", "format", "converted_from", "slide_count",
                                          "slide_width_in", "slide_height_in")},
            "title": info, "sections": sm, "statements": stmts, **struct, "publications": pubs,
            "findings": rep.items, "summary": c,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if c["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main())
