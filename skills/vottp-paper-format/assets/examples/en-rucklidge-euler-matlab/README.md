# Worked example: English research article with equations, tables and figures

A reconstructed **author draft** of a published VOTTP research paper, taken through
the skill pipeline. Read it when the manuscript is in English, has displayed equations,
many tables or multi-panel figures, and a Ukrainian translation of the front matter.

## Source and licence

- Razovyi O., Golevych O. "Performance comparison of explicit Euler implementations for an
  ensemble of Rucklidge system trajectories in MATLAB". *Measuring and computing devices in
  technological processes* 2026, No. 3 (issue 87), pp. 476-486 (11 pages, 2 authors).
- DOI: [10.31891/2219-9365-2026-87-55](https://doi.org/10.31891/2219-9365-2026-87-55)
- Article page: <https://vottp.khmnu.edu.ua/index.php/vottp/article/view/926>;
  PDF: <https://vottp.khmnu.edu.ua/index.php/vottp/article/download/926/931>
- Licence: **CC BY 4.0** (article page and the licence strip on page 1 of the PDF; checked
  2026-10-26). Copyright (c) 2026 the authors. This example reproduces text, tables and
  figures under that licence; attribution is the paragraph above. It is a layout
  reconstruction, not the authors' real submission file; cite the published article.

## Files

| File | What it is |
|---|---|
| `draft.docx` | Plain author-style manuscript: Word default template (Letter page, default margins), Times New Roman 12, bold paragraphs as headings, table grid style, native OMML equations, five inline PNG figures (92-198 KB each). |
| `roles.json` | The `inspect` inventory with every paragraph's role set (467 paragraphs, including table cells). Reference for how to classify a bilingual, table-heavy paper. |
| `paper.docx` | Output of `format` (default guide profile). |
| `layout-report.json` | Output of `check`: 0 errors, only F04 NOT VERIFIED. |

## Commands

```bash
S="${CLAUDE_SKILL_DIR}"; E="$S/assets/examples/en-rucklidge-euler-matlab"; mkdir -p work
uv run "$S/scripts/vottp_docx.py" inspect "$E/draft.docx" --out work/inspect.json   # same indices as roles.json
uv run "$S/scripts/vottp_docx.py" format "$E/draft.docx" --roles "$E/roles.json" --out work/paper.docx
uv run "$S/scripts/vottp_docx.py" check work/paper.docx --roles "$E/roles.json" --original "$E/draft.docx" --out work/layout-report.json
```

`layout-report.json` is identical to what these commands produce, and `paper.docx` has the same
`word/document.xml` (canonical XML; the zip bytes may differ).
`roles.json` carries the draft's SHA-256, so it only matches this exact `draft.docx`.

## What it demonstrates

- **Front matter, language order.** English body: UDC, authors (name / affiliation / ORCID /
  e-mail), English title, English abstract and keywords, then Ukrainian authors, title,
  abstract and keywords. Roles: `udc`, `author`, `affiliation`, `contact`, `title`,
  `abstract-en`, `keywords-en`, then `author`, `affiliation`, `title`, `abstract-uk`,
  `keywords-uk`. Each name line is `author`, ORCID and e-mail lines are `contact`.
- **Body.** Thirteen uppercase headings (`heading`) covering the five required functions
  (problem statement, analysis of research, aim, main material, conclusions and future work)
  plus method/result/limitation sections; a 3-item list is a Word `List Number` paragraph
  with role `body`.
- **Equations.** Two displayed systems (1) and (2) are native OMML (`m:eqArr`, `m:sSub`,
  `m:sSup`) with the number as a right-tab run in the same paragraph; role `equation`.
  The preservation check confirms the math XML is untouched. Inline symbols such as
  `Kₜ`, `Δt` stay Unicode text, as printed.
- **Tables.** Eight tables, each as `table-label` ("Table N", right) + `table-title`
  (bold, centred) + cells (`table`). Table 3 has multi-line cells; Table 6 has two-line
  headers. Column widths are set in the draft and preserved.
- **Figures.** Five `figure` paragraphs (image only) each followed by a `figure-caption`.
- **References.** One heading `References` (`reference-heading`) and 20 `reference`
  paragraphs whose numbers "1." ... "20." are typed text, kept as printed.

## Genuine properties of the published paper (lessons, not tool bugs)

- **Length (F04).** Published 11 pages for 2 authors (minimum 8, maximum 16). Rendered in
  LibreOffice 26.2.3.2 with Times New Roman: guide profile 14 pages, `--profile published`
  11 pages. Both are inside the limits; page count still has to be rendered, not inferred.
- **Cross-reference defects in the text.** Fig. 4 is never cited; the sentence about the
  dependence on q says "Fig. 5" where Fig. 4 is meant. "Results are listed in." ends
  without "Table 5". One sentence reads "Due to NVIDIA CUDA Compiler (NVCC) can contract
  operations - separate arithmetic tests were required." These are kept verbatim: report
  them to the author, do not silently repair them.
- **Bibliography.** A single list titled `References` (no separate Ukrainian-language list
  and no duplicate Latin list); sources 4 and 5 are Ukrainian-origin works listed with
  English titles. All 20 entries are cited, in order of first citation (ranges such as
  [6, 7], [8-10]). Entries 4 and 5 are by a co-author (2 of 20, self-citation to report).
  Several entries are web documentation without access dates.
- **Result support.** Table 5 values marked "median of maximum worker time" are
  critical-path estimates and the text says so; the paper also states the unequal
  evidence (two runs only for two MEX rows). Compare abstract claims with the labelled
  scopes before approving them. No table cell is empty.
- **Abstracts.** The English abstract is 1816 characters, the Ukrainian one 2148, so both
  meet the provisional ~1800 target (M04), unlike the Ukrainian example.

## Formatting observations from rendering the output

- Page 1 ends after the Ukrainian name line: the long Ukrainian abstract is kept together
  and moves to page 2, leaving white space (the helper sets keep-lines on every paragraph).
- Tables 4 and 5 break across pages, and the header row is not repeated. Fixing that
  needs a document editor (repeat-header / keep-together), not the helper.
- The two displayed equations render correctly in LibreOffice.

## Fidelity gaps of this reconstruction

- Text comes from the PDF text layer; every non-equation paragraph and table cell was
  verified to occur verbatim in the PDF (whitespace-insensitive). Tables were retyped from
  the PDF and checked word-for-word against it. Figures are the original embedded bitmaps
  (lossless PNG). The publisher's running header and footer, DOI line, received/accepted
  dates, licence strip and copyright line are omitted, as an author would not have them.
- Equations were rebuilt as OMML from the printed linear forms (fractions are `dx/dτ`
  as printed). The authors' actual Word source is not available.
- The original page layout (spacing, fonts, Tahoma abstracts) is not reproduced; the
  draft is deliberately unformatted so the helper has something to do.
