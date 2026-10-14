---
name: phd-report-presentation
description: Generates a KPI-branded PhD semester/progress-report presentation (.pptx) from a bundled template via a JSON spec, and updates or regenerates an existing one. Use when the user asks for a "report presi", "report presentation", "презентація звіту", "звіт за семестр", "атестація", PhD progress-report slides, or any semester/attestation .pptx deck for a KPI PhD student, or wants to add/change slides in one. Defaults to Ukrainian content and KPI navy/Exo 2 branding; never invents names, dates, or publications — ask only for missing essentials.
---

# PhD report presentation

## Overview

Produces a 12-16 slide `.pptx` deck for a KPI PhD semester/attestation report,
in the department's fixed visual style (navy `#1B3A6E`, Exo 2 font, KPI
wordmark/footer) — the same look a real reference deck uses, with that
deck's layout bugs (title/body overlap, autofit text shrink) deliberately
fixed. Content and geometry are driven entirely by a JSON spec; you never
edit the `.pptx` by hand.

Pipeline: **collect content → write a JSON spec → build the deck with
`build_deck.py` → render a PNG preview → visually verify it → iterate if
needed → deliver**.

Requirements:

1. `uv` — runs `scripts/build_deck.py` and `scripts/render_preview.py`
   directly; both are PEP 723 scripts that fetch their own dependencies
   (`python-pptx`, `pillow`, `pymupdf`) into an ephemeral environment on
   first run. No project install needed.
2. LibreOffice (`soffice`) — needed only for the preview-rendering step
   (`render_preview.py`), not for building the deck itself. If it's
   missing, the deck still builds; just skip preview rendering and ask the
   user to open the `.pptx` directly.
3. Exo 2 font — optional, affects preview/editing fidelity only (the
   generator always references it in the file regardless). See
   `${CLAUDE_SKILL_DIR}/assets/fonts/README.md` for install commands.

## Step-by-step workflow

Do all of this in a **working directory in the user's project** (or
wherever they asked for the output) — e.g. `./zvit-4-semestr/` — never
inside this plugin/skill directory. That's where `spec.json`, any copied
images, the output `.pptx`, and the preview PNGs all live.

1. **Gather content.** See "Content gathering" below and
   `references/report-structure.md` for the recommended slide sequence and
   the full pre-generation question checklist.

2. **Write the spec.** Start from the canonical example rather than from
   scratch:

   ```bash
   cp "${CLAUDE_SKILL_DIR}/assets/example-spec.json" spec.json
   ```

   Edit `spec.json` in place: replace `meta` fields, rewrite/add/remove
   slide objects. See "Writing the spec" below and
   `references/spec-schema.md` for the full field reference.

3. **Build the deck:**

   ```bash
   uv run "${CLAUDE_SKILL_DIR}/scripts/build_deck.py" --spec "spec.json" --out "zvit-4-semestr.pptx" --verbose
   ```

   Default output filename convention: `zvit-<semester>-semestr.pptx` (e.g.
   `zvit-4-semestr.pptx`) — use the user's own naming if they asked for
   something else. `--verbose` prints a one-line-per-slide build log to
   stderr; always pass it. The build is all-or-nothing: on any spec problem
   it prints one line like

   ```
   error: slides[1]: unknown slide type 'bogus_type'. Valid types: back_cover, bullets, conclusions, definition, image, references, table, thanks, title, two_column
   ```

   to stderr and exits non-zero without writing a partial file — fix
   `spec.json` and rerun.

4. **Render a preview:**

   ```bash
   uv run "${CLAUDE_SKILL_DIR}/scripts/render_preview.py" "zvit-4-semestr.pptx" --out preview
   ```

   This writes `preview/slide-NN.png` per slide plus `preview/contact-sheet.png`
   (all slides in a grid). If `soffice` isn't found it raises a clear
   `RuntimeError` naming the problem — report that to the user rather than
   retrying blindly.

5. **Visually verify** — see "Verification loop" below. Fix and rebuild
   until clean.

6. **Deliver** — see "Delivery" below.

## Content gathering

- Use `references/report-structure.md` for the recommended 12-16 slide
  sequence (title → object/subject/goal → tasks → results (2-5 slides) →
  publications/conferences → conclusions → next-semester plan → thanks →
  back cover) and its pre-generation checklist of exactly what to ask the
  student for.
- Use everything the user has already provided (chat text, pasted plan,
  previous deck, publication list, etc.) before asking anything.
- Ask only for the essentials that are genuinely missing and block
  generating a reasonable first draft (typically: semester number,
  dissertation topic, supervisor, this semester's tasks/results). Put the
  semester number in `meta.report_title` (e.g. `"Звіт про виконання плану
  аспіранта за 4 семестр"`) — don't hack it into `student_label_template`
  or another unrelated field.
- For any personal field you still don't know (name, group, supervisor
  degree, exact date, a publication's DOI, etc.), put a clearly-marked
  placeholder in the spec (e.g. `"[ПРІЗВИЩЕ Ім'я По батькові]"`,
  `"[уточнити дату]"`) instead of leaving it blank or guessing — **never
  invent a name, date, or publication**. List every such placeholder when
  you deliver the deck.

## Writing the spec

Ten slide `type`s, each a `{ "type": ..., ... }` object in the top-level
`slides` array (full fields in `references/spec-schema.md`):

1. `title` — cover slide; fields come from top-level `meta` (student, topic,
   supervisor, department), overridable per-slide. Optional `report_title`
   (e.g. the semester number) renders as a line above the dissertation
   topic — see `references/spec-schema.md`'s `meta.report_title` section.
2. `definition` — the canonical Об'єкт/Предмет/Мета дослідження 3-block
   slide.
3. `bullets` — numbered or bulleted list, up to 2 nesting levels; for
   tasks, dissertation structure, progress, teaching, next-semester plan.
4. `table` — titled data table, optional side image/chart.
5. `two_column` — two parallel sections (e.g. two indicators, each with
   pros/cons), optional per-column image.
6. `image` — intro text + one image + caption (e.g. a diagram or formula).
7. `references` — dense numbered bibliography/conference list, auto-sized
   font.
8. `conclusions` — like `bullets` but left-aligned, pairs with the tasks
   slide.
9. `thanks` — static closing slide.
10. `back_cover` — institutional branding bookend, no fields.

Volume limits (the tool prints a `WARN` — see below — rather than silently
shrinking text past these; prefer splitting into two slides):

- `bullets`/`conclusions`: ≤ 8-9 short items per slide.
- `table`: ≤ 8-10 data rows.
- `references`: ≤ 12 entries (≤ 6-7 recommended per `report-structure.md`).
- `definition` blocks and `two_column` sections: keep each to 1-3 wrapped
  lines.

Other rules:

- Any `image` path in the spec must already exist on disk before you run
  `build_deck.py` — it's resolved relative to **the spec file's own
  directory**, not the current working directory. Save/copy any
  chart/diagram/formula image into the working directory (or a subfolder
  of it) first.
- Equations must be **pre-rendered images**, not typed formulas — the
  generator has no native equation support (matches `image`/`two_column`
  column `image` fields).
- Mixing plain top-level items and `sub`-bearing items in the same
  `bullets`/`conclusions` list is discouraged — see `references/spec-schema.md`
  ("Nesting note") for the full explanation and why.
- Treat `assets/example-spec.json` as the canonical, copy-and-edit
  starting point — it exercises every slide type with realistic
  placeholder content.

## Verification loop

1. Read every `error:`/`WARN:` line `build_deck.py` printed to stderr.
   `error:` means nothing was written — fix and rerun. `WARN:` means it
   built anyway but flagged a specific overflow risk, e.g.:

   ```
   WARN: slide 1 (Overflow test): estimated ~28 lines of text at 20pt do not fit in the 8.50cm-tall box (~8.1 lines fit). Suggestion: shorten the text, raise fewer items, or split this into two slides.
   ```

   Always act on `WARN`s before delivering — shorten the content or split
   the slide.

2. Open `preview/contact-sheet.png` with the Read tool for a full-deck
   overview, then open any individual `preview/slide-NN.png` that looks
   suspicious at full resolution.

3. Check each slide for: text overflowing its box or running into the
   footer; overlapping shapes; an empty table cell or image placeholder;
   leftover literal placeholder text you forgot to fill in (vs. the
   intentional bracketed placeholders you deliberately left for the user);
   a cramped table; a blurry or wrong-aspect image.

4. Fix `spec.json`, rebuild, re-render, re-check — repeat until clean.

Known limitations to keep in mind (not bugs to "fix" by hand-editing the
`.pptx`):

- The overflow check is a text-length heuristic, not a true renderer
  measurement — a `WARN`-free build can still look tight; always eyeball
  the preview too.
- Table columns are always equal width.
- Mixing plain and `sub`-bearing bullet items in one list — see "Other
  rules" above.
- Formulas/equations render only as static images, never as editable
  native equations.

## Delivery

Report to the user: the output `.pptx`'s absolute path, the final slide
count, and an explicit list of any placeholder fields still left in the
spec that they need to fill in with real values (names, dates, exact
figures, publication details, etc.). Offer to keep iterating — e.g.
tightening a dense slide, adding a missing results slide, or regenerating
once they supply the remaining real content.

## Style rules

Full design system: `references/style-guide.md`. Summary:

1. Don't change the palette, fonts, or geometry through the spec — colors,
   font (Exo 2), and all positions are fixed constants in `build_deck.py`;
   the spec controls content only.
2. Don't add slide types or shapes by hand-editing the generated `.pptx`
   afterward — express everything through the spec and `build_deck.py`;
   extending the tool with a genuinely new slide type is a script change,
   out of scope for normal use of this skill.
3. Keep the deck to 12-16 slides total (`references/report-structure.md`);
   prefer splitting a dense slide over cramming or shrinking text.
4. Use the standard Ukrainian heading phrasing from
   `references/report-structure.md`'s conventions table (Об'єкт
   дослідження, Завдання на семестр, Висновки, etc.) — titles render
   ALL-CAPS automatically, write them in normal case in the spec.
5. Keep bibliographic entries in the standard Ukrainian reference-list
   format shown in `references/report-structure.md`.
6. Never invent a name, date, number, or publication — use a visible
   placeholder and flag it at delivery instead.
7. `back_cover` and `thanks` are meant to be sparse/static — don't add
   per-student text to `back_cover`.
