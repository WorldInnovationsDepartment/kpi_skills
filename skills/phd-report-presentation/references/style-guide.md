# Style guide -- KPI PhD semester-report deck (as implemented)

This is the canonical design system `scripts/build_deck.py` implements. It
is derived from a full OOXML/visual analysis of a real KPI department
report deck (see the task's analysis inputs), but it deliberately **fixes**
a handful of defects found in that original rather than reproducing them.
Every geometry number below matches a named constant at the top of
`build_deck.py`, with a comment citing where it comes from -- treat this
document and that CONSTANTS section as the same source of truth kept in
sync.

## Canvas

- 25.40 x 14.29 cm (9,144,000 x 5,143,500 EMU), 16:9, `screen16x9`.

## Palette

| Role | Hex | Notes |
|---|---|---|
| Brand navy (**the only navy used**) | `#1B3A6E` | Headers, titles, definition-block headers, title-slide text, footer bar. |
| Body text | `#000000` | All paragraph/body copy. |
| Reversed text | `#FFFFFF` | Footer strip, back-cover, slide-number field, table header text is navy-on-tint (see Tables). |
| Table body fill | `#DAE3F3` | = theme accent1 (`#4472C4`) tinted 20% -- reproduces the original exactly. |
| Table header fill | derived, ≈`#B8C9E9` | Same accent1 family, tinted ~38% (darker) -- computed in code via a `tint()` helper, not hand-picked. |
| Table gridlines | `#FFFFFF`, 1pt | Thin white lines between cells. |

**Fix vs. the original:** the source deck mixes THREE different "navy"
hex values for headings (`#1B3A6E` from the layout, `#203864` = accent1
darker 50% on hand-drawn headers, `#002060` hard-coded on the title slide).
This generator collapses all of that to the single `#1B3A6E` everywhere a
heading or title-slide branded text needs navy. If you are extending this
tool, do not reintroduce a second navy -- add a named role to the palette
table above instead and justify it here.

## Fonts

Theme major = minor = **Exo 2** (declared in `assets/template.pptx`'s
theme; not overridden anywhere in code). The generator **never sets
`run.font.name`** -- every run is left to inherit `+mn-lt`/`+mj-lt`, which
this template's theme resolves to Exo 2. This is what keeps the tool
language/font-neutral: swap the theme's font scheme and every slide type
follows without any code change.

| Role | Size | Weight | Colour |
|---|---|---|---|
| Content-slide title (all types except title/back_cover/thanks) | 24pt | bold, ALL CAPS (`cap="all"`, inherited from the layout's own lstStyle for this placeholder) | navy |
| Definition block header | 24pt | bold | navy |
| Definition block body (object/subject/goal statement) | 20pt | regular | black |
| Body / bullets / conclusions | 20pt | **bold** | black |
| Table cell text (body) | 10pt | regular | black |
| Table cell text (header row) | 10pt | **bold** | navy |
| Caption (table/two_column) | 16pt | bold | black |
| Two-column section heading | 13pt | bold | black |
| Two-column item | 12pt | regular | black |
| References entry | 8-12pt (auto by count, see spec-schema.md) | **bold** | black |
| Footer university wordmark | 8pt | bold | white (layout-owned, unchanged from source) |
| Slide-number field | 14pt | regular | white |
| Title-slide wordmark | 19pt | bold | navy |
| Title-slide department/author block | 16pt | regular | navy |
| Title-slide main statement | 22pt | bold | navy |
| Thanks/closing statement | 28pt | inherited bold+caps from the title placeholder | navy |

**Body/bullets/conclusions/references are bold -- measured directly, not
assumed (fidelity fix).** A full OOXML dump of the reference deck
(`scratchpad/analysis/dump_runs.py` output, `scratchpad/analysis/runs.txt`)
was re-run against the actual source presentation for this pass, closing
out the "re-derive once the material is available" note that used to sit
at the bottom of this document. The result is unambiguous: every sampled
bulleted/numbered list, publications list, and conference list in the
original carries an explicit `b="1"` on its runs --
  - `slide3.xml` ("Часткові наукові завдання"): every run `b="1"`, `sz`
    inherited from the layout's idx=13 lstStyle (`sz="1400"`, no
    `normAutofit` shrink) -- **14pt bold**.
  - `slide8.xml` ("Структура дисертації") and `slide12.xml` ("Висновки"):
    every run `sz="2000" b="1"` -- **20pt bold**, no shrink.
  - `slide9.xml` ("Стан роботи над дисертацією"): `b="1"`, inherited 14pt.
  - `slide10.xml`/`slide11.xml` (publications/conferences, `references`
    type): every run `b="1"`; `slide10` is explicit `sz="900"` with a
    `normAutofit fontScale="97500"` (~8.8pt effective); `slide11` inherits
    14pt with `fontScale="67500"` (~9.45pt effective) -- confirms the
    existing gotcha #8 autofit-shrink finding *and* that the shrunk text is
    still bold.
  - By contrast, the `definition` slide's three descriptive paragraphs
    (`slide2.xml`, e.g. "TextBox 4") and the `two_column` pros/cons items
    (`slide6.xml`, e.g. "TextBox 3") have **no** `b` attribute anywhere in
    their inheritance chain -- genuinely regular weight, which is why those
    two are the only body-text roles left `bold=False` above.

  This generator previously rendered every one of these bold-in-the-
  original roles as *regular* weight. `build_deck.py` now renders
  `bullets`/`conclusions` items and `references` entries bold
  (`render_bullets()`, `render_references()`), and the overflow heuristic
  (`_estimate_lines()`/`check_overflow()`) takes a `bold=` flag that widens
  its per-character estimate (`AVG_CHAR_W_FACTOR_BOLD = 0.66` vs `0.52`
  regular -- calibrated empirically against a real rendered test deck, see
  that constant's own comment in `build_deck.py`) so a now-bold list still
  gets an accurate WARN if it is tight. This recalibration is exactly what
  caught `assets/example-spec.json`'s own "Часткові наукові завдання"
  slide genuinely overflowing into the footer bar once its items were bold
  -- its items were shortened so the example stays WARN-free.
  `CONCLUSIONS_SIZE_PT` was also raised from 18pt to 20pt to match the
  measured, un-shrunk `slide12.xml` value exactly. `BODY_SIZE_PT` (20pt)
  is unchanged: the original's own per-slide sizes range 14-22pt with no
  single consistent value (hand-typed per slide, not a system), and 20pt
  already matches the `slide8.xml` sample exactly.

**Title-slide wordmark is 19pt, not 16pt (fidelity fix).** The wordmark
box (`slide1.xml` "Text Box 10") is a freeform, non-placeholder textbox
whose runs carry **no** `sz` anywhere in their XML -- there is no layout
placeholder to inherit from either, since it isn't one. Measured directly
off the reference render (`scratchpad/analysis/slides/slide-01.png`) by
comparing cap-height in pixels against the department/author lines'
*known* 16pt (both have an explicit `sz="1600"` in their XML): the
wordmark's cap-height is ~1.3x that reference, i.e. ~21-22pt -- clearly
larger than the department/author block below it, matching its role as
the top-level institutional heading. `TS_WORDMARK_PT` was 16pt (same size
as the department/author lines); the final value used is **19pt**, not
the raw ~21-22pt cap-height estimate -- see `TS_WORDMARK_PT`'s own comment
in `build_deck.py` for why (re-rendering this exact box at each candidate
size shows 20-21pt makes line 1 of the wordmark wrap to a second physical
line, which the original does not do; 19pt is the largest size that keeps
the same 1-line/2-line wrap split as the original, and it already sits
inside the cap-height estimate's own measurement uncertainty). The
wordmark box height and the department line's position were both widened
accordingly (`TS_WORDMARK_H` 2.00cm -> 2.60cm, `TS_DEPT_T` 2.55cm ->
3.05cm) so the taller wrapped wordmark still clears the department line
below it with a real gap -- confirmed by rendering the actual title
archetype, not just the isolated calibration deck (see "Do / don't" and
the `TS_DEPT_T` comment in `build_deck.py`).

**On body text looking "lighter/smaller" than the original's render (QA
note):** aside from the bold-weight fix above, nominal point sizes in this
generator are real, undiminished sizes in the generated `.pptx` XML -- not
autofit-shrunk, and they do not change between files. Any *remaining*
visible difference in weight/size versus a reference render (once both
files use the same bold/regular split documented above) is a **rendering
artifact of the preview pipeline, not the file**: both the original deck's
PNG renders and this generator's `render_preview.py` output go through
`soffice --headless` on a machine without the Exo 2 font installed (see
`assets/fonts/README.md`), so LibreOffice silently substitutes a fallback
font for every run that inherits `+mn-lt`/`+mj-lt`. Two different font
substitutions at two different nominal weights/metrics will not look
pixel-identical even when the underlying `sz`/`b` attributes match exactly
-- confirmed independently in this font-less environment by the
back-cover wordmark picture (`assets/template.pptx`'s baked-in brand image)
rendering with a collapsed inter-word space that is provably present as a
real space character in a non-image, live-text box using the same string
on the title slide. Install Exo 2 (see the fonts README) before doing any
further visual weight/size comparison against a reference render.

## Per-type geometry (cm, left/top/width/height unless noted)

| Element | L | T | W | H |
|---|---|---|---|---|
| Content title band (every content archetype) | 0.91 | 0.90 | 23.47 | 2.60 |
| Content body zone (bullets/references/conclusions/definition span) | 0.91 | 3.70 | 23.47 | 8.50 |
| Footer bar (layout-owned, not drawn by code) | 0.0 | 12.81 | 25.40 | 1.48 |
| Content-bottom safe line (nothing should render past this) | -- | 12.20 | -- | -- |
| Slide-number field | 17.94 | 13.24 | 5.71 | 0.76 |
| Title-slide wordmark | 4.25 | 0.37 | 18.11 | 2.60 |
| Title-slide department line | 4.89 | 3.05 | 16.79 | 0.94 |
| Title-slide main statement | 2.10 | 4.63 | 21.84 | 3.98 |
| Title-slide author block | 15.78 | 9.43 | 9.10 | 3.68 |
| Title-slide navy shield logo | 0.79 | 0.27 | 2.61 | 3.68 |
| Title-slide gold decorative icon | 21.47 | 0.0 | 3.93 | 3.93 |
| Back-cover wordmark | *(layout-owned; not drawn by code -- baked into `assets/template.pptx`'s "Титульний слайд" layout)* | | | |
| Caption band (table/two_column, when present) | 0.91 | 3.70 | 23.47 | 1.30 |
| Two-column image band (per column, when present) | -- | -- | -- | 2.60 |
| Two-column gutter between columns | -- | -- | 0.60 | -- |

**Footer clearance (QA fix):** `CONTENT_BOTTOM_CM` was `12.55`, only ~0.26cm
above `FOOTER_BAR_TOP_CM` (12.81) -- tight enough that a legitimately-sized
5-item numbered list (report-structure.md's own recommended max) rendered
its last line touching the footer bar with **no WARN**, because the
overflow heuristic only counted wrapped-line height and ignored the
`spcBef` gap between list items. Fixed two ways: (1) `CONTENT_BOTTOM_CM` is
now `12.20`, restoring a real **>=0.6cm** gap above the footer bar for
every archetype that derives its height from it; (2) `check_overflow()`
now also takes `extra_height_pt` for exactly this inter-paragraph spacing
(wired up in `bullets`/`conclusions`/`references`), so a dense list now
correctly WARNs before its text would reach the footer instead of after.
Note that text in a PowerPoint text box is never clipped by its nominal
height -- shrinking a box alone does not move already-overflowing text, so
the heuristic fix (point 2) is what actually prevents a silent miss; the
geometry fix (point 1) is what keeps images/tables/next-slide-type authors
inside a genuinely safe area.

## Footer / slide-number rules

- Footer bar, logo, university wordmark are 100% layout-owned (they live in
  `slideLayout2.xml`'s XML inside `assets/template.pptx` and are never
  duplicated per-slide) -- this matches the one thing the original deck
  actually got right.
- The slide-number field is **not** a real PowerPoint placeholder in this
  template (the layout declares none), so it is drawn as a plain textbox
  containing a proper `<a:fld type="slidenum">` on every content slide.
  This mirrors exactly how the original deck itself does it on its cleaner
  slides (confirmed by inspecting its raw XML) -- it is not an invented
  mechanism.
- The `title` and `back_cover` archetypes never get a slide-number shape
  (matches the original: its title slide and back cover show no page
  number either).

## Table style

- Flat "accent-tint" look: every cell filled with a tint of theme accent1,
  thin white 1pt gridlines, no native PowerPoint table style GUID relied
  upon (python-pptx cannot reproduce those faithfully across renderers --
  see the task's source analysis).
- **Fix vs. the original, re-confirmed directly from the XML:** both
  tables in the reference deck (`slide4.xml`/`slide5.xml`) reference the
  built-in table style `{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}`
  ("Средний стиль 2 — акцент 1") via `<a:tblPr><a:tableStyleId>...`, with
  **no** `firstRow`/`bandRow` attributes set on `<a:tblPr>` -- so that
  style's own distinct first-row/banding formatting (defined in
  `ppt/tableStyles.xml`) is never activated, and literally every cell
  (header included) falls back to the style's flat `wholeTbl` fill:
  `accent1 tint 20%`. There genuinely is no visual header distinction in
  the original. This generator gives the header row a visibly darker tint
  of the *same* accent family plus bold navy text, while keeping the flat,
  non-native look otherwise unchanged.

## Bullet style

- Real OOXML bullets throughout: `a:buAutoNum type="arabicPeriod"` for
  numbered lists, `a:buChar char="•"` for plain bulleted lists -- never a
  literal "•" or "1." typed into the text run.
- Numbered-list paragraph formatting: `marL=342900 indent=-342900` (0.95cm
  hang), 120% line spacing, matching the original's own numbered lists.
- Nested items (`bullets`/`conclusions` with `"sub"`) render the parent
  item as a bold, un-bulleted section header and start a **fresh** numbered
  or bulleted run for its children. See "Do / don't" below for why.
  (Mixing plain and `sub`-bearing items in one list is discouraged for the
  numbering-restart reason explained in `references/spec-schema.md`'s
  "Nesting note" — not repeated here.)

## Do / don't (defects from the original this generator deliberately does NOT reproduce)

| Original defect | What this generator does instead |
|---|---|
| Title placeholder defaults to 1.96cm tall -- exactly one line of 24pt caps -- causing a provable 2-line-title/body overlap on 2 of 14 slides. | Every content title band is a fixed 23.47 x 2.60cm, generous enough for 2 full lines at 24pt, used identically on every archetype. |
| "Об'єкт/Предмет/Мета" header/body pairs are stacked with a ~0.01cm gap via stale `spAutoFit` heights that PowerPoint/LibreOffice don't recompute -- headers visually overlap the paragraph above them. | Fixed, generous vertical rhythm (header 1.00cm + body 2.05cm + 0.45cm gap) computed once, never relying on autofit. |
| Three different "navy" hex values used inconsistently for headings. | A single brand navy (`#1B3A6E`) everywhere. |
| Table header row uses the exact same fill as every body row -- no visual distinction. | Header row gets a bold, navy-text, visibly-darker tint of the same accent family. |
| Dense reference/publication lists rely on PowerPoint's `normAutofit` to shrink text as low as 67.5% scale, meaning the nominal font size in the file is not what's actually shown. | An explicit, deliberately-chosen small font size picked from the item count up front; if it still won't fit, the tool prints a `WARN` instead of silently shrinking further. |
| "Висновки" (conclusions) uses full justification (`algn="just"`), which visibly stretches word gaps on short lines. | Left-aligned by default. |
| Slide-1's 2-line university wordmark box is only 1.45cm tall, causing it to visually overlap the department line directly below it. | Wordmark box raised to 2.60cm tall (it wraps to 3 lines at the now-measured 19pt bold); department line pushed down to 3.05cm top to guarantee clearance. |
| Per-slide geometry for the "same" element (e.g. the title placeholder) differs slide-to-slide because it was hand-tuned by trial and error. | One CONSTANTS section drives identical geometry for every slide of a given archetype -- no per-slide hand-tuning. |

## QA fidelity-audit note (title band / back cover / table / references)

The title-band casing/size/color/position (ALL CAPS, 24pt, bold, `#1B3A6E`,
left margin 0.91cm) was re-verified directly against
`assets/template.pptx`'s `ppt/slideLayouts/slideLayout2.xml` placeholder
`idx=11` `lstStyle` (`sz="2400" b="1" cap="all"`, `srgbClr val="1B3A6E"`, at
`x=328414,y=323254` EMU = 0.91/0.90cm) -- this is layout-owned and
untouched by `build_deck.py`, so it is provably faithful to whatever that
layout shipped with, independent of any separate analysis dump. The same
check on `slideLayout1.xml` (back cover) confirms it is a single
layout-owned picture + navy background with no per-slide shapes, matching
the "no per-student text" rule above.

**Update -- re-derived from the original reference deck (resolved, no
longer pending):** a full OOXML/visual analysis of the reference deck now
exists at `scratchpad/analysis/` (`source.pptx`, `slides/slide-NN.png`,
`dump_runs.py`, `runs.txt`), so the title-slide and body/references facts
below are re-derived from it directly, not left as "internally consistent
but unverified":

- **Title-slide geometry** (`scratchpad/analysis/runs.txt`, slide 1):
  wordmark box 4.249/0.372/18.106/1.453cm, department line
  4.894/1.602/16.789/0.94cm, main statement 2.095/4.634/21.845/3.98cm,
  author block 15.78/9.427/9.098/3.676cm, gold logo 21.47/0.0/3.93/3.93cm,
  shield logo 0.791/0.269/2.615/3.676cm. Every one of these is within
  0.02cm of this generator's own `TS_*` constants **except** the two
  already-documented deliberate fixes above (wordmark box height raised
  1.453cm -> 2.60cm; department line pushed down 1.602cm -> 3.05cm to
  compensate -- both widened further than a first pass, once rendering the
  wordmark at its measured 19pt bold size showed it now wraps to 3 lines,
  not 2, within the same width) -- no further undocumented geometry drift
  found, and nothing exceeds the 0.3cm fidelity tolerance.
- **Title main statement colour**: `schemeClr val="accent1"` with
  `lumMod val="50000"` (accent1 = theme `#4472C4`, darkened 50%) -- this is
  the second of the "three navies" this generator deliberately collapses
  to a single `#1B3A6E` (see Palette above); now directly reconfirmed from
  `slide1.xml` rather than inferred.
- **Title-slide wordmark size** and **body/bullets/conclusions/references
  bold weight and sizes**: see the dedicated notes under Fonts above.

The table/references nominal point sizes remain `build_deck.py` code
constants (not layout-inherited) by design -- the fix is to make those
constants match the measured facts above, not to inherit them at render
time.

## How to extend with a new slide type

1. Add the type name to `SLIDE_TYPES` in `build_deck.py`.
2. Add its required-field checks to `validate_spec()`.
3. Add geometry constants to the CONSTANTS section at the top of the file
   (cm values, with a comment explaining where the number comes from --
   even if it's "chosen to match the existing title/body band" rather than
   lifted from the original analysis).
4. Write a `render_<type>(prs, layout, slide_spec, ...)` function following
   the existing ones as a template: `add_slide`, drop unused placeholders
   (idx 12/13 if unused), set the title via `_setup_title_shape` if the
   type has one, draw the rest with `add_textbox`/`add_picture_fit`/
   `slide.shapes.add_table`, and call `check_overflow()` on any
   variable-length text you place.
5. Wire it into the `stype == ...` dispatch chain in `build_deck()`.
6. Document the new type's fields in `references/spec-schema.md` and add an
   example to `assets/example-spec.json`.
7. Re-run the quality loop: build the example spec, render it with
   `scripts/render_preview.py`, and visually check the new slide type next
   to the others for consistent title/footer/spacing treatment.
