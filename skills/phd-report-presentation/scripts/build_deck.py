# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = ["python-pptx>=1.0", "pillow"]
# ///
"""build_deck.py -- generate a KPI PhD semester-report .pptx from a JSON spec.

    uv run build_deck.py --spec spec.json --out deck.pptx
    python build_deck.py --spec spec.json --out deck.pptx --template assets/template.pptx

See references/spec-schema.md (in the skill root) for the full JSON schema and
references/style-guide.md for the design system this script implements.

Design note: this generator does NOT clone prototype slides from the original
reference deck. It adds a blank slide from the brand template's layout and
draws every shape (title, body, table, image, captions) at fixed, canonical
coordinates taken from the deck analysis (see the CONSTANTS section below,
each with a comment citing where the number comes from). This sidesteps the
original deck's own layout bugs (undersized title box causing 2-line-title
overlap, near-zero gaps between stacked text boxes, autofit-dependent dense
lists) -- see references/style-guide.md "Do / don't" section for the list of
defects this generator deliberately does not reproduce.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import uuid
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls, qn
from pptx.util import Cm, Emu, Pt

try:
    from PIL import Image
except ImportError:  # pragma: no cover - PEP 723 always installs pillow
    Image = None


# =====================================================================
# CONSTANTS -- canonical geometry / palette / typography.
# All positions are (left, top) and sizes (width, height) in centimetres
# unless noted. Every value below cites the section of the deck analysis
# it comes from (scratchpad/analysis/ANALYSIS.md and theme.md) so a future
# maintainer can trace *why* a number is what it is.
# =====================================================================

# ---- Canvas (ANALYSIS.md §b) -----------------------------------------
SLIDE_W_CM = 25.4          # 9,144,000 EMU
SLIDE_H_CM = 14.2875       # 5,143,500 EMU, 16:9

# ---- Layout names inside assets/template.pptx -------------------------
LAYOUT_CONTENT = "Слайд (варіант 1)"   # slideLayout2.xml -- footer/logo/title chrome
LAYOUT_BACKCOVER = "Титульний слайд"   # slideLayout1.xml -- full-bleed navy + wordmark pic

# ---- Palette (theme.md "three navies" + table tint) --------------------
# Fix (deliberate deviation from the original, per task brief): the source
# deck mixes THREE different navy hex values for headings (#1B3A6E from the
# layout, #203864 = accent1 darker 50%, #002060 hard-coded on slide 1).
# We collapse all of that to a single, consistent brand navy everywhere a
# heading/title/branded text needs navy. #1B3A6E is chosen because it is
# the one navy that is layout-owned (footer bar + default title colour),
# i.e. already "the" brand navy of the template.
NAVY = RGBColor(0x1B, 0x3A, 0x6E)
BLACK = RGBColor(0x00, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

ACCENT1 = (0x44, 0x72, 0xC4)  # theme accent1, used only to derive table tints


def _tint(rgb: tuple[int, int, int], t: float) -> RGBColor:
    """Reproduce OOXML's schemeClr tint transform: out = in*t + 255*(1-t).

    theme.md confirms accent1 tint 20% == #DAE3F3 (the original table fill);
    this helper lets us derive a second, slightly darker tint for header
    rows without hand-picking an unrelated colour (ANALYSIS.md gotcha #7 /
    task brief: "header row ... bold + slightly darker tint of the same
    accent while keeping the flat accent-tint table look").
    """
    r, g, b = rgb
    return RGBColor(
        round(r * t + 255 * (1 - t)),
        round(g * t + 255 * (1 - t)),
        round(b * t + 255 * (1 - t)),
    )


TABLE_FILL_BODY = _tint(ACCENT1, 0.20)    # #DAE3F3 -- matches the original exactly
TABLE_FILL_HEADER = _tint(ACCENT1, 0.38)  # visibly darker, same family -- fixes gotcha #7
TABLE_BORDER = WHITE                       # thin white gridlines, per theme.md

# ---- Slide-number field (master sldNum ph geometry, ANALYSIS.md §e) ----
SLDNUM_L, SLDNUM_T, SLDNUM_W, SLDNUM_H = 17.94, 13.24, 5.71, 0.76
SLDNUM_SIZE_PT = 14  # matches the per-slide lstStyle override seen on slides 3-13

# ---- Content-slide title band (fixes ANALYSIS.md gotcha #1) ------------
# Original default (layout2 ph idx=11) is 15.32 x 1.96 cm -- exactly one
# line of 24pt caps text tall, causing a provable overlap on 2-line titles
# (slides 4, 6). We widen to the deck's own "wide" variant (slide 10/11)
# and add real height headroom for 2 lines, used identically on every
# content archetype (fixes "geometry decided per-slide by trial and error").
TITLE_L, TITLE_T, TITLE_W, TITLE_H = 0.91, 0.90, 23.47, 2.60
TITLE_SIZE_PT = 24
TITLE_GAP_CM = 0.20  # min clearance enforced below every title box

# ---- Content body vertical safe zone ------------------------------------
FOOTER_BAR_TOP_CM = 12.81         # layout2's navy footer bar (ANALYSIS.md §e)
# Keep clear of the footer bar with a real safety margin: 12.55 (the
# previous value) left only ~0.26cm of clearance, which let a legitimately
# full slide (e.g. a 5-item numbered list wrapping to 2 lines each) render
# with its last line touching the footer bar with no WARN at all (QA
# finding). 12.20 restores a documented >=0.6cm gap above FOOTER_BAR_TOP_CM
# and -- since every archetype derives its usable height from this one
# constant -- also makes the overflow heuristic correctly fire a WARN
# earlier, before text gets anywhere near the footer, instead of after.
CONTENT_BOTTOM_CM = 12.20
BODY_TOP_CM = TITLE_T + TITLE_H + TITLE_GAP_CM   # 3.70
BODY_L, BODY_W = 0.91, 23.47
BODY_H_CM = CONTENT_BOTTOM_CM - BODY_TOP_CM

BODY_SIZE_PT = 20          # nominal bullets/body size (ANALYSIS.md §d.2)
BODY_LINE_SPACING_PCT = 120  # matches original numbered-list line spacing
# Fidelity fix (scratchpad/analysis/runs.txt, slides 3/8/9): every bulleted/
# numbered list item run in the original is explicitly bold (b="1") -- e.g.
# slide3.xml "Часткові наукові завдання" items are sz(inherited)=14pt b="1",
# slide8.xml "Структура дисертації" items are sz="2000" b="1". The nominal
# sizes used per-slide in the original range 14-22pt with no single
# consistent value (hand-typed per slide); 20pt is kept here since it
# already matches the "Структура дисертації" sample exactly and sits
# squarely inside that range. The bold weight, however, is a bold=1
# constant across every sampled list in the file, so render_bullets() now
# renders every item bold to match (see also CONCLUSIONS_SIZE_PT above and
# render_references() below).

CAPTION_SIZE_PT = 16
CAPTION_H_CM = 1.30
CAPTION_GAP_CM = 0.20

TABLE_CELL_SIZE_PT = 10    # theme.md "Table cell text: 10pt regular black"
TABLE_HEADER_SIZE_PT = 10

# Fidelity fix (scratchpad/analysis/runs.txt, slides 10-11): every reference
# entry run in the original carries an explicit b="1" (e.g. slide10 p0 r0:
# sz="900" b="1"; slide11's nominal 14pt is autofit-scaled to ~67.5% but
# still b="1") -- bold, not regular. Sizes are left unchanged (the original's
# own effective/autofit-scaled sizes, ~8.8-9.5pt, are already <= these
# explicit sizes, so there is no "larger" case to match here).
REFERENCES_SIZES = [(6, 12), (9, 10.5), (12, 9), (99, 8)]  # (max_items, pt)

TWO_COL_GUTTER_CM = 0.60
TWO_COL_IMAGE_H_CM = 2.60
TWO_COL_HEADING_PT = 13
TWO_COL_ITEM_PT = 12

IMAGE_TEXT_PT = 18
IMAGE_CAPTION_H_CM = 0.90

# Fidelity fix: the original's own "Висновки" (conclusions) placeholder
# (slide12.xml, idx=13) sets every item run to sz="2000" b="1" with no
# normAutofit fontScale shrink -- i.e. a real, undiminished 20pt bold, not
# the 18pt regular this generator used to render. 20pt also matches the
# "Структура дисертації" bullets slide (slide8.xml: sz="2000" b="1").
CONCLUSIONS_SIZE_PT = 20

THANKS_SIZE_PT = 28
THANKS_BOX_L, THANKS_BOX_T, THANKS_BOX_W, THANKS_BOX_H = 2.0, 5.8, 21.4, 2.4

# ---- Title-slide geometry (ANALYSIS.md §d.1, fixed per gotcha #3) -------
TS_WORDMARK_L, TS_WORDMARK_T, TS_WORDMARK_W, TS_WORDMARK_H = 4.25, 0.37, 18.11, 2.60
# Fidelity fix: the original's wordmark box ("Text Box 10" on slide1.xml) is
# a freeform (non-placeholder) textbox whose runs carry NO explicit sz --
# measured directly off the reference render (scratchpad/analysis/
# slides/slide-01.png): its glyph cap-height is ~1.3x the author/department
# block's own explicit 16pt text, i.e. ~21-22pt, clearly larger than the
# 16pt previously used here (which made the wordmark the same size as the
# department/author lines below it, when the original renders it larger,
# matching its role as the top-level institutional heading).
#
# 19pt (not the raw ~21-22pt cap-height estimate) is what's actually used:
# empirically re-rendering this exact box width (18.11cm, bold, this
# template's real Exo-2-substituted font -- see scratchpad/wordmark_test/)
# at each candidate size shows line 1 ("Національний технічний університет
# України") wraps to a SECOND physical line starting at 20pt, which the
# original does not do (its own render shows line 1 on one line, line 2
# wrapping once -- 3 total lines). 19pt is the largest size that reproduces
# that same 1+2=3-line wrap topology instead of a 2+2=4-line one, which is
# a more direct, falsifiable fidelity signal in this font-substituted
# environment than the cap-height estimate alone, and it sits well within
# that estimate's own measurement uncertainty. The box height/width and the
# department line's position below are sized for this 3-line wrap (see
# TS_DEPT_T).
TS_WORDMARK_PT = 19
# Fix (deliberate deviation, same family as the original TS_WORDMARK_H fix
# below): pushed from the original's 1.602cm and the prior fix's 2.55cm to
# clear the taller 3-line wordmark wrap at 19pt (ends ~2.75-2.8cm from the
# slide top at TS_WORDMARK_T=0.37, measured empirically -- see above) with
# a real >=0.2cm gap, while staying well clear of TS_MAIN_T (4.63cm) below.
TS_DEPT_L, TS_DEPT_T, TS_DEPT_W, TS_DEPT_H = 4.89, 3.05, 16.79, 0.94
TS_DEPT_PT = 16
TS_MAIN_L, TS_MAIN_T, TS_MAIN_W, TS_MAIN_H = 2.10, 4.63, 21.84, 3.98
TS_MAIN_PT = 22
# `meta.report_title` (task feature, not in the original deck -- the
# reference presentation never prints a semester number anywhere, see
# references/report-structure.md's own pitfall note). Rendered as a short
# heading line directly above the dissertation-topic block, same column
# (TS_MAIN_L/W) and colour as that block, sized between the department
# line (16pt regular) and the dissertation topic (22pt bold) in the
# title-slide hierarchy. It only occupies space when actually present: see
# render_title(), which leaves TS_MAIN_T completely untouched (today's
# exact layout) when `report_title` is absent/empty, and only pushes the
# dissertation-topic block down by TS_REPORT_TITLE_H + the gap when it is
# rendered -- so there is never an empty gap either way.
TS_REPORT_TITLE_PT = 16
TS_REPORT_TITLE_H = 0.70
TS_REPORT_TITLE_GAP_CM = 0.15
TS_AUTHOR_L, TS_AUTHOR_T, TS_AUTHOR_W, TS_AUTHOR_H = 15.78, 9.43, 9.10, 3.68
TS_AUTHOR_PT = 16
TS_LOGO_SHIELD_L, TS_LOGO_SHIELD_T, TS_LOGO_SHIELD_W, TS_LOGO_SHIELD_H = 0.79, 0.27, 2.61, 3.68
TS_LOGO_GOLD_L, TS_LOGO_GOLD_T, TS_LOGO_GOLD_W, TS_LOGO_GOLD_H = 21.47, 0.0, 3.93, 3.93

DEFAULT_UNIV_LINE1 = "Національний технічний університет України"
DEFAULT_UNIV_LINE2 = "«Київський політехнічний інститут імені Ігоря Сікорського»"
DEFAULT_SUPERVISOR_LABEL = "Науковий керівник:"
DEFAULT_STUDENT_LABEL_TEMPLATE = "Аспірант групи {group}"
DEFAULT_THANKS_TEXT = "Дякую за увагу!"

# Brand assets bundled with the skill, used only by the title archetype
# (the original deck's slide-1 logo pictures were per-slide, not
# layout-owned, so we ship copies and place them from code -- see
# ANALYSIS.md §d.1 and the task brief).
ASSET_LOGO_SHIELD = "logo_shield_title.png"
ASSET_LOGO_GOLD = "decor_molecule_gold.png"

SLIDE_TYPES = {
    "title", "definition", "bullets", "table", "two_column", "image",
    "references", "conclusions", "thanks", "back_cover",
}


# =====================================================================
# Spec loading / validation
# =====================================================================
class SpecError(Exception):
    """Raised for any problem with the input spec; caught in main() and
    reported as a clean, non-zero-exit error (never a raw traceback)."""


def load_spec(spec_path: Path) -> dict:
    try:
        raw = spec_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SpecError(f"cannot read spec file '{spec_path}': {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SpecError(f"spec file '{spec_path}' is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SpecError("spec file must contain a JSON object at the top level")
    return data


def _require(d: dict, key: str, where: str) -> object:
    if key not in d or d[key] in (None, ""):
        raise SpecError(f"{where}: missing required field '{key}'")
    return d[key]


def _require_str(d: dict, key: str, where: str) -> str:
    """Like _require, but also rejects non-string values (a number or
    boolean typed into a text field) with a clear, specific error instead
    of letting it reach python-pptx as a run.text assignment later, where
    the failure would be a confusing TypeError deep in rendering code."""
    val = _require(d, key, where)
    if not isinstance(val, str):
        raise SpecError(
            f"{where}: field '{key}' must be a string, got {type(val).__name__} ({val!r})"
        )
    return val


def _as_text(value: object, default: str = "") -> str:
    """Coerce an optional text field to a string for rendering: None (or an
    explicit JSON `null`) falls back to `default`; numbers/booleans are
    stringified rather than crashing python-pptx's run.text setter."""
    if value is None:
        return default
    if isinstance(value, str):
        return value
    return str(value)


SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp"}


def _resolve_image(path_str: str, spec_dir: Path, where: str) -> Path:
    if not isinstance(path_str, str) or not path_str:
        raise SpecError(f"{where}: image path must be a non-empty string, got {path_str!r}")
    p = Path(path_str)
    full = p if p.is_absolute() else (spec_dir / p)
    if p.suffix.lower() not in SUPPORTED_IMAGE_EXTS:
        raise SpecError(
            f"{where}: unsupported image extension '{p.suffix}' for '{path_str}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_IMAGE_EXTS))}"
        )
    if not full.is_file():
        raise SpecError(f"{where}: image not found: '{path_str}' (resolved to '{full}')")
    return full


# ---- Unknown-key ("typo") detection -----------------------------------
# Non-fatal: an unrecognised key is almost always a misspelled field name,
# so we WARN (stderr, exit code stays 0) rather than hard-fail, since the
# spec is otherwise valid and silently ignoring the typo'd field is the
# worse failure mode for an unattended build.
KNOWN_TOP_KEYS = {"lang", "meta", "slides"}
KNOWN_META_KEYS = {
    "university_name_line1", "university_name_line2", "department",
    "dissertation_title", "student_group", "student_name", "supervisor_name",
    "supervisor_label", "student_label_template", "report_title",
}
KNOWN_SLIDE_KEYS = {
    "title": {"type"} | KNOWN_META_KEYS,
    "definition": {"type", "object", "subject", "goal", "labels"},
    "bullets": {"type", "title", "items", "style", "font_size_pt"},
    "table": {"type", "title", "columns", "rows", "caption", "image"},
    "two_column": {"type", "title", "caption", "columns"},
    "image": {"type", "title", "text", "image", "caption"},
    "references": {"type", "title", "items", "font_size_pt"},
    "conclusions": {"type", "title", "items", "font_size_pt"},
    "thanks": {"type", "text"},
    "back_cover": {"type"},
}
KNOWN_TWO_COL_COLUMN_KEYS = {"image", "sections"}
KNOWN_TWO_COL_SECTION_KEYS = {"heading", "items"}


def _warn_unknown_keys(d: dict, known: set, where: str) -> None:
    extra = sorted(set(d.keys()) - known)
    if extra:
        print(
            f"WARN: {where}: unrecognised field(s) {', '.join(repr(k) for k in extra)} "
            f"(ignored -- check for a typo; known fields: {', '.join(sorted(known))})",
            file=sys.stderr,
        )


def _check_positive_number(d: dict, key: str, where: str) -> None:
    if key in d and d[key] is not None:
        val = d[key]
        if isinstance(val, bool) or not isinstance(val, (int, float)) or val <= 0:
            raise SpecError(f"{where}: '{key}' must be a positive number, got {val!r}")


def _check_enum(d: dict, key: str, where: str, allowed: set) -> None:
    if key in d and d[key] is not None and d[key] not in allowed:
        raise SpecError(
            f"{where}: '{key}' must be one of {sorted(allowed)}, got {d[key]!r} "
            f"(check for a typo)"
        )


def _validate_bullet_items(items: object, where: str) -> None:
    """Shared validation for `bullets.items` / `conclusions.items`: every
    item is a string, or an object with a string 'text' and an optional
    'sub' array of (at most) one more level of strings/objects. Rejects
    non-string/non-object items and nesting deeper than 2 levels with a
    precise, indexed error instead of silently dropping/mis-rendering it.
    """
    if not isinstance(items, list):
        raise SpecError(f"{where}: 'items' must be an array")
    for i, item in enumerate(items):
        iw = f"{where}.items[{i}]"
        if isinstance(item, str):
            continue
        if not isinstance(item, dict):
            raise SpecError(f"{iw}: must be a string or an object with a 'text' field, got {item!r}")
        if "text" in item and item["text"] is not None and not isinstance(item["text"], str):
            raise SpecError(f"{iw}.text: must be a string, got {item['text']!r}")
        _warn_unknown_keys(item, {"text", "sub"}, iw)
        sub = item.get("sub")
        if sub is None:
            continue
        if not isinstance(sub, list):
            raise SpecError(f"{iw}.sub: must be an array")
        for j, sub_item in enumerate(sub):
            sjw = f"{iw}.sub[{j}]"
            if isinstance(sub_item, str):
                continue
            if not isinstance(sub_item, dict):
                raise SpecError(
                    f"{sjw}: must be a string or an object with a 'text' field, got {sub_item!r}"
                )
            if "sub" in sub_item:
                raise SpecError(
                    f"{sjw}: nesting deeper than 2 levels is not supported -- "
                    f"remove this inner 'sub' (flatten it into text)"
                )
            if "text" in sub_item and sub_item["text"] is not None and not isinstance(sub_item["text"], str):
                raise SpecError(f"{sjw}.text: must be a string, got {sub_item['text']!r}")
            _warn_unknown_keys(sub_item, {"text"}, sjw)


def validate_spec(spec: dict, spec_dir: Path) -> None:
    if "slides" not in spec or not isinstance(spec["slides"], list) or not spec["slides"]:
        raise SpecError("spec must contain a non-empty top-level 'slides' array")
    meta = spec.get("meta", {})
    if not isinstance(meta, dict):
        raise SpecError("'meta' must be an object")
    _warn_unknown_keys(spec, KNOWN_TOP_KEYS, "spec")
    _warn_unknown_keys(meta, KNOWN_META_KEYS, "meta")

    for i, slide in enumerate(spec["slides"], start=1):
        where = f"slides[{i}]"
        if not isinstance(slide, dict):
            raise SpecError(f"{where}: must be an object")
        stype = slide.get("type")
        if stype not in SLIDE_TYPES:
            raise SpecError(
                f"{where}: unknown slide type '{stype}'. "
                f"Valid types: {', '.join(sorted(SLIDE_TYPES))}"
            )
        _warn_unknown_keys(slide, KNOWN_SLIDE_KEYS[stype], f"{where} ({stype})")
        if stype in ("bullets", "table", "two_column", "image", "references", "conclusions"):
            _require_str(slide, "title", where)
        if stype == "bullets":
            _require(slide, "items", where)
            if not isinstance(slide["items"], list) or not slide["items"]:
                raise SpecError(f"{where}: 'items' must be a non-empty array")
            _validate_bullet_items(slide["items"], where)
            _check_enum(slide, "style", where, {"numbered", "bulleted"})
            _check_positive_number(slide, "font_size_pt", where)
        if stype == "definition":
            for key in ("object", "subject", "goal"):
                block = _require(slide, key, where)
                if not isinstance(block, dict) or "text" not in block:
                    raise SpecError(f"{where}.{key}: must be an object with a 'text' field")
                if block["text"] is not None and not isinstance(block["text"], str):
                    raise SpecError(f"{where}.{key}.text: must be a string, got {block['text']!r}")
                _warn_unknown_keys(block, {"text"}, f"{where}.{key}")
            labels = slide.get("labels")
            if labels is not None:
                if not isinstance(labels, dict):
                    raise SpecError(f"{where}.labels: must be an object")
                _warn_unknown_keys(labels, {"object", "subject", "goal"}, f"{where}.labels")
        if stype == "table":
            cols = _require(slide, "columns", where)
            rows = _require(slide, "rows", where)
            if not isinstance(cols, list) or not cols:
                raise SpecError(f"{where}: 'columns' must be a non-empty array")
            for c_i, col_val in enumerate(cols):
                if isinstance(col_val, (dict, list)):
                    raise SpecError(f"{where}.columns[{c_i}]: must be a string, got {col_val!r}")
            if not isinstance(rows, list) or not rows:
                raise SpecError(f"{where}: 'rows' must be a non-empty array")
            for r_i, row in enumerate(rows):
                if not isinstance(row, list):
                    raise SpecError(f"{where}.rows[{r_i}]: must be an array of cells, got {row!r}")
                if len(row) != len(cols):
                    raise SpecError(
                        f"{where}.rows[{r_i}]: has {len(row)} cells, expected {len(cols)} "
                        f"(one per column)"
                    )
                for c_i, cell in enumerate(row):
                    if isinstance(cell, (dict, list)):
                        raise SpecError(
                            f"{where}.rows[{r_i}][{c_i}]: cell must be a string/number/boolean, "
                            f"got {cell!r}"
                        )
            if len(rows) > 12:
                print(
                    f"WARN: {where}: {len(rows)} rows is a lot for one table slide -- "
                    f"consider splitting it across two slides",
                    file=sys.stderr,
                )
            if slide.get("image"):
                _resolve_image(slide["image"], spec_dir, where)
        if stype == "two_column":
            cols = _require(slide, "columns", where)
            if not isinstance(cols, list) or len(cols) != 2:
                raise SpecError(f"{where}: 'columns' must be an array of exactly 2 items")
            for c_i, col in enumerate(cols):
                if not isinstance(col, dict):
                    raise SpecError(f"{where}.columns[{c_i}]: must be an object")
                _warn_unknown_keys(col, KNOWN_TWO_COL_COLUMN_KEYS, f"{where}.columns[{c_i}]")
                if "sections" not in col or not isinstance(col["sections"], list) or not col["sections"]:
                    raise SpecError(f"{where}.columns[{c_i}]: needs a non-empty 'sections' array")
                for s_i, sec in enumerate(col["sections"]):
                    secw = f"{where}.columns[{c_i}].sections[{s_i}]"
                    if not isinstance(sec, dict):
                        raise SpecError(f"{secw}: must be an object")
                    if "items" not in sec or not isinstance(sec["items"], list):
                        raise SpecError(f"{secw}: needs an 'items' array")
                    for it_i, it in enumerate(sec["items"]):
                        if not isinstance(it, str):
                            raise SpecError(f"{secw}.items[{it_i}]: must be a string, got {it!r}")
                    if "heading" in sec and sec["heading"] is not None and not isinstance(sec["heading"], str):
                        raise SpecError(f"{secw}.heading: must be a string")
                    _warn_unknown_keys(sec, KNOWN_TWO_COL_SECTION_KEYS, secw)
                if col.get("image"):
                    _resolve_image(col["image"], spec_dir, f"{where}.columns[{c_i}]")
        if stype == "image":
            img = _require(slide, "image", where)
            _resolve_image(img, spec_dir, where)
            text = slide.get("text")
            if text is not None and not isinstance(text, str):
                if isinstance(text, list):
                    for t_i, t in enumerate(text):
                        if not isinstance(t, str):
                            raise SpecError(f"{where}.text[{t_i}]: must be a string, got {t!r}")
                else:
                    raise SpecError(f"{where}.text: must be a string or array of strings")
        if stype == "references":
            items = _require(slide, "items", where)
            if not isinstance(items, list) or not items:
                raise SpecError(f"{where}: 'items' must be a non-empty array")
            for it_i, it in enumerate(items):
                if not isinstance(it, str):
                    raise SpecError(f"{where}.items[{it_i}]: must be a string, got {it!r}")
            _check_positive_number(slide, "font_size_pt", where)
        if stype == "conclusions":
            items = _require(slide, "items", where)
            if not isinstance(items, list) or not items:
                raise SpecError(f"{where}: 'items' must be a non-empty array")
            _validate_bullet_items(items, where)
            _check_positive_number(slide, "font_size_pt", where)
        if stype == "title":
            # All fields optional here -- they fall back to top-level `meta`;
            # missing values just WARN at render time (see render_title).
            pass
        if stype == "back_cover":
            pass


# =====================================================================
# Low-level OOXML helpers
# =====================================================================
def find_layout(prs: Presentation, name: str):
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            if layout.name == name:
                return layout
    raise RuntimeError(
        f"template is missing the '{name}' layout -- was assets/template.pptx "
        f"built from the right source deck?"
    )


def get_placeholder(slide, idx: int):
    for ph in slide.placeholders:
        if ph.placeholder_format.idx == idx:
            return ph
    return None


def drop_placeholder(slide, idx: int) -> None:
    """Remove an auto-cloned, unused placeholder shape so no empty box
    survives on the slide (task requirement)."""
    ph = get_placeholder(slide, idx)
    if ph is not None:
        ph._element.getparent().remove(ph._element)


def _next_shape_id(slide) -> int:
    ids = [sh.shape_id for sh in slide.shapes]
    return (max(ids) + 1) if ids else 1


def add_slide_number(slide, number: int) -> None:
    """Draw the slide-number field as a plain textbox with an <a:fld
    type="slidenum">, matching how the ORIGINAL deck actually does it on
    slides 3-13 (confirmed by inspecting ppt/slides/slide3.xml: it is a
    plain non-placeholder textbox, not a real sldNum placeholder, since
    slideLayout2.xml declares no sldNum placeholder at all). python-pptx's
    add_slide() would not give us this shape for free even if it *were* a
    placeholder, per the task brief -- so we always draw it explicitly.
    """
    guid = "{" + str(uuid.uuid4()).upper() + "}"
    shape_id = _next_shape_id(slide)
    xml = (
        f'<p:sp {nsdecls("p", "a")}>'
        f'<p:nvSpPr><p:cNvPr id="{shape_id}" name="Slide Number"/>'
        f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{Cm(SLDNUM_L)}" y="{Cm(SLDNUM_T)}"/>'
        f'<a:ext cx="{Cm(SLDNUM_W)}" cy="{Cm(SLDNUM_H)}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
        f'<p:txBody><a:bodyPr anchor="ctr" lIns="68580" tIns="34290" rIns="68580" '
        f'bIns="34290"/><a:lstStyle/>'
        f'<a:p><a:pPr algn="r"/>'
        f'<a:fld id="{guid}" type="slidenum">'
        f'<a:rPr lang="uk-UA" sz="{SLDNUM_SIZE_PT * 100}">'
        f'<a:solidFill><a:schemeClr val="bg1"/></a:solidFill></a:rPr>'
        f'<a:t>{number}</a:t></a:fld></a:p></p:txBody></p:sp>'
    )
    slide.shapes._spTree.append(parse_xml(xml))


def _set_pPr(paragraph, marL=None, indent=None, algn=None, lnSpcPct=None,
             spcBefPts=0, bullet="none") -> None:
    """Rebuild a paragraph's <a:pPr> from scratch with explicit bullet XML
    (a:buChar / a:buAutoNum / a:buNone) -- python-pptx has no high-level API
    for real OOXML bullets, so every numbered/bulleted list in this
    generator goes through here (task requirement: proper buChar/buAutoNum,
    not literal bullet characters typed into the text run).
    """
    p = paragraph._p
    old = p.find(qn("a:pPr"))
    if old is not None:
        p.remove(old)
    attrs = []
    if marL is not None:
        attrs.append(f'marL="{marL}"')
    if indent is not None:
        attrs.append(f'indent="{indent}"')
    if algn is not None:
        attrs.append(f'algn="{algn}"')
    children = ""
    if lnSpcPct is not None:
        children += f'<a:lnSpc><a:spcPct val="{lnSpcPct * 1000}"/></a:lnSpc>'
    children += f'<a:spcBef><a:spcPts val="{int(spcBefPts * 100)}"/></a:spcBef>'
    if bullet == "none":
        children += "<a:buNone/>"
    elif bullet == "auto_num":
        children += '<a:buFont typeface="+mj-lt"/><a:buAutoNum type="arabicPeriod"/>'
    elif bullet == "char":
        children += '<a:buFont typeface="Arial"/><a:buChar char="•"/>'
    xml = f'<a:pPr {nsdecls("a")} {" ".join(attrs)}>{children}</a:pPr>'
    p.insert(0, parse_xml(xml))


def _style_run(run, size_pt, color=BLACK, bold=False):
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.color.rgb = color
    # Deliberately never touch run.font.name here: leaving <a:latin> unset
    # lets the run inherit the theme's minor/major font token, which this
    # template resolves to "Exo 2" (see theme.md). This is what makes the
    # generator language/font-neutral per the task brief.


def add_textbox(slide, l, t, w, h, anchor=None, word_wrap=True):
    box = slide.shapes.add_textbox(Cm(l), Cm(t), Cm(w), Cm(h))
    tf = box.text_frame
    tf.word_wrap = word_wrap
    tf.margin_left = tf.margin_right = Cm(0)
    tf.margin_top = tf.margin_bottom = Cm(0)
    if anchor is not None:
        tf.vertical_anchor = anchor
    return box


def add_picture_fit(slide, path, l, t, w, h, halign="center", valign="top"):
    """Place an image scaled to fit inside the given box, aspect preserved,
    centered horizontally by default (task requirement)."""
    if Image is not None:
        with Image.open(path) as im:
            iw, ih = im.size
    else:  # pragma: no cover -- Pillow is a hard PEP 723 dependency
        iw, ih = 4, 3
    box_w_emu, box_h_emu = Cm(w), Cm(h)
    box_ratio = box_w_emu / box_h_emu
    img_ratio = iw / ih
    if img_ratio > box_ratio:
        new_w = box_w_emu
        new_h = int(box_w_emu / img_ratio)
    else:
        new_h = box_h_emu
        new_w = int(box_h_emu * img_ratio)
    x = Cm(l) + ((box_w_emu - new_w) // 2 if halign == "center" else 0)
    if valign == "center":
        y = Cm(t) + (box_h_emu - new_h) // 2
    elif valign == "bottom":
        y = Cm(t) + (box_h_emu - new_h)
    else:
        y = Cm(t)
    return slide.shapes.add_picture(str(path), Emu(int(x)), Emu(int(y)), Emu(int(new_w)), Emu(int(new_h)))


def _set_cell_fill_and_border(cell, fill_rgb) -> None:
    cell.fill.solid()
    cell.fill.fore_color.rgb = fill_rgb
    cell.margin_left = cell.margin_right = Cm(0.15)
    cell.margin_top = cell.margin_bottom = Cm(0.05)
    tcPr = cell._tc.get_or_add_tcPr()
    ln_xml = "".join(
        f'<a:ln{side} {nsdecls("a")} w="12700">'
        f'<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:ln{side}>'
        for side in ("L", "R", "T", "B")
    )
    frag = parse_xml(f'<a:tcPr {nsdecls("a")}>{ln_xml}</a:tcPr>')
    for i, child in enumerate(list(frag)):
        tcPr.insert(i, child)


# =====================================================================
# Overflow heuristic (task requirement: WARN, never silently shrink)
# =====================================================================
CM_TO_PT = 28.346
# Bold glyphs run measurably wider per character than regular weight at the
# same nominal size (ANALYSIS.md fidelity fix: bullets/conclusions/
# references are now rendered bold -- see CONCLUSIONS_SIZE_PT /
# render_bullets() / render_references()). Without a wider per-char
# estimate here, the line-wrap estimate silently under-counts how many
# lines bold text actually wraps to, which would let a dense bold list pass
# the overflow heuristic with no WARN.
#
# AVG_CHAR_W_FACTOR_BOLD is calibrated empirically, not guessed: a test
# deck of numbered-list items at controlled exact character counts (20pt
# bold, the real marL=342900/indent=-342900 hanging-indent paragraph
# formatting render_bullets()/render_references() actually use) was built
# with this generator and rasterized, then its real per-line text spans
# were read back with PyMuPDF (scratchpad/calib/). Result: a 50-character
# item still fit on one line; a 53-character item wrapped to two -- i.e.
# this exact box (23.47cm wide, minus the hanging indent's effective width
# loss) fits ~50-52 chars/line at 20pt bold, not the ~64 chars/line the old
# single blanket 0.52 factor implied. 0.66 reproduces ~50 chars/line
# (665.4pt box / (20pt * 0.66) ~= 50.4), which is conservative (flags a
# borderline item as wrapping slightly before the measured real boundary,
# never after).
AVG_CHAR_W_FACTOR = 0.52
AVG_CHAR_W_FACTOR_BOLD = 0.66


def _estimate_lines(text: str, font_pt: float, box_w_cm: float, bold: bool = False) -> int:
    box_w_pt = box_w_cm * CM_TO_PT
    factor = AVG_CHAR_W_FACTOR_BOLD if bold else AVG_CHAR_W_FACTOR
    avg_char_w_pt = font_pt * factor  # heuristic average glyph width for a sans font
    chars_per_line = max(1, box_w_pt / avg_char_w_pt)
    return max(1, math.ceil(len(text) / chars_per_line))


def check_overflow(slide_idx, label, texts, font_pt, box_w_cm, box_h_cm,
                    line_spacing_pct=100, extra_lines=0, extra_height_pt=0.0,
                    bold: bool = False) -> None:
    """`extra_height_pt` accounts for inter-paragraph gaps (`spcBef`) that are
    real vertical space in the rendered slide but are not part of any single
    paragraph's wrapped-line count -- omitting it previously let a dense,
    multi-item list (e.g. 5 numbered items, each with its own `spcBef`
    before it) pass the heuristic with no WARN while its last line actually
    rendered on top of the footer bar (QA finding: box height alone does not
    clip/move already-laid-out text, so the heuristic must model the real
    text height, not just assume the box's declared height matters).

    `bold` selects the wider bold-glyph character-width estimate (see
    AVG_CHAR_W_FACTOR_BOLD above) -- pass it whenever the caller renders
    these runs bold."""
    total_lines = extra_lines + sum(_estimate_lines(t, font_pt, box_w_cm, bold=bold) for t in texts)
    line_h_pt = font_pt * (line_spacing_pct / 100.0) * 1.24  # + paragraph leading, w/ safety margin
    max_lines = (box_h_cm * CM_TO_PT - extra_height_pt) / line_h_pt
    if total_lines > max_lines:
        print(
            f"WARN: slide {slide_idx} ({label}): estimated ~{total_lines} lines of text at "
            f"{font_pt}pt do not fit in the {box_h_cm:.2f}cm-tall box (~{max_lines:.1f} lines fit). "
            f"Suggestion: shorten the text, raise fewer items, or split this into two slides.",
            file=sys.stderr,
        )


# =====================================================================
# Archetype renderers
# =====================================================================
def _slide_label(spec_slide: dict) -> str:
    return spec_slide.get("title") or spec_slide.get("type", "?")


def render_title(prs, layout, spec: dict, slide_spec: dict, assets_dir: Path, idx: int):
    slide = prs.slides.add_slide(layout)
    for pidx in (11, 12, 13):
        drop_placeholder(slide, pidx)
    meta = spec.get("meta", {})

    def field(key, default=""):
        # An explicit JSON `null` on the slide (or in meta) falls back the
        # same way an absent key would -- treating "present but null" as a
        # hard override to an empty string would silently blank out a
        # field the author almost certainly meant to leave unset.
        val = slide_spec.get(key)
        if val is None:
            val = meta.get(key)
        if val is None:
            val = default
        return _as_text(val, default)

    # Logos (brand assets bundled with the skill -- ANALYSIS.md §d.1).
    shield_path = assets_dir / ASSET_LOGO_SHIELD
    gold_path = assets_dir / ASSET_LOGO_GOLD
    if shield_path.is_file():
        slide.shapes.add_picture(
            str(shield_path), Cm(TS_LOGO_SHIELD_L), Cm(TS_LOGO_SHIELD_T),
            Cm(TS_LOGO_SHIELD_W), Cm(TS_LOGO_SHIELD_H),
        )
    if gold_path.is_file():
        slide.shapes.add_picture(
            str(gold_path), Cm(TS_LOGO_GOLD_L), Cm(TS_LOGO_GOLD_T),
            Cm(TS_LOGO_GOLD_W), Cm(TS_LOGO_GOLD_H),
        )

    # University wordmark (2 lines, centered, fixed height so it never
    # overlaps the department line below it -- fixes ANALYSIS.md gotcha #3).
    box = add_textbox(slide, TS_WORDMARK_L, TS_WORDMARK_T, TS_WORDMARK_W, TS_WORDMARK_H)
    line1 = field("university_name_line1", DEFAULT_UNIV_LINE1)
    line2 = field("university_name_line2", DEFAULT_UNIV_LINE2)
    for i, line in enumerate((line1, line2)):
        p = box.text_frame.paragraphs[0] if i == 0 else box.text_frame.add_paragraph()
        _set_pPr(p, algn="ctr", spcBefPts=0)
        r = p.add_run()
        r.text = line
        _style_run(r, TS_WORDMARK_PT, color=NAVY, bold=True)

    # Department line.
    dept_box = add_textbox(slide, TS_DEPT_L, TS_DEPT_T, TS_DEPT_W, TS_DEPT_H)
    p = dept_box.text_frame.paragraphs[0]
    _set_pPr(p, algn="l", spcBefPts=0)
    r = p.add_run()
    dept_text = field("department", "Кафедра ...")
    r.text = dept_text
    _style_run(r, TS_DEPT_PT, color=NAVY, bold=False)

    # Report-title line (e.g. "Звіт ... за 4 семестр") -- optional, renders
    # directly above the dissertation-topic block only when present, and
    # otherwise leaves TS_MAIN_T completely untouched (no reserved empty
    # gap -- task requirement).
    report_title_text = field("report_title", "")
    main_top = TS_MAIN_T
    if report_title_text:
        # The report-title line takes over the slot the dissertation-topic
        # block used to start at (TS_MAIN_T); the topic block itself is
        # pushed down below it by its height + the gap.
        main_top = TS_MAIN_T + TS_REPORT_TITLE_H + TS_REPORT_TITLE_GAP_CM
        rt_box = add_textbox(slide, TS_MAIN_L, TS_MAIN_T, TS_MAIN_W, TS_REPORT_TITLE_H)
        p = rt_box.text_frame.paragraphs[0]
        _set_pPr(p, algn="ctr", spcBefPts=0)
        r = p.add_run()
        r.text = report_title_text
        _style_run(r, TS_REPORT_TITLE_PT, color=NAVY, bold=True)
        check_overflow(idx, "title/report-title", [report_title_text], TS_REPORT_TITLE_PT,
                        TS_MAIN_W, TS_REPORT_TITLE_H, bold=True)

    # Main dissertation-title statement.
    main_box = add_textbox(slide, TS_MAIN_L, main_top, TS_MAIN_W, TS_MAIN_H, anchor=MSO_ANCHOR.TOP)
    p = main_box.text_frame.paragraphs[0]
    _set_pPr(p, algn="ctr", spcBefPts=0)
    r = p.add_run()
    title_text = field("dissertation_title", "")
    r.text = title_text
    _style_run(r, TS_MAIN_PT, color=NAVY, bold=True)
    check_overflow(idx, "title/main-statement", [title_text], TS_MAIN_PT, TS_MAIN_W, TS_MAIN_H)

    # Author / supervisor block.
    author_box = add_textbox(slide, TS_AUTHOR_L, TS_AUTHOR_T, TS_AUTHOR_W, TS_AUTHOR_H)
    group = field("student_group", "")
    student_label_tpl = field("student_label_template", DEFAULT_STUDENT_LABEL_TEMPLATE)
    supervisor_label = field("supervisor_label", DEFAULT_SUPERVISOR_LABEL)
    student_name = field("student_name", "")
    supervisor_name = field("supervisor_name", "")
    try:
        student_line = student_label_tpl.format(group=group)
    except (KeyError, IndexError, ValueError):
        # A hand-edited `student_label_template` with a bad/unknown {placeholder}
        # would otherwise crash str.format(); fall back to the literal template
        # text and WARN instead of raising, since this is cosmetic, not fatal.
        print(
            f"WARN: slide {idx} (title): 'student_label_template' {student_label_tpl!r} is not "
            f"a valid template for {{group}} -- using it literally",
            file=sys.stderr,
        )
        student_line = student_label_tpl
    lines = [student_line, student_name, supervisor_label, supervisor_name]
    for i, line in enumerate(lines):
        p = author_box.text_frame.paragraphs[0] if i == 0 else author_box.text_frame.add_paragraph()
        _set_pPr(p, algn="l", spcBefPts=0)
        r = p.add_run()
        r.text = line
        _style_run(r, TS_AUTHOR_PT, color=NAVY, bold=False)

    missing = [
        name for name, val in (
            ("dissertation_title", title_text), ("department", dept_text),
            ("student_name", student_name), ("supervisor_name", supervisor_name),
        ) if not val
    ]
    if missing:
        print(
            f"WARN: slide {idx} (title): missing meta/slide field(s) {', '.join(missing)} -- "
            f"rendering blank placeholder text instead of failing",
            file=sys.stderr,
        )
    return slide


def render_back_cover(prs, layout, spec: dict):
    # Fully layout-owned: slideLayout1.xml already carries the navy
    # background and the centered wordmark picture (confirmed by the
    # original deck's slide14.xml having ZERO shapes of its own). We add
    # nothing at all -- this is the one archetype where "add slide, stop"
    # is correct and faithful.
    return prs.slides.add_slide(layout)


def _setup_title_shape(slide, title_text: str):
    ph = get_placeholder(slide, 11)
    ph.left, ph.top, ph.width, ph.height = Cm(TITLE_L), Cm(TITLE_T), Cm(TITLE_W), Cm(TITLE_H)
    tf = ph.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    for r in list(p.runs):
        r.text = ""
    if not p.runs:
        r = p.add_run()
    else:
        r = p.runs[0]
    r.text = title_text
    # Colour/size/weight/caps come from the layout's own lstStyle for ph
    # idx=11 (24pt bold, cap="all", NAVY) -- left untouched on purpose so
    # the single canonical navy stays centrally controlled in one place.
    return ph


def render_definition(prs, layout, slide_spec: dict, idx: int):
    slide = prs.slides.add_slide(layout)
    for pidx in (11, 12, 13):
        drop_placeholder(slide, pidx)

    labels = slide_spec.get("labels") or {}
    blocks = [
        (_as_text(labels.get("object"), "Об'єкт дослідження:"), _as_text(slide_spec["object"]["text"])),
        (_as_text(labels.get("subject"), "Предмет дослідження:"), _as_text(slide_spec["subject"]["text"])),
        (_as_text(labels.get("goal"), "Мета дослідження:"), _as_text(slide_spec["goal"]["text"])),
    ]
    # 3 header+body pairs, fixed generous gaps (fixes ANALYSIS.md gotcha #2:
    # original stacks these with ~0 gap via stale spAutoFit heights).
    top = 0.60
    header_h = 1.00
    body_h = 2.05
    gap = 0.45
    texts_for_overflow = []
    for header_text, body_text in blocks:
        hbox = add_textbox(slide, 0.60, top, 24.20, header_h)
        p = hbox.text_frame.paragraphs[0]
        _set_pPr(p, algn="l", spcBefPts=0)
        r = p.add_run()
        r.text = header_text
        _style_run(r, TITLE_SIZE_PT, color=NAVY, bold=True)

        top += header_h
        bbox = add_textbox(slide, 0.60, top, 24.20, body_h)
        p = bbox.text_frame.paragraphs[0]
        _set_pPr(p, algn="l", spcBefPts=0)
        r = p.add_run()
        r.text = body_text
        _style_run(r, BODY_SIZE_PT, color=BLACK, bold=False)
        # Keep the block's own header text (e.g. "Об'єкт дослідження:") so a
        # WARN below can name exactly which of the three blocks overflows,
        # instead of a single generic "definition block" label that left the
        # reader to guess which one of the three was actually the problem.
        texts_for_overflow.append((header_text, body_text, body_h))

        top += body_h + gap

    for header_text, body_text, body_h in texts_for_overflow:
        check_overflow(idx, f"definition / {header_text}", [body_text], BODY_SIZE_PT, 24.20, body_h)
    return slide


def render_bullets(prs, layout, slide_spec: dict, idx: int, *, algn="l",
                    default_size_pt=BODY_SIZE_PT, numbered_default=True):
    """Render the 'bullets' (and, via a thin wrapper, 'conclusions') archetype.

    Items are either a plain string (a normal list item at the top level) or
    an object {"text": ..., "sub": [...]} for up to 2 nesting levels (task
    requirement). The dict's own "text" is drawn as a bold, un-bulleted
    section header, and each of its "sub" entries starts its OWN indented
    numbered/bulleted run beginning at 1.

    Why a header, not a numbered top-level item, for the "sub" case: OOXML
    buAutoNum numbering is a renderer-computed *run* of consecutive
    same-level paragraphs -- interrupting a numbered run with a
    differently-indented paragraph and then resuming it causes at least
    LibreOffice to restart the count at 1 instead of continuing (verified
    empirically while building this generator). Treating a "sub"-bearing
    item as a header sidesteps that inconsistency entirely instead of
    producing a deck that silently mis-numbers itself in one renderer.
    """
    slide = prs.slides.add_slide(layout)
    drop_placeholder(slide, 12)
    _setup_title_shape(slide, slide_spec["title"])

    body_ph = get_placeholder(slide, 13)
    body_ph.left, body_ph.top = Cm(BODY_L), Cm(BODY_TOP_CM)
    body_ph.width, body_ph.height = Cm(BODY_W), Cm(BODY_H_CM)
    tf = body_ph.text_frame
    tf.word_wrap = True

    style = slide_spec.get("style", "numbered" if numbered_default else "bulleted")
    bullet_kind = "auto_num" if style == "numbered" else "char"
    size_pt = slide_spec.get("font_size_pt", default_size_pt)
    items = slide_spec["items"]

    all_texts: list[str] = []
    total_spcbef_pts = 0.0
    first = True

    def _next_para():
        nonlocal first
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        return p

    for item in items:
        if isinstance(item, str):
            p = _next_para()
            _set_pPr(p, marL=342900, indent=-342900, algn=algn,
                     lnSpcPct=BODY_LINE_SPACING_PCT, spcBefPts=6, bullet=bullet_kind)
            r = p.add_run()
            r.text = item
            # Fidelity fix: the original's own list items are bold (b="1")
            # in every sampled bullets/conclusions slide -- see
            # BODY_SIZE_PT's comment above for the citations.
            _style_run(r, size_pt, color=BLACK, bold=True)
            all_texts.append(item)
            total_spcbef_pts += 6
        elif isinstance(item, dict):
            header_text = _as_text(item.get("text"))
            p = _next_para()
            _set_pPr(p, algn=algn, spcBefPts=10, bullet="none")
            r = p.add_run()
            r.text = header_text
            _style_run(r, size_pt, color=BLACK, bold=True)
            all_texts.append(header_text)
            total_spcbef_pts += 10
            for sub in item.get("sub") or []:
                sub_text = _as_text(sub) if isinstance(sub, str) else _as_text(sub.get("text"))
                p = tf.add_paragraph()
                _set_pPr(p, marL=685800, indent=-342900, algn=algn,
                          lnSpcPct=BODY_LINE_SPACING_PCT, spcBefPts=4, bullet=bullet_kind)
                r = p.add_run()
                r.text = sub_text
                _style_run(r, size_pt, color=BLACK, bold=True)
                all_texts.append(sub_text)
                total_spcbef_pts += 4
        else:
            raise SpecError(f"bullet item must be a string or object, got: {item!r}")

    # extra_height_pt: the inter-paragraph `spcBef` gaps above are real
    # vertical space the laid-out text consumes but which _estimate_lines()
    # (a pure char-count-per-wrapped-line estimate) never sees -- without
    # this, a list of several short-but-separate items can under-count the
    # true text height enough to miss a real footer-bar collision (see
    # check_overflow's docstring / QA finding).
    check_overflow(
        idx, slide_spec["title"], all_texts, size_pt, BODY_W, BODY_H_CM,
        line_spacing_pct=BODY_LINE_SPACING_PCT, extra_height_pt=total_spcbef_pts,
        bold=True,
    )
    return slide


def render_conclusions(prs, layout, slide_spec: dict, idx: int):
    # Same mechanics as `bullets`, but left-aligned (fixes ANALYSIS.md
    # gotcha: original slide 12 uses algn="just", which visibly stretches
    # word-gaps on short lines) and a slightly larger nominal size.
    return render_bullets(
        prs, layout, slide_spec, idx, algn="l",
        default_size_pt=slide_spec.get("font_size_pt", CONCLUSIONS_SIZE_PT),
        numbered_default=True,
    )


def render_references(prs, layout, slide_spec: dict, idx: int):
    slide = prs.slides.add_slide(layout)
    drop_placeholder(slide, 12)
    _setup_title_shape(slide, slide_spec["title"])

    body_ph = get_placeholder(slide, 13)
    body_ph.left, body_ph.top = Cm(BODY_L), Cm(BODY_TOP_CM)
    body_ph.width, body_ph.height = Cm(BODY_W), Cm(BODY_H_CM)
    tf = body_ph.text_frame
    tf.word_wrap = True

    items = slide_spec["items"]
    size_pt = slide_spec.get("font_size_pt")
    if size_pt is None:
        # Explicit small font by expected item count instead of trusting
        # PowerPoint's normAutofit (ANALYSIS.md gotcha #8).
        for max_items, pt in REFERENCES_SIZES:
            if len(items) <= max_items:
                size_pt = pt
                break

    for i, text in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        _set_pPr(p, marL=342900, indent=-342900, algn="l",
                 lnSpcPct=115, spcBefPts=4, bullet="auto_num")
        r = p.add_run()
        r.text = text
        # Fidelity fix: both sampled references slides in the original
        # (publications and conferences) carry an explicit b="1" on every
        # entry run (scratchpad/analysis/runs.txt, slides 10-11) -- bold,
        # not regular.
        _style_run(r, size_pt, color=BLACK, bold=True)

    check_overflow(idx, slide_spec["title"], items, size_pt, BODY_W, BODY_H_CM,
                   line_spacing_pct=115, extra_height_pt=4.0 * len(items), bold=True)
    return slide


def render_table(prs, layout, slide_spec: dict, spec_dir: Path, idx: int):
    slide = prs.slides.add_slide(layout)
    drop_placeholder(slide, 12)
    drop_placeholder(slide, 13)
    _setup_title_shape(slide, slide_spec["title"])

    content_top = BODY_TOP_CM
    caption = _as_text(slide_spec.get("caption"))
    if caption:
        cap_box = add_textbox(slide, BODY_L, content_top, BODY_W, CAPTION_H_CM)
        p = cap_box.text_frame.paragraphs[0]
        _set_pPr(p, algn="l", spcBefPts=0)
        r = p.add_run()
        r.text = caption
        _style_run(r, CAPTION_SIZE_PT, color=BLACK, bold=True)
        content_top += CAPTION_H_CM + CAPTION_GAP_CM

    content_h = CONTENT_BOTTOM_CM - content_top
    image_rel = slide_spec.get("image")
    if image_rel:
        img_w = 10.6
        table_l = BODY_L + img_w + 0.5
        table_w = BODY_W - img_w - 0.5
        img_path = _resolve_image(image_rel, spec_dir, "table.image")
        add_picture_fit(slide, img_path, BODY_L, content_top, img_w, content_h, valign="center")
    else:
        table_l = BODY_L
        table_w = BODY_W

    columns = slide_spec["columns"]
    rows = slide_spec["rows"]
    n_rows = len(rows) + 1
    n_cols = len(columns)
    # 0.75cm is the documented row-height floor: never shrink rows tighter
    # than that just to force-fit the available area (bug fix -- a previous
    # version re-divided content_h/n_rows whenever the floor-based height
    # didn't fit, which silently produced rows *below* the documented
    # minimum for >=11 data rows, with no WARN since the post-shrink height
    # was made to exactly equal content_h). Instead, keep the floor and let
    # the table legitimately overflow the nominal content area -- the WARN
    # below (using the un-shrunk table_h_cm) always fires when that happens.
    row_h_cm = max(0.75, min(1.1, content_h / n_rows))
    table_h_cm = row_h_cm * n_rows

    gframe = slide.shapes.add_table(
        n_rows, n_cols, Cm(table_l), Cm(content_top), Cm(table_w), Cm(table_h_cm)
    )
    tbl = gframe.table
    tbl.first_row = False
    tbl.horz_banding = False
    col_w = int(Cm(table_w) / n_cols)
    for c in range(n_cols):
        tbl.columns[c].width = Emu(col_w)
    for r in range(n_rows):
        tbl.rows[r].height = Emu(int(Cm(row_h_cm)))

    for c, header_text in enumerate(columns):
        cell = tbl.cell(0, c)
        _set_cell_fill_and_border(cell, TABLE_FILL_HEADER)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        _set_pPr(p, algn="ctr", spcBefPts=0)
        r_ = p.add_run()
        r_.text = _as_text(header_text)
        _style_run(r_, TABLE_HEADER_SIZE_PT, color=NAVY, bold=True)

    for r_i, row in enumerate(rows, start=1):
        for c_i, value in enumerate(row):
            cell = tbl.cell(r_i, c_i)
            _set_cell_fill_and_border(cell, TABLE_FILL_BODY)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            _set_pPr(p, algn="ctr", spcBefPts=0)
            r_ = p.add_run()
            r_.text = _as_text(value)
            _style_run(r_, TABLE_CELL_SIZE_PT, color=BLACK, bold=False)

    if table_h_cm >= content_h + 0.05:
        print(
            f"WARN: slide {idx} ({slide_spec['title']}): table with {len(rows)} rows is tight "
            f"against the available {content_h:.2f}cm -- consider fewer rows or a references-"
            f"style split.",
            file=sys.stderr,
        )
    return slide


def render_two_column(prs, layout, slide_spec: dict, spec_dir: Path, idx: int):
    slide = prs.slides.add_slide(layout)
    drop_placeholder(slide, 12)
    drop_placeholder(slide, 13)
    _setup_title_shape(slide, slide_spec["title"])

    content_top = BODY_TOP_CM
    caption = _as_text(slide_spec.get("caption"))
    if caption:
        cap_box = add_textbox(slide, BODY_L, content_top, BODY_W, CAPTION_H_CM)
        p = cap_box.text_frame.paragraphs[0]
        _set_pPr(p, algn="ctr", spcBefPts=0)
        r = p.add_run()
        r.text = caption
        _style_run(r, CAPTION_SIZE_PT, color=BLACK, bold=True)
        content_top += CAPTION_H_CM + CAPTION_GAP_CM

    col_w = (BODY_W - TWO_COL_GUTTER_CM) / 2
    col_lefts = [BODY_L, BODY_L + col_w + TWO_COL_GUTTER_CM]
    content_h = CONTENT_BOTTOM_CM - content_top

    for col_l, col in zip(col_lefts, slide_spec["columns"]):
        col_top = content_top
        image_rel = col.get("image")
        if image_rel:
            img_path = _resolve_image(image_rel, spec_dir, "two_column.columns[].image")
            add_picture_fit(slide, img_path, col_l, col_top, col_w, TWO_COL_IMAGE_H_CM, valign="top")
            col_top += TWO_COL_IMAGE_H_CM + 0.25

        remaining_h = CONTENT_BOTTOM_CM - col_top
        n_sections = len(col["sections"])
        sec_texts = []
        box = add_textbox(slide, col_l, col_top, col_w, remaining_h)
        tf = box.text_frame
        tf.word_wrap = True
        first = True
        for sec in col["sections"]:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            _set_pPr(p, algn="l", spcBefPts=(0 if p is tf.paragraphs[0] else 10))
            r = p.add_run()
            r.text = _as_text(sec.get("heading"))
            _style_run(r, TWO_COL_HEADING_PT, color=BLACK, bold=True)
            for item_text in sec["items"]:
                item_text = _as_text(item_text)
                p = tf.add_paragraph()
                _set_pPr(p, marL=228600, indent=-228600, algn="l", spcBefPts=2, bullet="char")
                r = p.add_run()
                r.text = item_text
                _style_run(r, TWO_COL_ITEM_PT, color=BLACK, bold=False)
                sec_texts.append(item_text)

        check_overflow(idx, slide_spec["title"] + " (column)", sec_texts, TWO_COL_ITEM_PT,
                        col_w, remaining_h, extra_lines=n_sections)
    return slide


def render_image(prs, layout, slide_spec: dict, spec_dir: Path, idx: int):
    slide = prs.slides.add_slide(layout)
    drop_placeholder(slide, 12)
    drop_placeholder(slide, 13)
    _setup_title_shape(slide, slide_spec["title"])

    top = BODY_TOP_CM
    text = slide_spec.get("text")
    if text:
        text_lines = [_as_text(t) for t in text] if isinstance(text, list) else [_as_text(text)]
        wrapped_lines = sum(_estimate_lines(t, IMAGE_TEXT_PT, BODY_W, bold=True) for t in text_lines)
        line_h_cm = IMAGE_TEXT_PT * 1.22 / CM_TO_PT
        text_h = min(4.2, wrapped_lines * line_h_cm + 0.15)
        tbox = add_textbox(slide, BODY_L, top, BODY_W, text_h)
        tf = tbox.text_frame
        tf.word_wrap = True
        for i, line in enumerate(text_lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            _set_pPr(p, algn="l", spcBefPts=4)
            r = p.add_run()
            r.text = line
            _style_run(r, IMAGE_TEXT_PT, color=BLACK, bold=True)
        top += text_h + 0.25
        check_overflow(idx, slide_spec["title"] + " (intro text)", text_lines, IMAGE_TEXT_PT, BODY_W, text_h,
                        bold=True)

    caption = _as_text(slide_spec.get("caption"))
    bottom = CONTENT_BOTTOM_CM - (IMAGE_CAPTION_H_CM + 0.15 if caption else 0)
    img_h = bottom - top
    img_path = _resolve_image(slide_spec["image"], spec_dir, "image.image")
    add_picture_fit(slide, img_path, BODY_L, top, BODY_W, img_h, valign="top")

    if caption:
        cbox = add_textbox(slide, BODY_L, bottom + 0.15, BODY_W, IMAGE_CAPTION_H_CM)
        p = cbox.text_frame.paragraphs[0]
        _set_pPr(p, algn="ctr", spcBefPts=0)
        r = p.add_run()
        r.text = caption
        _style_run(r, 12, color=BLACK, bold=False)
    return slide


def render_thanks(prs, layout, slide_spec: dict):
    slide = prs.slides.add_slide(layout)
    for pidx in (12, 13):
        drop_placeholder(slide, pidx)
    ph = get_placeholder(slide, 11)
    ph.left, ph.top = Cm(THANKS_BOX_L), Cm(THANKS_BOX_T)
    ph.width, ph.height = Cm(THANKS_BOX_W), Cm(THANKS_BOX_H)
    tf = ph.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    for r in list(p.runs):
        r.text = ""
    p_align = p._p.find(qn("a:pPr"))
    if p_align is None:
        p_align = parse_xml(f'<a:pPr {nsdecls("a")} algn="ctr"/>')
        p._p.insert(0, p_align)
    else:
        p_align.set("algn", "ctr")
    r = p.add_run() if not p.runs else p.runs[0]
    r.text = _as_text(slide_spec.get("text"), DEFAULT_THANKS_TEXT)
    r.font.size = Pt(THANKS_SIZE_PT)
    return slide


# =====================================================================
# Main dispatch
# =====================================================================
def build_deck(spec: dict, spec_dir: Path, template_path: Path, out_path: Path,
                assets_dir: Path, verbose: bool = False) -> int:
    prs = Presentation(str(template_path))
    layout_content = find_layout(prs, LAYOUT_CONTENT)
    layout_backcover = find_layout(prs, LAYOUT_BACKCOVER)

    for i, slide_spec in enumerate(spec["slides"], start=1):
        # `i` is also the slide's true 1-based physical position in the
        # output deck (we add exactly one slide per spec entry, in order),
        # which is what the <a:fld type="slidenum"> cached text should show
        # -- real viewers recompute the field from actual position anyway,
        # but the cached text should still be correct for viewers that don't.
        stype = slide_spec["type"]
        if stype == "title":
            slide = render_title(prs, layout_content, spec, slide_spec, assets_dir, i)
        elif stype == "back_cover":
            slide = render_back_cover(prs, layout_backcover, spec)
        else:
            if stype == "definition":
                slide = render_definition(prs, layout_content, slide_spec, i)
            elif stype == "bullets":
                slide = render_bullets(prs, layout_content, slide_spec, i)
            elif stype == "conclusions":
                slide = render_conclusions(prs, layout_content, slide_spec, i)
            elif stype == "references":
                slide = render_references(prs, layout_content, slide_spec, i)
            elif stype == "table":
                slide = render_table(prs, layout_content, slide_spec, spec_dir, i)
            elif stype == "two_column":
                slide = render_two_column(prs, layout_content, slide_spec, spec_dir, i)
            elif stype == "image":
                slide = render_image(prs, layout_content, slide_spec, spec_dir, i)
            elif stype == "thanks":
                slide = render_thanks(prs, layout_content, slide_spec)
            else:  # pragma: no cover -- validated earlier
                raise SpecError(f"unhandled slide type: {stype}")
            add_slide_number(slide, i)

        if verbose:
            print(f"[{i}/{len(spec['slides'])}] {stype}: {_slide_label(slide_spec)!r}", file=sys.stderr)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out_path))
    return len(spec["slides"])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True, type=Path, help="path to the JSON spec file")
    ap.add_argument("--out", required=True, type=Path, help="path to write the generated .pptx")
    ap.add_argument("--template", type=Path, default=None,
                     help="override path to template.pptx (default: assets/template.pptx next to this script)")
    ap.add_argument("--assets-dir", type=Path, default=None,
                     help="override path to the skill's assets/ dir (brand logos, default: sibling of scripts/)")
    ap.add_argument("--verbose", action="store_true", help="print a per-slide summary to stderr")
    args = ap.parse_args()

    default_assets_dir = Path(__file__).resolve().parent.parent / "assets"
    assets_dir = args.assets_dir.resolve() if args.assets_dir else default_assets_dir
    template_path = args.template.resolve() if args.template else assets_dir / "template.pptx"

    if not args.spec.is_file():
        print(f"error: spec file not found: {args.spec}", file=sys.stderr)
        raise SystemExit(2)
    if not template_path.is_file():
        print(f"error: template not found: {template_path} (pass --template)", file=sys.stderr)
        raise SystemExit(2)

    try:
        spec = load_spec(args.spec)
        spec_dir = args.spec.resolve().parent
        validate_spec(spec, spec_dir)
        n = build_deck(spec, spec_dir, template_path, args.out.resolve(), assets_dir, verbose=args.verbose)
    except SpecError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except RuntimeError as exc:
        # e.g. find_layout() when --template points at a deck that isn't
        # built from the expected brand template -- a user/input error, not
        # a bug, so it gets the same clean one-line treatment as SpecError.
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:
        # Anything else is unexpected (a real bug, not a bad spec). Never
        # swallow the traceback silently -- without --verbose, keep the
        # one-line contract this tool promises everywhere else; with
        # --verbose, let it propagate so the real traceback is visible.
        if args.verbose:
            raise
        print(f"error: unexpected failure ({type(exc).__name__}): {exc}", file=sys.stderr)
        raise SystemExit(1)

    print(f"wrote {args.out.resolve()} ({n} slides)")


if __name__ == "__main__":
    main()
