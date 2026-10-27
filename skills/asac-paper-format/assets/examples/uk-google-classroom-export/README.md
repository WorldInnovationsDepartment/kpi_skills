# Real example (Ukrainian): Google Classroom export to the campus module

A real, published article of the journal converted into the skill's `paper.md` format
with `language: uk`. Use it to see how an accepted Ukrainian paper maps onto the source
format: a short title-block abstract, descriptive headings, four figures, one table, a
three-entry reference list.

## Source and licence

| | |
|---|---|
| Article | К. Мамедова, А. Губський, В. Березін, О. Величко. *Інтеграційне рішення експорту даних Google Classroom у модуль поточного контролю ІАС «Електронний кампус НТУУ «КПІ»* |
| Journal | «Адаптивні системи автоматичного управління», 2026, № 2 (49), pp. 79-84 |
| DOI | 10.20535/1560-8956.49.2026.369473 |
| URL | https://asac.kpi.ua/article/view/369473 |
| Licence | Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (as stated on the article page). © К. Мамедова, А. Губський, В. Березін, О. Величко |
| Authors | NTUU «Київський політехнічний інститут імені Ігоря Сікорського». ORCID: Мамедова 0000-0002-0666-5009, Губський 0000-0002-5361-5485, Березін 0009-0007-0050-7476, Величко 0009-0006-7894-4038 |
| Retrieved | 2026-10-26 from a Wayback copy of the journal PDF (the live site was unreachable) and the article page |

Attribution: text, figures, table and references belong to the authors. They are
reproduced here under the licence above, as a worked example of the format. Do not use the
article as the basis for a submission.

How to comply with CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/):

1. Attribution: keep this README with the files (authors, title, journal, DOI/URL and the
   licence link above), and indicate the changes: the article was converted from the journal
   PDF/page into the skill's `paper.md` source format (typesetting, numbering and some
   metadata changed; figures cropped or re-encoded; `TODO` markers added), as listed below.
2. NonCommercial: do not use this folder commercially.
3. ShareAlike: anything adapted from these files must be released under the same licence
   (CC BY-NC-SA 4.0 or a compatible one). This folder is therefore licensed CC BY-NC-SA 4.0,
   unlike the rest of this skill; do not relicense it and add no further restrictions.
4. No endorsement by the authors or the journal is implied.

## What is faithful and what is not

Taken as printed: title, UDC, the title-block abstract (`abstract_top`), keywords, all
section text, Table 1, the four figures (the PDF's embedded images, 126 dpi, JPEG) and
the three references.

Not published, so left out or marked `TODO` (never invented):

1. English title, English abstract and English keywords (the paper has only Ukrainian
   metadata: `title_en`, `abstract_en`, `keywords_en` are `TODO`);
2. English spelling of the author names (`surname_en`, `name_en`, `position_en`: `TODO`),
   full first names and patronymics (the journal prints initials: `name_uk: "К."`),
   e-mails, phone, corresponding author, degrees, departments and positions.

The longer abstract in `abstract_uk` is the one on the journal's article page. The PDF
prints a different, shorter two-sentence abstract, which is kept as `abstract_top`.

Conversion choices:

1. Table 1 has merged cells in the PDF; the pipe-table format has none, so the entity
   names are repeated in every row;
2. the "Етап 1..5" lines are paragraphs with a bold run-in label;
3. the Ukrainian text keeps the printed typos and grammar;
4. the built article part is 8 pages (the journal's typesetting: 6), because the builder
   uses the author-guide layout.

## What it demonstrates, and what `check_paper.py` says

Expected result: build succeeds; the checker reports 8 ERRORs, all from unpublished data
(`meta.todo`, `keywords.uk.count`, `keywords.en.count`, `authors.corresponding`,
`authors.email` ×4; the 4 UK keywords are also below the guide's 5), and WARNs that are
genuine properties of the published paper:

1. 83-word unstructured abstract (guide: 200-250, five parts);
2. an abbreviation in the title (ІАС);
3. 3 references, none from the last five years, none in DSTU 8302:2015 form;
4. no Materials and methods, Results or Discussion sections;
5. a one-sentence Conclusion without future work;
6. the Introduction is not literature-based and cites nothing.

Lesson for the agent: lenient editorial enforcement does not make these fine for a
user's own paper; report or fix each one. The paper is the reference for figure, table
and cross-reference syntax in Ukrainian ("рис. 1", "таблиця 1", "Рисунок 1."), not for
content quality.

## Commands

```bash
S=skills/asac-paper-format
uv run $S/scripts/build_paper.py $S/assets/examples/uk-google-classroom-export/paper.md --out /tmp/uk.docx --verbose
uv run $S/scripts/check_paper.py $S/assets/examples/uk-google-classroom-export/paper.md --docx /tmp/uk.docx
```
