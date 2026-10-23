# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-docx>=1.1",
#     "pyyaml>=6",
#     "pypandoc_binary>=1.13",
# ]
# ///
"""build_paper.py -- Markdown + YAML manuscript -> .docx formatted for the
journal «Адаптивні системи автоматичного управління» (ASAC, https://asac.kpi.ua).

    uv run build_paper.py paper.md --out paper.docx [--verbose]

The source is one Markdown file whose YAML front matter carries everything
that is not running text (UDC, titles, authors, both abstracts and keyword
lists, references, funding...) and whose body is the article itself
(`# Heading` sections, `## Subheading`, $$display math$$, pipe tables with a
`Table: caption` line, `![caption](image.png)` figures, numeric citations [1]).
See references/manuscript-format.md for the full field reference.

Pipeline: the body goes through pandoc (bundled via pypandoc_binary, so display
math becomes native, editable Word equations -- the journal accepts
"Microsoft Equation"), then python-docx post-processing applies the journal's
fixed layout: A4, 25 mm margins, Times New Roman 13 pt, line spacing 1.3,
12.5 mm first-line indent, no automatic hyphenation, the official title block
(UDC / authors / TITLE / Abstract / Keywords), "Figure N." and "Table N."
captions, right-aligned equation numbers, the reference list, and the
separate-page end matter (both abstracts, keywords and author information in
Ukrainian and English).

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
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Emu, Mm, Pt
from docx.table import Table
from docx.text.paragraph import Paragraph

from asac_common import (
    ABSTRACT_PARTS,
    FIRST_LINE_INDENT_MM,
    FONT,
    FONT_SIZE_PT,
    LABELS,
    LINE_SPACING,
    MARGIN_MM,
    PAGE_H_MM,
    PAGE_W_MM,
    TEXT_WIDTH_MM,
    SourceError,
    author_bib,
    author_full,
    author_short,
    inline_segments,
    load_source,
    required_errors,
)

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
CODE_STYLES = {"SourceCode", "VerbatimChar"}
BODY_STYLES = {"BodyText", "FirstParagraph", "Compact", "BlockText", "Normal", None}
INDENT = Mm(FIRST_LINE_INDENT_MM)
TWIPS_PER_MM = 1440 / 25.4

J = WD_ALIGN_PARAGRAPH


def fail(msgs: list[str]) -> None:
    for m in msgs:
        print(f"error: {m}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------- low-level formatting

def style_run(r_el, *, size: float = FONT_SIZE_PT, bold: bool | None = None, italic: bool | None = None,
              font: str = FONT, black: bool = False) -> None:
    rPr = r_el.get_or_add_rPr()
    rfonts = rPr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rPr.insert(0, rfonts)
    for attr in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        rfonts.attrib.pop(qn(f"w:{attr}"), None)
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        rfonts.set(qn(f"w:{attr}"), font)
    for tag in ("w:sz", "w:szCs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = OxmlElement(tag)
            rPr.append(el)
        el.set(qn("w:val"), str(int(round(size * 2))))
    for tag, val in (("w:b", bold), ("w:i", italic)):
        if val is None:
            continue
        for old in rPr.findall(qn(tag)):
            rPr.remove(old)
        el = OxmlElement(tag)
        if not val:
            el.set(qn("w:val"), "0")
        rPr.append(el)
    if black:
        for old in rPr.findall(qn("w:color")) + rPr.findall(qn("w:u")):
            rPr.remove(old)
        c = OxmlElement("w:color")
        c.set(qn("w:val"), "000000")
        rPr.append(c)
    _sort_rpr(rPr)


# CT_RPr children must appear in schema order or Word reports the file as corrupt.
_RPR_ORDER = ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline",
              "shadow", "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing",
              "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText",
              "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath"]


def _sort_rpr(rPr) -> None:
    rank = {qn(f"w:{n}"): i for i, n in enumerate(_RPR_ORDER)}
    kids = list(rPr)
    kids.sort(key=lambda e: rank.get(e.tag, len(_RPR_ORDER)))
    for k in kids:
        rPr.remove(k)
    for k in kids:
        rPr.append(k)


def fmt(p: Paragraph, align, *, first=INDENT, left=Mm(0), sb: float = 0, sa: float = 0,
        ls: float = LINE_SPACING, keep_next: bool = False, page_break_before: bool = False) -> None:
    pf = p.paragraph_format
    pf.alignment = align
    pf.first_line_indent = first
    pf.left_indent = left
    pf.right_indent = Mm(0)
    pf.space_before = Pt(sb)
    pf.space_after = Pt(sa)
    pf.line_spacing = ls
    pf.keep_with_next = keep_next
    pf.widow_control = True
    if page_break_before:
        pf.page_break_before = True


def runs_of(el):
    """All w:r under a paragraph, including those nested in w:hyperlink / smart tags (not math runs)."""
    return el.iter(qn("w:r"))


def restyle_runs(p_el, *, size: float = FONT_SIZE_PT, bold: bool | None = None, italic: bool | None = None,
                 code: bool = False) -> None:
    for r in runs_of(p_el):
        rstyle = r.find(f"{qn('w:rPr')}/{qn('w:rStyle')}")
        is_code = code or (rstyle is not None and rstyle.get(qn("w:val")) in CODE_STYLES)
        in_link = r.getparent().tag == qn("w:hyperlink")
        if is_code:
            style_run(r, size=11, font="Courier New")
        else:
            style_run(r, size=size, bold=bold, italic=italic, black=in_link or rstyle is not None)


def p_style(p_el) -> str | None:
    ps = p_el.find(f"{qn('w:pPr')}/{qn('w:pStyle')}")
    return ps.get(qn("w:val")) if ps is not None else None


def add_text(p: Paragraph, text: str, *, bold=False, italic=False, size: float = FONT_SIZE_PT, markup: bool = True):
    segs = inline_segments(text) if markup else [(text, False, False)]
    for t, b, i in segs:
        r = p.add_run(t)
        style_run(r._r, size=size, bold=bold or b, italic=italic or i)


def new_par(doc, text: str = "", **kw) -> Paragraph:
    p = doc.add_paragraph()
    if text:
        add_text(p, text, **kw)
    return p


def set_tabs(p_el, stops: list[tuple[str, float]]) -> None:
    pPr = p_el.get_or_add_pPr()
    tabs = pPr.find(qn("w:tabs"))
    if tabs is not None:
        pPr.remove(tabs)
    tabs = OxmlElement("w:tabs")
    for kind, mm in stops:
        t = OxmlElement("w:tab")
        t.set(qn("w:val"), kind)
        t.set(qn("w:pos"), str(int(round(mm * TWIPS_PER_MM))))
        tabs.append(t)
    # w:tabs sits right after pStyle/keepNext/... -- inserting after pStyle (or first) is schema-valid enough
    # for Word because python-docx keeps pPr children ordered on its own setters; place it early.
    anchor = pPr.find(qn("w:pStyle"))
    if anchor is not None:
        anchor.addnext(tabs)
    else:
        pPr.insert(0, tabs)


def make_run(text: str | None = None, *, tab: bool = False, italic: bool = False):
    r = OxmlElement("w:r")
    if tab:
        r.append(OxmlElement("w:tab"))
    if text is not None:
        t = OxmlElement("w:t")
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = text
        r.append(t)
    style_run(r, italic=italic or None)
    return r


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


# ---------------------------------------------------------------- document-level settings

def setup_document(doc, lang: str, title: str, authors: str) -> None:
    for s in doc.sections:
        s.page_width, s.page_height = Mm(PAGE_W_MM), Mm(PAGE_H_MM)
        s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Mm(MARGIN_MM)
        s.header_distance = s.footer_distance = Mm(MARGIN_MM / 2)

    settings = doc.settings.element
    for el in settings.findall(qn("w:autoHyphenation")):
        settings.remove(el)
    hy = OxmlElement("w:autoHyphenation")
    hy.set(qn("w:val"), "false")
    anchor = settings.find(qn("w:defaultTabStop"))
    if anchor is not None:
        anchor.addnext(hy)
    else:
        settings.insert(0, hy)

    lang_code = "uk-UA" if lang == "uk" else "en-US"
    defaults = doc.styles.element.find(qn("w:docDefaults"))
    if defaults is not None:
        rpr = defaults.find(f"{qn('w:rPrDefault')}/{qn('w:rPr')}")
        if rpr is not None:
            style_run_like_rpr(rpr, lang_code)
            for tag in ("w:sz", "w:szCs"):
                el = rpr.find(qn(tag))
                if el is not None:
                    el.set(qn("w:val"), str(FONT_SIZE_PT * 2))
        spacing = defaults.find(f"{qn('w:pPrDefault')}/{qn('w:pPr')}/{qn('w:spacing')}")
        if spacing is not None:
            spacing.set(qn("w:after"), "0")
    styles = doc.styles
    for name in ("Normal", "Body Text", "First Paragraph", "Compact", "Block Text", "Image Caption",
                 "Table Caption", "Captioned Figure", "Figure", "Heading 1", "Heading 2", "Heading 3",
                 "Heading 4", "Title", "Footnote Text"):
        try:
            st = styles[name]
        except KeyError:
            continue
        st.font.name = FONT
        st.font.size = Pt(FONT_SIZE_PT)
        st.font.color.rgb = None
        rPr = st.element.get_or_add_rPr()
        style_run_like_rpr(rPr, lang_code)
        pf = st.paragraph_format
        pf.line_spacing = LINE_SPACING
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)

    doc.core_properties.title = title
    doc.core_properties.author = authors
    doc.core_properties.language = lang_code
    doc.core_properties.comments = "Formatted for «Адаптивні системи автоматичного управління» (asac.kpi.ua)"


def style_run_like_rpr(rPr, lang_code: str) -> None:
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
    lg.set(qn("w:val"), lang_code)
    rPr.append(lg)
    _sort_rpr(rPr)


def fix_numbering(doc) -> None:
    """Bullets become '–', every list's first level starts at the paragraph indent like body text."""
    try:
        numbering = doc.part.numbering_part.element
    except (NotImplementedError, KeyError, AttributeError):
        return
    indent_twips = str(int(round(FIRST_LINE_INDENT_MM * TWIPS_PER_MM)))
    for absnum in numbering.findall(qn("w:abstractNum")):
        for lvl in absnum.findall(qn("w:lvl")):
            ilvl = int(lvl.get(qn("w:ilvl")))
            fmt_el = lvl.find(qn("w:numFmt"))
            if fmt_el is not None and fmt_el.get(qn("w:val")) == "bullet":
                lvl_text = lvl.find(qn("w:lvlText"))
                if lvl_text is not None:
                    lvl_text.set(qn("w:val"), "–")
            pPr = lvl.find(qn("w:pPr"))
            if pPr is None:
                pPr = OxmlElement("w:pPr")
                lvl.append(pPr)
            for old in pPr.findall(qn("w:ind")):
                pPr.remove(old)
            ind = OxmlElement("w:ind")
            ind.set(qn("w:left"), str(int(round(ilvl * FIRST_LINE_INDENT_MM * TWIPS_PER_MM))))
            ind.set(qn("w:firstLine"), indent_twips)
            pPr.append(ind)
            for old in lvl.findall(qn("w:suff")):
                lvl.remove(old)
            suff = OxmlElement("w:suff")
            suff.set(qn("w:val"), "space")
            # w:suff comes right after w:lvlText / w:lvlRestart / w:pStyle / w:isLgl in CT_Lvl
            after = lvl.find(qn("w:lvlText"))
            (after if after is not None else lvl[-1]).addnext(suff)
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
            # Restore CT_Lvl child order: ... lvlText, lvlPicBulletId, legacy, lvlJc, pPr, rPr
            for tag in ("w:pPr", "w:rPr"):
                el = lvl.find(qn(tag))
                if el is not None:
                    lvl.remove(el)
                    lvl.append(el)


# ---------------------------------------------------------------- body post-processing

class Counters:
    def __init__(self):
        self.figures = 0
        self.tables = 0
        self.equations = 0


def scale_drawing(p_el) -> None:
    max_emu = int(Mm(TEXT_WIDTH_MM))
    for ext in p_el.iter(f"{{{WP_NS}}}extent"):
        cx, cy = int(ext.get("cx")), int(ext.get("cy"))
        if cx <= max_emu:
            continue
        k = max_emu / cx
        ext.set("cx", str(max_emu))
        ext.set("cy", str(int(cy * k)))
        drawing = ext.getparent()
        for aext in drawing.iter(f"{{{A_NS}}}ext"):
            if aext.get("cx") is not None:
                aext.set("cx", str(max_emu))
                aext.set("cy", str(int(int(aext.get("cy")) * k)))


def split_display_math(doc, p_el, lang: str, counters: Counters, log) -> None:
    """Turn a paragraph holding m:oMathPara into: [text before] / numbered equation line / [text after]."""
    children = [c for c in p_el if c.tag != qn("w:pPr")]
    # Pandoc emits one oMathPara per $$...$$; there may be several in one paragraph,
    # interleaved with the sentence that introduces the formula and the "where ..." that follows.
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

    anchor = p_el
    seen_eq = False
    for kind, nodes in groups:
        if kind == "text" and not has_visible_text(nodes):
            continue
        new_p = OxmlElement("w:p")
        if p_el.find(qn("w:pPr")) is not None:
            new_p.append(copy.deepcopy(p_el.find(qn("w:pPr"))))
        anchor.addnext(new_p)
        anchor = new_p
        para = Paragraph(new_p, doc._body)
        if kind == "eq":
            counters.equations += 1
            n = counters.equations
            omp = nodes[0]
            maths = omp.findall(f"{{{M_NS}}}oMath")
            new_p.append(make_run(tab=True))
            for k, m in enumerate(maths):
                if k:
                    new_p.append(make_run(" "))
                new_p.append(m)
            new_p.append(make_run(tab=True))
            new_p.append(make_run(f"({n})"))
            fmt(para, J.LEFT, first=Mm(0), sb=3, sa=3, keep_next=False)
            set_tabs(new_p, [("center", TEXT_WIDTH_MM / 2), ("right", TEXT_WIDTH_MM)])
            seen_eq = True
            log(f"equation ({n})")
        else:
            for nd in nodes:
                new_p.append(nd)
            _trim_leading_space(new_p)
            text = "".join(t.text or "" for t in new_p.iter(qn("w:t")))
            # The template sets the "where ..." explanation after a formula flush left, without indent.
            starts_where = seen_eq and starts_with_where(text, lang)
            fmt(para, J.JUSTIFY, first=Mm(0) if starts_where else INDENT)
            restyle_runs(new_p)
    p_el.getparent().remove(p_el)


def starts_with_where(text: str, lang: str) -> bool:
    return re.match(rf"\s*{LABELS[lang]['where']}\b", text, re.I) is not None


def _trim_leading_space(p_el) -> None:
    """Drop whitespace-only runs (pandoc's soft line breaks) at the start of a split-off paragraph."""
    for r in list(p_el.iter(qn("w:r"))):
        ts = r.findall(qn("w:t"))
        if not ts:
            continue
        if "".join(t.text or "" for t in ts).strip():
            ts[0].text = (ts[0].text or "").lstrip()
            return
        r.getparent().remove(r)


def number_figure_caption(doc, cap_el, lang: str, counters: Counters, log) -> None:
    counters.figures += 1
    n = counters.figures
    para = Paragraph(cap_el, doc._body)
    restyle_runs(cap_el, italic=False, bold=False)
    ppr = cap_el.find(qn("w:pPr"))
    label = make_run(f"{LABELS[lang]['figure']} {n}.", italic=True)
    cap_el.insert(0 if ppr is None else 1, label)
    label.addnext(make_run(" "))
    fmt(para, J.CENTER, first=Mm(0), sa=6)
    log(f"figure {n}")


def number_table(doc, cap_el, tbl_el, lang: str, counters: Counters, log) -> None:
    counters.tables += 1
    n = counters.tables
    if cap_el is not None:
        title = Paragraph(cap_el, doc._body)
        restyle_runs(cap_el, italic=False, bold=False)
        fmt(title, J.CENTER, first=Mm(0), keep_next=True)
        label_p = OxmlElement("w:p")
        cap_el.addprevious(label_p)
    else:
        label_p = OxmlElement("w:p")
        tbl_el.addprevious(label_p)
    lp = Paragraph(label_p, doc._body)
    label_p.append(make_run(f"{LABELS[lang]['table']} {n}.", italic=True))
    fmt(lp, J.RIGHT, first=Mm(0), keep_next=True)
    format_table(doc, tbl_el)
    log(f"table {n}" + ("" if cap_el is not None else " (WITHOUT caption)"))


def format_table(doc, tbl_el) -> None:
    tbl = Table(tbl_el, doc._body)
    tblPr = tbl_el.tblPr
    for tag in ("w:tblBorders", "w:jc"):
        for old in tblPr.findall(qn(tag)):
            tblPr.remove(old)
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "8")
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), "000000")
        borders.append(e)
    jc = OxmlElement("w:jc")
    jc.set(qn("w:val"), "center")
    # CT_TblPr order: tblStyle, tblpPr, tblOverlap, bidiVisual, tblStyleRowBandSize, tblStyleColBandSize, tblW, jc,
    # tblCellSpacing, tblInd, tblBorders, shd, tblLayout, tblCellMar, tblLook, tblCaption, tblDescription
    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        style = tblPr.find(qn("w:tblStyle"))
        (style.addnext(tblW) if style is not None else tblPr.insert(0, tblW))
    tblW.set(qn("w:type"), "pct")
    tblW.set(qn("w:w"), "5000")
    tblW.addnext(jc)
    jc.addnext(borders)
    rows = list(tbl.rows)
    for k, row in enumerate(rows):
        trPr = row._tr.get_or_add_trPr()
        if trPr.find(qn("w:cantSplit")) is None:
            trPr.insert(0, OxmlElement("w:cantSplit"))
        for cell in row.cells:
            for p in cell.paragraphs:
                # Keep short tables on one page (keep-with-next chains the rows; Word ignores it
                # once a table is longer than a page, so long tables still break normally).
                fmt(p, J.LEFT, first=Mm(0), ls=1.0, keep_next=k < len(rows) - 1)
                restyle_runs(p._p)


def process_body(doc, lang: str, log) -> Counters:
    counters = Counters()
    body = doc.element.body
    children = list(body)
    i = 0
    after_eq = False  # previous block was a display formula -> a following "where ..." is set flush left
    while i < len(children):
        el = children[i]
        was_after_eq, after_eq = after_eq, False
        if el.tag == qn("w:tbl"):
            prev = children[i - 1] if i else None
            cap = prev if prev is not None and prev.tag == qn("w:p") and p_style(prev) == "TableCaption" else None
            number_table(doc, cap, el, lang, counters, log)
            i += 1
            continue
        if el.tag != qn("w:p"):
            i += 1
            continue
        st = p_style(el)
        para = Paragraph(el, doc._body)
        if st == "TableCaption":
            i += 1  # handled together with the table that follows it
            continue
        if el.find(f"{{{M_NS}}}oMathPara") is not None:
            # Ends with a formula unless text follows the last $$...$$ in the same paragraph.
            tail = [c for c in el if c.tag != qn("w:pPr")]
            last_eq = max(k for k, c in enumerate(tail) if c.tag == f"{{{M_NS}}}oMathPara")
            after_eq = not has_visible_text(tail[last_eq + 1:])
            split_display_math(doc, el, lang, counters, log)
            i += 1
            continue
        if st == "Heading1":
            fmt(para, J.CENTER, first=Mm(0), sb=6, sa=3, keep_next=True)
            restyle_runs(el, bold=True)
        elif st == "Heading2":
            fmt(para, J.JUSTIFY, sb=3, keep_next=True)
            restyle_runs(el, bold=True)
        elif st in ("Heading3", "Heading4", "Heading5", "Heading6"):
            fmt(para, J.JUSTIFY, sb=3, keep_next=True)
            restyle_runs(el, bold=True, italic=True)
        elif st in ("CaptionedFigure", "Figure") or (el.find(f".//{qn('w:drawing')}") is not None
                                                      and not "".join(t.text or "" for t in el.iter(qn("w:t"))).strip()):
            fmt(para, J.CENTER, first=Mm(0), keep_next=True)
            scale_drawing(el)
            nxt = children[i + 1] if i + 1 < len(children) else None
            if nxt is not None and nxt.tag == qn("w:p") and p_style(nxt) == "ImageCaption":
                number_figure_caption(doc, nxt, lang, counters, log)
                i += 2
                continue
            counters.figures += 1
            log(f"figure {counters.figures} (WITHOUT caption)")
        elif st == "ImageCaption":
            number_figure_caption(doc, el, lang, counters, log)
        elif st == "SourceCode":
            fmt(para, J.LEFT, first=Mm(0), ls=1.0)
            restyle_runs(el, code=True)
        elif el.find(f"{qn('w:pPr')}/{qn('w:numPr')}") is not None:
            fmt(para, J.JUSTIFY, first=INDENT)
            restyle_runs(el)
        else:
            text = "".join(t.text or "" for t in el.iter(qn("w:t")))
            starts_where = was_after_eq and starts_with_where(text, lang)
            fmt(para, J.JUSTIFY, first=Mm(0) if starts_where else INDENT)
            restyle_runs(el)
        i += 1
    return counters


# ---------------------------------------------------------------- generated blocks

def abstract_paragraphs(value, lang: str, *, labelled: bool) -> list[list[tuple[str, bool]]]:
    """Abstract -> list of paragraphs; each paragraph is [(text, italic_label?), ...]."""
    if isinstance(value, dict):
        out = []
        for key, names in ABSTRACT_PARTS:
            txt = str(value.get(key) or "").strip()
            if not txt:
                continue
            out.append(([(f"{names[lang]}. ", True)] if labelled else []) + [(txt, False)])
        return out
    return [[(p.strip(), False)] for p in str(value).split("\n\n") if p.strip()]


def emit_abstract(doc, value, lang: str, *, labelled: bool, label_lang: str) -> list[Paragraph]:
    paras = []
    for k, chunks in enumerate(abstract_paragraphs(value, lang, labelled=labelled)):
        p = doc.add_paragraph()
        if k == 0:
            add_text(p, f"{LABELS[label_lang]['abstract']}: ", italic=True)
        for txt, is_label in chunks:
            add_text(p, txt, italic=is_label)
        fmt(p, J.JUSTIFY)
        paras.append(p)
    return paras


def emit_keywords(doc, kws: list, lang: str) -> Paragraph:
    p = doc.add_paragraph()
    add_text(p, f"{LABELS[lang]['keywords']}: ", italic=True)
    text = ", ".join(str(k).strip() for k in kws if str(k).strip())
    add_text(p, text if text.endswith(".") else text + ".")
    fmt(p, J.JUSTIFY)
    return p


def emit_heading(doc, text: str, *, page_break=False) -> Paragraph:
    try:
        p = doc.add_paragraph(style="Heading 1")  # as in the official sample (keeps the navigation pane useful)
    except KeyError:
        p = doc.add_paragraph()
    add_text(p, text, bold=True)
    fmt(p, J.CENTER, first=Mm(0), sb=6, sa=3, keep_next=True, page_break_before=page_break)
    return p


def build_front(doc, meta: dict, lang: str) -> list:
    L = LABELS[lang]
    els = []
    p = new_par(doc, f"{L['udc']} {str(meta['udc']).strip()}")
    fmt(p, J.LEFT, first=Mm(0))
    els.append(p)
    p = new_par(doc, ", ".join(author_short(a, lang) for a in meta["authors"]), bold=True)
    fmt(p, J.RIGHT, first=Mm(0), sa=6)
    els.append(p)
    p = new_par(doc, str(meta[f"title_{lang}"]).strip().upper(), bold=True, markup=False)
    fmt(p, J.CENTER, first=Mm(0), sa=6, keep_next=True)
    els.append(p)
    top = meta.get("abstract_top") or meta[f"abstract_{lang}"]
    els += emit_abstract(doc, top, lang, labelled=False, label_lang=lang)
    els.append(emit_keywords(doc, meta[f"keywords_{lang}"], lang))
    return [e._p for e in els]


def build_tail(doc, meta: dict, lang: str, counters: Counters) -> None:
    L = LABELS[lang]
    if str(meta.get("acknowledgements") or "").strip():
        emit_heading(doc, L["acknowledgements"])
        fmt(new_par(doc, str(meta["acknowledgements"]).strip()), J.JUSTIFY)
    disclosure = [str(meta.get(k) or "").strip() for k in ("funding", "conflict_of_interest")]
    if any(disclosure):
        emit_heading(doc, L["disclosure"])
        for txt in disclosure:
            if txt:
                fmt(new_par(doc, txt), J.JUSTIFY)

    emit_heading(doc, L["references"])
    for n, ref in enumerate([r for r in meta["references"] if str(r).strip()], 1):
        p = doc.add_paragraph()
        add_text(p, f"{n}. ")
        add_text(p, str(ref).strip())
        fmt(p, J.JUSTIFY)

    # End matter: "в кінці файлу окремими сторінками" -- each language block starts a new page.
    refs = len([r for r in meta["references"] if str(r).strip()])
    for lg in ("uk", "en"):
        Lg = LABELS[lg]
        p = new_par(doc, f"{Lg['udc']} {str(meta['udc']).strip()}")
        fmt(p, J.JUSTIFY, page_break_before=True)
        p = doc.add_paragraph()
        add_text(p, str(meta[f"title_{lg}"]).strip(), bold=True, markup=False)
        year = str(meta.get("year") or "20__")
        issue = str(meta.get("issue") or "№ _ (__)")
        add_text(p, f" / {', '.join(author_bib(a, lg) for a in meta['authors'])} // {Lg['journal']}. – "
                    f"{year}. – {issue}. – {Lg['pages']}", markup=False)
        fmt(p, J.JUSTIFY)
        fmt(new_par(doc, Lg["counts"].format(refs=refs, figs=counters.figures, tabs=counters.tables)), J.JUSTIFY)
        emit_abstract(doc, meta[f"abstract_{lg}"], lg, labelled=True, label_lang=lg)
        emit_keywords(doc, meta[f"keywords_{lg}"], lg)
        fmt(doc.add_paragraph(), J.JUSTIFY)

    emit_heading(doc, "Про авторів / About the authors", page_break=True)
    for label, key in (("Назва статті", "title_uk"), ("Article title", "title_en")):
        p = doc.add_paragraph()
        add_text(p, f"{label}: ", italic=True)
        add_text(p, str(meta[key]).strip(), markup=False)
        fmt(p, J.JUSTIFY, first=Mm(0))
    fmt(doc.add_paragraph(), J.JUSTIFY, first=Mm(0))
    for a in meta["authors"]:
        for lg in ("en", "uk"):
            p = doc.add_paragraph()
            add_text(p, author_full(a, lg), bold=True, markup=False)
            details = [str(a.get(f"{k}_{lg}") or "").strip() for k in ("degree", "rank", "position")]
            details = [d for d in details if d]
            if details:
                add_text(p, " – " + ", ".join(details) + ".", markup=False)
            fmt(p, J.JUSTIFY, first=Mm(0))
        lines = []
        if a.get("interests_uk"):
            lines.append(("Наукові інтереси: ", str(a["interests_uk"]).strip()))
        if a.get("interests_en"):
            lines.append(("Research interests: ", str(a["interests_en"]).strip()))
        for label, key in (("ORCID: ", "orcid"), ("ScopusID: ", "scopus_id"), ("ResearcherID: ", "researcher_id"),
                           ("E-mail: ", "email"), ("Телефон / Phone: ", "phone")):
            if str(a.get(key) or "").strip():
                lines.append((label, str(a[key]).strip()))
        for label, val in lines:
            p = doc.add_paragraph()
            add_text(p, label)
            add_text(p, val, markup=False)
            fmt(p, J.JUSTIFY, first=Mm(0))
        if a.get("corresponding"):
            fmt(new_par(doc, "Відповідальний автор / Corresponding author", italic=True), J.JUSTIFY, first=Mm(0))
        fmt(doc.add_paragraph(), J.JUSTIFY, first=Mm(0))


# ---------------------------------------------------------------- pandoc

def run_pandoc(body: str, resource_dir: Path, out: Path) -> None:
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


# ---------------------------------------------------------------- main

def build(src_path: Path, out_path: Path, verbose: bool = False) -> Counters:
    log = (lambda m: print(f"  {m}", file=sys.stderr)) if verbose else (lambda m: None)
    try:
        src = load_source(src_path)
    except SourceError as exc:
        fail([str(exc)])
    errs = required_errors(src.meta)
    if errs:
        fail(errs)
    meta, lang = src.meta, src.meta["language"]

    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "pandoc.docx"
        run_pandoc(src.body, src_path.parent.resolve(), raw)
        doc = Document(str(raw))

        setup_document(doc, lang, str(meta[f"title_{lang}"]).strip(),
                       ", ".join(author_short(a, "en") for a in meta["authors"]))
        fix_numbering(doc)
        counters = process_body(doc, lang, log)
        front = build_front(doc, meta, lang)
        body = doc.element.body
        for k, el in enumerate(front):
            body.remove(el)
            body.insert(k, el)
        build_tail(doc, meta, lang, counters)

        tmp_out = Path(td) / "out.docx"
        doc.save(str(tmp_out))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(tmp_out, out_path)
    refs = len([r for r in meta["references"] if str(r).strip()])
    print(f"built {out_path} -- language={lang}, figures={counters.figures}, tables={counters.tables}, "
          f"equations={counters.equations}, references={refs}", file=sys.stderr)
    return counters


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("source", type=Path, help="manuscript Markdown file with YAML front matter")
    ap.add_argument("--out", type=Path, help="output .docx (default: <source>.docx next to the source)")
    ap.add_argument("--verbose", action="store_true", help="log every numbered figure/table/equation")
    args = ap.parse_args(argv)
    if not args.source.is_file():
        fail([f"source file not found: {args.source}"])
    out = args.out or args.source.with_suffix(".docx")
    if out.suffix.lower() != ".docx":
        fail([f"--out must end with .docx (the journal does not accept PDF): {out}"])
    build(args.source, out, args.verbose)
    return 0


if __name__ == "__main__":
    sys.exit(main())
