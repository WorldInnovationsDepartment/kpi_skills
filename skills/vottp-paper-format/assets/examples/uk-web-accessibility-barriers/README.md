# Worked example: Ukrainian research article, three authors, two institutions

A reconstructed **author draft** of a published VOTTP paper, taken through the skill
pipeline. Read it when the manuscript is in Ukrainian, has several authors with different
affiliations, figures but no tables or equations, and two reference lists.

## Source and licence

- Січко Т., Афанасьєва Д., Частоколенко І. "Системний аналіз бар'єрів доступності
  вебресурсів на основі аналітики даних" (Sichko T., Afanasieva D., Chastokolenko I.,
  "Systemic analysis of web accessibility barriers based on data analytics").
  *Measuring and computing devices in technological processes* 2026, No. 3 (issue 87),
  pp. 8-15 (8 pages, 3 authors).
- DOI: [10.31891/2219-9365-2026-87-1](https://doi.org/10.31891/2219-9365-2026-87-1)
- Article page: <https://vottp.khmnu.edu.ua/index.php/vottp/article/view/975>;
  PDF: <https://vottp.khmnu.edu.ua/index.php/vottp/article/download/975/896>
- Licence: **CC BY 4.0** (article page and the licence strip on page 1 of the PDF; checked
  2026-10-26). Copyright (c) 2026 the authors. This example reproduces text and figures
  under that licence; attribution is the paragraph above. It is a layout reconstruction,
  not the authors' real submission file; cite the published article.

## Files

| File | What it is |
|---|---|
| `draft.docx` | Plain author-style manuscript: Word default template (Letter page, default margins), Times New Roman 12, bold paragraphs as headings, three inline PNG figures (59-102 KB each). |
| `roles.json` | The `inspect` inventory with every paragraph's role set (105 paragraphs). |
| `paper.docx` | Output of `format` (default guide profile). |
| `layout-report.json` | Output of `check`: 0 errors, only F04 NOT VERIFIED. |

## Commands

```bash
S="${CLAUDE_SKILL_DIR}"; E="$S/assets/examples/uk-web-accessibility-barriers"; mkdir -p work
uv run "$S/scripts/vottp_docx.py" inspect "$E/draft.docx" --out work/inspect.json   # same indices as roles.json
uv run "$S/scripts/vottp_docx.py" format "$E/draft.docx" --roles "$E/roles.json" --out work/paper.docx
uv run "$S/scripts/vottp_docx.py" check work/paper.docx --roles "$E/roles.json" --original "$E/draft.docx" --out work/layout-report.json
```

`layout-report.json` is identical to what these commands produce, and `paper.docx` has the same
`word/document.xml` (canonical XML; the zip bytes may differ).
`roles.json` carries the draft's SHA-256, so it only matches this exact `draft.docx`.

## What it demonstrates

- **Front matter, language order.** Ukrainian body: UDC, three authors (each `author` +
  `affiliation` + `contact` lines for ORCID and e-mail; the third author's two-line
  affiliation is one `affiliation` paragraph), Ukrainian title, `abstract-uk`,
  `keywords-uk`, then the English names/affiliations, English title, `abstract-en` (four
  paragraphs) and `keywords-en`.
- **Body.** Five Ukrainian uppercase headings that map to the five required functions
  (problem statement, analysis of research, aim, main material, conclusions and
  prospects); a four-item POUR list as `List Number` paragraphs with role `body`.
- **Figures.** Three dashboard screenshots (`figure`) with captions "Рис. N. ..."
  (`figure-caption`), cited in the text as "рис. 1" ... "рис. 3".
- **Two reference lists.** `Література` (original-language list) and `References` (Latin
  list), each a `reference-heading` followed by 11 `reference` paragraphs with typed numbers.

## Genuine properties of the published paper (lessons, not tool bugs)

- **Length (F04).** Published 8 pages for 3 authors. The conservative reading
  `6 + 2 x (authors - 1)` needs 10, so the published paper itself falls short (conflict
  X07 in requirements.md). The formatted guide-profile draft renders to 10 pages in
  LibreOffice 26.2.3.2 (9 with `--profile published`): the 10 pt, 1.3 spacing rule alone
  makes it longer than the published PDF, which is not evidence of more content.
- **Unequal abstracts.** The Ukrainian abstract is 744 characters, the English one 2204;
  the checker only warns when English is short, so compare the two by hand (M03/M04).
  Authors' contact lines are in the Ukrainian block only.
- **Bibliography.** Only references 1-7 are cited in the text; 8-11 are listed but never
  cited, and citations 1-7 are in first-mention order. References 9, 10 and 11 are all by
  the first author (3 of 11), a self-citation share to flag. Reference 1 has no author or
  year; reference 5 has an access date in `References` but not in `Література`. The
  Latin list repeats the same eleven sources, so for sources already in Latin script it
  is redundant (flag, do not delete).
- **No tables, no formulas.** C03 table-completeness and equation checks are vacuous
  here; the evidence is three Power BI dashboard images, read by the text rather than by
  tables of numbers. Verify that numbers quoted in the prose (for example 73 libraries,
  mean AIM score 6.41, 95.1 %, 54.8 errors per page) appear in the figures or sources.
- Language: the paper writes decimals with a dot ("6.41") in Ukrainian text while the
  abstract uses a comma elsewhere ("2,2 мільярда"); a language editor would normalise it.

## Formatting observations from rendering the output

- Page 1 ends after the English abstract's second paragraph: the helper's keep-lines
  setting moves the next long paragraph to page 2 and leaves white space.
- The last page holds only references 9-11.

## Fidelity gaps of this reconstruction

- Text comes from the PDF text layer; every paragraph was verified to occur verbatim in
  the PDF (whitespace-insensitive). Figures are the original embedded bitmaps (lossless
  PNG). The running header and footer, DOI line, received/accepted dates, licence strip
  and copyright line are omitted, as an author would not have them.
- The numbered list is Word auto-numbering (numbers not in the text). The authors' actual
  Word source is not available; the original page layout is not reproduced.
