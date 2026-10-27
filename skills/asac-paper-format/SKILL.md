---
name: asac-paper-format
description: Formats and checks a research paper for submission to the KPI journal «Адаптивні системи автоматичного управління» (Adaptive Systems of Automatic Control, ASAC, asac.kpi.ua, ISSN 1560-8956), producing the .docx the editors require (A4, 25 mm margins, Times New Roman 13, spacing 1.3, UDC/authors/TITLE block, numbered native Word equations, "Figure N."/"Table N." captions, DSTU 8302:2015 references, UA+EN structured abstracts, keywords and author info on separate end pages) plus a requirement-by-requirement compliance report. Use when the user wants a paper/article/стаття formatted, prepared, checked or converted for ASAC, "Адаптивні системи автоматичного управління", asac.kpi.ua, or "the KPI adaptive control journal", from a .docx/.tex/.md draft or pasted text, including revised resubmissions. Never invents data, ORCIDs, DOIs, references or results.
---

# ASAC paper formatter

Turns a draft into a submission-ready `.docx` for **«Адаптивні системи автоматичного
управління»** (asac.kpi.ua), and reports every requirement the paper does not yet meet.

Pipeline: **intake → `paper.md` (Markdown + YAML) → content pass → `build_paper.py` →
`render_preview.py` → `check_paper.py` → fix, rebuild, re-check → deliver**.

Requirements:

1. `uv`. All scripts are PEP 723 and fetch their own dependencies (python-docx, PyYAML,
   pypandoc_binary, which bundles pandoc, and PyMuPDF).
2. LibreOffice (`soffice`) only for `render_preview.py` (the page count and visual
   check). Without it, build and check still work. Then say the page count is an
   estimate.

References, loaded on demand:

1. `references/requirements.md`: every journal rule with its source, and the rule code
   that `check_paper.py` reports. Read it before the content pass.
2. `references/manuscript-format.md`: the `paper.md` field and syntax reference.
3. `references/reference-style.md`: DSTU 8302:2015 in the journal's form, with templates.
4. `references/published-papers-review.md`: what recent accepted papers look like and
   where they deviate.
5. `assets/official/sample_eng.docx`, `assets/official/sample_ua.docx`: the journal's own
   templates. `assets/example/paper.md`: a complete worked source to copy (fictional
   authors and numbers, so every field is filled).
6. `assets/examples/`: two REAL published papers of the journal (2026, CC BY-NC-SA 4.0)
   converted to `paper.md`, each with a `README.md` (source, DOI, licence, fidelity gaps,
   what the checker reports):
   1. `en-software-cost-fuzzy/`: English, equations, one figure, DSTU-like references;
   2. `uk-google-classroom-export/`: Ukrainian, four figures, one table.

   Read one to see how an accepted paper is laid out (an English one for `language: en`,
   the Ukrainian one for `uk`, figure/table cross-references, short abstracts). They are
   not templates: their e-mails, English fields or Ukrainian keywords are `TODO` because
   the journal does not publish them, and their checker findings (short abstracts, few
   references) are real flaws of accepted papers, not targets to copy. For a new paper
   start from `assets/example/paper.md`.

Work in a directory of the user's choice (e.g. `./asac-submission/`), never inside this
skill directory. Keep `paper.md`, images, the output `.docx` and `preview/` there.

## 1. Intake

1. **Existing file** (.docx, .odt, .tex, .md, .rtf, .html):

   ```bash
   uv run "${CLAUDE_SKILL_DIR}/scripts/import_source.py" draft.docx --out asac-submission/paper.md
   ```

   This converts the file, keeping equations as LaTeX and images in `media/`. It moves
   the reference list into `references:`, picks up the UDC, abstract and keywords where
   it can, and writes `TODO` in every field it could not fill. **Read the whole result**
   and finish the structure by hand: put the title in `title_*`, remove the title,
   author lines and any end-matter leftovers from the body, and restructure the
   abstract.
2. **PDF only**: ask for the source file. If the user cannot provide it, read the PDF
   and retype it into `paper.md`.
3. **Pasted text or notes**: start from `cp "${CLAUDE_SKILL_DIR}/assets/example/paper.md"
   paper.md` and replace everything. Use the fictional
   example as the template, never the real ones.
4. Ask only for what blocks a correct file and cannot be found in the material:
   1. ORCID, e-mail, position and degree of each author;
   2. the corresponding author's phone;
   3. the UDC code. You may *suggest* one from the topic, but the author confirms it;
   4. the article language, if unclear.

   Ask for all of these in one message. Everything else goes ahead with a visible
   `TODO`, and the user gets a list of what is still missing.

## 2. Content pass (edit `paper.md`)

Work through `references/requirements.md` §2-4. Concretely:

1. **Sections**: map the draft onto Introduction, Materials and methods, Results,
   Discussion and Conclusions (UA: Вступ, Матеріали і методи, Результати, Обговорення,
   Висновки). Rename or merge headings. Do not invent content to fill a missing
   section. Flag it instead. A review article needs a disclosure statement.
2. **Introduction**: it must end with the problem statement or the aim, and must contain
   no figures or tables. Move any floats to a later section.
3. **Conclusions**: 5-10 sentences: what is new, why it is better, its significance, and
   future research. Condense the author's own statements. Never add claims.
4. **Abstracts**: 200-250 words and ≤ 1800 characters each, in five parts (problem,
   purpose, methods, results, conclusions). Write them from the paper's own content.
   Translating between Ukrainian and English is expected, but tell the user the
   translation needs their review. Avoid abbreviations and use no citations.
5. **Keywords**: 5-10 phrases in each language that match each other and add to the
   title.
6. **References**: convert every entry to DSTU 8302:2015 (`reference-style.md`). Order
   the list by first citation and renumber every `[n]` in the body in the same pass. Add
   DOIs only after verifying them (doi.org / Crossref). Never fabricate an entry, a DOI,
   pages or a year. Remove unpublished data and personal communications from the list.
7. **Figures and tables**: one caption each, without the number (the builder adds it). A
   mention in the text must come before each one. Formulas must be `$$...$$`, not
   images.
8. **Length**: the article must be 5-10 pages (≤ 15 with editorial consent). Do not pad
   or cut the science to fit. Report the length and let the author decide.

## 3. Build, render, check

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/build_paper.py" paper.md --out paper.docx --verbose
uv run "${CLAUDE_SKILL_DIR}/scripts/render_preview.py" paper.docx --out preview
uv run "${CLAUDE_SKILL_DIR}/scripts/check_paper.py" paper.md --docx paper.docx --pdf preview/paper.pdf
```

1. `build_paper.py` is all-or-nothing. `error: ...` means nothing was written, so fix
   `paper.md` and rerun. `--verbose` lists each numbered figure, table and equation.
   Compare that list with the text.
2. `check_paper.py` prints `ERROR` (a stated requirement is violated), `WARN` (a guide
   recommendation or likely problem) and `INFO` (reminders), then a `SUMMARY` line. It
   exits 1 on any ERROR.
3. Open `preview/contact-sheet.png`, then any suspicious `preview/page-NN.png`. Check:
   1. the title block matches the sample;
   2. equations are numbered and the "where" line sits flush left;
   3. captions and the figure size are right;
   4. tables are ruled and not split awkwardly;
   5. the end matter starts on new pages;
   6. no `TODO` or stray markup remains.
4. Loop until there are no ERRORs, and every WARN is either fixed or consciously
   accepted with the reason given to the user.

Do not hand-edit the generated `.docx`. Change `paper.md` (or the builder) and rebuild,
so that the source and the file never diverge.

## 4. Deliver

Report:

1. the absolute path of `paper.docx`;
2. the page count of the article part, plus the end-matter pages;
3. the `check_paper.py` summary, with each remaining WARN and why it was accepted;
4. every placeholder still to be filled (ORCID, phone, `year`/`issue`, unverified DOIs);
5. every place where you wrote or translated text that the author must review (the
   abstracts, the translated title, keywords and conclusions);
6. the submission checklist:
   1. upload the `.docx` through asac.kpi.ua (PDF is not accepted);
   2. attach the expert-commission act (акт експертизи, for authors from Ukraine);
   3. attach permissions for any borrowed figures or tables;
   4. state funding and conflicts of interest;
   5. confirm the work is original and unpublished, and approved by the co-authors and
      the institution;
   6. declare any generative-AI use in Materials and methods (language editing is
      exempt).

## Revisions (resubmission after review)

1. Rebuild from the updated `paper.md`.
2. Produce a copy with marked changes. Either let the author use Word's *Compare
   Documents* on the old and new `.docx`, or show the main changes in the response
   letter.
3. Draft a point-by-point response letter: each reviewer comment, then the answer and
   where the text changed.

## Rules

1. Never invent data, results, authors, affiliations, ORCIDs, DOIs, references or page
   numbers. Use `TODO` and report it.
2. The fixed layout lives in `build_paper.py` and must match
   `assets/official/sample_*.docx`. Do not tweak fonts or spacing per paper. If the
   journal changes its template, update `build_paper.py`, `references/requirements.md`
   and the tests together.
3. Add no running header, footer, page numbers or "©" line. The editors add these.
4. Keep the author's scientific content and voice. Edits for structure, length or
   language are proposals, and must be listed at delivery.
5. If the journal site shows different rules from `references/requirements.md` (dated
   2026-10-23), the site wins. Tell the user, and update the reference.
