# Real example: arXiv draft to Axioms (MDPI) manuscript

A published Axioms article, converted the way the skill converts an author's draft:
`draft/` is the arXiv LaTeX source (plain `article` class), `paper.tex` + `references.bib` is the
result on the MDPI class (`Definitions/mdpi.cls`), after `import_source.py` and a content pass.

## Source and licence

| | |
|---|---|
| Paper | Bollati, J.; Olguín, M.; Tarzia, D.A. *Explicit Discrete Solution for Some Optimization Problems and Estimations with Respect to the Exact Solution* |
| Published | *Axioms* **2026**, *15*(3), 190; DOI [10.3390/axioms15030190](https://doi.org/10.3390/axioms15030190); issued 2026-03-05 |
| arXiv | [arXiv:2603.11313](https://arxiv.org/abs/2603.11313) (v1, 2026-03-11; journal ref "Axioms 15 (2026)"); source from `arxiv.org/e-print/2603.11313` |
| Licence | Published version: CC BY 4.0 (Crossref licence metadata, `vor` and `tdm`). arXiv abstract page: CC BY 4.0 |
| Content | Rectangular domain, Poisson equation, six optimal control problems, finite-difference schemes; 22 lemmas with proofs, 12 remarks, 14 figures, 1 table, 22 references; 36 pages on the class |

Attribution: the text, equations, figures and references are by Julieta Bollati, Mariela Olguín and
Domingo A. Tarzia, used under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Changes:
reformatted onto the MDPI class as described below. The layout and wording of the published PDF
were not consulted (mdpi.com blocks automated access), so this is a reconstruction from the arXiv
source, not a copy of the journal PDF. The Definitions/ folder is not duplicated here; copy it from
`../../mdpi-template/Definitions/`.

## What it demonstrates

1. A real draft to Axioms port: `Lemma`/`Remark` environments and `proof` on the class, 52 `$$`
   displays rewritten, `eqnarray` replaced by `align`, an inline `thebibliography` turned into
   `references.bib` with ISO 4 journal abbreviations, a long numbered-equation paper with
   `\eqref` cross-references, figures and one table with captions, `\acknowledgments`.
2. `draft/Bollati-Olguin-Tarzia-Arxiv.tex` (input) next to `paper.tex` (output); `import-report.md`
   is the importer's report on that draft.
3. A checker run on a real manuscript: only the placeholder ERRORs listed below (statements the draft does not contain) plus the genuine warnings.

## Differences from the draft (what the content pass did)

1. `\documentclass[axioms,article,submit,moreauthors]{Definitions/mdpi}` instead of `article` with
   geometry and packages the class already loads.
2. Title block rebuilt (`\Title`, `\Author`, `\address`, `\corres`, `\abstract`, `\keyword`, `\MSC`). The
   draft had the abstract, keywords and "2000 AMS Subject Classification" in the body, which the
   importer cannot find; they were moved by hand. Keywords were lower-cased and separated
   by semicolons. The MSC codes are those of the draft (35C05; 49J20; 49K20; 49M25; 65N15;
   65N30), not re-checked against MSC2020.
3. Affiliations: the draft has three unnumbered lines; they were numbered and given city
   and postcode only where the draft gives them. The e-mail addresses come from a commented-out line of
   the draft. Which author is the corresponding one is not stated in the draft, so no author is
   marked with `*` and `\corres{}` is a TODO placeholder (nothing is guessed).
4. The first display (three systems) was `eqnarray`; it is `align` now (checker rule `math.eqnarray`).
5. The reference list was typed by the authors as `thebibliography`. It is now `references.bib`
   with initials as the authors wrote them (full first names were not invented), no DOIs (the draft has
   none, none were added) and ISO 4 abbreviations that I supplied for the journal names.
6. Comment-only lines were removed. The importer used to leave them as blank lines, which are
   paragraph breaks and broke a display in this paper; `import_source.py` was fixed for this
   (`strip_comment_lines`) while converting it.

## Gaps against the published version

1. **Back matter is not the published wording, and is not invented.** The draft has only an
   Acknowledgments section; its sentence is used verbatim for `\acknowledgments` and, because the
   draft has no separate funding statement, for `\funding` (the facts are the same; "Nº" is set
   with `\textordmasculine`). `\authorcontributions`, `\dataavailability`, `\conflictsofinterest` and
   `\corres` are `TODO` placeholders; the ethics statements are omitted (the checker only informs).
   The authors' real statements must replace the four placeholders.
2. The published text may differ from arXiv v1 (copy editing by MDPI, the reference formatting, the
   figure sizes, equation numbering). I could not compare: no differences are known from
   the metadata, and the arXiv source carries MDPI's copy-editor comments, so it is probably
   the version sent after acceptance.
3. Figures are the PNGs of the arXiv source, with the draft's `scale=0.5`; the figure sizes and
   placement in the journal PDF were not compared.
4. Several PDF-only elements (running header, page numbers, DOI, dates) are generated by the class
   with placeholder values (`\pubvolume{1}`, `\articlenumber{0}`), as in a submission.

## Checker findings that come from the paper

Run on `paper.tex`: 6 errors, 19 warnings, 8 infos. The errors are the placeholders and
nothing else:

1. `front.corresponding`, `front.corres`: no corresponding author is named in the draft.
2. `template.todo` (x4): `\corres`, `\authorcontributions`, `\dataavailability`,
   `\conflictsofinterest` are TODO placeholders.

The warnings are as follows.

1. `abstract.length`: the abstract has 227 words (limit about 200); this is the authors' own text.
2. `bib.doi`: the draft's references have no DOI.
3. `bib.journal-abbrev` for "J. Optim. Theory Appl." is a false positive; the form is the ISO 4 one.
4. `back.contributions`: no CRediT roles (see Gaps 1).
5. Informational: no ORCID iDs, title capitals in `Gr1985`, ethics statements omitted.

## Commands

```bash
S=skills/axioms-paper-format
D=$S/assets/examples/en-discrete-optimization
W=$(mktemp -d) && cp -R $D/. $W && rm -rf $W/draft $W/import-report.md && cp -R $S/assets/mdpi-template/Definitions $W/Definitions

uv run $S/scripts/check_paper.py $W/paper.tex                 # 6 placeholder errors (see above)
uv run $S/scripts/build_paper.py $W/paper.tex                 # needs latexmk/pdflatex or tectonic
# the importer, from the draft:
uv run $S/scripts/import_source.py $D/draft/Bollati-Olguin-Tarzia-Arxiv.tex --out /tmp/axioms-import
```

Compile check done while building this example: `tectonic` 0.17.0 (run from a scratch folder)
compiled `paper.tex` to a 36-page PDF with no undefined citations or references. Tectonic cannot embed
the class's `.eps` logos, so for that run the two logos were converted with Ghostscript and the copy
of `mdpi.cls` pointed at the `.pdf` files; nothing in this folder was changed for it. Page 1 was
inspected visually. With pdfLaTeX (the MDPI target) it was not compiled.
