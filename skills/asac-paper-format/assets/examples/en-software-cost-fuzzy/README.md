# Real example (English): software cost prediction with fuzzy logic

A real, published article of the journal converted into the skill's `paper.md` format.
Use it to see how an accepted English paper maps onto the source format: unstructured
abstract, descriptive section headings, numbered equations, one figure, a DSTU-like
reference list.

## Source and licence

| | |
|---|---|
| Article | M. Stelmashenko, A. Deveciogullari. *Software development cost prediction method* (UA: «Метод прогнозування вартості розробки програмного забезпечення») |
| Journal | «Адаптивні системи автоматичного управління» (Adaptive Systems of Automatic Control), 2026, № 1 (48), pp. 3-10 |
| DOI | 10.20535/1560-8956.48.2026.351874 |
| URL | https://asac.kpi.ua/article/view/351874 |
| Licence | Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (as stated on the article page). © M. Stelmashenko, A. Deveciogullari |
| Authors | M. Stelmashenko (ORCID 0009-0008-8948-3358), A. Deveciogullari (ORCID 0000-0003-2342-8475), NTUU «Igor Sikorsky Kyiv Polytechnic Institute» |
| Retrieved | 2026-10-26 from a Wayback copy of the journal PDF (the live site was unreachable) and the article page |

Attribution: text, formulas, figure and references belong to the authors. They are
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

Taken as printed: title, UDC, authors and their public ORCIDs, the abstract, keywords,
all section text, equations (1)-(4) and the worked example, Figure 1 (re-cropped from the
PDF page), and the eight references (with the "application date" form).

Not published, so left out or marked `TODO` (never invented):

1. author e-mails, phone, the corresponding-author mark, degrees, patronymics and full
   first names (the journal prints initials only: `name_en: "M."`);
2. Ukrainian keywords (the article page lists the English keywords only: `keywords_uk: [TODO]`);
3. department and position (only the university is given).

The Ukrainian title and abstract are the ones on the journal's article page. They are not
part of the PDF.

Conversion choices:

1. the English abstract is one unstructured paragraph (111 words) under both `abstract_en`
   and the title block;
2. the builder numbers every display formula, so the seven worked-example formulas that
   the journal prints unnumbered are numbered (5)-(12) here, and the printed
   multi-line "Substituting" formula is one display;
3. the six numbered module descriptions are written as `1\.` paragraphs (an escaped dot),
   so the bullets and equations between them do not restart a Markdown list;
4. the printed text "the phasing for is similarly performed" has a lost symbol; it is
   kept as printed;
5. the built article part is 9 pages (the journal's typesetting: 8), because the builder
   uses the author-guide layout and the journal re-typesets accepted papers.

## What it demonstrates, and what `check_paper.py` says

Expected result: build succeeds; the checker reports 5 ERRORs, all from unpublished data
(`meta.todo`, `keywords.uk.count`, `authors.corresponding`, `authors.email`), and WARNs
that are genuine properties of the published paper:

1. abstract about 110 words, unstructured (guide: 200-250, five parts);
2. 8 references, 2 from the last five years, 3 web pages (Medium, Wikipedia, GeeksforGeeks), 1 DOI;
3. the Introduction cites nothing and does not end with the aim (it comes in "Literature
   review and problem statement");
4. Conclusions do not mention future research.

Lesson for the agent: a paper can be accepted with these deviations, but they are
exactly what the guide and reviewers can cite. For a user's own paper, fix them or
report them. Do not copy this paper's content.

## Commands

```bash
S=skills/asac-paper-format
uv run $S/scripts/build_paper.py $S/assets/examples/en-software-cost-fuzzy/paper.md --out /tmp/en.docx --verbose
uv run $S/scripts/check_paper.py $S/assets/examples/en-software-cost-fuzzy/paper.md --docx /tmp/en.docx
```
