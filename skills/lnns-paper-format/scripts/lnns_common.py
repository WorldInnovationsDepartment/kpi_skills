"""Shared helpers for the lnns-paper-format scripts (build_paper.py, check_paper.py, renumber_refs.py).

Not a standalone script: the other scripts import it from their own directory
(Python puts a script's directory first on sys.path), so it must stay next to
them and must only import the standard library plus PyYAML, which every
script that imports it declares in its PEP 723 header.

Holds everything the scripts need to agree on: the manuscript source format
(Markdown body + YAML front matter), the Springer proceedings layout constants
(taken from the official LaTeX class llncs.cls and the Word template
splnproc2510), author/affiliation handling, the tiny inline-markup parser used
for YAML strings, and citation/year extraction.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

SERIES = "Lecture Notes in Networks and Systems"
SERIES_URL = "https://link.springer.com/bookseries/15179"
ISSN = "2367-3370"

# Fixed Springer proceedings layout (splnproc2510 Word template; llncs.cls for LaTeX).
FONT = "Times New Roman"
PAGE_W_MM, PAGE_H_MM = 210.0, 297.0           # Word template: A4
MARGIN_TB_MM, MARGIN_LR_MM = 52.0, 44.0       # leaves the 122 x 193 mm text area
HEADER_MM, FOOTER_MM = 42.0, 41.0
TEXT_WIDTH_MM = PAGE_W_MM - 2 * MARGIN_LR_MM  # 122
TEXT_HEIGHT_MM = PAGE_H_MM - 2 * MARGIN_TB_MM  # 193
INDENT_MM = 227 / 1440 * 25.4                  # Normal: first-line indent 227 twips = 0.4 cm

SIZE = {  # pt
    "title": 14, "author": 10, "address": 9, "abstract": 9, "body": 10, "h1": 12, "h2": 10,
    "caption": 9, "reference": 9, "credits": 9, "table": 9, "code": 9,
}

CITATION_ORDERS = ("citation", "alphabetical")

# Abstract: "150--250 words" (samplepaper.tex). Keyword count is not fixed by Springer;
# the templates show three, conferences typically ask for 3-5 (see requirements.md).
ABSTRACT_WORDS = (150, 250)
KEYWORDS_RANGE = (3, 6)

DEFAULT_DISCLOSURE = ("The authors have no competing interests to declare that are relevant to the content "
                      "of this article.")

_FRONT_MATTER_RE = re.compile(r"\A﻿?---[ \t]*\r?\n(.*?)\r?\n(?:---|\.\.\.)[ \t]*(?:\r?\n|\Z)", re.S)


class SourceError(Exception):
    """The manuscript source is unusable (bad/missing front matter or required field)."""


@dataclass
class Source:
    path: Path
    meta: dict
    body: str
    front_text: str = ""
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
    return Source(path=path, meta=meta, body=text[m.end():], front_text=text[: m.end()])


def text_of(value) -> str:
    return "" if value is None else str(value).strip()


def references(meta: dict) -> list[str]:
    return [str(r).strip() for r in (meta.get("references") or []) if str(r).strip()]


def keywords(meta: dict) -> list[str]:
    return [str(k).strip() for k in (meta.get("keywords") or []) if str(k).strip()]


def citation_order(meta: dict) -> str:
    return str(meta.get("citation_order") or "citation").strip().lower()


def required_errors(meta: dict) -> list[str]:
    """Fields without which build_paper.py cannot produce a manuscript."""
    errs: list[str] = []
    if not text_of(meta.get("title")):
        errs.append("title: missing")
    if not text_of(meta.get("abstract")):
        errs.append("abstract: missing (150-250 words)")
    kws = meta.get("keywords")
    if not isinstance(kws, list) or not keywords(meta):
        errs.append("keywords: missing or not a list")
    if citation_order(meta) not in CITATION_ORDERS:
        errs.append(f"citation_order: must be one of {', '.join(CITATION_ORDERS)}")
    affs = meta.get("affiliations")
    if not isinstance(affs, list) or not affs:
        errs.append("affiliations: missing or empty list")
        affs = []
    authors = meta.get("authors")
    if not isinstance(authors, list) or not authors:
        errs.append("authors: missing or empty list")
    else:
        for i, a in enumerate(authors):
            if not isinstance(a, dict):
                errs.append(f"authors[{i}]: must be a mapping")
                continue
            for f in ("given", "family"):
                if not text_of(a.get(f)):
                    errs.append(f"authors[{i}].{f}: missing")
            inst = a.get("affiliations")
            if not isinstance(inst, list) or not inst:
                errs.append(f"authors[{i}].affiliations: list of affiliation numbers (1-based) required")
            else:
                for n in inst:
                    if not isinstance(n, int) or not 1 <= n <= len(affs):
                        errs.append(f"authors[{i}].affiliations: {n!r} is not an affiliation number 1..{len(affs)}")
    if not references(meta):
        errs.append("references: missing or empty list")
    return errs


# ---------------------------------------------------------------- authors / affiliations

def _initials(given: str) -> str:
    """'Danylo' -> 'D.', 'Anna-Maria' -> 'A.-M.', 'John Ronald' -> 'J. R.'"""
    out = []
    for word in given.split():
        out.append("-".join(p[:1].upper() + "." for p in word.split("-") if p))
    return " ".join(out)


def author_name(a: dict) -> str:
    return f"{text_of(a.get('given'))} {text_of(a.get('family'))}".strip()


def author_running(authors: list[dict]) -> str:
    """Running head: 'D. Vorvul', 'D. Vorvul and O. Petrenko', 'D. Vorvul et al.' (samplepaper.tex)."""
    short = [f"{_initials(text_of(a.get('given')))} {text_of(a.get('family'))}".strip() for a in authors]
    if len(short) == 1:
        return short[0]
    if len(short) == 2:
        return f"{short[0]} and {short[1]}"
    return f"{short[0]} et al."


def affiliation_text(aff) -> str:
    """An affiliation is a plain string or a mapping {department, organization, address, city, country}."""
    if isinstance(aff, dict):
        keys = ("department", "organization", "address", "city", "country")
        return ", ".join(text_of(aff.get(k)) for k in keys if text_of(aff.get(k)))
    return text_of(aff)


def affiliation_emails(meta: dict) -> dict[int, list[str]]:
    """1-based affiliation number -> e-mails of the authors whose first affiliation it is."""
    out: dict[int, list[str]] = {}
    for a in meta.get("authors") or []:
        if not isinstance(a, dict) or not text_of(a.get("email")):
            continue
        inst = a.get("affiliations") or []
        if inst and isinstance(inst[0], int):
            out.setdefault(inst[0], []).append(text_of(a.get("email")))
    return out


def normalize_orcid(value) -> str:
    return text_of(value).removeprefix("https://orcid.org/").removeprefix("http://orcid.org/")


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


# ---------------------------------------------------------------- citations / references

CITE_RE = re.compile(r"(?<![!\w\\])\[(\d+(?:\s*[-–—,;]\s*\d+)*)\](?![(:])")


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
    """(position, reference number) for every numeric citation in reading order (code and math excluded)."""
    clean = strip_math(strip_code(body))
    out: list[tuple[int, int]] = []
    for m in CITE_RE.finditer(clean):
        for n in citation_numbers(m.group(1)):
            out.append((m.start(), n))
    return out


def format_citation(nums: list[int]) -> str:
    """[1, 2, 3, 5] -> '[1–3, 5]' (Springer: '[4–6, 9]')."""
    nums = sorted(set(nums))
    parts, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        if j - i >= 2:
            parts.append(f"{nums[i]}–{nums[j]}")
        else:
            parts.extend(str(n) for n in nums[i:j + 1])
        i = j + 1
    return "[" + ", ".join(parts) + "]"


_ACCESS_RE = re.compile(r"(?:last\s+)?accessed\s*:?\s*[\d/.\-]+|\(accessed[^)]*\)", re.I)
_URL_RE = re.compile(r"(?:https?://|doi:\s*|DOI:\s*|www\.)\S+", re.I)
_YEAR_RE = re.compile(r"(?<!\d)(19[5-9]\d|20\d{2})(?!\d)")


def reference_year(ref: str) -> int | None:
    """Best-effort publication year. splncs04 puts it in parentheses at the end: '... Springer, Cham (2024)'."""
    s = _ACCESS_RE.sub(" ", str(ref))
    s = _URL_RE.sub(" ", s)
    paren = re.findall(r"\((?:[^()]*?\s)?(19[5-9]\d|20\d{2})[a-z]?\)", s)
    if paren:
        return int(paren[-1])
    m = _YEAR_RE.search(s)
    return int(m.group(1)) if m else None


def has_doi(ref: str) -> bool:
    return bool(re.search(r"doi\.org/10\.|\bdoi\s*:?\s*10\.|\b10\.\d{4,9}/\S+", str(ref), re.I))


def sort_key(ref: str) -> str:
    """Alphabetical order key as splncs04 sorts: first author surname, then the rest."""
    s = strip_markup(ref).lower()
    return re.sub(r"[^\w\s]", "", s, flags=re.U)


# ---------------------------------------------------------------- markdown body structure

def strip_code(body: str) -> str:
    """Blank out fenced code blocks (keeping offsets) so headings/citations inside them are ignored."""
    return re.sub(r"(?ms)^(```|~~~).*?^\1[ \t]*$", lambda m: re.sub(r"[^\n]", " ", m.group(0)), body)


def strip_math(body: str) -> str:
    """Blank out $...$ and $$...$$ (keeping offsets)."""
    return re.sub(r"\$\$.+?\$\$|(?<![\\$])\$[^$\n]+\$", lambda m: re.sub(r"[^\n]", " ", m.group(0)), body,
                  flags=re.S)


@dataclass
class Section:
    title: str
    level: int
    start: int
    end: int
    text: str


def sections(body: str, level: int = 1) -> list[Section]:
    clean = strip_code(body)
    heads = [(m.start(), m.group(2).strip())
             for m in re.finditer(r"(?m)^(#{%d})[ \t]+(.+?)[ \t#]*$" % level, clean)]
    out: list[Section] = []
    for i, (pos, title) in enumerate(heads):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(body)
        out.append(Section(title=re.sub(r"\s*\{[^}]*\}\s*$", "", title), level=level, start=pos, end=end,
                           text=body[pos:end]))
    return out


SECTION_KINDS = {
    "introduction": ("introduction",),
    "related": ("related work", "literature review", "background", "state of the art", "related research"),
    "methods": ("method", "materials", "approach", "proposed", "model", "architecture", "design", "framework"),
    "results": ("result", "experiment", "evaluation", "case study", "validation"),
    "discussion": ("discussion",),
    "conclusions": ("conclusion", "concluding", "summary"),
    "appendix": ("appendix",),
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


def image_attr(attr: str | None, key: str) -> str | None:
    """Value of key=... in a pandoc attribute block like {width=10cm alt="..."}."""
    if not attr:
        return None
    m = re.search(r'(?<![\w-])%s\s*=\s*(?:"([^"]*)"|(\S+?))(?=[\s}])' % re.escape(key), attr)
    return (m.group(1) if m.group(1) is not None else m.group(2)) if m else None
