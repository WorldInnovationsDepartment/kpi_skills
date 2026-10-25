---
name: axioms-paper-format
description: Formats and checks a mathematics paper for submission to the MDPI journal Axioms (mdpi.com/journal/axioms, ISSN 2075-1680) on the official MDPI LaTeX class (Definitions/mdpi.cls, option axioms). It ports a LaTeX (amsart/article/elsarticle) or Word/Markdown draft to the template, mapping theorem environments to the class ones (Theorem, Lemma, ...) with global numbering. It fills the front matter (Title Case title, authors with affiliations and e-mails, a one-paragraph abstract of about 200 words, 3-10 keywords, MSC2020 codes) and the back matter (CRediT contributions, funding, data availability, conflicts of interest, GenAI disclosure) in MDPI wording, and converts references to MDPI/ACS style with ISO 4 abbreviations and DOIs. It produces a rule-by-rule compliance report, the compiled PDF, the SuSy zip and a cover letter. Use when the user wants a paper/article/manuscript formatted, prepared, checked or converted for Axioms or "the MDPI Axioms journal", including revisions. Never invents results, references, DOIs, ORCIDs, MSC codes or statements.
---

# Axioms (MDPI) paper formatter

Turns a draft into a submission-ready LaTeX manuscript for **Axioms** (MDPI) on the official
class, and reports every requirement it does not yet meet.

Pipeline: **intake → `import_source.py` → content pass on `paper.tex` → `check_paper.py` →
`build_paper.py` (compile) → `render_preview.py` → fix, re-check → `build_paper.py --zip` →
deliver**.

Requirements:

1. `uv`. All scripts are PEP 723 and fetch their own dependencies (pypandoc_binary for Word or
   Markdown input, PyMuPDF and Pillow for checks and previews).
2. A TeX engine for compiling: latexmk/pdflatex (TeX Live, MacTeX) or `tectonic`. Without one,
   everything except compiling still works. Then the user compiles on Overleaf (see
   `references/latex-conversion.md`), and you say the PDF checks were not run.

References, loaded on demand:

1. `references/requirements.md`: every journal rule with its source and the rule code that
   `check_paper.py` reports, including the conflicts between guide, template and practice.
   Read it before the content pass.
2. `references/published-papers-review.md`: three Axioms 15(11) papers (algebra, PDE,
   statistics). It shows what accepted papers look like and what varies between them.
3. `references/reference-style.md`: MDPI/ACS references, citation rules, ISO 4 abbreviations
   and DOIs.
4. `references/latex-conversion.md`: what the importer maps, what to finish by hand, typical
   compile errors, and Overleaf.
5. Assets:
   1. `assets/mdpi-template/`: the official MDPI template (`template.tex`, `template.pdf`,
      `Definitions/` with `mdpi.cls` v6.5d) and the Axioms Word template `.dot`.
   2. `assets/example/`: a complete Axioms manuscript (`paper.tex`, `references.bib`,
      `fig1.png`). It passes the checker with 0 errors and 0 warnings; copy patterns from it.
   3. `assets/cover-letter.md`: the cover letter with the two required sentences.

Work in a folder of the user's choice (e.g. `./axioms-submission/`), never inside this skill
directory.

## 1. Intake

1. **LaTeX draft** (the usual case for Axioms):

   ```bash
   uv run "${CLAUDE_SKILL_DIR}/scripts/import_source.py" draft.tex --out axioms-submission
   ```

   This flattens `\input`, maps the theorem environments, and moves the title, authors,
   abstract, keywords, `\subjclass`, acknowledgments, funding, COI, data, bibliography and
   appendix into MDPI places. It copies `Definitions/`, the `.bib` files and the figures, and
   writes `import-report.md`. **Read the report and the whole `paper.tex`.**
2. **Word, ODT or Markdown draft**: the same command. Pandoc converts the body, and you rebuild
   theorems, tables, captions and cross-references (`latex-conversion.md` items 6-9). Equations
   in a Word draft must be Equation Editor or MathType objects, not images. If they are images,
   tell the user they must be retyped.
3. **PDF only**: ask for the source. If the user has none, retype the paper into a skeleton:
   `import_source.py --new --out axioms-submission --authors N`.
4. Ask the user **in one message** for everything that blocks a correct file and is not in
   the draft:
   1. the corresponding author(s), and every author's e-mail and ORCID;
   2. full first names and affiliations as department, institution, city with postcode, country;
   3. the **MSC2020 codes**. You may *suggest* codes from the topic, but the author confirms
      them;
   4. funding, with funder and grant number, or none;
   5. the CRediT contributions of each author;
   6. the data or code situation (purely theoretical, or data and code somewhere);
   7. whether generative AI was used beyond language editing;
   8. the article type (Article, Review, Communication) and the target section or Special Issue,
      if any.

   Everything else goes ahead, with a visible `TODO` in `paper.tex`.

## 2. Content pass (edit `paper.tex`)

Work through `references/requirements.md` §3-8:

1. **Front matter.**
   1. Put the title in Title Case, without abbreviations or a final period.
   2. Write `\Author` with full names, superscripts and `*`, and repeat the names in
      `\AuthorNames`.
   3. `\address`: one line per affiliation, with an e-mail for every author.
   4. `\corres` and the ORCID lines (`\newcommand{\orcidauthorA}{...}` + `\orcidA{}`).
2. **Abstract.** One paragraph of at most about 200 words covering background, method, main
   result and significance. No citations and no display math; define abbreviations. If the
   draft's abstract is longer, condense it **from the paper's own statements** and show the user
   the new version.
3. **Keywords** (3-10, separated by semicolons) and **`\MSC{...}`** (codes separated by
   semicolons, without Primary/Secondary).
4. **Structure.** Use Introduction, Preliminaries, main-result sections, optional examples or
   applications, then Conclusions, as Axioms papers do. The Introduction ends with the outline
   paragraph ("The rest of this paper is organized as follows. ..."). Recommend Conclusions
   (summary, significance, open problems), but do not invent its content: condense the author's
   own claims, or leave a `TODO` and ask.
5. **Mathematics.**
   1. Use the class environments `Theorem`, `Lemma`, `Corollary`, `Proposition`, `Definition`,
      `Remark`, `Example`, ...; cross-references with `\label`/`\ref`/`\eqref`.
   2. Numbering is global (Theorem 1, equation (1)), so replace hard-coded "Theorem 2.3".
   3. Proofs use `\begin{proof}` (or `[Proof of Theorem~\ref{...}]`). Attribute cited results
      as `\begin{Lemma}[\cite{key}, Lemma 1.3]`.
   4. Punctuate displays, and write "where" in lower case after them.
6. **Floats.** Each needs a caption (below figures, above tables), a label and a mention in
   the text. Tables use booktabs with no vertical rules. Figures are vector PDF or raster at
   600 dpi or more at the printed size.
7. **References.**
   1. Prefer BibTeX with `\bibliography{references}`. The class applies `mdpi.bst`.
   2. Put the ISO 4 abbreviation in `journal`, and add a `doi` field after **verifying** it
      (doi.org or api.crossref.org). Never fabricate a DOI, page or year.
   3. In the text: "Ref.~\cite{x} proves", and `\cite{x} (p.~5)` rather than `\cite[p.~5]{x}`.
   4. An inline `thebibliography` must follow first-citation order.
8. **Back matter**, in MDPI order and with the standard wording (`requirements.md` §8):
   1. `\authorcontributions`: CRediT roles with initials, ending with "All authors have read and
      agreed to the published version of the manuscript.";
   2. `\funding`;
   3. `\institutionalreview` and `\informedconsent` as "Not applicable." (or delete both);
   4. `\dataavailability`: for pure theory, "No new data were created or analyzed in this study.
      Data sharing is not applicable to this article.";
   5. `\acknowledgments`, including the GenAI disclosure sentence if AI was used beyond editing;
   6. `\conflictsofinterest`: "The authors declare no conflicts of interest."

   Write a statement only with the user's answer. Otherwise keep the `TODO`.

## 3. Check, compile, look

```bash
S="${CLAUDE_SKILL_DIR}/scripts"
uv run "$S/check_paper.py" paper.tex                               # source, .bib, figures
uv run "$S/build_paper.py" paper.tex                               # -> paper.pdf, paper.log
uv run "$S/check_paper.py" paper.tex --log paper.log --pdf paper.pdf
uv run "$S/render_preview.py" paper.pdf --out preview
```

1. `check_paper.py` prints `ERROR` (a requirement is violated or compilation will break),
   `WARN` (an MDPI guideline, or a likely problem) and `INFO` (reminders), then `SUMMARY`. It
   exits 1 on any ERROR. Each rule code is explained in `requirements.md`.
2. `build_paper.py` uses latexmk, then pdflatex+bibtex, then tectonic. Exit 3 means no engine
   was found: tell the user, offer Overleaf, and continue with `--zip --no-compile`.
3. Open `preview/contact-sheet.png`, then the pages that look suspicious. Compare page 1 with
   `assets/mdpi-template/template.pdf`. Check:
   1. the title, authors and affiliations block;
   2. Abstract / Keywords / MSC;
   3. that no line sticks into the margin;
   4. theorem heads in bold with italic bodies, and QED boxes;
   5. figure and table captions;
   6. reference formatting (bold year, italic volume);
   7. that no `??` or `TODO` is left.
4. Loop until there are 0 ERRORs and every WARN is fixed or consciously accepted, with the
   reason given to the user.

## 4. Package and deliver

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/build_paper.py" paper.tex --zip      # -> submission.zip
```

Fill `assets/cover-letter.md` as `cover-letter.md` in the working folder. Then report:

1. the absolute paths of `paper.tex`, `paper.pdf`, `submission.zip` and `cover-letter.md`;
2. the page count and the `check_paper.py` summary, with each remaining WARN and why it was
   accepted;
3. every `TODO` still open (ORCIDs, e-mails, statements, unverified DOIs, MSC confirmation);
4. every place where you wrote or condensed text that the author must review (the abstract,
   the outline paragraph, the conclusions, translated or edited sentences);
5. the SuSy checklist:
   1. upload the zip together with the PDF;
   2. paste the cover letter;
   3. enter 3 suggested reviewers (other institutions, no joint papers in the last 3 years);
   4. declare GenAI use if any;
   5. choose the section or Special Issue;
   6. note that the APC is CHF 2400 on acceptance.

## Revisions

1. Edit `paper.tex`, then re-run the check, the compile and the zip. MDPI expects the revision
   in the template, with changes highlighted. Either use `latexdiff old.tex paper.tex >
   diff.tex` and compile it, or mark the changes in colour, as the editor asks.
2. Draft the point-by-point response: each reviewer comment, the answer, and where the text
   changed (section, line, equation number).

## Rules

1. Never invent data, results, proofs, authors, affiliations, e-mails, ORCIDs, MSC codes,
   references, DOIs, page numbers or ethics, funding or AI statements. Use `TODO` and report it.
2. The layout belongs to `Definitions/mdpi.cls`. Do not add `geometry`, fonts, `\linespread`,
   running heads or manual title blocks, and do not edit the MDPI internal commands.
3. Keep the author's mathematics and voice. Structural and language edits are proposals, and
   they are listed at delivery.
4. If the live MDPI pages or a newer template differ from `references/requirements.md` (checked
   on 2026-10-25), the site wins. Tell the user, and update the reference, `check_paper.py`, the
   bundled `Definitions/` and the tests together.
