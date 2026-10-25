# DOCX helper and verification

`scripts/vottp_docx.py` edits only `word/document.xml`, preserving other ZIP members
byte-for-byte. It applies paragraph/run layout properties without recreating
paragraphs, equations, hyperlinks, tables or embedded objects. It refuses macros,
tracked insertions/deletions, an in-place output, stale inventories and unknown
roles. It preserves existing headers/footers; inspect whether imported publisher
furniture needs removal in a separate author-approved edit.

## Inventory and roles

```bash
uv run "$S/scripts/vottp_docx.py" inspect draft.docx --out roles.json
```

The JSON contains a source SHA-256 and every body paragraph (including table-cell
paragraphs), in document order with a zero-based `index`. Read the text, then edit
only each paragraph's `role`. Non-table paragraphs initially default to `body`,
table-cell paragraphs to `table`, and native-math paragraphs to `equation`; this is
a mechanical default, not a completed semantic classification. Leave `index`,
`text` and the source hash unchanged. Regenerate the inventory after any content
edit; indices are not stable across author revisions.

Roles: `body`, `udc`, `author`, `affiliation`, `contact`, `title`, `abstract-uk`,
`abstract-en`, `keywords-uk`, `keywords-en`, `heading`, `subheading`, `figure`,
`figure-caption`, `table-label`, `table-title`, `table`, `reference-heading`,
`reference`, `equation`, `keep`.

Use `figure` for an image-only paragraph and `equation` for a displayed equation;
for a body paragraph with an inline equation choose `body` manually. Math XML and
scientific Symbol/Cambria Math font runs stay untouched regardless of role.
Use `keep` only for intentionally preserved special layout, and record the reason
in the manual report; the checker reports those paragraphs as NOT VERIFIED.

The helper's default **guide** profile uses TNR 10 pt and 1.3 spacing for all
ordinary text. Both profiles set A4 portrait and L25/R15/T25/B25 mm margins. These
additional role treatments are local layout conventions, not independently stated
journal mandates:

| Roles | Alignment / layout |
|---|---|
| body | Justified; 12.5 mm first-line indent; no extra paragraph spacing |
| udc | Left; no first-line indent |
| author, affiliation, contact | Right; no first-line indent |
| title, heading, reference-heading | Center; bold; keep with next |
| subheading | Left; bold; keep with next |
| abstract-*, keywords-* | Justified; 12.5 mm first-line indent |
| figure, equation | Center; no first-line indent |
| figure-caption | Center; keep lines together |
| table-label | Right; keep with next |
| table-title | Center; bold; keep with next |
| table | Left; preserve cell contents/widths and table structure |
| reference | Left; no first-line indent; retain existing citation text/numbering |

The optional **published** profile changes author/title to TNR 12 pt; affiliation,
contact, reference and table to TNR 8 pt; abstracts/keywords to Tahoma 8 pt italic.
Those compact roles use single spacing. It approximates the measured PDFs; it is
not an official template and does not resolve the conflicting author guide.
Body/headings stay TNR 10 / 1.3. Existing body emphasis, subscripts/superscripts,
links, list numbering, equation fields and media are preserved. The script does not
uppercase text, remove underlining, remove existing forced page breaks, or change
table/figure sizes; inspect these separately.

## Formatting and checks

```bash
uv run "$S/scripts/vottp_docx.py" format draft.docx --roles roles.json --out paper.docx
uv run "$S/scripts/vottp_docx.py" check paper.docx --roles roles.json --original draft.docx --out layout-report.json
# If the author explicitly chooses the observed production appearance:
uv run "$S/scripts/vottp_docx.py" format draft.docx --roles roles.json --out published-style.docx --profile published
uv run "$S/scripts/vottp_docx.py" check published-style.docx --roles roles.json --original draft.docx --out published-layout-report.json --profile published
```

The checker validates A4/margins, explicit role formatting and floating DrawingML
objects, reports per-language abstract character counts, identifies legacy VML/OLE
for manual inspection, and compares document content/structure plus unchanged ZIP
parts against the original. It returns 1 for detected errors and 0 otherwise;
zero means only that this limited automated subset passed. Missing body functions,
reference quality, actual identities, source-language policy, self-citation, table
completeness, length and appearance need the separate manual review.

OMML/Cambria Math and symbol-only runs are excluded from ordinary-font checks.
Never call an unrendered manuscript visually verified. If table widths overflow the
170 mm text area, resize without cutting content and regenerate the role inventory
for that edited source before formatting again. The helper's preservation check
expects only its documented layout edits; deliberate content changes belong in a
separately versioned source with a new inventory.

## Report and disclosure

Use the rule IDs in requirements.md. Attach a full report rather than presenting
the JSON layout report as acceptance validation. Example:

```text
F02 PASS — all 2 sections A4 portrait, L25/R15/T25/B25 mm.
F04 NOT VERIFIED — DOCX not rendered; page count unknown.
M06 EDITOR CLARIFICATION — four authors; guide says both three and four.
C03 NEEDS AUTHOR — Table 2, row B has no quality measurement.
P03 NEEDS AUTHOR — review the AI-use disclosure below.
```

Disclosure wording must reflect actual use. A draft may say the author used
`[tool, developer, version/configuration]` for layout checks and/or translation,
and verified the changes. Populate only known details, identify missing ones,
and obtain author review. Do not claim that the tool created or verified research
results when it only formatted supplied text.
