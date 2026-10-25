# Porting a draft onto the MDPI class

`import_source.py` does the mechanical part. This file covers what it cannot decide and the
errors you will meet when compiling.

## What the importer already did (check `import-report.md`)

| Draft | MDPI |
|---|---|
| `\documentclass{amsart/article/elsarticle/...}` | `\documentclass[axioms,article,submit,moreauthors]{Definitions/mdpi}` |
| `\title{}` | `\Title{}` (still to be put in Title Case by hand) |
| amsart `\author{} \address{} \email{}` ×n, or article `\author{A \and B}` | `\Author{A $^{1}$ and B $^{2,}$*}`, `\AuthorNames{}`, `\address{$^{1}$ \quad ...; e-mail\\ ...}`, `\corres{}` |
| `\begin{abstract}` | `\abstract{}` (blank lines removed) |
| `\keywords{a, b, c}`, or a "Keywords:" line | `\keyword{a; b; c}` |
| `\subjclass[2020]{Primary 35J60; Secondary 35J96}` | `\MSC{35J60; 35J96}` |
| `\newtheorem{thm}{Theorem}[section]`, `\newtheorem{lem}[thm]{Lemma}` | removed; `thm` becomes `Theorem` and `lem` becomes `Lemma` (class environments, each with its own counter) |
| `\newtheorem{conj}{Conjecture}` (not in the class) | `\theoremstyle{mdpi}\newtheorem{Conjecture}{Conjecture}` |
| `\numberwithin{equation}{section}`, `\geometry`, `\linespread`, margins, `\bibliographystyle` | removed |
| `\usepackage{amsmath,amsthm,graphicx,hyperref,geometry,...}` | removed (the class loads them); other packages kept |
| `$$...$$` | `\[...\]` |
| `\section*{Acknowledgments}`, `Funding`, `Conflicts of interest`, `Data availability`, `Author contributions` | `\acknowledgments{}`, `\funding{}`, `\conflictsofinterest{}`, `\dataavailability{}`, `\authorcontributions{}` |
| `\bibliography{refs}` | kept; `refs.bib` copied |
| `thebibliography` | moved into the reference block (still to be reformatted to MDPI style) |
| `\appendix ...` | `\appendixtitles{yes}\appendixstart\appendix ...` |
| `\input{sec1}` | inlined (one file) |
| `% comments` | removed |

## What you still do by hand

1. **Title Case** in `\Title{}` and in the headings.
2. **Corresponding author.** Put `*` after that author's superscript (`$^{2,}$*`) and the e-mail
   in `\corres{Correspondence: ...}`. Several corresponding authors take initials:
   `x@a.org (A.B.); y@b.org (C.D.)`.
3. **Affiliations.** Order them department, institution, city with postcode, country. Put the
   postcode before the city in continental Europe ("03056 Kyiv, Ukraine"). Give an e-mail for
   every author, and use `\address[1]{...}` when there is only one affiliation.
4. **Hard-coded numbers.** "Theorem 2.3", "(3.1)" and "Section 4" typed as text are wrong now
   that numbering is global. Use `Theorem~\ref{...}`, `\eqref{...}` and `Section~\ref{...}`.
   `check_paper.py` flags them as `refs.hardcoded`.
5. **Shared counters.** In the draft, Lemma 2.3 may have followed Theorem 2.2. With the class
   they become Lemma 1 and Theorem 1. That is the published Axioms practice, so leave it.
6. **Theorem-like environments typed as text** (from Word, or `\textbf{Theorem 1.}`). Turn
   them into `\begin{Theorem}\label{...} ... \end{Theorem}` with `\begin{proof} ...
   \end{proof}`.
7. **Cited results.** Write `\begin{Lemma}[\cite{key}, Lemma 1.3]`.
8. **Tables.** Rebuild each as a float with the caption above:
   ```latex
   \begin{table}[H]
   \caption{Self-explanatory caption.\label{tab:x}}
   \begin{tabularx}{\textwidth}{CCC}
   \toprule
   \textbf{Head 1} & \textbf{Head 2} & \textbf{Head 3}\\
   \midrule
   a & b & c\\
   \bottomrule
   \end{tabularx}
   \end{table}
   ```
   Use no vertical rules and no `\hline`. For a full-width table, wrap it in
   `\begin{adjustwidth}{-\extralength}{0cm}` and use `\fulllength`.
9. **Figures.** Put the caption below and the label inside the caption:
   `\includegraphics[width=8cm]{fig1}` followed by `\caption{...\label{fig:x}}`. Use `[H]`
   placement as the template does. Panels use `\subfloat[\centering]{...}`, and the caption
   describes them as "(\textbf{a}) ...; (\textbf{b}) ...".
10. **Wide displays.** Break them with `align`/`multline`, or wrap them in
    `\begin{adjustwidth}{-\extralength}{0cm} ... \end{adjustwidth}`.
11. **Footnotes.** Move them into the text, or use `\endnote{}` (MDPI uses no footnotes).
12. **`thebibliography`.** Reformat each `\bibitem` to the MDPI pattern
    (`reference-style.md`), or better, move the entries to a `.bib` file and use
    `\bibliography{}`. The order must follow first citation.
13. **cleveref.** The class loads it. Put any `\crefname` definitions **after**
    `\begin{document}`.
14. **The draft's own macros.** `\newcommand`, `\DeclareMathOperator` and the like stay in the
    preamble. Rename any that clash with the class (`\abstract`, `\keyword`, `\address`,
    `\Title`, `\Author`, `\funding`, `\proof`, `\theorem`, `\lemma`, ...).

## Typical compile errors

| Message | Cause | Fix |
|---|---|---|
| `Command \c@theorem already defined` | a draft `\newtheorem{theorem}{...}` | delete it and use the class `Theorem` |
| `Environment theorem undefined` | lower-case environment names | `Theorem`, `Lemma`, ... (capitalised) |
| `Undefined control sequence \TitleCitation` | an old-template macro | delete `\TitleCitation` and `\AuthorCitation` |
| `Option clash for package ...` | a package the class loads, given other options | remove the `\usepackage`, or use `\PassOptionsToPackage` before `\documentclass` |
| `File 'Definitions/mdpi.cls' not found` | the folder is missing | copy `assets/mdpi-template/Definitions/` next to the .tex |
| `Citation ... undefined` | BibTeX was not run, or a key is wrong | run latexmk or `build_paper.py`; check the key |
| `Package natbib Error: Bibliography not compatible with author-year citations` | `\bibitem[...]` with author-year labels | use plain `\bibitem{key}` |
| `Overfull \hbox (xx pt too wide)` | long formulas or URLs | break the formula, or use `adjustwidth`; `\url{}` for URLs |

## No TeX installation?

1. **Overleaf.** Upload the folder (paper.tex, Definitions/, the .bib, figures) to Overleaf and
   compile with pdfLaTeX. Then "Submit to an MDPI journal", or download the PDF and upload
   `build_paper.py --zip --no-compile` plus the PDF to SuSy.
2. **Local.** Install MacTeX or TeX Live, or the single-binary `tectonic`
   (`brew install tectonic`). `build_paper.py` detects latexmk, pdflatex or tectonic, in that
   order.
