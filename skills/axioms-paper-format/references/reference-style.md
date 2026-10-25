# MDPI (ACS-based) reference style for Axioms

Sources:

1. *MDPI ACS Reference Guide*, 11th ed. (Dec 2025):
   <https://res.mdpi.com/data/mdpi-acs-references-guide-v11-2025.12.pdf>
2. The MDPI references page: <https://www.mdpi.com/authors/references>
3. The MDPI layout guide, section 8.11.
4. `Definitions/mdpi.bst` (updated 17 Dec 2024).
5. The references of Axioms 15(11) papers 789, 791 and 793.

## In the text

1. Use `\cite{key}` or `\cite{a,b,c}`. natbib with `sort&compress` prints [1], [2,3] and [4–6],
   numbered in order of first citation. Captions count too.
2. The bracket goes **before** punctuation: "as shown in [3]."
3. **Not as the subject of a sentence.** Write "Ref.~\cite{x} proves", "Refs.~\cite{x,y} show"
   or "Kirk~\cite{x} proved", never "\cite{x} proves".
4. **Locators** go after the bracket, in parentheses: `\cite{x} (p.~10)` gives "[5] (p. 10)",
   and `\cite{x} (pp.~101--105)` gives "[5] (pp. 101–105)". Do **not** write `\cite[p.~10]{x}`,
   which gives "[5, p. 10]".
5. **Results from a reference** are attributed in the theorem head:
   `\begin{Lemma}[\cite{x}, Lemma 1.3]` gives "**Lemma 2** ([16], Lemma 1.3)."

## In the list (what `mdpi.bst` prints)

Authors are written "Surname, I.I." and separated by semicolons. After ten authors, write
"et al.". The journal is the italic ISO 4 abbreviation, the **year is bold** and the *volume
italic*. There is no issue number. Pages use an en dash, or an article number replaces them.
The DOI is added as `https://doi.org/...`.

| Type | Printed form | BibTeX |
|---|---|---|
| Journal | Wang, X.K. Derivations in prime near rings. *Proc. Am. Math. Soc.* **1994**, *121*, 361–366. https://doi.org/... | `@article{key, author={Wang, X. K.}, title={...}, journal={Proc. Am. Math. Soc.}, year={1994}, volume={121}, pages={361--366}, doi={10....}}` |
| Journal, article number | ... *Asian-Eur. J. Math.* **2023**, *16*, 2350193. | `pages={2350193}` |
| Book | Gilbarg, D.; Trudinger, N.S. *Elliptic Partial Differential Equations of Second Order*; Springer: Berlin/Heidelberg, Germany, 2001. | `@book{..., publisher={Springer}, address={Berlin/Heidelberg, Germany}, year={2001}}` |
| Book, edition and pages | Author, A.; Author, B. *Book Title*, 3rd ed.; Publisher: City, Country, 2008; pp. 154–196. | `edition={3rd}, pages={154--196}` |
| Chapter in an edited book | Balakrishnan, N.; He, M. A record-based transmuted family of distributions. In *Advances in Statistics–Theory and Applications*; Ghosh, I., Balakrishnan, N., Ng, H.K.T., Eds.; Springer: Cham, Switzerland, 2021; pp. 3–24. | `@incollection{..., booktitle={...}, editor={...}, publisher={...}, address={...}, pages={3--24}}` |
| Book in a series | ... *Topics in Metric Fixed Point Theory*; Cambridge Studies in Advanced Mathematics; Cambridge University Press: Cambridge, UK, 1990; Volume 28. | `series={...}, volume={28}` |
| Conference | Chum, O.; Philbin, J.; Zisserman, A. Near duplicate image detection: Min-Hash and tf-idf weighting. In Proceedings of the 19th British Machine Vision Conference (BMVC 2008), Leeds, UK, 1–4 September 2008; pp. 812–815. | `@inproceedings{..., booktitle={Proceedings of the ...}, address={Leeds, UK}, pages={...}}` |
| Thesis | Arik, I. New Distribution Families .... Ph.D. Thesis, Anadolu University, Eskisehir, Türkiye, 2018. | `@phdthesis{..., school={...}, address={...}}` |
| arXiv | Shaw, W.T.; Buckley, I.R.C. The alchemy of probability distributions. *arXiv* **2009**, arXiv:0901.0434. | `@article{..., journal={arXiv}, year={2009}, eprint={0901.0434}, archiveprefix={arXiv}}`, or put `arXiv:0901.0434` in `pages` |
| Unpublished | Author, A.B. Title. *Abbrev. J.* year, *submitted / accepted / in press*. | `note={in press}` |
| Website | Title of Site. Available online: URL (accessed on 25 October 2026). | `@misc{..., url={...}, urldate={2026-10-25}}` |
| Software | Mathematica, version 14.1; Wolfram Research: Champaign, IL, USA, 2024. | `@misc` |

Cities in the USA and Canada are written "City, ST, USA".

## Journal abbreviations (ISO 4)

1. Use the ISO 4 / LTWA abbreviation: <https://portal.issn.org/ltwa>. The quickest lookup is
   the "ISO4" field in the ISSN Portal, the "Journal title abbreviation" in Crossref metadata,
   or the abbreviation printed on the journal's own pages.
2. Single-word titles are not abbreviated: *Axioms*, *Mathematics*, *Symmetry*, *Entropy*.
3. If you are not sure, MDPI accepts the **full title**. Never guess a wrong abbreviation.

Common abbreviations in Axioms reference lists:

| Full title | ISO 4 |
|---|---|
| Proceedings of the American Mathematical Society | Proc. Am. Math. Soc. |
| Transactions of the American Mathematical Society | Trans. Am. Math. Soc. |
| Journal of Mathematical Analysis and Applications | J. Math. Anal. Appl. |
| Fixed Point Theory and Applications | Fixed Point Theory Appl. |
| Nonlinear Analysis: Theory, Methods & Applications | Nonlinear Anal. Theory Methods Appl. |
| Journal of Differential Equations | J. Differ. Equ. |
| Calculus of Variations and Partial Differential Equations | Calc. Var. Partial Differ. Equ. |
| Annals of Mathematics | Ann. Math. |
| Fundamenta Mathematicae | Fundam. Math. |
| Communications in Algebra | Commun. Algebra |
| Journal of the London Mathematical Society | J. Lond. Math. Soc. |
| The American Mathematical Monthly | Am. Math. Mon. |
| Fractal and Fractional | Fractal Fract. |
| Annals of Statistics | Ann. Stat. |
| Fuzzy Sets and Systems | Fuzzy Sets Syst. |
| Applied Mathematics and Computation | Appl. Math. Comput. |
| Mathematical Methods in the Applied Sciences | Math. Methods Appl. Sci. |

## DOIs

1. Give a DOI for **every** reference that has one, as a bare `doi = {10.xxxx/...}`. Do not
   write a URL or a "doi:" prefix.
2. MDPI turns DOIs into "[CrossRef]" links in the published version.
3. **Verify** each DOI before adding it, by resolving it at `https://doi.org/<doi>` or querying
   `https://api.crossref.org/works/<doi>`. Never add a DOI you have not resolved, and never invent
   one.
4. Older classics (pre-1950 journals, many books) often have no DOI. That is fine.

## BibTeX hygiene

1. Protect capitals and proper names in titles with braces: `{M}onge--{A}mp{\`e}re`, `{H}ilbert`,
   `{$L^p$}`.
2. Do not use `\bibliographystyle`: the class sets `Definitions/mdpi` itself.
3. Do not use biblatex (`\addbibresource`, `\printbibliography`, `\autocite`).
4. Upload the `.bib`, and the `.bbl` if you have one, in the zip.
5. One work per key, with no duplicate DOIs, and no notes or comments inside entries.
