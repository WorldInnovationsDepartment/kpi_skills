# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-docx>=1.1",
#     "pyyaml>=6",
#     "pymupdf>=1.24",
#     "pillow",
# ]
# ///
"""check_paper.py -- check a manuscript against the requirements for Springer
"Lecture Notes in Networks and Systems" (LNNS) proceedings papers.

    uv run check_paper.py paper.md                       # content checks on the source
    uv run check_paper.py paper.md --docx paper.docx     # + layout checks on the built Word file
    uv run check_paper.py paper.md --pdf paper.pdf       # + page count, fonts, text area of the final PDF

The PDF can be the LibreOffice rendering of the .docx (render_preview.py) or the
PDF compiled from the LaTeX project (Overleaf / latexmk).

Prints one line per finding:

    ERROR <code>: ...   violates a stated Springer/template requirement -> fix before submitting
    WARN  <code>: ...   a recommendation, published practice, or a likely problem
    INFO  <code>: ...   reminders that cannot be checked automatically

then `SUMMARY: E error(s), W warning(s), I info`, and exits 1 if there is any
ERROR (0 otherwise). Every rule and its source is listed in
references/requirements.md.
"""
from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

from lnns_common import (
    ABSTRACT_WORDS,
    DISPLAY_MATH_RE,
    FONT,
    IMAGE_RE,
    KEYWORDS_RANGE,
    MARGIN_LR_MM,
    MARGIN_TB_MM,
    PAGE_H_MM,
    PAGE_W_MM,
    TEXT_WIDTH_MM,
    SourceError,
    citation_order,
    find_citations,
    has_doi,
    image_attr,
    keywords,
    load_source,
    normalize_orcid,
    reference_year,
    references,
    required_errors,
    section_kind,
    sections,
    sort_key,
    strip_code,
    strip_markup,
    strip_math,
    table_blocks,
    text_of,
)

ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SMALL_WORDS = {"a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet", "as", "at", "by", "in", "of", "off",
               "on", "per", "to", "up", "via", "vs", "with", "from", "into", "onto", "over", "upon", "than", "versus"}


class Report:
    def __init__(self):
        self.items: list[tuple[str, str, str]] = []

    def add(self, level: str, code: str, msg: str) -> None:
        self.items.append((level, code, msg))

    def error(self, code, msg):
        self.add("ERROR", code, msg)

    def warn(self, code, msg):
        self.add("WARN", code, msg)

    def info(self, code, msg):
        self.add("INFO", code, msg)

    def count(self, level):
        return sum(1 for lv, _, _ in self.items if lv == level)

    def print(self) -> None:
        order = {"ERROR": 0, "WARN": 1, "INFO": 2}
        for lv, code, msg in sorted(self.items, key=lambda x: order[x[0]]):
            print(f"{lv:<5} {code}: {msg}")
        print(f"SUMMARY: {self.count('ERROR')} error(s), {self.count('WARN')} warning(s), {self.count('INFO')} info")


def words(text: str) -> int:
    return len([w for w in re.findall(r"\S+", text) if re.search(r"\w", w)])


def title_case_problems(title: str) -> list[str]:
    """Words that break Springer's title case (capitalise all words except short articles/conjunctions/prepositions)."""
    bad = []
    toks = re.findall(r"[A-Za-z][\w'’-]*", strip_markup(title))
    for k, w in enumerate(toks):
        first = w.split("-")[0]
        if k == 0 or first.lower() in SMALL_WORDS or not first[0].isalpha():
            continue
        if first[0].islower() and not re.search(r"[A-Z0-9]", first[1:]):  # skip 'iPhone', 'k-means'-like tokens
            bad.append(w)
    return bad


def conference(meta: dict) -> dict:
    c = meta.get("conference")
    return c if isinstance(c, dict) else {}


# ---------------------------------------------------------------- content checks (source)

def find_todos(value, path: str = "") -> list[str]:
    if isinstance(value, dict):
        return [p for k, v in value.items() for p in find_todos(v, f"{path}.{k}" if path else str(k))]
    if isinstance(value, list):
        return [p for i, v in enumerate(value) for p in find_todos(v, f"{path}[{i}]")]
    return [path] if isinstance(value, str) and re.search(r"\bTODO\b", value) else []


def check_meta(meta: dict, rep: Report, year_now: int) -> None:
    for e in required_errors(meta):
        rep.error("meta.required", e)
    todos = find_todos(meta)
    if todos:
        rep.error("meta.todo", f"TODO placeholder(s) left in: {', '.join(todos)}")

    # Title
    title = strip_markup(text_of(meta.get("title")))
    if title:
        if title.isupper():
            rep.error("title.case", "the title is in capitals; write it in title case")
        else:
            bad = title_case_problems(title)
            if bad:
                rep.warn("title.case", f"title case: capitalise {bad} (all words except articles, conjunctions and "
                                       "short prepositions)")
        if title.endswith("."):
            rep.error("title.period", "titles have no end punctuation")
        if len(title) > 70 and not text_of(meta.get("running_title")):
            rep.warn("title.running", f"the title has {len(title)} characters; give an abbreviated `running_title` "
                                      "for the running head (\\titlerunning)")

    # Authors and affiliations
    authors = [a for a in (meta.get("authors") or []) if isinstance(a, dict)]
    affs = meta.get("affiliations") or []
    if authors:
        corr = [a for a in authors if a.get("corresponding")]
        if len(corr) != 1:
            rep.error("authors.corresponding", f"{len(corr)} corresponding authors marked; Springer requires exactly one "
                                               "(`corresponding: true`), who also signs the Licence to Publish")
        used = set()
        for i, a in enumerate(authors):
            who = text_of(a.get("family")) or f"#{i + 1}"
            used.update(n for n in (a.get("affiliations") or []) if isinstance(n, int))
            if text_of(a.get("given")) and re.fullmatch(r"([A-Z]\.\s*)+", text_of(a.get("given"))):
                rep.warn("authors.initials", f"{who}: give the first name in full, not initials (Springer: "
                                             "'given name(s) followed by family name(s)')")
            orcid = normalize_orcid(a.get("orcid"))
            if not orcid:
                rep.warn("authors.orcid", f"{who}: no ORCID; Springer encourages ORCIDs in the paper header")
            elif not ORCID_RE.match(orcid):
                rep.error("authors.orcid", f"{who}: ORCID '{orcid}' is not in the 0000-0000-0000-0000 form")
            elif orcid.startswith("0000-0000-0000-000"):
                rep.warn("authors.placeholder", f"{who}: ORCID {orcid} looks like a placeholder")
            email = text_of(a.get("email"))
            if a.get("corresponding") and not email:
                rep.error("authors.email", f"{who}: the corresponding author's e-mail address is mandatory")
            if email and not EMAIL_RE.match(email):
                rep.error("authors.email", f"{who}: e-mail '{email}' is malformed")
            elif email.endswith("@example.com"):
                rep.warn("authors.placeholder", f"{who}: e-mail {email} looks like a placeholder")
        unused = [n for n in range(1, len(affs) + 1) if n not in used]
        if unused:
            rep.error("affiliations.unused", f"affiliation(s) {unused} are not referenced by any author")
    for n, aff in enumerate(affs, 1):
        txt = text_of(aff) if not isinstance(aff, dict) else ", ".join(text_of(v) for v in aff.values())
        if isinstance(aff, dict) and not (text_of(aff.get("city")) and text_of(aff.get("country"))):
            rep.warn("affiliations.place", f"affiliation {n}: give city and country")
        elif not isinstance(aff, dict) and txt.count(",") < 1:
            rep.warn("affiliations.place", f"affiliation {n} ('{txt}'): it must include town/city and country")

    # Abstract
    abstract = text_of(meta.get("abstract"))
    if abstract:
        n = words(abstract)
        lo, hi = ABSTRACT_WORDS
        if not lo <= n <= hi:
            rep.error("abstract.words", f"the abstract has {n} words; the template requires {lo}-{hi}")
        if find_citations(abstract):
            rep.warn("abstract.citations", "the abstract cites references; it must stand alone (no citations, "
                                           "no footnotes)")
        if "\n\n" in str(meta.get("abstract")):
            rep.warn("abstract.paragraphs", "the abstract has several paragraphs; LNNS abstracts are one paragraph")
        if re.match(r"(?i)\s*(background|purpose|objective|aim)\s*[:.]", abstract):
            rep.warn("abstract.structured", "the abstract looks structured (labelled parts); LNNS uses one "
                                            "unstructured paragraph")

    # Keywords
    kws = keywords(meta)
    if kws:
        lo, hi = KEYWORDS_RANGE
        if not lo <= len(kws) <= hi:
            rep.warn("keywords.count", f"{len(kws)} keywords; give {lo}-{hi} (the template shows 3, published LNNS "
                                       "papers use 5-6, check the call for papers)")
        lower = [k for k in kws if k[:1].islower()]
        if lower:
            rep.warn("keywords.case", f"capitalise the first letter of each keyword: {lower}")
        if any(k.endswith(".") for k in kws):
            rep.warn("keywords.period", "do not end keywords with a period; the builder adds the final one")

    # Credits
    if not text_of(meta.get("disclosure")):
        rep.error("credits.disclosure", "no `disclosure` (Disclosure of Interests); it is mandatory, e.g. \"The "
                                        "authors have no competing interests to declare that are relevant to the "
                                        "content of this article.\" -- the authors must confirm the wording")
    ack = text_of(meta.get("acknowledgments"))
    if re.search(r"(?i)\bgrant|funded|support", ack) and not re.search(r"\d", ack):
        rep.warn("credits.funding", "the acknowledgments mention funding but no grant number")
    if text_of(meta.get("ai_disclosure")):
        rep.info("ai.disclosure", "ai_disclosure given: the builder adds the prescribed first-page footnote and the "
                                  "end-of-chapter statement")

    # Conference settings
    conf = conference(meta)
    for key in ("min_pages", "max_pages"):
        if key in conf and not isinstance(conf[key], int):
            rep.error("conference.pages", f"conference.{key} must be an integer")
    if not conf.get("max_pages"):
        rep.warn("conference.pages", "no conference.max_pages: LNNS page limits are set by each conference -- "
                                     "copy the limit from the call for papers")

    # References
    refs = references(meta)
    if refs:
        recent = [r for r in refs if (y := reference_year(r)) and year_now - 5 <= y <= year_now]
        if len(refs) < 15:
            rep.warn("refs.count", f"{len(refs)} references; recent LNNS papers cite 10-38 (median ~34) -- "
                                   "a short list weakens the related-work section")
        if len(recent) < 0.4 * len(refs):
            rep.warn("refs.recent", f"{len(recent)} of {len(refs)} references are from {year_now - 5}-{year_now}; "
                                    "aim for at least 40 %")
        no_doi = [i for i, r in enumerate(refs, 1) if not has_doi(r) and not re.search(r"https?://", r)]
        if no_doi:
            rep.warn("refs.doi", f"no DOI in reference(s) {no_doi}; Springer strongly encourages DOIs -- add each "
                                 "after verifying it on doi.org / Crossref")
        numbered = [i for i, r in enumerate(refs, 1) if re.match(r"^\s*\[?\d+[.)\]]\s", r)]
        if numbered:
            rep.error("refs.numbering", f"reference(s) {numbered} start with their own number; the builder numbers "
                                        "the list -- remove it")
        cyr = [i for i, r in enumerate(refs, 1) if re.search(r"[А-Яа-яЁёІіЇїЄєҐґ]", r)]
        if cyr:
            rep.error("refs.latin", f"reference(s) {cyr} contain Cyrillic; write every reference in the Latin "
                                    "alphabet (transliterate, translate the title in [...], add '(in Ukrainian)')")
        no_year = [i for i, r in enumerate(refs, 1) if reference_year(r) is None]
        if no_year:
            rep.warn("refs.year", f"no publication year found in reference(s) {no_year}")
        style = [i for i, r in enumerate(refs, 1)
                 if not re.search(r"\((?:[^()]*\s)?(?:19|20)\d{2}[a-z]?\)", r) and not re.search(r"accessed", r, re.I)]
        if style:
            rep.warn("refs.format", f"reference(s) {style} do not end with the year in parentheses as splncs04 does "
                                    "('Author, F.: Title. Journal 2(5), 99–110 (2016)')")
        heads = [i for i, r in enumerate(refs, 1)
                 if not re.match(r"^[^:]{2,}:\s", strip_markup(r)) and not re.search(r"https?://", r)]
        if heads:
            rep.warn("refs.format", f"reference(s) {heads} lack the 'Surname, I., Surname, I.: Title' head of splncs04")
        long_lists = []
        for i, r in enumerate(refs, 1):
            head = strip_markup(r).split(":", 1)[0]
            n_auth = len(re.findall(r"[A-Z][\w'’\-]+(?:\s+[\w'’\-]+)*,\s+(?:[A-Z]\.[-\s]?)+", head))
            if n_auth > 6 and "et al" not in head:
                long_lists.append(i)
        if long_lists:
            rep.warn("refs.etal", f"reference(s) {long_lists} list more than six authors; Springer shortens these "
                                  "to the first author + 'et al.'")
        web = [i for i, r in enumerate(refs, 1) if re.search(r"https?://", r) and not has_doi(r)]
        no_access = [i for i in web if not re.search(r"(?i)accessed", refs[i - 1])]
        if no_access:
            rep.warn("refs.url", f"web reference(s) {no_access} need an access date, e.g. 'last accessed 2026/10/25'")
        if len(web) > 0.25 * len(refs):
            rep.warn("refs.web", f"{len(web)} of {len(refs)} references are web pages; prefer peer-reviewed sources")
        bad = [i for i, r in enumerate(refs, 1) if re.search(r"(?i)unpublished|personal communication", r)]
        if bad:
            rep.warn("refs.unpublished", f"reference(s) {bad} cite unpublished material; cite it in the text instead")


def check_body(meta: dict, body: str, rep: Report, source_dir: Path) -> None:
    clean = strip_code(body)
    if re.search(r"\bTODO\b", clean):
        rep.error("body.todo", "TODO placeholder(s) left in the body")
    secs = sections(body, 1)
    if not secs:
        rep.error("body.sections", "the body has no '# Section' headings")
        return
    if any(re.match(r"(?i)^(references|bibliography|abstract|keywords|acknowledg|disclosure)", s.title)
           for s in secs):
        rep.error("body.generated", "remove Abstract/Keywords/References/Acknowledgments/Disclosure sections from "
                                    "the body -- they come from the front matter")

    # Headings
    heads = [(len(m.group(1)), m.group(2).strip()) for m in re.finditer(r"(?m)^(#{1,6})[ \t]+(.+?)[ \t#]*$", clean)]
    if any(lvl > 4 for lvl, _ in heads):
        rep.error("headings.depth", "headings deeper than level 4 (#####); the template allows at most four levels")
    numbered = [t for _, t in heads if re.match(r"^(\d+(\.\d+)*\.?|[IVX]+\.)\s", t)]
    if numbered:
        rep.error("headings.numbered", f"heading(s) {numbered[:3]} carry their own number; the builder numbers "
                                       "levels 1-2 (and levels 3-4 are unnumbered run-in headings)")
    for lvl, t in heads:
        if lvl <= 2:
            bad = title_case_problems(t)
            if bad:
                rep.warn("headings.case", f"heading '{t}': use title case (capitalise {bad})")
    kinds = [section_kind(s.title) for s in secs]
    if kinds[0] != "introduction":
        rep.warn("body.order", f"the first section is '{secs[0].title}', expected 'Introduction'")
    if "conclusions" not in kinds:
        rep.warn("body.conclusions", "no 'Conclusion(s)' section; most LNNS papers end with one (it may be "
                                     "'Conclusion and Future Work')")
    else:
        last = [k for k in kinds if k != "appendix"]
        if last and last[-1] != "conclusions":
            rep.warn("body.order", "the Conclusion is not the last section (only an Appendix may follow it)")
    if "related" not in kinds and "introduction" in kinds:
        intro = secs[kinds.index("introduction")]
        if len({n for _, n in find_citations(intro.text)}) < 5:
            rep.warn("body.related", "no Related Work section and few citations in the Introduction; reviewers "
                                     "expect the state of the art to be discussed")
    for s, k in zip(secs, kinds):
        if k == "conclusions" and not re.search(r"(?i)future|further|next step|outlook|plan", s.text):
            rep.info("conclusions.future", "the Conclusion has no outlook/future-work sentence")

    # Figures
    figs = list(IMAGE_RE.finditer(clean))
    fig_ref = re.compile(r"(?i)\bfig(?:ure)?s?\.?\s*(\d+)")
    for n, m in enumerate(figs, 1):
        alt = m.group("alt").strip()
        if not alt:
            rep.error("figure.caption", f"figure {n} ({m.group('src')}) has no caption: write ![Caption](file)")
        elif alt.rstrip().endswith(".") and len(re.findall(r"[.!?](\s|$)", alt)) == 1 and words(alt) < 8:
            rep.info("figure.caption", f"figure {n}: a caption that is not a full sentence has no final period")
        mentions = [r.start() for r in fig_ref.finditer(clean) if int(r.group(1)) == n and r.start() < m.start()
                    or int(r.group(1)) == n and r.start() > m.end()]
        if not mentions:
            rep.error("figure.ref", f"figure {n} is never referred to in the text ('Fig. {n}')")
        elif min(mentions) > m.start():
            rep.warn("figure.ref", f"figure {n} appears before its first mention; place it after it")
        if not image_attr(m.group("attr"), "alt"):
            rep.warn("figure.alt", f"figure {n}: no alt text; Springer requires alt text for every figure -- add "
                                   "{alt=\"...\"} describing what the figure shows")
        src = Path(m.group("src"))
        src = src if src.is_absolute() else source_dir / src
        if not src.exists():
            rep.error("figure.file", f"figure {n}: file not found: {m.group('src')}")
        else:
            check_image(src, n, image_attr(m.group("attr"), "width"), rep)

    # Tables
    tables = table_blocks(body)
    tab_ref = re.compile(r"(?i)\btab(?:le)?s?\.?\s*(\d+)")
    for n, (pos, cap) in enumerate(tables, 1):
        if not cap:
            rep.error("table.caption", f"table {n} has no caption: add a 'Table: <title>' line before it")
        mentions = [r.start() for r in tab_ref.finditer(clean) if int(r.group(1)) == n
                    and not re.match(r"\s*(?:Table)?:", clean[clean.rfind("\n", 0, r.start()) + 1: r.start()] or "x")]
        if not mentions:
            rep.error("table.ref", f"table {n} is never referred to in the text ('Table {n}')")
        elif min(mentions) > pos:
            rep.warn("table.ref", f"table {n} appears before its first mention; place it after it")

    # Equations
    if DISPLAY_MATH_RE.search(clean):
        rep.info("equations", f"{len(DISPLAY_MATH_RE.findall(clean))} display equation(s) are numbered (1), (2)... "
                              "consecutively; punctuate them like ordinary text")
    if re.search(r"!\[[^\]]*\]\([^)]*(formula|equation|eq\d)[^)]*\)", clean, re.I):
        rep.error("equations.images", "an image looks like a formula; equations must be editable ($$...$$)")
    if re.search(r"(?i)\\(color|textcolor)\b|<span style=\"color", clean):
        rep.error("body.color", "coloured text: Springer does not support colour in text, tables or equations")

    # Citations
    refs = references(meta)
    cites = find_citations(body)
    cited = {n for _, n in cites}
    if refs:
        over = sorted(n for n in cited if n < 1 or n > len(refs))
        if over:
            rep.error("cite.range", f"citation(s) {over} exceed the {len(refs)} entries of the reference list")
        never = [i for i in range(1, len(refs) + 1) if i not in cited]
        if never:
            rep.error("cite.unused", f"reference(s) {never} are never cited in the text")
        order = citation_order(meta)
        if order == "citation":
            seen, expected = [], 1
            for _, n in cites:
                if n in seen:
                    continue
                seen.append(n)
                if n != expected:
                    rep.error("cite.order", f"[{n}] is cited before [{expected}] but citation_order is 'citation'; "
                                            "renumber with renumber_refs.py --order citation")
                    break
                expected += 1
        elif order == "alphabetical":
            keys = [sort_key(r) for r in refs]
            if keys != sorted(keys):
                rep.error("cite.order", "citation_order is 'alphabetical' but the reference list is not sorted by "
                                        "first author; run renumber_refs.py --order alphabetical")
    if not cites and re.search(r"\(\s*[A-Z][\w'-]+(?: et al\.| and [A-Z][\w'-]+)?,?\s+(?:19|20)\d{2}\s*\)", clean):
        rep.warn("cite.style", "author-year citations found; the skill builds numbered citations [1] (preferred by "
                               "the llncs template) -- use author-year only if the conference asks for it")

    # Length estimate (a real page count needs --pdf)
    n_words = words(strip_math(clean)) + words(" ".join(refs)) * 0.8 + words(text_of(meta.get("abstract"))) * 0.8
    pages = 0.6 + n_words / 340 + 0.5 * len(figs) + 0.12 * len(tables) + 0.05 * len(DISPLAY_MATH_RE.findall(clean))
    limit = conference(meta).get("max_pages")
    rep.info("length.estimate", f"~{int(n_words)} words, roughly {pages:.1f} pages in the 122 x 193 mm layout"
                                + (f" (conference limit {limit})" if limit else "") + "; pass --pdf for an exact count")


def check_image(path: Path, n: int, width_attr: str | None, rep: Report) -> None:
    if path.suffix.lower() in (".pdf", ".eps", ".svg"):
        return
    try:
        from PIL import Image
        with Image.open(path) as im:
            px = im.width
    except Exception:  # noqa: BLE001 -- unreadable image: let the builder report it
        return
    width_mm = TEXT_WIDTH_MM
    if width_attr:
        m = re.match(r"([\d.]+)\s*(cm|mm|in|%)$", width_attr.strip())
        if m:
            v, unit = float(m.group(1)), m.group(2)
            width_mm = {"cm": v * 10, "mm": v, "in": v * 25.4, "%": TEXT_WIDTH_MM * v / 100}[unit]
    width_mm = min(width_mm, TEXT_WIDTH_MM)
    dpi = px / (width_mm / 25.4)
    if dpi < 300:
        rep.warn("figure.resolution", f"figure {n} ({path.name}): ~{dpi:.0f} dpi at the printed width; give at least "
                                      "300 dpi for photos and 800-1200 dpi (or vector graphics) for line art")


def reminders(meta: dict, rep: Report) -> None:
    rep.info("template.flavour", "most LNNS volumes use the llncs template (this skill); a few (e.g. ICICT, "
                                 "Springer Singapore) use the svmult chapter layout -- follow the call for papers")
    rep.info("submit.ltp", "the corresponding author signs the Licence to Publish (by hand, unmodified) for all "
                           "authors; authorship cannot change after submission")
    rep.info("submit.package", "camera-ready: source files (.docx without macros, or .tex + images + .bib/.bbl), "
                               "a final PDF identical to them, alt text for figures, permissions for third-party "
                               "material; short file names (e.g. Petrenko_DriftAwareReweighting.docx)")
    rep.info("submit.figures", "figures are printed in black and white: check that colour figures stay readable "
                               "in greyscale; lettering at least 6 pt")
    rep.info("ai.policy", "AI cannot be an author; any AI-generated or AI-edited text must be verified and "
                          "disclosed (set ai_disclosure)")
    rep.info("submit.original", "the paper must be original and not published or under review elsewhere; the "
                                "volume editors may run a plagiarism check")


# ---------------------------------------------------------------- layout checks (docx / pdf)

def check_docx(path: Path, rep: Report) -> None:
    import zipfile

    from docx import Document
    from docx.oxml.ns import qn

    with zipfile.ZipFile(path) as z:
        if any(n.endswith("vbaProject.bin") for n in z.namelist()):
            rep.error("docx.macros", "the file contains macros; save as .docx without macros (never submit .docm)")
    doc = Document(str(path))
    for i, s in enumerate(doc.sections):
        w, h = s.page_width.mm, s.page_height.mm
        if abs(w - PAGE_W_MM) > 1 or abs(h - PAGE_H_MM) > 1:
            rep.warn("docx.page", f"section {i + 1}: page is {w:.0f}x{h:.0f} mm; the Word template uses A4")
        tw = w - s.left_margin.mm - s.right_margin.mm
        th = h - s.top_margin.mm - s.bottom_margin.mm
        if abs(tw - 122) > 1 or abs(th - 193) > 1:
            rep.error("docx.textarea", f"section {i + 1}: text area {tw:.0f}x{th:.0f} mm, must be 122x193 mm "
                                       f"(margins {MARGIN_TB_MM:.0f}/{MARGIN_LR_MM:.0f} mm on A4)")
        for part in (s.header, s.footer):
            if any(p.text.strip() for p in part.paragraphs):
                rep.error("docx.header", "the file has header/footer text; do not add running heads or page "
                                         "numbers -- Springer adds them")

    def eff(run_el, para, attr):
        rPr = run_el.rPr
        if rPr is not None:
            if attr == "font":
                rf = rPr.find(qn("w:rFonts"))
                if rf is not None and rf.get(qn("w:ascii")):
                    return rf.get(qn("w:ascii"))
            else:
                sz = rPr.find(qn("w:sz"))
                if sz is not None:
                    return int(sz.get(qn("w:val"))) / 2
        st = para.style
        while st is not None:
            v = st.font.name if attr == "font" else (st.font.size.pt if st.font.size else None)
            if v:
                return v
            st = st.base_style
        return None

    bad_font, bad_size, n_runs = 0, 0, 0
    allowed_fonts = {FONT, "Courier New", "Segoe UI Symbol", "Cambria Math"}
    for p in doc.paragraphs:
        for r in p.runs:
            if not r.text.strip():
                continue
            n_runs += 1
            if (eff(r._r, p, "font") or "") not in allowed_fonts:
                bad_font += 1
            size = eff(r._r, p, "size")
            if size is not None and size not in (9, 10, 12, 14):
                bad_size += 1
    if bad_font:
        rep.error("docx.font", f"{bad_font} of {n_runs} text runs are not in {FONT}")
    if bad_size:
        rep.error("docx.size", f"{bad_size} of {n_runs} text runs are not 14/12/10/9 pt (title/heading/body/small)")
    texts = [p.text.strip() for p in doc.paragraphs]
    if not any(re.match(r"^Abstract\.", t) for t in texts):
        rep.error("docx.abstract", "no paragraph starting with 'Abstract.'")
    if not any(re.match(r"^Keywords:", t) for t in texts):
        rep.error("docx.keywords", "no paragraph starting with 'Keywords:'")
    if not any(t.startswith("Disclosure of Interests.") for t in texts):
        rep.error("docx.disclosure", "no 'Disclosure of Interests.' paragraph")
    if not any(re.match(r"^1\s+\S", t) for t in texts):
        rep.warn("docx.headings", "no numbered level-1 heading ('1 Introduction') found")


def check_pdf(path: Path, meta: dict, rep: Report) -> None:
    try:
        import pymupdf as fitz
    except ImportError:  # pragma: no cover
        import fitz
    conf = conference(meta)
    with fitz.open(str(path)) as doc:
        pages = doc.page_count
        type3, unembedded, wide = set(), set(), []
        for i, page in enumerate(doc):
            for f in page.get_fonts(full=True):
                ext, ftype, name = f[1], f[2], f[3]
                if ftype == "Type3":
                    type3.add(name)
                elif not ext:
                    unembedded.add(name)
            xs = [b[:4] for b in page.get_text("blocks") if b[4].strip()]
            if xs:
                width_mm = (max(b[2] for b in xs) - min(b[0] for b in xs)) / 72 * 25.4
                if width_mm > TEXT_WIDTH_MM + 3:
                    wide.append(i + 1)
    lo, hi = conf.get("min_pages"), conf.get("max_pages")
    if hi and pages > hi:
        rep.error("pages", f"{pages} pages; the conference limit is {hi} (references included unless the call "
                           "says otherwise)")
    elif lo and pages < lo:
        rep.error("pages", f"{pages} pages; the conference minimum is {lo}")
    elif not hi and pages > 15:
        rep.warn("pages", f"{pages} pages; LNNS conferences usually allow 10-15 (published papers: 12-13)")
    elif pages < 4:
        rep.warn("pages", f"{pages} pages; very short papers may be moved to the back matter and not indexed")
    else:
        rep.info("pages", f"{pages} pages" + (f" (conference range {lo or '?'}-{hi})" if hi else ""))
    if type3:
        rep.error("pdf.type3", f"Type 3 fonts {sorted(type3)}: Springer omits their characters -- regenerate the "
                               "PDF with Type 1/TrueType fonts (e.g. use T1 fonts / newtx in LaTeX)")
    if unembedded:
        rep.warn("pdf.fonts", f"fonts not embedded: {sorted(unembedded)}")
    if wide:
        rep.warn("pdf.textarea", f"text wider than the 122 mm text area on page(s) {wide[:10]}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("source", type=Path, help="manuscript Markdown file with YAML front matter")
    ap.add_argument("--docx", type=Path, help="built .docx to check the layout of")
    ap.add_argument("--pdf", type=Path, help="final PDF (render_preview.py output or compiled LaTeX)")
    ap.add_argument("--year", type=int, default=datetime.date.today().year,
                    help="current year for the 'last 5 years' rule (default: this year)")
    ap.add_argument("--no-reminders", action="store_true", help="omit the submission-checklist INFO lines")
    args = ap.parse_args(argv)
    rep = Report()
    try:
        src = load_source(args.source)
    except (SourceError, OSError) as exc:
        print(f"ERROR source: {exc}")
        print("SUMMARY: 1 error(s), 0 warning(s), 0 info")
        return 1
    check_meta(src.meta, rep, args.year)
    check_body(src.meta, src.body, rep, args.source.parent.resolve())
    if not args.no_reminders:
        reminders(src.meta, rep)
    if args.docx:
        if args.docx.suffix.lower() != ".docx":
            rep.error("docx.format", "submit Word papers as .docx (no .docm, no .doc)")
        elif not args.docx.is_file():
            rep.error("docx.missing", f"not found: {args.docx}")
        else:
            check_docx(args.docx, rep)
    if args.pdf:
        if not args.pdf.is_file():
            rep.error("pdf.missing", f"not found: {args.pdf}")
        else:
            check_pdf(args.pdf, src.meta, rep)
    rep.print()
    return 1 if rep.count("ERROR") else 0


if __name__ == "__main__":
    sys.exit(main())
