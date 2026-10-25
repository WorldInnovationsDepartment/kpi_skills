# Axioms (MDPI) requirements for submitted papers

Journal: **Axioms**, ISSN 2075-1680, MDPI (Basel). Monthly, open access (CC BY), journal of
mathematics, mathematical logic and mathematical physics. Editor-in-Chief: Humberto Bustince.
Indexed in SCIE; JCR Q2 (Mathematics, Applied), IF 1.5. Site: <https://www.mdpi.com/journal/axioms>.
Sections: Algebra and Number Theory; Geometry and Topology; Hilbert's Sixth Problem; Logic;
Mathematical Analysis; Mathematical Physics.

Sources, as captured on 2026-10-25. www.mdpi.com returns HTTP 403 to scripts, so its pages were
read through the Wayback Machine. The template files came directly from MDPI's file servers.

1. S1. Instructions for Authors: <https://www.mdpi.com/journal/axioms/instructions>
   (snapshot of 2026-07-10, the newest available).
2. S2. Aims & Scope: <https://www.mdpi.com/journal/axioms/about> (2025-09-08). S3. Journal home
   (2026-10-19). S4. APC page (2025-09-12). S5. Sections (2026-10-13).
3. S7. MDPI LaTeX page: <https://www.mdpi.com/authors/latex>. S8. MDPI Author Layout Style Guide:
   <https://www.mdpi.com/authors/layout> (2026-10-17).
4. S9 and S10. MDPI references page and the *ACS Reference Guide* PDF, 11th ed., Dec 2025:
   <https://res.mdpi.com/data/mdpi-acs-references-guide-v11-2025.12.pdf>.
5. S11. MDPI Research and Publication Ethics: <https://www.mdpi.com/ethics> (2026-10-17).
6. S13. The LaTeX template: <https://res.mdpi.com/data/MDPI_template_ACS.zip?v=20260901>,
   containing `mdpi.cls` v6.5d of 2026-10-19. It is bundled here as `assets/mdpi-template/`.
7. S14. The Axioms Word template: <https://mdpi-res.com/files/word-templates/axioms-template.dot>,
   bundled as `assets/mdpi-template/axioms-template.dot`.
8. S15. Three papers from Axioms 15(11), published 2026-10-22. See `published-papers-review.md`.

The "Rule" column gives the code that `scripts/check_paper.py` reports: E = ERROR, W = WARN,
I = INFO. Where the guide, the template and published practice disagree, see "Conflicts" at the
end.

## 1. Submission

| # | Requirement | Source | Rule |
|---|---|---|---|
| 1.1 | Submit online through SuSy (<https://susy.mdpi.com>, Axioms form id 47). The submitting author is normally the corresponding author | S1 | I `submit.files` |
| 1.2 | **Free-format first submission** is allowed: "We do not have strict formatting requirements", but all required sections must be present. At revision, the manuscript **must** follow the template | S1 | (skill formats to the template from the start) |
| 1.3 | LaTeX: "must be collated into one ZIP folder (including all source files and images, so that the Editorial Office can recompile the submitted PDF)". Also upload the compiled PDF. That is standard practice, but not stated explicitly | S1 | `build_paper.py --zip`; I `submit.files` |
| 1.4 | Figures for the upload: PNG, JPEG or TIFF, preferably ≥ 600 dpi, in a single zip. The total upload limit is 120 MB | S1 | W/I `figure.dpi`; `build_paper.py` size warning |
| 1.5 | Templates may be used only for submission, not for preprint posting (use the `preprints` option for that) | S1 | – |
| 1.6 | **Cover letter** (mandatory): significance and fit with the scope, any earlier MDPI submission with its ID, and these two sentences verbatim: "We confirm that neither the manuscript nor any parts of its content are currently under consideration for publication with or published in another journal." and "All authors have approved the manuscript and agree with its submission to Axioms." | S1 | I `submit.cover-letter`; `assets/cover-letter.md` |
| 1.7 | Suggest **3 reviewers** with full contact details: from other institutions, not current collaborators, and with no joint papers with any author in the last 3 years. Reviewers can also be excluded. Enter them in SuSy, not in the letter | S1 | I `submit.reviewers` |
| 1.8 | Preprints are allowed if not peer reviewed. An extended conference paper must be expanded to article size, cited with `\conference{}`, cleared for copyright and disclosed in the cover letter | S1 | – |
| 1.9 | Review is single-anonymised (single-blind), with at least two reports. The author has about 5 days for a minor and 10 days for a major revision. iThenticate plagiarism check | S1 | – |
| 1.10 | APC: **CHF 2400** for accepted papers. Waivers exist, and members of affiliated societies (IFSA, JSMF, Eurekas) get discounts. Minor English editing is included; extensive editing needs are returned to the authors | S4, S1 | – |
| 1.11 | Medians in H1 2026: first decision about 21.6 days after submission, publication 2.9 days after acceptance | S3 | – |

## 2. Template and class

| # | Requirement | Source | Rule |
|---|---|---|---|
| 2.1 | Use `\documentclass[axioms,article,submit,moreauthors]{Definitions/mdpi}`. Use `oneauthor` for a single author, and `review`/`communication`/... for other types. The editorial office switches `submit` to `accept`. Compile with pdfLaTeX | S13 | E `class.mdpi`, `class.journal`, `class.type`, `class.submit`, `class.authors` |
| 2.2 | The `Definitions/` folder (mdpi.cls, mdpi.bst, journalnames.tex, logos) sits next to the .tex | S13 | E `class.files` |
| 2.3 | `\TitleCitation` and `\AuthorCitation` belong to pre-2024 templates and are **undefined** in v6.5. `pdftex` is no longer an option | S13 | E `template.obsolete`; W `class.pdftex` |
| 2.4 | Do not reload packages the class already loads with conflicting options. Never use packages that change the layout or fonts (geometry settings, times, lmodern, fullpage, biblatex, ...) | S13 | W/E `preamble.package`; E `preamble.layout` |
| 2.5 | Remove all template instruction text and the `\setcounter{section}{-1}` line | S13 | E `template.leftover`, `template.todo` |
| 2.6 | Leave the MDPI internal commands (`\pubvolume`, `\datereceived`, ...) untouched. Running heads, the left metadata column, the copyright line and the Publisher's Note are produced by the class | S13 | W `back.publishersnote` |

## 3. Front matter

| # | Requirement | Source | Rule |
|---|---|---|---|
| 3.1 | Title: concise, specific, in **Title Case**, with no running title, no final period and no abbreviations or jargon | S1, S8, S13 | E `front.title`; W `front.title.case`, `front.title.abbr`, `front.title.length` |
| 3.2 | Authors: **full first and last names** (middle initials allowed), no titles or degrees, no comma before "and". Superscript affiliation numbers. At least one corresponding author marked `*`. Equal contribution: † plus `\secondnote{These authors contributed equally to this work.}`. GenAI cannot be an author | S1, S8, S13 | E `front.author`, `front.corresponding`; W `front.author.title`, `front.author.fullname` |
| 3.3 | `\AuthorNames{}` repeats the names for the PDF metadata | S13 | W `front.authornames` |
| 3.4 | Affiliations in PubMed format: department, institution, city with postcode, country (postcode before the city in continental Europe). One affiliation per number, no duplicates. Use `\address[1]{...}` when there is only one. **Every author's e-mail is published**, after the affiliation ("...; e-mail") | S1, S8, S13 | E `front.address`; W `front.email` |
| 3.5 | `\corres{Correspondence: e-mail}`. Add initials when there are several corresponding authors. Phone is optional | S13 | E `front.corres` |
| 3.6 | ORCID is "strongly recommended": `\newcommand{\orcidauthorA}{0000-...}` plus `\orcidA{}` after the name | S1, S8 | E/W/I `front.orcid` |
| 3.7 | **Abstract: about 200 words maximum, a single paragraph**, structured but without headings (background, methods, results, conclusions). No citations, no display equations, no figure or table references. Define all abbreviations | S1, S8, S13 | W `abstract.length`, `abstract.abbr`, `abstract.reference`; E `abstract.paragraph`, `abstract.citation`, `abstract.equation` |
| 3.8 | **Keywords: three to ten**, separated by semicolons, with no final period | S1, S13 | E `keywords.count`, `keywords.separator`; W `keywords.period` |
| 3.9 | **MSC**: `\MSC{35J60; 35J96}`, MSC2020 codes separated by semicolons, without Primary/Secondary. Not stated as mandatory, but present in the Axioms Word template and in every reviewed paper (see Conflicts) | S13, S14, S15 | W `msc.missing`, `msc.separator`; E `msc.format` |

## 4. Body

| # | Requirement | Source | Rule |
|---|---|---|---|
| 4.1 | The generic MDPI structure is Introduction, Materials and Methods, Results, Discussion, Conclusions (optional). The layout guide says proof-based papers "have a structure that differs". In practice Axioms papers use Introduction, Preliminaries, Main Results, (Applications/Examples), Conclusions | S1, S8, S15 | W `body.introduction`; W `body.conclusions` (optional, recommended) |
| 4.2 | Up to three numbered heading levels (1., 1.1., 1.1.1.) in Title Case. A fourth level is an unnumbered paragraph head | S8 | W `body.unnumbered`; I `body.heading.case` |
| 4.3 | The Introduction places the work in context, cites the key literature, states the aim and the main results, and should be readable outside the subfield. All reviewed papers end it with "The rest of this paper is organized as follows ..." | S13, S15 | W `intro.citations`; I `intro.outline` |
| 4.4 | Describe GenAI use (beyond grammar or formatting) in the methods part | S1, S13 | I `back.ai` |
| 4.5 | No footnotes: MDPI uses endnotes (`\endnote`) | S13 | W `text.footnote` |
| 4.6 | Numbers: write 0.01, not .01. Write a × 10^b, never 3.7e5. Use a comma thousands separator from five digits (123,456). Write zero to nine in words unless a unit follows | S8 | W `text.enotation`; I `text.leadingzero` |

## 5. Mathematics

| # | Requirement | Source | Rule |
|---|---|---|---|
| 5.1 | Use the class environments `Theorem, Lemma, Corollary, Proposition, Characterization, Property, Problem, Example, Remark, Definition, Hypothesis, Notation, Assumption, Algorithm`, with capital first letters. Style: bold head, italic body | S13 | E `math.env` |
| 5.2 | The class owns the counters `theorem`, `lemma`, ... so a draft's `\newtheorem{theorem}{Theorem}` fails ("Command \c@theorem already defined") | S13 (mdpi.cls l.255-310) | E `math.newtheorem` |
| 5.3 | Number every environment type with Arabic numerals **through the whole paper** (Theorem 1, Lemma 1, ...), never per section (2.1). Equations are (1), (2), ...; appendix equations (A1) | S8, S15 | W `math.numbering`, `refs.hardcoded` |
| 5.4 | Proofs use `\begin{proof}` or `\begin{proof}[Proof of Theorem~\ref{...}]`. The class prints a bold "Proof." and the QED box right after the text. If the proof does not follow its result, say which result it proves | S8, S13 | W `math.proof` |
| 5.5 | Attribute a cited result in the head: `\begin{Lemma}[\cite{key}, Lemma 1.3]` | S15 | – |
| 5.6 | Punctuate displays as part of the sentence. A "where" after a display is lower case and not indented. Define every symbol. Variables in italics, words and units upright | S8, S13 | W `text.where` |
| 5.7 | Use `equation`/`align` (or `\[...\]`), not `$$...$$` or `eqnarray`. Wide displays go in `\begin{adjustwidth}{-\extralength}{0cm}` | S13 | W `math.display`, `math.eqnarray`; W `log.overfull` |
| 5.8 | Long proofs of results that are not central may move to an appendix (`\appendixstart`, `\appendix`), which must be cited in the text | S8, S13 | W `back.appendix` |

## 6. Figures and tables

| # | Requirement | Source | Rule |
|---|---|---|---|
| 6.1 | Number figures, schemes and tables in order of appearance. Place each near its first citation; every one must be cited ("Figure 1", "Table 1", never "Fig.") | S1, S8 | W `figure.cited`, `table.cited`, `figure.label`, `table.label`, `text.abbrev` |
| 6.2 | Captions are mandatory and self-explanatory: **below** figures, **above** tables. Multi-panel: (a), (b) described as "(**a**) ..." | S1, S8 | E `figure.caption`, `table.caption`; W `*.caption.position` |
| 6.3 | Tables must be editable (not images), use booktabs rules, and have **no vertical lines**. `tabularx` with `C` columns as in the template | S1, S13 | W `table.vrules`, `table.hline` |
| 6.4 | Figure resolution ≥ 600 dpi (PNG/JPEG/TIFF), RGB, English text, a dot as the decimal point, no watermarks. Vector PDF is fine in LaTeX | S1, S8 | W/I `figure.dpi`; W `figure.format`; E `figure.file` |
| 6.5 | Reprinted figures need permission: "(Reprinted with permission from Ref. [X]. Copyright Year Owner.)" | S8 | – |

## 7. References and citations

| # | Requirement | Source | Rule |
|---|---|---|---|
| 7.1 | Number references **in order of first appearance** (including captions). Square brackets go **before** punctuation: [1], [1,3], [1–3]. `\cite` with natbib sort&compress does this | S1, S10 | E `refs.order`, `refs.undefined-cite`, `refs.uncited`; W `cite.manual` |
| 7.2 | Page locators: "[5] (p. 10)", **not** "[5, p. 10]" | S1, S10 | W `cite.locator` |
| 7.3 | A citation is not the subject of a sentence: "Ref. [1] proves", or "Liu [1] proves" | S10 | W `cite.sentence-start` |
| 7.4 | ACS-based MDPI style: `Author, A.B.; Author, C.D. Title. Abbrev. J. Year, Vol, pages.` with the journal in italics, **year bold** and *volume italic*. No issue number. **ISO 4 journal abbreviations** (full title if unsure). DOI for every reference that has one | S10, S13 | W `bib.journal-abbrev`, `bib.doi`, `refs.issue`; I `refs.doi`, `refs.format`, `bib.number` |
| 7.5 | BibTeX: the class sets `\bibliographystyle{Definitions/mdpi}` itself; write only `\bibliography{file}` (or an inline `thebibliography`). biblatex is not supported | S13 | W `refs.style`; E `refs.biblatex`, `refs.bibfile`, `bib.fields` |
| 7.6 | One work per number, no duplicates, no notes inside references. Unpublished work: "(submitted; accepted; in press)" | S10 | E `refs.duplicate` |
| 7.7 | arXiv: `Authors. Title. arXiv Year, arXiv:ID.` (in BibTeX: `eprint`, `archiveprefix`) | S8 | I `bib.arxiv` |

See `reference-style.md` for templates of every entry type.

## 8. Back matter

Unnumbered, in this order (S8 §8, S13): Supplementary Materials, Author Contributions,
Funding, Institutional Review Board Statement, Informed Consent Statement, Data Availability
Statement, Acknowledgments, Conflicts of Interest, Abbreviations, Appendix, References.

| # | Requirement and standard wording | Source | Rule |
|---|---|---|---|
| 8.1 | **Author Contributions** (several authors), CRediT roles with initials, ending with "All authors have read and agreed to the published version of the manuscript." Example: "Conceptualization, X.X. and Y.Y.; methodology, X.X.; formal analysis, X.X.; writing---original draft preparation, X.X.; writing---review and editing, Y.Y.; supervision, Y.Y. All authors have read and agreed to the published version of the manuscript." MDPI gives no wording for a single author | S1, S13 | E `back.contributions`; W initials mismatch or missing role |
| 8.2 | **Funding**: "This research received no external funding." or "This research was funded by NAME OF FUNDER grant number XXX." (Crossref Funder Registry spelling; declare APC funding too) | S1, S13 | E `back.funding` |
| 8.3 | **IRB / Informed Consent**: "Not applicable." for work without humans or animals, or omit them (the Axioms Word template omits them) | S13, S14 | I `back.ethics` |
| 8.4 | **Data Availability** (mandatory). Theoretical work: "No new data were created or analyzed in this study. Data sharing is not applicable to this article." Results in the paper: "The original contributions presented in this study are included in the article. Further inquiries can be directed to the corresponding author." Repository: "The original data presented in the study are openly available in [repository] at [DOI/URL]." Code should be deposited or supplied as supplementary material | S1, S11 | E `back.data` |
| 8.5 | **Acknowledgments**: support not covered above, with full names and no titles. **GenAI disclosure** (any use beyond grammar, spelling or formatting), verbatim: "During the preparation of this manuscript/study, the author(s) used [tool name, version information] for the purposes of [description of use]. The authors have reviewed and edited the output and take full responsibility for the content of this publication." Also declare it in SuSy and in the methods | S1, S11, S13 | W/I `back.ai` |
| 8.6 | **Conflicts of Interest**: "The authors declare no conflicts of interest." (single author: "The author declares no conflicts of interest."). With funding, add: "The funders had no role in the design of the study; in the collection, analyses, or interpretation of data; in the writing of the manuscript; or in the decision to publish the results." | S1, S13 | E `back.coi` |
| 8.7 | Optional Abbreviations table (`\abbreviations`) and Appendix (`\appendixstart\appendix`; Figure A1, Table A1, (A1)) | S13 | W `back.appendix` |
| 8.8 | The order above | S8 | W `back.order` |

## 9. Compiled output

| # | Check | Rule |
|---|---|---|
| 9.1 | No LaTeX errors, undefined references or citations, missing files | E `log.error`, `log.undefined`, `log.missing-file`, `pdf.unresolved` |
| 9.2 | No lines sticking out by more than 10 pt (wide formulas) | W `log.overfull` |
| 9.3 | The first page names Axioms (class option set). Page count reported; there is no length limit | W `pdf.journal`; I `pdf.pages` |
| 9.4 | No Type 3 (bitmap) fonts | W `pdf.type3` |

## Conflicts and decisions

1. **MSC.** The Instructions never mention MSC, but the Axioms Word template has an "MSC:" line
   and all three reviewed papers print one. The skill treats it as expected: a missing `\MSC` is
   a WARN, a malformed code an ERROR. Use MSC2020 (<https://zbmath.org/classification/>), and let
   the author confirm the codes.
2. **Theorem numbering.** The template text says "Proposition 2 follows Theorem 1" (one shared
   counter), but the class gives every type its own counter. Published papers follow the class
   (Lemma 1–8, Theorem 1–7), and the skill does too.
3. **Abstract length.** The limit is "about 200 words maximum", but published abstracts range from
   71 to about 355 words. The skill warns above 200 and does not error.
4. **Structure.** The generic IMRaD wording of the Instructions is not applied to proof papers
   (S8 §3.1). The skill asks for an Introduction and recommends Conclusions.
5. **IRB / consent.** The LaTeX template has these sections; the Axioms Word template does not.
   The importer writes "Not applicable."; deleting both is also acceptable.
6. **DOIs.** MDPI asks for DOIs, but the typeset references show "[CrossRef]" links instead of the
   DOI text. Supply `doi` fields anyway.
7. **Unverified** (2026-10-25): any change to the Instructions after 2026-07-10, the APC after
   2025-09, whether the compiled PDF must be uploaded next to the zip, and Scopus/zbMATH coverage.
   If the live site differs from this file, the site wins: tell the user and update this file,
   `check_paper.py` and the tests.
