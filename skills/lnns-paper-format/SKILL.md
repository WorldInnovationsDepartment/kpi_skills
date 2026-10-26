---
name: lnns-paper-format
description: Formats and checks a research paper for Springer's book series "Lecture Notes in Networks and Systems" (LNNS, ISSN 2367-3370, link.springer.com/bookseries/15179), producing a submission in Springer's proceedings template (llncs) as a Word .docx in the splnproc layout (122 x 193 mm text area, Times 10 pt, 14 pt title, numbered 1 / 1.1 headings and run-in level 3/4, bold "Fig. N." below figures and "Table N." above tables, numbered equations, Acknowledgments + mandatory Disclosure of Interests, splncs04 references) and/or a ready-to-compile llncs LaTeX project (Overleaf), plus a rule-by-rule compliance report (abstract 150-250 words, keywords, title case, ORCID, one corresponding author, citations, DOIs, alt text, figure resolution, conference page limit, Type 3 fonts). Use when the user wants a paper/article/стаття formatted, prepared, checked or converted for LNNS, "Lecture Notes in Networks and Systems", a Springer LNNS conference, the llncs/LNCS-style proceedings template, or springerprofessional.de's LNNS page, from a .docx/.tex/.md draft or pasted text, including camera-ready versions. Never invents data, ORCIDs, DOIs, references or results.
---

# LNNS paper formatter

Turns a draft into a camera-ready paper for **Lecture Notes in Networks and Systems**, using
Springer's proceedings template (llncs). It also reports every requirement the paper does not yet
meet.

Pipeline: **intake → `paper.md` (Markdown + YAML) → content pass → `build_paper.py` (.docx and/or
LaTeX) → `render_preview.py` → `check_paper.py` → fix, rebuild, re-check → deliver**.

Requirements:

1. `uv`. All scripts are PEP 723 and fetch their own dependencies (python-docx, PyYAML, PyMuPDF,
   Pillow, and pypandoc_binary, which bundles pandoc).
2. LibreOffice (`soffice`), optional: needed only to render the .docx to a PDF for the page count
   and the visual check.
3. A TeX engine (`latexmk`/`pdflatex`/`tectonic`), optional: needed only for `--compile`. Without
   one, the LaTeX folder is uploaded to Overleaf as is.

References, loaded on demand:

1. `references/requirements.md`: every Springer/LNNS rule with its source and the rule code that
   `check_paper.py` reports. Read it before the content pass.
2. `references/manuscript-format.md`: the `paper.md` field and syntax reference.
3. `references/reference-style.md`: the splncs04 reference style, with templates and conversions.
4. `references/published-papers-review.md`: three recent LNNS papers, what is enforced in
   practice and what is not.
5. `assets/example/paper.md`: a complete worked source to copy (fictional content, every feature).
   `assets/examples/en-ils-simulator-review/`: a real open-access LNNS chapter (CC BY 4.0, llncs
   layout, 11 pages) converted to `paper.md`, with its figure and a README on source, licence and
   known checker findings.
6. `assets/latex/`: llncs.cls and splncs04.bst (CTAN, CC BY 4.0).

Work in a directory of the user's choice (e.g. `./lnns-submission/`), never inside this skill
directory.

## 1. Intake

1. **Conference first.** LNNS page limits, deadlines and sometimes the citation style come from
   the conference, not from Springer. Ask for the call-for-papers link or these details:
   1. the page limit (min/max, and whether references count);
   2. Word or LaTeX;
   3. citation style if the call specifies one;
   4. whether the volume uses llncs. A few, like ICICT from Springer Singapore, use the svmult
      chapter layout, which this skill does not build.

   Put the answers in `conference:`.
2. **Existing file** (.docx, .odt, .tex, .md, .rtf, .html):

   ```bash
   uv run "${CLAUDE_SKILL_DIR}/scripts/import_source.py" draft.docx --out lnns-submission/paper.md
   ```

   1. What it does: converts the file (equations to LaTeX, images to `media/`), strips hand-typed
      heading numbers, moves the reference list, abstract and keywords into the front matter, and
      picks up `\title`, `\keywords`, `thebibliography` and `credits` from an llncs `.tex` file.
      Every field it could not fill is marked `TODO`.
   2. What you do next: **read the whole result**, remove the title, author and affiliation lines
      left in the body, and fill in `authors`/`affiliations`.
3. **PDF only**: ask for the source. If there is none, read the PDF and retype it into `paper.md`.
4. **Pasted text or notes**: `cp "${CLAUDE_SKILL_DIR}/assets/example/paper.md" paper.md`, then
   replace everything.
5. Ask in one message for only the things that block a correct file:
   1. each author's full given name, ORCID and e-mail;
   2. which single author is the corresponding author;
   3. the affiliations with city and country;
   4. the funding and grant numbers;
   5. the competing-interests statement;
   6. whether AI tools were used for writing.

   Everything else goes ahead with a visible `TODO`.

## 2. Content pass (edit `paper.md`)

Work through `references/requirements.md` §3-6. Concretely:

1. **Title**: use title case with no final period. Add `running_title` if the title is longer than
   70 characters.
2. **Abstract**: one paragraph of 150-250 words with no citations or footnotes, covering problem,
   approach, results and significance. Condense the author's own text and never add claims.
3. **Keywords**: 3-6 phrases (the conference may fix the number), each capitalised.
4. **Structure**: Introduction (ending with the aim and contributions), then Related Work, method,
   experiments/evaluation, and Conclusion with an outlook. Rename headings to title case and remove
   their numbers. At most four heading levels. Do not invent missing content; flag it instead.
5. **References**: convert every entry to splncs04 (`reference-style.md`), in the Latin alphabet.
   Then run `renumber_refs.py --order citation|alphabetical` so the list and every `[n]` in the
   body agree. Add a DOI only after verifying it on doi.org or Crossref. Never fabricate an entry, a
   DOI, pages or a year.
6. **Figures and tables**: one caption each, without the number. Mention "Fig. N"/"Table N" before
   each float, and give every figure `alt="..."`. Formulas go in `$$...$$`, never as images, and are
   punctuated like text. Ask for vector or ≥ 300 dpi images (line art 800-1200 dpi) when the checker
   flags resolution.
7. **Credits**: `acknowledgments` (funding with grant number) and the mandatory `disclosure`. Never
   write the competing-interests statement on the author's behalf without asking. Proposing the
   standard "no competing interests" wording for confirmation is fine. If AI was used for writing,
   fill in `ai_disclosure` with the tool, version and date.
8. **Length**: compare with `conference.max_pages` after the first build. Do not pad or cut the
   science to fit. Report the overrun and propose cuts for the author to decide on.

## 3. Build, render, check

```bash
S="${CLAUDE_SKILL_DIR}/scripts"
uv run "$S/build_paper.py" paper.md --docx paper.docx --latex latex/ --verbose   # either or both
uv run "$S/render_preview.py" paper.docx --out preview          # or: latex/paper.pdf after compiling
uv run "$S/check_paper.py" paper.md --docx paper.docx --pdf preview/paper.pdf
```

1. `build_paper.py` is all-or-nothing. `error: ...` means nothing was written. `--verbose` lists
   each numbered section, figure, table and equation, so compare it with the text. `--latex DIR`
   writes `paper.tex`, `llncs.cls`, `splncs04.bst` and the images. Add `--compile` when a TeX
   engine is installed; otherwise tell the user to upload the folder to Overleaf and compile there.
2. `check_paper.py` prints `ERROR` (a stated requirement is violated), `WARN` (a recommendation,
   published practice or a likely problem) and `INFO` (reminders), then a `SUMMARY` line. It exits
   1 on any ERROR. Pass `--pdf` with the PDF that will actually be submitted: Word's own "Save as
   PDF" output or the compiled LaTeX. That run gives the real page count, Type 3 and embedded-font
   checks, and the text-area check.
3. Open `preview/contact-sheet.png`, then any suspicious `preview/page-NN.png`. Check:
   1. the title block (authors, superscripts, (✉), ORCIDs, centred affiliations);
   2. that **Abstract.** and **Keywords:** are indented;
   3. heading numbers and run-in headings;
   4. that equations are numbered at the right margin;
   5. captions (bold labels, figure below, table above) and that tables fit the text width;
   6. that the credits come before the references;
   7. that no `TODO` or stray markup remains.
4. Loop until there are no ERRORs, and every WARN is either fixed or accepted with a reason given
   to the user.

Do not hand-edit the generated `.docx` or `paper.tex`. Change `paper.md` and rebuild, so the
source and the outputs never diverge. If the author must edit the LaTeX later (e.g. after review),
say that `paper.tex` becomes the master from then on.

## 4. Deliver

Report:

1. the absolute paths of `paper.docx` and/or `latex/paper.tex` (and the PDF);
2. the page count against the conference limit;
3. the `check_paper.py` summary, with every remaining WARN and why it was accepted;
4. every placeholder still to be filled (ORCIDs, e-mails, unverified DOIs, the disclosure wording);
5. every place where you wrote or condensed text that the author must review (the abstract,
   keywords, any shortened sections);
6. the camera-ready checklist:
   1. source files (.docx without macros, or .tex + .bib/.bbl + images) plus a PDF identical to
      them, with short file names such as `Surname_ShortTitle`;
   2. the Licence to Publish, signed **by hand** by the corresponding author for all authors (no
      changes to authorship after submission);
   3. alt text for all figures (in the source, or as an Excel list for Word);
   4. permissions for third-party material;
   5. that colour figures are readable in greyscale;
   6. registration and presentation as the conference requires.

## Rules

1. Never invent data, results, authors, affiliations, ORCIDs, DOIs, references, grant numbers or
   competing-interest statements. Use `TODO` and report it.
2. The fixed layout lives in `build_paper.py` and must match Springer's templates. Do not tweak
   fonts, margins or spacing per paper. If Springer changes the template, update `build_paper.py`,
   `references/requirements.md`, `assets/latex/` and the tests together.
3. Add no page numbers, running heads (Word), © lines or colour. Springer adds the first three
   itself.
4. Keep the author's scientific content and voice. Edits for structure, length or language are
   proposals and must be listed at delivery.
5. The conference's instructions override the defaults here (page limit, citation style,
   template copy). If Springer's pages show different rules from `references/requirements.md`
   (captured 2026-10-25), the official page wins. Tell the user and update the reference.
