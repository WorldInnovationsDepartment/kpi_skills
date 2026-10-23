"""Shared helpers for the asac-paper-format scripts (build_paper.py, check_paper.py).

Not a standalone script: build_paper.py and check_paper.py import it from their
own directory (Python puts a script's directory first on sys.path), so it must
stay next to them and must only import the standard library plus PyYAML, which
both scripts already declare in their PEP 723 headers.

Holds everything both scripts need to agree on: the manuscript source format
(Markdown body + YAML front matter), the journal's fixed labels in both
languages, author-name derivation, the tiny inline-markup parser used for YAML
strings, and citation/year extraction.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

JOURNAL_URL = "https://asac.kpi.ua"
ISSN = "1560-8956"

# Fixed journal formatting (Керівництво для авторів + official sample_*.docx).
FONT = "Times New Roman"
FONT_SIZE_PT = 13
LINE_SPACING = 1.3
MARGIN_MM = 25.0
PAGE_W_MM = 210.0
PAGE_H_MM = 297.0
FIRST_LINE_INDENT_MM = 12.5  # paragraph indent used throughout the official samples
TEXT_WIDTH_MM = PAGE_W_MM - 2 * MARGIN_MM

LANGS = ("uk", "en")
ARTICLE_TYPES = ("original", "review", "short")

LABELS = {
    "en": {
        "udc": "UDC",
        "abstract": "Abstract",
        "keywords": "Keywords",
        "figure": "Figure",
        "table": "Table",
        "references": "REFERENCES",
        "acknowledgements": "Acknowledgements",
        "disclosure": "Disclosure of interests",
        "counts": "Ref. {refs}, fig. {figs}, tab. {tabs}",
        "journal": "Interdepartmental scientific-technical journal «Adaptive systems of automatic control»",
        "pages": "p.",
        "where": "where",
    },
    "uk": {
        "udc": "УДК",
        "abstract": "Анотація",
        "keywords": "Ключові слова",
        "figure": "Рисунок",
        "table": "Таблиця",
        "references": "СПИСОК ВИКОРИСТАНИХ ДЖЕРЕЛ",
        "acknowledgements": "Подяки",
        "disclosure": "Розкриття інтересів",
        "counts": "Бібл. {refs}, іл. {figs}, табл. {tabs}",
        "journal": "Міжвідомчий науково-технічний збірник «Адаптивні системи автоматичного управління»",
        "pages": "с.",
        "where": "де",
    },
}

# Structured-abstract parts, in the order the author guide prescribes.
ABSTRACT_PARTS = (
    ("problem", {"uk": "Проблематика", "en": "Background"}),
    ("purpose", {"uk": "Мета", "en": "Objective"}),
    ("methods", {"uk": "Методика реалізації", "en": "Methods"}),
    ("results", {"uk": "Результати", "en": "Results"}),
    ("conclusions", {"uk": "Висновки", "en": "Conclusions"}),
)

FUNDING_PREFIX = {"uk": "Ця робота була підтримана", "en": "This work was supported"}

_FRONT_MATTER_RE = re.compile(r"\A﻿?---[ \t]*\r?\n(.*?)\r?\n(?:---|\.\.\.)[ \t]*(?:\r?\n|\Z)", re.S)


class SourceError(Exception):
    """The manuscript source is unusable (bad/missing front matter or required field)."""


@dataclass
class Source:
    path: Path
    meta: dict
    body: str
    body_offset_line: int = 0  # 1-based line number where the body starts in the file
    problems: list[str] = field(default_factory=list)


def load_source(path: Path) -> Source:
    text = path.read_text(encoding="utf-8")
    m = _FRONT_MATTER_RE.match(text)
    if not m:
        raise SourceError(f"{path}: no YAML front matter (the file must start with a '---' line)")
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        raise SourceError(f"{path}: invalid YAML front matter: {exc}") from exc
    if not isinstance(meta, dict):
        raise SourceError(f"{path}: YAML front matter must be a mapping")
    body = text[m.end():]
    return Source(path=path, meta=meta, body=body, body_offset_line=text[: m.end()].count("\n") + 1)


def text_of(value) -> str:
    """Plain text of a string or a structured-abstract mapping."""
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(str(value.get(k) or "").strip() for k, _ in ABSTRACT_PARTS).strip()
    return str(value).strip()


def required_errors(meta: dict) -> list[str]:
    """Fields without which build_paper.py cannot produce a submission file."""
    errs: list[str] = []
    lang = meta.get("language")
    if lang not in LANGS:
        errs.append(f"language: must be one of {', '.join(LANGS)} (got {lang!r})")
    if meta.get("article_type", "original") not in ARTICLE_TYPES:
        errs.append(f"article_type: must be one of {', '.join(ARTICLE_TYPES)}")
    if not str(meta.get("udc") or "").strip():
        errs.append("udc: missing (UDC/УДК code, e.g. \"004.89\")")
    for lg in LANGS:
        if not str(meta.get(f"title_{lg}") or "").strip():
            errs.append(f"title_{lg}: missing (the journal needs the title in both languages)")
        if not text_of(meta.get(f"abstract_{lg}")):
            errs.append(f"abstract_{lg}: missing (200-250 word structured abstract in both languages)")
        kws = meta.get(f"keywords_{lg}")
        if not isinstance(kws, list) or not [k for k in kws if str(k).strip()]:
            errs.append(f"keywords_{lg}: missing or not a list")
    authors = meta.get("authors")
    if not isinstance(authors, list) or not authors:
        errs.append("authors: missing or empty list")
    else:
        for i, a in enumerate(authors):
            if not isinstance(a, dict):
                errs.append(f"authors[{i}]: must be a mapping")
                continue
            for f in ("surname_uk", "name_uk", "surname_en", "name_en"):
                if not str(a.get(f) or "").strip():
                    errs.append(f"authors[{i}].{f}: missing")
    refs = meta.get("references")
    if not isinstance(refs, list) or not [r for r in refs if str(r).strip()]:
        errs.append("references: missing or empty list")
    for key in ("abstract_uk", "abstract_en"):
        v = meta.get(key)
        if isinstance(v, dict):
            unknown = set(v) - {k for k, _ in ABSTRACT_PARTS}
            if unknown:
                errs.append(f"{key}: unknown part(s) {sorted(unknown)}; allowed: {[k for k, _ in ABSTRACT_PARTS]}")
    return errs


# ---------------------------------------------------------------- author names

def _initial(name: str) -> str:
    name = name.strip()
    if not name:
        return ""
    # Hyphenated given names keep both initials (e.g. Анна-Марія -> А.-М.).
    return "-".join(part[:1].upper() + "." for part in name.split("-") if part)


def author_short(a: dict, lang: str) -> str:
    """'О. Гавриленко' / 'O. Gavrylenko' -- the byline form used under the UDC."""
    return f"{_initial(a.get(f'name_{lang}', ''))} {a.get(f'surname_{lang}', '').strip()}".strip()


def author_bib(a: dict, lang: str) -> str:
    """'Гавриленко О.О.' / 'Gavrylenko O.' -- the form used in the end-matter citation line."""
    inits = _initial(a.get(f"name_{lang}", ""))
    if lang == "uk":
        inits += _initial(a.get("patronymic_uk", "") or "")
    return f"{a.get(f'surname_{lang}', '').strip()} {inits}".strip()


def author_full(a: dict, lang: str) -> str:
    parts = [a.get(f"surname_{lang}", ""), a.get(f"name_{lang}", "")]
    if lang == "uk":
        parts.append(a.get("patronymic_uk", "") or "")
    return " ".join(p.strip() for p in parts if p and p.strip())


# ---------------------------------------------------------------- inline markup

_INLINE_RE = re.compile(r"(\*\*.+?\*\*|\*[^*\s][^*]*?\*)")


def inline_segments(text: str) -> list[tuple[str, bool, bool]]:
    """Split a YAML string with **bold** / *italic* markup into (text, bold, italic) runs.

    Only asterisks are markup: underscores are left alone because they occur in
    URLs and DOIs that reference lists are full of.
    """
    out: list[tuple[str, bool, bool]] = []
    for tok in _INLINE_RE.split(str(text)):
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
            out.append((tok[2:-2], True, False))
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            out.append((tok[1:-1], False, True))
        else:
            out.append((tok, False, False))
    return out


def strip_markup(text: str) -> str:
    return "".join(t for t, _, _ in inline_segments(text))


# ---------------------------------------------------------------- citations / years

_CITE_RE = re.compile(r"(?<![!\w])\[(\d+(?:\s*[-–—,;]\s*\d+)*)\](?!\()")


def citation_numbers(group: str) -> list[int]:
    nums: list[int] = []
    for part in re.split(r"\s*[,;]\s*", group):
        rng = re.split(r"\s*[-–—]\s*", part)
        if len(rng) == 2 and rng[0].isdigit() and rng[1].isdigit():
            lo, hi = int(rng[0]), int(rng[1])
            if lo <= hi and hi - lo < 200:
                nums.extend(range(lo, hi + 1))
                continue
        nums.extend(int(x) for x in rng if x.isdigit())
    return nums


def find_citations(body: str) -> list[tuple[int, int]]:
    """(position, reference number) for every numeric citation in reading order."""
    out: list[tuple[int, int]] = []
    for m in _CITE_RE.finditer(body):
        for n in citation_numbers(m.group(1)):
            out.append((m.start(), n))
    return out


_ACCESS_DATE_RE = re.compile(
    r"\((?:[^()]*?(?:дата звернення|application date|accessed|access date|дата обращения)[^()]*)\)", re.I
)
_URL_RE = re.compile(r"(?:https?://|doi:\s*|DOI:\s*|www\.)\S+", re.I)
_YEAR_RE = re.compile(r"(?<!\d)(19[5-9]\d|20\d{2})(?!\d)")


def reference_year(ref: str) -> int | None:
    """Best-effort publication year: the first plausible year once URLs/DOIs/access dates are removed."""
    s = _ACCESS_DATE_RE.sub(" ", str(ref))
    s = _URL_RE.sub(" ", s)
    m = _YEAR_RE.search(s)
    return int(m.group(1)) if m else None


def has_doi(ref: str) -> bool:
    return bool(re.search(r"doi\.org/10\.|\bdoi\s*:?\s*10\.|\b10\.\d{4,9}/\S+", str(ref), re.I))


# ---------------------------------------------------------------- markdown body structure

@dataclass
class Section:
    title: str
    level: int
    start: int  # char offset of the heading line in the body
    end: int
    text: str


def strip_code(body: str) -> str:
    """Blank out fenced code blocks (keeping offsets) so headings/citations inside them are ignored."""
    return re.sub(r"(?ms)^(```|~~~).*?^\1[ \t]*$", lambda m: re.sub(r"[^\n]", " ", m.group(0)), body)


def sections(body: str, level: int = 1) -> list[Section]:
    clean = strip_code(body)
    # The [ \t]+ after exactly `level` hashes already excludes deeper headings ('## X' for level 1).
    heads = [(m.start(), m.group(2).strip())
             for m in re.finditer(r"(?m)^(#{%d})[ \t]+(.+?)[ \t#]*$" % level, clean)]
    out: list[Section] = []
    for i, (pos, title) in enumerate(heads):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(body)
        out.append(Section(title=re.sub(r"\s*\{[^}]*\}\s*$", "", title), level=level, start=pos, end=end,
                           text=body[pos:end]))
    return out


SECTION_KINDS = {
    "introduction": ("introduction", "вступ"),
    "methods": ("method", "materials", "методи", "методика", "матеріали"),
    "results": ("result", "experiment", "результат", "експеримент"),
    "discussion": ("discussion", "обговорення"),
    "conclusions": ("conclusion", "висновк"),
}


def section_kind(title: str) -> str | None:
    t = title.lower()
    for kind, needles in SECTION_KINDS.items():
        if any(n in t for n in needles):
            return kind
    return None


IMAGE_RE = re.compile(r"!\[(?P<alt>(?:[^\[\]]|\[[^\]]*\])*)\]\((?P<src>[^)\s]+)(?:\s+\"[^\"]*\")?\)(?P<attr>\{[^}]*\})?")
DISPLAY_MATH_RE = re.compile(r"\$\$(.+?)\$\$", re.S)


def table_blocks(body: str) -> list[tuple[int, str]]:
    """(offset, caption) for each pipe/grid table, using pandoc's 'Table: x' / ': x' caption syntax."""
    clean = strip_code(body)
    lines = clean.split("\n")
    offsets, pos = [], 0
    for ln in lines:
        offsets.append(pos)
        pos += len(ln) + 1
    out: list[tuple[int, str]] = []
    i = 0
    cap_re = re.compile(r"^\s*(?:Table)?:\s+(.+)$")
    while i < len(lines):
        if re.match(r"^\s*(\||\+[-=+:]+\+)", lines[i]):
            j = i
            while j < len(lines) and re.match(r"^\s*(\||\+)", lines[j]):
                j += 1
            caption = ""
            k = i - 1
            while k >= 0 and not lines[k].strip():
                k -= 1
            if k >= 0 and cap_re.match(lines[k]):
                caption = cap_re.match(lines[k]).group(1).strip()
            else:
                k = j
                while k < len(lines) and not lines[k].strip():
                    k += 1
                if k < len(lines) and cap_re.match(lines[k]):
                    caption = cap_re.match(lines[k]).group(1).strip()
            out.append((offsets[i], caption))
            i = j
        else:
            i += 1
    return out
