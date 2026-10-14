# Spec schema reference -- phd-report-presentation

This document is the field-by-field reference for the JSON spec consumed by
`scripts/build_deck.py`. See `assets/example-spec.json` for a complete,
realistic example that exercises every slide type, and
`references/style-guide.md` for the geometry/palette/typography those types
render with.

## Top-level shape

```json
{
  "lang": "uk",
  "meta": { "...": "..." },
  "slides": [ { "type": "...", "...": "..." } ]
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `lang` | string | no | Informational only today (e.g. `"uk"`). All built-in label defaults are Ukrainian; pass explicit `labels`/`meta` overrides to use another language -- the generator itself does not translate anything. |
| `meta` | object | no (defaults to `{}`) | Person/institution fields consumed by the `title` slide type. See "meta fields" below. |
| `slides` | array | **yes**, non-empty | Ordered list of slide objects, one per output slide. |

Image paths anywhere in a slide object are resolved **relative to the spec
file's own directory** (not the current working directory, not the skill's
`assets/` dir -- that separate lookup is only used internally for the title
slide's brand logos).

## `meta` fields (used by the `title` slide type)

| Field | Default | Notes |
|---|---|---|
| `university_name_line1` | "Національний технічний університет України" | Line 1 of the wordmark. |
| `university_name_line2` | "«Київський політехнічний інститут імені Ігоря Сікорського»" | Line 2 of the wordmark. |
| `department` | (none -- required in practice) | Shown as-is under the wordmark. |
| `dissertation_title` | (none -- required in practice) | The big centred statement. |
| `student_group` | "" | Substituted into `student_label_template`. |
| `student_name` | "" | Author's own name line. |
| `supervisor_name` | "" | Supervisor's name/degree line. |
| `supervisor_label` | "Науковий керівник:" | Label line before `supervisor_name`. |
| `student_label_template` | "Аспірант групи {group}" | `{group}` is replaced with `student_group`. |
| `report_title` | (none -- optional) | Short heading line (e.g. the semester number), rendered directly above `dissertation_title` in the title-slide hierarchy. See below. |

Any of these can be overridden per-slide on a `title` slide entry itself
(the slide's own field wins over `meta`).

### `meta.report_title` (semester / report-title line)

The reference deck this skill's styling is based on never printed a
semester number anywhere (see `references/report-structure.md`'s own
pitfall note for the `title` slide) -- a real run had to hack it into
`student_label_template` for lack of a dedicated slot. `report_title` is
that dedicated slot: an optional string rendered as a short bold heading
line directly above the `dissertation_title` block, in title-slide navy,
sized between the department line and the dissertation topic in the
hierarchy (16pt bold vs. the department line's 16pt regular and the topic
's 22pt bold).

```json
{ "meta": { "report_title": "Звіт про виконання плану аспіранта за 4 семестр", "...": "..." } }
```

Behaviour:

- **Optional, and additive only.** If `report_title` is absent (or `null`,
  or an empty string) on both `meta` and the `title` slide, the title
  slide's layout is **pixel-identical** to a spec with no `report_title`
  at all -- the dissertation-topic block stays at its original position;
  there is no reserved empty gap.
- When present, the dissertation-topic block is pushed down to make room,
  the same way every other archetype in this generator reserves fixed,
  non-overlapping space rather than relying on autofit.
- **Overridable per-slide**, exactly like every other title field: set
  `"report_title"` directly on the `{ "type": "title", ... }` slide object
  to override (or, with an explicit `""`, suppress) a `meta`-level value
  for that one slide.
- Keep it short -- one line, well under half the slide width at 16pt bold;
  a `WARN` fires (and the dissertation-topic block still only moves down
  by one line's worth of space) if it's long enough to need two.

## Slide types

Every slide object has a `type` field, one of: `title`, `definition`,
`bullets`, `table`, `two_column`, `image`, `references`, `conclusions`,
`thanks`, `back_cover`. Unknown types are a hard validation error.

### `title`
Content comes from `meta` (see above); every field can be overridden inline
on the slide object using the same field names, plus `dissertation_title`.
No other fields. Renders logos, university wordmark, main title and the
author/supervisor block. No footer/slide-number (matches the original: the
title slide never shows a page number).

```json
{ "type": "title" }
```

or with an override:

```json
{ "type": "title", "dissertation_title": "Override for this one deck" }
```

or with the optional semester/report-title line (see `meta.report_title`
above for the full behaviour):

```json
{ "type": "title", "report_title": "Звіт про виконання плану аспіранта за 4 семестр" }
```

### `definition`
The canonical "Об'єкт / Предмет / Мета дослідження" 3-block slide. No title
band (matches the original, which never puts a heading above these three
blocks).

| Field | Type | Required | Notes |
|---|---|---|---|
| `object` | object `{ "text": str }` | yes | |
| `subject` | object `{ "text": str }` | yes | |
| `goal` | object `{ "text": str }` | yes | |
| `labels` | object | no | Override header strings: keys `object`, `subject`, `goal`; defaults `"Об'єкт дослідження:"`, `"Предмет дослідження:"`, `"Мета дослідження:"`. |

Recommended limit: each block's `text` should be at most ~2-3 wrapped lines
at 20pt in a 24.2cm-wide, 2.05cm-tall box; longer text triggers a `WARN`.

### `bullets`
Numbered or bulleted list, up to 2 nesting levels.

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | yes | |
| `items` | array | yes, non-empty | Each item is either a string, or an object `{ "text": str, "sub": [str, ...] }`. |
| `style` | `"numbered"` \| `"bulleted"` | no (default `"numbered"`) | Applies to every top-level item and every `sub` list. |
| `font_size_pt` | number | no (default 20) | |

Nesting note: an item with `"sub"` renders its own `"text"` as a **bold,
un-numbered section header**, and each `sub` entry starts a fresh
numbered/bulleted mini-list beginning at 1 -- this is a deliberate departure
from naive "1., a." outline nesting because true continuous top-level
auto-numbering across an interrupting sub-list is unreliable across
renderers (see style-guide.md "Do / don't"). Mixing plain top-level strings
and `sub`-bearing items in the same list is technically allowed but not
recommended, since the plain items' own numbering may restart around a
`sub`-bearing item.

Recommended limit: **≤ 8-9 short items** (or fewer if items are long/wrap to
2 lines) per slide at the default 20pt; the tool prints a `WARN` past that
and suggests splitting -- it will never silently shrink the font.

### `table`
| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | yes | |
| `columns` | array of strings | yes, non-empty | Header row labels. |
| `rows` | array of arrays | yes, non-empty | Each row must have exactly `len(columns)` cells; cells are stringified as-is. |
| `caption` | string | no | Bold caption line above the table/image. |
| `image` | path | no | Optional side image (e.g. a chart); if present, the table is narrowed to make room on the right and the image occupies the left ~40%, vertically centred. |

Recommended limit: **≤ 8-10 data rows** per slide at the default row-height
floor (0.75cm); the tool prints a `WARN` if the table is computed tighter
than the available area.

### `two_column`
| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | yes | |
| `caption` | string | no | Centred, spans both columns, above them. |
| `columns` | array of exactly 2 objects | yes | See below. |

Each column object:

| Field | Type | Required | Notes |
|---|---|---|---|
| `image` | path | no | e.g. a formula screenshot; placed at the top of the column, fit into a fixed-height band. |
| `sections` | array, non-empty | yes | Each `{ "heading": str, "items": [str, ...] }` renders a bold heading followed by a plain (round-bullet) list. |

Recommended limit: 2 sections per column, ≤ 3 short items each (matches
the original's "Основні переваги / Основні недоліки" pattern).

### `image`
| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | yes | |
| `text` | string or array of strings | no | Intro paragraph(s), bold, above the image. |
| `image` | path | yes | Scaled to fit, aspect preserved, centred horizontally, top-anchored. |
| `caption` | string | no | Small centred line below the image. |

### `references`
Dense numbered bibliography/conference list with a smaller, explicit font
(never relies on PowerPoint's autofit).

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | yes | |
| `items` | array of strings | yes, non-empty | One bibliographic entry per string. |
| `font_size_pt` | number | no | If omitted, auto-picked from item count: ≤6 → 12pt, ≤9 → 10.5pt, ≤12 → 9pt, else 8pt (+ a `WARN`). |

Recommended limit: **≤ 12 entries** per slide; beyond that, split across two
`references` slides.

### `conclusions`
Same mechanics as `bullets` (including the `items`/nesting rules above) but
left-aligned by default (the original's justified conclusions text is a
known defect this generator does not reproduce -- see style-guide.md) and a
slightly larger nominal size.

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | yes | |
| `items` | array | yes | Same shape as `bullets.items`. |
| `font_size_pt` | number | no (default 18) | |

### `thanks`
| Field | Type | Required | Notes |
|---|---|---|---|
| `text` | string | no (default `"Дякую за увагу!"`) | |

### `back_cover`
No fields. Fully brand-template-owned (navy background + centred wordmark
picture) -- the generator adds a bare slide and draws nothing on it.

```json
{ "type": "back_cover" }
```

## Minimal example

```json
{
  "meta": {
    "department": "Кафедра ...",
    "dissertation_title": "Тема дисертації ...",
    "student_group": "XX-00ф",
    "student_name": "Прізвище Ім'я По батькові",
    "supervisor_name": "д.т.н., проф. Прізвище І. П."
  },
  "slides": [
    { "type": "title" },
    { "type": "bullets", "title": "Часткові наукові завдання",
      "items": ["Перше завдання.", "Друге завдання."] },
    { "type": "thanks" },
    { "type": "back_cover" }
  ]
}
```

## Full example

See `assets/example-spec.json` (exercises every slide type with generic
placeholder content) and `assets/example/` for the tiny sample chart/formula
images it references.

## Validation behaviour

`build_deck.py` validates the whole spec **before** touching the output
file: unknown slide type, a missing required field, a table row with the
wrong number of cells, or an image path that does not resolve all produce a
one-line `error: ...` message on stderr and a non-zero exit code -- never a
raw Python traceback and never a partially-written .pptx.
