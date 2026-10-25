# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-docx>=1.1",
#     "pyyaml>=6",
#     "pypandoc_binary>=1.13",
# ]
# ///
"""build_paper.py -- Markdown + YAML manuscript -> a Springer proceedings paper for
"Lecture Notes in Networks and Systems" (LNNS), as a Word .docx and/or a LaTeX project.

    uv run build_paper.py paper.md --docx paper.docx [--verbose]
    uv run build_paper.py paper.md --latex latex/ [--compile]
    uv run build_paper.py paper.md --docx paper.docx --latex latex/

The source is one Markdown file whose YAML front matter carries everything that
is not running text (title, authors, affiliations, abstract, keywords,
references, acknowledgments, disclosure of interests...) and whose body is the
paper itself (`# Section`, `## Subsection`, `### Run-in heading`, $$display
math$$, pipe tables with a `Table: caption` line, `![caption](image.png)`
figures, numeric citations [1]). See references/manuscript-format.md.

--docx: the body goes through pandoc (bundled via pypandoc_binary, so display
math becomes native Word equations), then python-docx applies the layout of
Springer's Word template splnproc2510: A4 with the 122 x 193 mm text area,
Times New Roman 10 pt, 0.4 cm first-line indent (none after headings and
floats), 14 pt title, 9 pt affiliations/abstract/captions/references, numbered
level-1/2 headings, run-in level-3/4 headings, bold "Fig. N." below figures and
"Table N." above tables, right-numbered equations, the Acknowledgments and
Disclosure of Interests run-in paragraphs and the numbered reference list.

--latex: writes <dir>/paper.tex for Springer's llncs class (bundled llncs.cls,
CC BY 4.0) with \\title, \\author/\\inst/\\orcidID, \\institute/\\email,
abstract + \\keywords, the body converted by pandoc with a Lua filter (numbered
equation environments, figure/table floats with \\caption and \\label, \\cite),
the credits environment and a thebibliography list in the given order. Images
are copied next to it. --compile runs latexmk/pdflatex if one is installed;
otherwise upload the folder to Overleaf.

All-or-nothing: on any source problem it prints `error: ...` lines to stderr,
exits 1 and writes nothing.
"""
from __future__ import annotations

import argparse
import copy
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pypandoc
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt
from docx.table import Table
from docx.text.paragraph import Paragraph

from lnns_common import (
    CITE_RE,
    FONT,
    FOOTER_MM,
    HEADER_MM,
    IMAGE_RE,
    INDENT_MM,
    MARGIN_LR_MM,
    MARGIN_TB_MM,
    PAGE_H_MM,
    PAGE_W_MM,
    SIZE,
    TEXT_WIDTH_MM,
    SourceError,
    affiliation_emails,
    affiliation_text,
    author_name,
    author_running,
    citation_numbers,
    format_citation,
    inline_segments,
    keywords,
    load_source,
    normalize_orcid,
    references,
    required_errors,
    strip_code,
)

SKILL_DIR = Path(__file__).resolve().parent.parent
LATEX_ASSETS = SKILL_DIR / "assets" / "latex"

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
CODE_STYLES = {"SourceCode", "VerbatimChar"}
INDENT = Mm(INDENT_MM)
TWIPS_PER_MM = 1440 / 25.4
HEADING_HANG = Mm(10)  # heading1/heading2: left 567, hanging 567 twips
ENVELOPE = "\u2709"
AI_NOTE = ("This chapter was prepared with the assistance of AI. See disclosure at the end of chapter for "
           "further details.")

J = WD_ALIGN_PARAGRAPH


def fail(msgs: list[str]) -> None:
    for m in msgs:
        print(f"error: {m}", file=sys.stderr)
    sys.exit(1)


# ================================================================ Word (.docx)

# CT_RPr children must appear in schema order or Word reports the file as corrupt.
_RPR_ORDER = ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline",
              "shadow", "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing",
              "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText",
              "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath"]


def _sort_rpr(rPr) -> None:
    rank = {qn(f"w:{n}"): i for i, n in enumerate(_RPR_ORDER)}
    kids = sorted(rPr, key=lambda e: rank.get(e.tag, len(_RPR_ORDER)))
    for k in kids:
        rPr.remove(k)
    for k in kids:
        rPr.append(k)


def style_run(r_el, *, size: float = SIZE["body"], bold: bool | None = None, italic: bool | None = None,
              font: str = FONT, black: bool = False, superscript: bool = False) -> None:
    rPr = r_el.find(qn("w:rPr"))
    if rPr is None:  # works on plain lxml elements too (e.g. runs of the footnotes part)
        rPr = r_el.makeelement(qn("w:rPr"), {})
        r_el.insert(0, rPr)
    rfonts = rPr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = rPr.makeelement(qn("w:rFonts"), {})
        rPr.insert(0, rfonts)
    for attr in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        rfonts.attrib.pop(qn(f"w:{attr}"), None)
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        rfonts.set(qn(f"w:{attr}"), font)
    for tag in ("w:sz", "w:szCs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {})
            rPr.append(el)
        el.set(qn("w:val"), str(int(round(size * 2))))
    for tag, val in (("w:b", bold), ("w:i", italic)):
        if val is None:
            continue
        for old in rPr.findall(qn(tag)):
            rPr.remove(old)
        el = rPr.makeelement(qn(tag), {})
        if not val:
            el.set(qn("w:val"), "0")
        rPr.append(el)
    if black:
        for old in rPr.findall(qn("w:color")) + rPr.findall(qn("w:u")):
            rPr.remove(old)
        c = rPr.makeelement(qn("w:color"), {})
        c.set(qn("w:val"), "000000")
        rPr.append(c)
    if superscript:
        for old in rPr.findall(qn("w:vertAlign")):
            rPr.remove(old)
        va = rPr.makeelement(qn("w:vertAlign"), {})
        va.set(qn("w:val"), "superscript")
        rPr.append(va)
    _sort_rpr(rPr)


def fmt(p: Paragraph, align, *, first=INDENT, left=Mm(0), right=Mm(0), sb: float = 0, sa: float = 0,
        line_pt: float | None = 12, keep_next: bool = False) -> None:
    """Paragraph layout. line_pt is the template's 'at least' line height (12 pt body, 11 pt for 9 pt text)."""
    pf = p.paragraph_format
    pf.alignment = align
    pf.first_line_indent = first
    pf.left_indent = left
    pf.right_indent = right
    pf.space_before = Pt(sb)
    pf.space_after = Pt(sa)
    if line_pt is None:
        pf.line_spacing = 1.0
    else:
        pf.line_spacing_rule = WD_LINE_SPACING.AT_LEAST
        pf.line_spacing = Pt(line_pt)
    pf.keep_with_next = keep_next
    pf.widow_control = True


def runs_of(el):
    return el.iter(qn("w:r"))


def restyle_runs(p_el, *, size: float = SIZE["body"], bold: bool | None = None, italic: bool | None = None,
                 code: bool = False) -> None:
    for r in runs_of(p_el):
        rstyle = r.find(f"{qn('w:rPr')}/{qn('w:rStyle')}")
        is_code = code or (rstyle is not None and rstyle.get(qn("w:val")) in CODE_STYLES)
        in_link = r.getparent().tag == qn("w:hyperlink")
        if is_code:
            style_run(r, size=SIZE["code"], font="Courier New")
        else:
            style_run(r, size=size, bold=bold, italic=italic, black=in_link or rstyle is not None)


def p_style(p_el) -> str | None:
    ps = p_el.find(f"{qn('w:pPr')}/{qn('w:pStyle')}")
    return ps.get(qn("w:val")) if ps is not None else None


def p_text(p_el) -> str:
    return "".join(t.text or "" for t in p_el.iter(qn("w:t")))


def add_text(p: Paragraph, text: str, *, bold=False, italic=False, size: float = SIZE["body"], markup: bool = True,
             superscript: bool = False, font: str = FONT):
    segs = inline_segments(text) if markup else [(text, False, False)]
    for t, b, i in segs:
        r = p.add_run(t)
        style_run(r._r, size=size, bold=bold or b, italic=italic or i, superscript=superscript, font=font)


def make_run(text: str | None = None, *, tab: bool = False, bold: bool | None = None, italic: bool | None = None,
             size: float = SIZE["body"]):
    r = OxmlElement("w:r")
    if tab:
        r.append(OxmlElement("w:tab"))
    if text is not None:
        t = OxmlElement("w:t")
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = text
        r.append(t)
    style_run(r, size=size, bold=bold, italic=italic)
    return r


def insert_runs_first(p_el, runs: list) -> None:
    """Insert runs at the start of a paragraph's content (after w:pPr)."""
    ppr = p_el.find(qn("w:pPr"))
    pos = 0 if ppr is None else list(p_el).index(ppr) + 1
    for k, r in enumerate(runs):
        p_el.insert(pos + k, r)


def set_tabs(p_el, stops: list[tuple[str, float]]) -> None:
    pPr = p_el.get_or_add_pPr()
    for old in pPr.findall(qn("w:tabs")):
        pPr.remove(old)
    tabs = OxmlElement("w:tabs")
    for kind, mm in stops:
        t = OxmlElement("w:tab")
        t.set(qn("w:val"), kind)
        t.set(qn("w:pos"), str(int(round(mm * TWIPS_PER_MM))))
        tabs.append(t)
    # CT_PPr order: pStyle, keepNext, keepLines, pageBreakBefore, framePr, widowControl, numPr,
    # suppressLineNumbers, pBdr, shd, tabs, ...
    anchor = None
    for tag in ("w:shd", "w:pBdr", "w:suppressLineNumbers", "w:numPr", "w:widowControl", "w:framePr",
                "w:pageBreakBefore", "w:keepLines", "w:keepNext", "w:pStyle"):
        anchor = pPr.find(qn(tag))
        if anchor is not None:
            break
    if anchor is not None:
        anchor.addnext(tabs)
    else:
        pPr.insert(0, tabs)


def has_visible_text(nodes) -> bool:
    for n in nodes:
        for t in n.iter(qn("w:t")):
            if t.text and t.text.strip():
                return True
        if n.tag == f"{{{M_NS}}}oMath" or n.find(f".//{{{M_NS}}}oMath") is not None:
            return True
        if n.find(f".//{qn('w:drawing')}") is not None:
            return True
    return False


def setup_document(doc, title: str, authors: str) -> None:
    for s in doc.sections:
        s.page_width, s.page_height = Mm(PAGE_W_MM), Mm(PAGE_H_MM)
        s.top_margin = s.bottom_margin = Mm(MARGIN_TB_MM)
        s.left_margin = s.right_margin = Mm(MARGIN_LR_MM)
        s.header_distance, s.footer_distance = Mm(HEADER_MM), Mm(FOOTER_MM)

    defaults = doc.styles.element.find(qn("w:docDefaults"))
    if defaults is not None:
        rpr = defaults.find(f"{qn('w:rPrDefault')}/{qn('w:rPr')}")
        if rpr is not None:
            _rpr_defaults(rpr)
            for tag in ("w:sz", "w:szCs"):
                el = rpr.find(qn(tag))
                if el is not None:
                    el.set(qn("w:val"), str(SIZE["body"] * 2))
        spacing = defaults.find(f"{qn('w:pPrDefault')}/{qn('w:pPr')}/{qn('w:spacing')}")
        if spacing is not None:
            spacing.set(qn("w:after"), "0")
    for name in ("Normal", "Body Text", "First Paragraph", "Compact", "Block Text", "Image Caption",
                 "Table Caption", "Captioned Figure", "Figure", "Heading 1", "Heading 2", "Heading 3",
                 "Heading 4", "Title", "Footnote Text"):
        try:
            st = doc.styles[name]
        except KeyError:
            continue
        st.font.name = FONT
        st.font.size = Pt(SIZE["caption"] if name == "Footnote Text" else SIZE["body"])
        st.font.color.rgb = None
        _rpr_defaults(st.element.get_or_add_rPr())
        pf = st.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.AT_LEAST
        pf.line_spacing = Pt(11 if name == "Footnote Text" else 12)
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)

    doc.core_properties.title = title
    doc.core_properties.author = authors
    doc.core_properties.language = "en-US"
    doc.core_properties.comments = "Formatted for Springer Lecture Notes in Networks and Systems (splnproc layout)"


def _rpr_defaults(rPr) -> None:
    rfonts = rPr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rPr.insert(0, rfonts)
    for attr in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        rfonts.attrib.pop(qn(f"w:{attr}"), None)
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        rfonts.set(qn(f"w:{attr}"), FONT)
    for old in rPr.findall(qn("w:color")) + rPr.findall(qn("w:lang")):
        rPr.remove(old)
    c = OxmlElement("w:color")
    c.set(qn("w:val"), "000000")
    rPr.append(c)
    lg = OxmlElement("w:lang")
    lg.set(qn("w:val"), "en-US")
    rPr.append(lg)
    _sort_rpr(rPr)


def fix_numbering(doc) -> None:
    """Lists as in splnproc (bulletitem / numitem): marker at 0, text at 0.4 cm, Times New Roman."""
    try:
        numbering = doc.part.numbering_part.element
    except (NotImplementedError, KeyError, AttributeError):
        return
    step = int(round(INDENT_MM * TWIPS_PER_MM))
    for absnum in numbering.findall(qn("w:abstractNum")):
        for lvl in absnum.findall(qn("w:lvl")):
            ilvl = int(lvl.get(qn("w:ilvl")))
            fmt_el = lvl.find(qn("w:numFmt"))
            if fmt_el is not None and fmt_el.get(qn("w:val")) == "bullet":
                lvl_text = lvl.find(qn("w:lvlText"))
                if lvl_text is not None:
                    lvl_text.set(qn("w:val"), "•" if ilvl % 2 == 0 else "–")
            pPr = lvl.find(qn("w:pPr"))
            if pPr is None:
                pPr = OxmlElement("w:pPr")
                lvl.append(pPr)
            for old in pPr.findall(qn("w:ind")) + pPr.findall(qn("w:tabs")):
                pPr.remove(old)
            tabs = OxmlElement("w:tabs")
            tab = OxmlElement("w:tab")
            tab.set(qn("w:val"), "num")
            tab.set(qn("w:pos"), str(step * (ilvl + 1) + (114 if fmt_el is not None and fmt_el.get(qn("w:val")) != "bullet" else 0)))
            tabs.append(tab)
            pPr.insert(0, tabs)
            ind = OxmlElement("w:ind")
            left = step * (ilvl + 1) + (114 if fmt_el is not None and fmt_el.get(qn("w:val")) != "bullet" else 0)
            ind.set(qn("w:left"), str(left))
            ind.set(qn("w:hanging"), str(left - step * ilvl))
            pPr.append(ind)
            rPr = lvl.find(qn("w:rPr"))
            if rPr is None:
                rPr = OxmlElement("w:rPr")
                lvl.append(rPr)
            for old in rPr.findall(qn("w:rFonts")):
                rPr.remove(old)
            rf = OxmlElement("w:rFonts")
            for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
                rf.set(qn(f"w:{attr}"), FONT)
            rPr.insert(0, rf)
            for tag in ("w:pPr", "w:rPr"):
                el = lvl.find(qn(tag))
                if el is not None:
                    lvl.remove(el)
                    lvl.append(el)


class Counters:
    def __init__(self):
        self.figures = 0
        self.tables = 0
        self.equations = 0
        self.h1 = 0
        self.h2 = 0


def scale_drawing(p_el) -> None:
    max_emu = int(Mm(TEXT_WIDTH_MM))
    for ext in p_el.iter(f"{{{WP_NS}}}extent"):
        cx, cy = int(ext.get("cx")), int(ext.get("cy"))
        if cx <= max_emu:
            continue
        k = max_emu / cx
        ext.set("cx", str(max_emu))
        ext.set("cy", str(int(cy * k)))
        for aext in ext.getparent().iter(f"{{{A_NS}}}ext"):
            if aext.get("cx") is not None:
                aext.set("cx", str(max_emu))
                aext.set("cy", str(int(int(aext.get("cy")) * k)))


def split_display_math(doc, p_el, counters: Counters, log) -> bool:
    """Paragraph with m:oMathPara -> [text before] / numbered equation line / [text after].

    Returns True if the paragraph ended with an equation (the next paragraph is then not indented)."""
    children = [c for c in p_el if c.tag != qn("w:pPr")]
    groups: list[tuple[str, list]] = []
    cur: list = []
    for c in children:
        if c.tag == f"{{{M_NS}}}oMathPara":
            if cur:
                groups.append(("text", cur))
                cur = []
            groups.append(("eq", [c]))
        else:
            cur.append(c)
    if cur:
        groups.append(("text", cur))
    groups = [g for g in groups if g[0] == "eq" or has_visible_text(g[1])]

    anchor = p_el
    first_text = True
    for kind, nodes in groups:
        new_p = OxmlElement("w:p")
        if p_el.find(qn("w:pPr")) is not None:
            new_p.append(copy.deepcopy(p_el.find(qn("w:pPr"))))
        anchor.addnext(new_p)
        anchor = new_p
        para = Paragraph(new_p, doc._body)
        if kind == "eq":
            counters.equations += 1
            n = counters.equations
            new_p.append(make_run(tab=True))
            for k, m in enumerate(nodes[0].findall(f"{{{M_NS}}}oMath")):
                if k:
                    new_p.append(make_run(" "))
                new_p.append(m)
            new_p.append(make_run(tab=True))
            new_p.append(make_run(f"({n})"))
            fmt(para, J.LEFT, first=Mm(0), sb=8, sa=8)  # splnproc 'equation': 8 pt before/after
            set_tabs(new_p, [("center", TEXT_WIDTH_MM / 2), ("right", TEXT_WIDTH_MM)])
            log(f"equation ({n})")
        else:
            for nd in nodes:
                new_p.append(nd)
            _trim_leading_space(new_p)
            # Text after a formula continues the paragraph: no indent (samplepaper.tex).
            fmt(para, J.JUSTIFY, first=INDENT if first_text and groups[0][0] == "text" else Mm(0))
            restyle_runs(new_p)
        first_text = False
    p_el.getparent().remove(p_el)
    return bool(groups) and groups[-1][0] == "eq"


def _trim_leading_space(p_el) -> None:
    for r in list(p_el.iter(qn("w:r"))):
        ts = r.findall(qn("w:t"))
        if not ts:
            continue
        if "".join(t.text or "" for t in ts).strip():
            ts[0].text = (ts[0].text or "").lstrip()
            return
        r.getparent().remove(r)


def caption_align(text: str):
    """llncs: short captions are centred, long ones justified (one line is about 95 characters at 9 pt)."""
    return J.CENTER if len(text) <= 95 else J.JUSTIFY


def number_figure_caption(doc, cap_el, counters: Counters, log) -> None:
    counters.figures += 1
    n = counters.figures
    para = Paragraph(cap_el, doc._body)
    restyle_runs(cap_el, size=SIZE["caption"], italic=False, bold=False)
    label = f"Fig. {n}."
    insert_runs_first(cap_el, [make_run(label, bold=True, italic=False, size=SIZE["caption"]), make_run(" ", bold=False, italic=False, size=SIZE["caption"])])
    fmt(para, caption_align(label + " " + p_text(cap_el)), first=Mm(0), sb=6, sa=12, line_pt=11)
    log(f"figure {n}")


def number_table(doc, cap_el, tbl_el, counters: Counters, log) -> None:
    counters.tables += 1
    n = counters.tables
    label = f"Table {n}."
    if cap_el is not None:
        restyle_runs(cap_el, size=SIZE["caption"], italic=False, bold=False)
        insert_runs_first(cap_el, [make_run(label, bold=True, italic=False, size=SIZE["caption"]),
                                   make_run(" ", bold=False, italic=False, size=SIZE["caption"])])
    else:
        cap_el = OxmlElement("w:p")
        tbl_el.addprevious(cap_el)
        cap_el.append(make_run(label, bold=True, italic=False, size=SIZE["caption"]))
    fmt(Paragraph(cap_el, doc._body), caption_align(p_text(cap_el)), first=Mm(0), sb=12, sa=6, line_pt=11,
        keep_next=True)
    format_table(doc, tbl_el)
    log(f"table {n}" + ("" if p_text(cap_el).strip() != label else " (WITHOUT caption)"))


def _border(tag: str, sz: int):
    e = OxmlElement(f"w:{tag}")
    e.set(qn("w:val"), "single" if sz else "nil")
    if sz:
        e.set(qn("w:sz"), str(sz))
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), "000000")
    return e


def format_table(doc, tbl_el) -> None:
    """Centred table with horizontal rules only (top, under the header row, bottom), 9 pt text."""
    tbl = Table(tbl_el, doc._body)
    tblPr = tbl_el.tblPr
    for tag in ("w:tblBorders", "w:jc", "w:tblStyle"):
        for old in tblPr.findall(qn(tag)):
            tblPr.remove(old)
    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.insert(0, tblW)
    tblW.set(qn("w:type"), "auto")
    tblW.set(qn("w:w"), "0")
    jc = OxmlElement("w:jc")
    jc.set(qn("w:val"), "center")
    tblW.addnext(jc)
    borders = OxmlElement("w:tblBorders")
    for edge, sz in (("top", 8), ("left", 0), ("bottom", 8), ("right", 0), ("insideH", 0), ("insideV", 0)):
        borders.append(_border(edge, sz))
    ind = tblPr.find(qn("w:tblInd"))
    (ind if ind is not None else jc).addnext(borders)
    fit_table_width(tbl_el)
    rows = list(tbl.rows)
    header_rows = sum(1 for r in rows if r._tr.trPr is not None and r._tr.trPr.find(qn("w:tblHeader")) is not None)
    header_rows = header_rows or 1
    for k, row in enumerate(rows):
        trPr = row._tr.get_or_add_trPr()
        if trPr.find(qn("w:cantSplit")) is None:
            trPr.insert(0, OxmlElement("w:cantSplit"))
        for cell in row.cells:
            if k == header_rows - 1 and len(rows) > 1:
                tcPr = cell._tc.get_or_add_tcPr()
                for old in tcPr.findall(qn("w:tcBorders")):
                    tcPr.remove(old)
                tcb = OxmlElement("w:tcBorders")
                tcb.append(_border("bottom", 4))
                # CT_TcPr order: cnfStyle, tcW, gridSpan, hMerge, vMerge, tcBorders, ...
                after = None
                for tag in ("w:vMerge", "w:hMerge", "w:gridSpan", "w:tcW", "w:cnfStyle"):
                    after = tcPr.find(qn(tag))
                    if after is not None:
                        break
                (after.addnext(tcb) if after is not None else tcPr.insert(0, tcb))
            for p in cell.paragraphs:
                fmt(p, J.LEFT, first=Mm(0), line_pt=11, keep_next=k < len(rows) - 1)
                restyle_runs(p._p, size=SIZE["table"], bold=True if k < header_rows and len(rows) > 1 else None)


def fit_table_width(tbl_el) -> None:
    """Keep the table inside the 122 mm text width: scale pandoc's column grid, drop per-cell widths."""
    max_tw = int(round(TEXT_WIDTH_MM * TWIPS_PER_MM))
    grid = tbl_el.find(qn("w:tblGrid"))
    cols = grid.findall(qn("w:gridCol")) if grid is not None else []
    widths = [int(c.get(qn("w:w")) or 0) for c in cols]
    total = sum(widths)
    if cols and (total == 0 or total > max_tw):
        widths = [max_tw // len(cols)] * len(cols) if total == 0 else [w * max_tw // total for w in widths]
        for c, w in zip(cols, widths):
            c.set(qn("w:w"), str(w))
    for tcW in tbl_el.iter(qn("w:tcW")):
        tcW.getparent().remove(tcW)
    tblW = tbl_el.tblPr.find(qn("w:tblW"))
    if tblW is not None and cols:
        tblW.set(qn("w:type"), "dxa")
        tblW.set(qn("w:w"), str(sum(widths)))
    layout = tbl_el.tblPr.find(qn("w:tblLayout"))
    if layout is not None:
        layout.set(qn("w:type"), "fixed")


def is_figure_par(el) -> bool:
    return el.find(f".//{qn('w:drawing')}") is not None and not p_text(el).strip()


def process_body(doc, log) -> Counters:
    counters = Counters()
    body = doc.element.body
    children = list(body)
    i = 0
    no_indent = True  # first paragraph of the paper, after a heading, float or equation: not indented
    after_table = False  # the paragraph after a table gets the 12 pt space a float has in llncs
    while i < len(children):
        el = children[i]
        if el.tag == qn("w:p") and after_table:
            after_table = False
            if p_style(el) not in ("Heading1", "Heading2", "Heading3", "Heading4"):
                el.get_or_add_pPr()
                spacing_after_table = True
            else:
                spacing_after_table = False
        else:
            spacing_after_table = False
        if el.tag == qn("w:tbl"):
            prev = children[i - 1] if i else None
            cap = prev if prev is not None and prev.tag == qn("w:p") and p_style(prev) == "TableCaption" else None
            number_table(doc, cap, el, counters, log)
            no_indent = True
            after_table = True
            i += 1
            continue
        if el.tag != qn("w:p"):
            i += 1
            continue
        st = p_style(el)
        para = Paragraph(el, doc._body)
        if st == "TableCaption":
            i += 1
            continue
        if el.find(f"{{{M_NS}}}oMathPara") is not None:
            ended_eq = split_display_math(doc, el, counters, log)
            no_indent = ended_eq
            i += 1
            continue
        if st == "Heading1":
            counters.h1 += 1
            counters.h2 = 0
            insert_runs_first(el, [make_run(str(counters.h1), size=SIZE["h1"], bold=True),
                                   make_run(tab=True, size=SIZE["h1"])])
            fmt(para, J.LEFT, first=-HEADING_HANG, left=HEADING_HANG, sb=18, sa=12, line_pt=15, keep_next=True)
            restyle_runs(el, size=SIZE["h1"], bold=True)
            log(f"section {counters.h1} {p_text(el).strip()}")
            no_indent = True
        elif st == "Heading2":
            counters.h2 += 1
            num = f"{counters.h1}.{counters.h2}"
            insert_runs_first(el, [make_run(num, bold=True), make_run(tab=True)])
            fmt(para, J.LEFT, first=-HEADING_HANG, left=HEADING_HANG, sb=18, sa=8, keep_next=True)
            restyle_runs(el, size=SIZE["h2"], bold=True)
            log(f"subsection {num} {p_text(el).strip()}")
            no_indent = True
        elif st in ("Heading3", "Heading4", "Heading5", "Heading6"):
            run_in(doc, el, children, i, bold=st == "Heading3")
            no_indent = False
            nxt = children[i + 1] if i + 1 < len(children) else None
            if nxt is not None and nxt.getparent() is None:  # merged into the run-in heading paragraph
                i += 2
                continue
        elif st in ("CaptionedFigure", "Figure") or is_figure_par(el):
            fmt(para, J.CENTER, first=Mm(0), sb=12, sa=6, line_pt=None, keep_next=True)
            scale_drawing(el)
            no_indent = True
            nxt = children[i + 1] if i + 1 < len(children) else None
            if nxt is not None and nxt.tag == qn("w:p") and p_style(nxt) == "ImageCaption":
                number_figure_caption(doc, nxt, counters, log)
                i += 2
                continue
            counters.figures += 1
            log(f"figure {counters.figures} (WITHOUT caption)")
        elif st == "ImageCaption":
            number_figure_caption(doc, el, counters, log)
            no_indent = True
        elif st == "SourceCode":
            fmt(para, J.LEFT, first=Mm(0), sb=8, sa=8, line_pt=10)
            restyle_runs(el, code=True)
            no_indent = True
        elif el.find(f"{qn('w:pPr')}/{qn('w:numPr')}") is not None:
            fmt(para, J.JUSTIFY, first=None, left=None)
            pf = para.paragraph_format
            pf.first_line_indent = None
            pf.left_indent = None
            restyle_runs(el)
            no_indent = True
        else:
            fmt(para, J.JUSTIFY, first=Mm(0) if no_indent else INDENT, sb=12 if spacing_after_table else 0)
            restyle_runs(el)
            no_indent = False
        i += 1
    return counters


def run_in(doc, head_el, children, i, *, bold: bool) -> None:
    """Level-3/4 headings are run-in: 'Heading. Text follows' (bold / italic), unnumbered."""
    title = p_text(head_el).strip().rstrip(".")
    nxt = children[i + 1] if i + 1 < len(children) else None
    head_run = make_run(f"{title}.", bold=bold, italic=not bold)
    space = make_run(" ")
    sb = 18 if bold else 12  # splnproc: heading 3 18 pt before, heading 4 12 pt before
    if nxt is not None and nxt.tag == qn("w:p") and p_style(nxt) not in (
            "Heading1", "Heading2", "Heading3", "Heading4", "ImageCaption", "TableCaption", "SourceCode",
            "CaptionedFigure", "Figure") and not is_figure_par(nxt) and nxt.find(f"{{{M_NS}}}oMathPara") is None \
            and nxt.find(f"{qn('w:pPr')}/{qn('w:numPr')}") is None:
        para = Paragraph(nxt, doc._body)
        fmt(para, J.JUSTIFY, first=Mm(0), sb=sb)
        restyle_runs(nxt)
        insert_runs_first(nxt, [head_run, space])
        _trim_leading_space_after(nxt, 2)
        nxt.getparent().remove(nxt)
        head_el.addprevious(nxt)
        head_el.getparent().remove(head_el)
        children[i] = nxt
        children[i + 1] = OxmlElement("w:p")  # detached marker: tells process_body to skip it
    else:
        for r in list(runs_of(head_el)):
            r.getparent().remove(r)
        head_el.append(head_run)
        fmt(Paragraph(head_el, doc._body), J.JUSTIFY, first=Mm(0), sb=sb, keep_next=True)


def _trim_leading_space_after(p_el, skip: int) -> None:
    runs = [r for r in p_el if r.tag == qn("w:r")]
    for r in runs[skip:]:
        ts = r.findall(qn("w:t"))
        if ts and (ts[0].text or "").strip():
            ts[0].text = ts[0].text.lstrip()
            return


def par(doc, align, *, size: float, first=Mm(0), left=Mm(0), right=Mm(0), sb=0, sa=0, line_pt=11, keep_next=False):
    p = doc.add_paragraph()
    fmt(p, align, first=first, left=left, right=right, sb=sb, sa=sa, line_pt=line_pt, keep_next=keep_next)
    return p


def build_front(doc, meta: dict) -> list:
    els = []
    p = par(doc, J.CENTER, size=SIZE["title"], sa=24, line_pt=18, keep_next=True)
    add_text(p, str(meta["title"]).strip(), bold=True, size=SIZE["title"])
    els.append(p)

    # Authors: "First Author1[0000-...], Second Author2,3(✉)[...], and Third Author3"
    p = par(doc, J.CENTER, size=SIZE["author"], sa=10)
    authors = meta["authors"]
    multi_aff = len(meta["affiliations"]) > 1
    for k, a in enumerate(authors):
        if k:
            add_text(p, ", and " if k == len(authors) - 1 and len(authors) > 2 else
                     (" and " if k == len(authors) - 1 else ", "), markup=False)
        add_text(p, author_name(a), markup=False)
        if multi_aff:
            add_text(p, ",".join(str(n) for n in a["affiliations"]), superscript=True, markup=False)
        if a.get("corresponding"):
            add_text(p, f"({ENVELOPE})", markup=False, font="Segoe UI Symbol", size=SIZE["address"])
        orcid = normalize_orcid(a.get("orcid"))
        if orcid:
            add_text(p, f"[{orcid}]", superscript=True, markup=False)
    els.append(p)

    emails = affiliation_emails(meta)
    affs = meta["affiliations"]
    for n, aff in enumerate(affs, 1):
        p = par(doc, J.CENTER, size=SIZE["address"], sa=0 if n < len(affs) else 10)
        if multi_aff:
            add_text(p, str(n), superscript=True, size=SIZE["address"], markup=False)
            add_text(p, " ", size=SIZE["address"], markup=False)
        add_text(p, affiliation_text(aff), size=SIZE["address"], markup=False)
        if emails.get(n):
            p.add_run().add_break()
            add_text(p, ", ".join(emails[n]), size=SIZE["address"], markup=False, font="Courier New")
        els.append(p)

    p = par(doc, J.JUSTIFY, size=SIZE["abstract"], left=Mm(10), right=Mm(10), sb=30, sa=0)
    add_text(p, "Abstract. ", bold=True, size=SIZE["abstract"], markup=False)
    add_text(p, " ".join(str(meta["abstract"]).split()), size=SIZE["abstract"])
    els.append(p)
    p = par(doc, J.LEFT, size=SIZE["abstract"], left=Mm(10), right=Mm(10), sb=11, sa=18)
    add_text(p, "Keywords: ", bold=True, size=SIZE["abstract"], markup=False)
    kws = ", ".join(keywords(meta))
    add_text(p, kws if kws.endswith(".") else kws + ".", size=SIZE["abstract"])
    els.append(p)
    return [e._p for e in els]


def build_tail(doc, meta: dict) -> None:
    credits = [("Acknowledgments.", meta.get("acknowledgments")),
               ("Disclosure of Interests.", meta.get("disclosure")),
               ("Disclosure of AI Use.", meta.get("ai_disclosure"))]
    first = True
    for head, text in credits:
        if not str(text or "").strip():
            continue
        p = par(doc, J.JUSTIFY, size=SIZE["credits"], sb=12 if first else 6)
        add_text(p, head + " ", bold=True, size=SIZE["credits"], markup=False)
        add_text(p, " ".join(str(text).split()), size=SIZE["credits"])
        first = False

    p = par(doc, J.LEFT, size=SIZE["h1"], sb=18, sa=12, line_pt=15, keep_next=True)
    add_text(p, "References", bold=True, size=SIZE["h1"], markup=False)
    hang = 8.0  # mm: number, tab, entry text aligned like llncs' thebibliography
    for n, ref in enumerate(references(meta), 1):
        p = par(doc, J.JUSTIFY, size=SIZE["reference"], first=-Mm(hang), left=Mm(hang))
        set_tabs(p._p, [("left", hang)])
        add_text(p, f"{n}.", size=SIZE["reference"], markup=False)
        p._p.append(make_run(tab=True, size=SIZE["reference"]))
        add_text(p, ref, size=SIZE["reference"])


def preprocess_docx_body(body: str, meta: dict) -> str:
    """Normalise citation groups ('[3-5]' -> '[3–5]') and attach the AI-use footnote to the first paragraph."""
    clean = strip_code(body)
    out, last = [], 0
    for m in CITE_RE.finditer(clean):
        out.append(body[last:m.start()])
        out.append(format_citation(citation_numbers(m.group(1))))
        last = m.end()
    out.append(body[last:])
    body = "".join(out)
    if str(meta.get("ai_disclosure") or "").strip():
        # pandoc footnote on the first ordinary paragraph (first page) -- the wording Springer prescribes.
        paras = list(re.finditer(r"(?ms)^(?![#|!$:>\-*\d\s])[^\n].*?(?=\n\s*\n|\Z)", body))
        if paras:
            p = paras[0]
            body = body[:p.end()] + f"^[{AI_NOTE}]" + body[p.end():]
    return body


def run_pandoc_docx(body: str, resource_dir: Path, out: Path) -> None:
    pandoc = pypandoc.get_pandoc_path()
    cmd = [pandoc, "-f", "markdown-citations-auto_identifiers", "-t", "docx", "-o", str(out),
           "--resource-path", str(resource_dir), "--wrap=none"]
    proc = subprocess.run(cmd, input=body, capture_output=True, text=True, encoding="utf-8")
    problems = [ln for ln in proc.stderr.splitlines()
                if "Could not fetch resource" in ln or "Could not find image" in ln or "Could not convert TeX math" in ln]
    if proc.returncode != 0 or problems:
        fail([f"pandoc: {ln}" for ln in (problems or proc.stderr.splitlines() or ["failed"])])
    for ln in proc.stderr.splitlines():
        if ln.strip():
            print(f"WARN: pandoc: {ln}", file=sys.stderr)


def style_footnotes(doc) -> None:
    """Footnotes (the AI-use note) in 9 pt Times like the template's 'footnote text'."""
    from lxml import etree

    for rel in doc.part.rels.values():
        if not rel.reltype.endswith("/footnotes"):
            continue
        part = rel.target_part
        root = part.element if hasattr(part, "element") else etree.fromstring(part.blob)
        for r in root.iter(qn("w:r")):
            if r.find(f"{qn('w:rPr')}/{qn('w:vertAlign')}") is None:
                style_run(r, size=SIZE["caption"])
        if not hasattr(part, "element"):
            part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def build_docx(src, out_path: Path, log) -> Counters:
    meta = src.meta
    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "pandoc.docx"
        run_pandoc_docx(preprocess_docx_body(src.body, meta), src.path.parent.resolve(), raw)
        doc = Document(str(raw))
        setup_document(doc, str(meta["title"]).strip(), ", ".join(author_name(a) for a in meta["authors"]))
        fix_numbering(doc)
        counters = process_body(doc, log)
        front = build_front(doc, meta)
        body = doc.element.body
        for k, el in enumerate(front):
            body.remove(el)
            body.insert(k, el)
        build_tail(doc, meta)
        style_footnotes(doc)
        tmp_out = Path(td) / "out.docx"
        doc.save(str(tmp_out))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(tmp_out, out_path)
    return counters


# ================================================================ LaTeX (llncs)

_TEX_SPECIAL = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
                "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
_URL_IN_TEXT = re.compile(r"https?://[^\s<>()]+[^\s<>().,;:]|www\.[^\s<>()]+[^\s<>().,;:]")


def tex_escape(s: str) -> str:
    return "".join(_TEX_SPECIAL.get(c, c) for c in s)


def tex_url(url: str) -> str:
    m = re.match(r"https?://(?:dx\.)?doi\.org/(10\..+)$", url)
    if m:
        return r"\doi{" + m.group(1) + "}"
    return r"\url{" + url.replace("%", r"\%").replace("#", r"\#") + "}"


def tex_plain(s: str) -> str:
    """Escape plain text but turn URLs into \\url / \\doi."""
    out, last = [], 0
    for m in _URL_IN_TEXT.finditer(s):
        out.append(tex_escape(s[last:m.start()]))
        out.append(tex_url(m.group(0)))
        last = m.end()
    out.append(tex_escape(s[last:]))
    return "".join(out)


def tex_inline(text: str, *, math: bool = True) -> str:
    """YAML string -> LaTeX: **bold**/*italic* markup, $math$ kept as is, URLs/DOIs, everything else escaped."""
    text = " ".join(str(text).split())
    pieces = re.split(r"((?<!\\)\$[^$]+\$)", text) if math else [text]
    out = []
    for piece in pieces:
        if math and piece.startswith("$") and piece.endswith("$") and len(piece) > 1:
            out.append(piece)
            continue
        for t, b, i in inline_segments(piece):
            s = tex_plain(t)
            out.append(r"\textbf{" + s + "}" if b else r"\emph{" + s + "}" if i else s)
    return "".join(out)


LUA_FILTER = r"""
-- Lua filter for build_paper.py --latex: llncs-friendly figures, tables and numbered equations.
local function latex(blocks)
  return (pandoc.write(pandoc.Pandoc(blocks), 'latex'):gsub('%s+$', ''))
end
local function inl(inlines)
  return latex({pandoc.Plain(inlines)})
end
local function blocks_text(blocks)
  local out = {}
  for _, b in ipairs(blocks) do
    if b.content then table.insert(out, inl(b.content)) else table.insert(out, latex({b})) end
  end
  return table.concat(out, ' ')
end

local fig_n, tab_n = 0, 0

function Figure(fig)
  fig_n = fig_n + 1
  local img
  fig.content:walk({Image = function(i) img = i end})
  if not img then return nil end
  local width = img.attributes['width']
  local opt
  if width and width:match('%%$') then
    opt = string.format('width=%.2f\\textwidth', tonumber(width:sub(1, -2)) / 100)
  elseif width then
    opt = 'width=' .. width
  else
    opt = 'width=\\textwidth,height=0.45\\textheight,keepaspectratio'
  end
  local cap = blocks_text(fig.caption.long)
  -- pandoc stores {alt="..."} as the image's own inlines (it equals the caption when no alt is given)
  local alt = pandoc.utils.stringify(img.caption)
  if alt == '' then alt = pandoc.utils.stringify(fig.caption.long) end
  local lines = {
    '\\begin{figure}[tbp]',
    '\\centering',
    string.format('\\includegraphics[%s]{%s}', opt, img.src),
    '\\Description{' .. alt:gsub('[%%#&_{}$]', function(c) return '\\' .. c end) .. '}',
    '\\caption{' .. cap .. '}\\label{fig' .. fig_n .. '}',
    '\\end{figure}'
  }
  return pandoc.RawBlock('latex', table.concat(lines, '\n'))
end

local function cell_tex(cell)
  return blocks_text(cell.contents)
end

local align_map = {AlignLeft = 'l', AlignRight = 'r', AlignCenter = 'c', AlignDefault = 'l'}

function Table(tbl)
  tab_n = tab_n + 1
  local spec = {}
  for _, cs in ipairs(tbl.colspecs) do table.insert(spec, align_map[tostring(cs[1])] or 'l') end
  local rows = {}
  local function add_rows(rs, bold)
    for _, row in ipairs(rs) do
      local cells = {}
      for _, c in ipairs(row.cells) do
        local t = cell_tex(c)
        if bold and t ~= '' then t = '\\textbf{' .. t .. '}' end
        table.insert(cells, t)
      end
      table.insert(rows, table.concat(cells, ' & ') .. ' \\\\')
    end
  end
  local has_head = #tbl.head.rows > 0
  add_rows(tbl.head.rows, true)
  if has_head then table.insert(rows, '\\hline') end
  for _, b in ipairs(tbl.bodies) do add_rows(b.body, false) end
  local cap = blocks_text(tbl.caption.long)
  local lines = {
    '\\begin{table}[tbp]',
    '\\centering',
    '\\caption{' .. cap .. '}\\label{tab' .. tab_n .. '}',
    '\\begin{tabular}{' .. table.concat(spec) .. '}',
    '\\hline',
    table.concat(rows, '\n'),
    '\\hline',
    '\\end{tabular}',
    '\\end{table}'
  }
  return pandoc.RawBlock('latex', table.concat(lines, '\n'))
end

-- A paragraph that holds display math: split into text / equation / text; text after an equation gets \noindent.
function Para(p)
  local has = false
  for _, x in ipairs(p.content) do if x.t == 'Math' and x.mathtype == 'DisplayMath' then has = true end end
  if not has then return nil end
  local out, cur, after_eq = {}, {}, false
  local function flush()
    while #cur > 0 and (cur[1].t == 'Space' or cur[1].t == 'SoftBreak') do table.remove(cur, 1) end
    if #cur > 0 then
      local t = inl(cur)
      if after_eq then t = '\\noindent ' .. t end
      table.insert(out, pandoc.RawBlock('latex', t))
    end
    cur = {}
  end
  for _, x in ipairs(p.content) do
    if x.t == 'Math' and x.mathtype == 'DisplayMath' then
      flush()
      table.insert(out, pandoc.RawBlock('latex', '\\begin{equation}\n' .. x.text:gsub('^%s+', ''):gsub('%s+$', '') .. '\n\\end{equation}'))
      after_eq = true
    else
      table.insert(cur, x)
    end
  end
  flush()
  return out
end
"""


def preprocess_latex_body(body: str) -> str:
    """Numeric citations -> raw \\cite{refN,...} (refN = Nth entry of the reference list)."""
    clean = strip_code(body)
    out, last = [], 0
    for m in CITE_RE.finditer(clean):
        keys = ",".join(f"ref{n}" for n in citation_numbers(m.group(1)))
        out.append(body[last:m.start()])
        out.append("`\\cite{" + keys + "}`{=latex}")
        last = m.end()
    out.append(body[last:])
    return "".join(out)


def run_pandoc_latex(body: str, resource_dir: Path) -> str:
    pandoc = pypandoc.get_pandoc_path()
    with tempfile.TemporaryDirectory() as td:
        lua = Path(td) / "llncs.lua"
        lua.write_text(LUA_FILTER, encoding="utf-8")
        cmd = [pandoc, "-f", "markdown-citations-auto_identifiers-implicit_figures+implicit_figures",
               "-t", "latex", "--wrap=preserve", "--lua-filter", str(lua), "--resource-path", str(resource_dir)]
        proc = subprocess.run(cmd, input=body, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        fail([f"pandoc: {ln}" for ln in (proc.stderr.splitlines() or ["failed"])])
    tex = proc.stdout
    # pandoc adds \hypertarget/\label wrappers for headings only with auto_identifiers (disabled) -- nothing to strip.
    # Tight lists: pandoc emits \tightlist, which llncs does not define (defined in the preamble instead).
    return tex


def latex_document(meta: dict, body_tex: str) -> str:
    affs = meta["affiliations"]
    multi_aff = len(affs) > 1
    emails = affiliation_emails(meta)
    author_tex = []
    for a in meta["authors"]:
        s = tex_escape(author_name(a))
        if multi_aff:
            s += r"\inst{" + ",".join(str(n) for n in a["affiliations"]) + "}"
        if a.get("corresponding"):
            s += r"\textsuperscript{(\Envelope)}"
        orcid = normalize_orcid(a.get("orcid"))
        if orcid:
            s += r"\orcidID{" + tex_escape(orcid) + "}"
        author_tex.append(s)
    inst_tex = []
    for n, aff in enumerate(affs, 1):
        s = tex_plain(affiliation_text(aff))
        if emails.get(n):
            s += r"\\" + "\n" + r"\email{" + ", ".join(tex_escape(e) for e in emails[n]) + "}"
        inst_tex.append(s)
    kws = r" \and ".join(tex_inline(k) for k in keywords(meta))
    kws = kws if kws.endswith(".") else kws + "."

    credits = []
    if str(meta.get("acknowledgments") or "").strip():
        credits.append(r"\subsubsection{\ackname} " + tex_inline(meta["acknowledgments"]))
    if str(meta.get("disclosure") or "").strip():
        credits.append(r"\subsubsection{\discintname} " + tex_inline(meta["disclosure"]))
    if str(meta.get("ai_disclosure") or "").strip():
        credits.append(r"\subsubsection{Disclosure of AI Use.} " + tex_inline(meta["ai_disclosure"]))

    refs = references(meta)
    bib = [r"\begin{thebibliography}{" + "9" * len(str(len(refs))) + "}"]
    for n, r in enumerate(refs, 1):
        bib.append(r"\bibitem{ref" + str(n) + "}\n" + tex_inline(r, math=False))
    bib.append(r"\end{thebibliography}")

    title = tex_inline(meta["title"])
    lines = [
        "% Generated by lnns-paper-format/build_paper.py from paper.md -- edit paper.md and rebuild.",
        "% Springer proceedings template (llncs), as used by Lecture Notes in Networks and Systems.",
        r"\documentclass[runningheads]{llncs}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage{newtxtext}",
        r"\usepackage[varvw]{newtxmath}  % Times, as in samplepaper.tex v2.25 (2026); loads amsmath",
        r"\usepackage{graphicx}",
        r"\usepackage{url}",
        r"\usepackage{bbding}  % \Envelope marks the corresponding author",
        r"\providecommand{\Description}[1]{}  % alt text; defined by llncs.cls v2.25 (2026), harmless otherwise",
        r"\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}",
        r"\providecommand{\pandocbounded}[1]{#1}",
        r"\begin{document}",
        r"\title{" + title + "}",
    ]
    if str(meta.get("running_title") or "").strip():
        lines.append(r"\titlerunning{" + tex_inline(meta["running_title"]) + "}")
    lines += [
        r"\author{" + " \\and\n".join(author_tex) + "}",
        r"\authorrunning{" + tex_escape(author_running(meta["authors"])) + "}",
        r"\institute{" + " \\and\n".join(inst_tex) + "}",
        r"\maketitle",
    ]
    if str(meta.get("ai_disclosure") or "").strip():
        lines.append(r"{\renewcommand{\thefootnote}{}\footnotetext{" + tex_escape(AI_NOTE) + "}}")
    lines += [
        r"\begin{abstract}",
        tex_inline(meta["abstract"]),
        "",
        r"\keywords{" + kws + "}",
        r"\end{abstract}",
        "",
        body_tex.strip(),
        "",
    ]
    if credits:
        lines += [r"\begin{credits}", "\n\n".join(credits), r"\end{credits}", ""]
    lines += bib + [r"\end{document}", ""]
    return "\n".join(lines)


def build_latex(src, out_dir: Path, log, compile_pdf: bool) -> Path:
    meta = src.meta
    body_tex = run_pandoc_latex(preprocess_latex_body(src.body), src.path.parent.resolve())
    tex = latex_document(meta, body_tex)
    images = []
    for m in IMAGE_RE.finditer(strip_code(src.body)):
        p = Path(m.group("src"))
        images.append((m.group("src"), p if p.is_absolute() else src.path.parent / p))
    missing = [s for s, p in images if not p.is_file()]
    if missing:
        fail([f"image not found: {s}" for s in missing])
    out_dir.mkdir(parents=True, exist_ok=True)
    for rel, p in images:
        dst = out_dir / (Path(rel).name if Path(rel).is_absolute() or rel.startswith("..") else rel)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, dst)
        if Path(rel).is_absolute() or rel.startswith(".."):
            tex = tex.replace("{" + rel + "}", "{" + Path(rel).name + "}")
    for f in ("llncs.cls", "splncs04.bst"):
        shutil.copyfile(LATEX_ASSETS / f, out_dir / f)
    tex_path = out_dir / "paper.tex"
    tex_path.write_text(tex, encoding="utf-8")
    log(f"latex: {tex_path} ({len(images)} image(s) copied)")
    if compile_pdf:
        compile_latex(tex_path)
    return tex_path


def compile_latex(tex_path: Path) -> None:
    if shutil.which("latexmk"):
        cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
    elif shutil.which("pdflatex"):
        cmd = ["sh", "-c", f"pdflatex -interaction=nonstopmode -halt-on-error {tex_path.name} && "
                           f"pdflatex -interaction=nonstopmode -halt-on-error {tex_path.name}"]
    elif shutil.which("tectonic"):
        cmd = ["tectonic", tex_path.name]
    else:
        print("WARN: no LaTeX engine found (latexmk/pdflatex/tectonic); upload the folder to Overleaf and "
              "compile paper.tex there", file=sys.stderr)
        return
    proc = subprocess.run(cmd, cwd=tex_path.parent, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = "\n".join(proc.stdout.splitlines()[-25:])
        fail([f"LaTeX compilation failed ({cmd[0]}); last lines of the log:\n{tail}"])
    print(f"compiled {tex_path.with_suffix('.pdf')}", file=sys.stderr)


# ================================================================ main

def build(src_path: Path, docx_out: Path | None, latex_out: Path | None, verbose: bool = False,
          compile_pdf: bool = False):
    log = (lambda m: print(f"  {m}", file=sys.stderr)) if verbose else (lambda m: None)
    try:
        src = load_source(src_path)
    except SourceError as exc:
        fail([str(exc)])
    errs = required_errors(src.meta)
    if errs:
        fail(errs)
    counters = None
    if docx_out:
        counters = build_docx(src, docx_out, log)
        print(f"built {docx_out} -- sections={counters.h1}, figures={counters.figures}, tables={counters.tables}, "
              f"equations={counters.equations}, references={len(references(src.meta))}", file=sys.stderr)
    if latex_out:
        tex = build_latex(src, latex_out, log, compile_pdf)
        print(f"built {tex}", file=sys.stderr)
    return counters


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("source", type=Path, help="manuscript Markdown file with YAML front matter")
    ap.add_argument("--docx", type=Path, help="output .docx (Springer Word template layout)")
    ap.add_argument("--latex", type=Path, help="output directory for the llncs LaTeX project (paper.tex)")
    ap.add_argument("--compile", action="store_true", help="compile the LaTeX project if a TeX engine is installed")
    ap.add_argument("--verbose", action="store_true", help="log every numbered section/figure/table/equation")
    args = ap.parse_args(argv)
    if not args.source.is_file():
        fail([f"source file not found: {args.source}"])
    if not args.docx and not args.latex:
        args.docx = args.source.with_suffix(".docx")
    if args.docx and args.docx.suffix.lower() != ".docx":
        fail([f"--docx must end with .docx (Springer does not accept .docm or .doc): {args.docx}"])
    build(args.source, args.docx, args.latex, args.verbose, args.compile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
