# Manuscript source format (`paper.md`)

`build_paper.py` and `check_paper.py` read **one Markdown file**. The YAML front matter
holds everything that is not running text, and the Markdown body is the article from
the Introduction to the Conclusions. `assets/example/paper.md` uses every feature. Copy
it rather than starting from scratch.

## Front matter fields

| Field | Required | Notes |
|---|---|---|
| `language` | yes | `en` or `uk`: the language of the article body. Headings, captions ("Figure"/"Рисунок", "Table"/"Таблиця"), "Abstract"/"Анотація", "REFERENCES"/"СПИСОК ВИКОРИСТАНИХ ДЖЕРЕЛ" and the "where"/"де" detection follow it |
| `article_type` | no | `original` (default), `review` or `short`. A review needs a `funding` or `conflict_of_interest` disclosure |
| `udc` | yes | UDC code only, e.g. `"004.852"`. The builder writes "UDC"/"УДК" |
| `title_en`, `title_uk` | yes | Normal case; the builder upper-cases the title block. No atypical abbreviations |
| `authors` | yes | A list, in byline order. See the table below |
| `abstract_en`, `abstract_uk` | yes | A mapping with `problem`, `purpose`, `methods`, `results`, `conclusions` (rendered with the labels Background/Objective/Methods/Results/Conclusions and Проблематика/Мета/Методика реалізації/Результати/Висновки). 200-250 words and ≤ 1800 characters in total. A plain string is accepted but reported as unstructured |
| `abstract_top` | no | Text under the title. Default: the article-language abstract without part labels, as in recent issues. Set a 150-300 character version to follow the official sample literally |
| `keywords_en`, `keywords_uk` | yes | Lists of 5-10 (at most 20) phrases that correspond across the two languages |
| `references` | yes | A list of DSTU 8302:2015 strings in citation order, **without numbers**. `*Italic*` and `**bold**` markup is allowed. See `reference-style.md` |
| `acknowledgements` | no | Rendered under "Acknowledgements"/"Подяки" before the references |
| `funding` | no | Must start with "This work was supported..." / "Ця робота була підтримана...". Rendered under "Disclosure of interests"/"Розкриття інтересів" |
| `conflict_of_interest` | no | Rendered in the same disclosure section |
| `year`, `issue` | no | For the end-matter citation line, e.g. `2026` and `"№ 2 (51)"`. If absent, it shows "20__" and "№ _ (__)" for the editors to fill in |

### Author fields

| Field | Required | Notes |
|---|---|---|
| `surname_en`, `name_en`, `surname_uk`, `name_uk` | yes (build) | Byline "I. Petrenko"/"І. Петренко", citation line "Petrenko I."/"Петренко І.О." |
| `patronymic_uk` | checker WARN | Needed for the full Ukrainian name and the "І.О." initials |
| `orcid` | checker ERROR | `0000-0000-0000-0000` form, mandatory |
| `email` | checker ERROR | |
| `phone` | ERROR for the corresponding author | |
| `corresponding` | one author must have `true` | |
| `position_en`, `position_uk` | checker ERROR | Place of work and position as a full phrase, e.g. "доцент кафедри ... КПІ ім. Ігоря Сікорського" |
| `degree_en`, `degree_uk` | checker WARN | "к.т.н." / "Candidate of Technical Sciences (PhD)"; "аспірант" / "PhD student" |
| `rank_en`, `rank_uk` | no | "доцент" / "Associate Professor" |
| `interests_uk`, `interests_en` | no | "Наукові інтереси" line, as in the sample |
| `scopus_id`, `researcher_id` | no | Only if they exist |

## Body syntax

| Element | Write | Result in .docx |
|---|---|---|
| Section | `# Introduction` | Bold, centred heading. Use the guide's sections: Introduction / Вступ, Materials and methods / Матеріали і методи, Results / Результати, Discussion / Обговорення, Conclusions / Висновки (synonyms are accepted) |
| Sub-section | `## Compared configurations` | Bold, indented heading |
| Paragraph | plain text, blank line between paragraphs | Justified, TNR 13, 1.3, 12.5 mm indent |
| Citation | `[1]`, `[3–5]`, `[2, 7]` | Kept as typed. Number by first appearance |
| Inline math | `$w_i$` | Native Word equation |
| Display formula | `$$ ... $$` on its own lines (LaTeX) | Native Word equation, centred, numbered "(n)" at the right margin. **Every** display formula is numbered; refer to it as "(1)" |
| "where" line | a paragraph right after the formula starting with "where" / "де" | Set flush left, as in the sample |
| Bulleted list | `- item;` | "–" bullets at the paragraph indent |
| Numbered list | `1. item;` | "1." at the paragraph indent |
| Figure | `![Caption without number](fig1.png){width=13cm}` as its own paragraph | Centred image, "*Figure N.* Caption" below. Mention "Fig. N" / "рис. N" in the text **before** it |
| Table | `Table: Caption` line, then a pipe table | "*Table N.*" right-aligned, caption centred, fully ruled table. Mention "Table N" / "табл. N" before it |
| Emphasis | `*italic*`, `**bold**` | As typed |

Do **not** put the Abstract, Keywords, References, author information, UDC or title in
the body. They come from the front matter and are generated in the right places
(`check_paper.py` reports `body.generated` otherwise).

Image paths are relative to `paper.md`. Images wider than the 160 mm text width are
scaled down. Give at least 300 dpi raster images or use vector images exported as
high-resolution PNG.

## What the builder produces, in order

1. UDC / authors / TITLE / *Abstract:* / *Keywords:*
2. The body with numbered figures, tables and equations
3. Acknowledgements and Disclosure of interests (if given)
4. REFERENCES (numbered)
5. *New page:* Ukrainian end matter: УДК, citation line, "Бібл. N, іл. N, табл. N"
   (computed), structured Анотація, Ключові слова
6. *New page:* the same in English
7. *New page:* "Про авторів / About the authors": the title in both languages, then for
   each author the full name in EN and UA with degree, rank and position, research
   interests, ORCID / ScopusID / ResearcherID, e-mail, phone, and the corresponding-author
   mark

It adds no running headers, footers, page numbers or "©" line. The editors add those.
