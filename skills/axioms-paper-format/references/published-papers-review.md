# Review of three recently published Axioms papers

Purpose: to see how MDPI actually typesets accepted Axioms papers, how strictly the author
guide (`requirements.md`) is applied, and which choices the skill should copy.

Reviewed on 2026-10-25 from the published PDFs. The HTML pages on www.mdpi.com return HTTP 403
to scripts, so each paper's journal section could not be verified. The newest issue,
**Vol. 15, Issue 11** (published 2026-10-22), came from the Crossref API. Three regular *Article*
papers from different areas were chosen.

| | Paper A | Paper B | Paper C |
|---|---|---|---|
| Area | Algebra (near-rings) | Analysis / PDE | Applied probability and statistics |
| Citation | Aldwoah, ul Huque, Alnoghashi, Suhail, Touati, Al-omary. "Commutativity Criteria and Structural Properties of Prime Near-Rings Admitting Right Generalized Derivations on Specific Ideals". *Axioms* **2026**, *15*, 789 | He, Wang. "Boundary Hölder Regularity of a Class of Monge–Ampère Equations at Some Special Points". *Axioms* **2026**, *15*, 791 | Arık, Arık, Kantar. "Record-Based Transmuted Pareto Distribution: Properties, Estimation, and Applications to Medical and Hydrological Data". *Axioms* **2026**, *15*, 793 |
| DOI | 10.3390/axioms15110789 | 10.3390/axioms15110791 | 10.3390/axioms15110793 |
| Received → published | 22 Sep → 22 Oct 2026 (30 days) | 16 Sep → 22 Oct 2026 | 24 Aug → 22 Oct 2026 |
| Pages | 18 | 14 | 33 |
| Sections | 5, no subsections | 3, no subsections | 7, with subsections 3 levels deep |
| Figures / tables | 0 / 0 | 1 (two panels) / 0 | 6 / 13 |
| Numbered equations | about 42 | 24 | about 51 |
| Environments | Lemma 1–8, Theorem 1–7, Corollary 1–3, Example 1–2; 11 proofs | Definition 1–2, Remark 1–3, Theorem 1–2, Lemma 1–6 | none; results derived in running text |
| Abstract | 71 words | about 90 words | **about 355 words** |
| Keywords | 6 | 4 | 7 |
| MSC | 16N60; 16W25; 16Y30 | 35J60; 35J96; 53A15; 53C45 | 62E15; 62F10; 60E05 |
| References | 18 (22% from 2021 on, 3 self-citations) | 20 (30% from 2021 on, none [CrossRef]-linked) | 38 (24% from 2021 on, 3 self-citations) |
| Conclusions | yes, with "Recommendations for Further Study" | **none**: ends with the last proof | yes, about 1.5 pages, with limitations and future work |

## Paper A: algebra (789)

1. **Front matter.**
   1. The page starts with the italic "*Article*" label and a bold title in Title Case.
   2. The bold author line uses superscripts, and two authors are corresponding ("Muntasir
      Suhail 4,*").
   3. Six numbered affiliations follow, each "Department, Faculty, University, City Postcode,
      Country; e-mail".
   4. The correspondence line reads "* Correspondence: m.suhail@... (M.S.); raradwan959@...
      (R.M.A.-o.)", with initials because there are two corresponding authors.
2. **Abstract and keywords.** A separate bold **Abstract** heading is followed by a single
   paragraph. **Keywords:** are lower case, separated by semicolons, with no final period, and
   **MSC:** follows them.
3. **Left margin of page 1.** The Academic Editor, the four dates and the CC BY copyright line sit
   there. The class generates all of it.
4. **Sections.** 1 Introduction, 2 Preliminary Results, 3 and 4 results sections, 5 Conclusions.
   The Introduction states the "primary objective and main contribution" and ends with "The paper
   is organized as follows: Section 2 provides … Finally, Section 5 summarizes …".
5. **Environments.** Each type is numbered separately through the whole paper.
   1. The head is bold and the body italic, including Examples.
   2. A cited result carries its source in the head: "**Lemma 2** ([16], Lemmas 1.3 and 1.4)."
   3. Proofs start with a bold "Proof." and end with an open square placed right after the text.
6. **Equations.** Numbered (1)–(42) through the paper, with (1a)/(1b) used once inside a proof.
   The text refers to them as "Equation (6) implies" or "by (1)".
7. **Back matter.**
   1. Author Contributions is written **per author** ("Project administration and
      writing—review and editing, K.A.; …") and ends with "All authors have read and agreed to
      the published version of the manuscript."
   2. Funding names the university grant QU-APC-2026, which funded the APC.
   3. IRB and Informed Consent read "Not applicable."
   4. Data: "The original contributions presented in this study are included in the article.
      Further inquiries can be directed to the corresponding authors."
   5. "The authors declare no conflicts of interest."
8. **References.** In MDPI style with ISO 4 abbreviations:
   1. `Wang, X.K. Derivations in prime near rings. *Proc. Am. Math. Soc.* **1994**, *121*, 361–366.`
   2. With an article number: `*Asian-Eur. J. Math.* **2023**, *16*, 2350193.`
   3. A chapter in a series: `In *Near-Rings and Near-Fields*; North-Holland Mathematics Studies;
      North-Holland: Amsterdam, The Netherlands, 1987; Volume 137, pp. 31–35.`
   4. One abbreviation is malformed ("Bol. Soc. Parana. MatemáTica"), the work of an automatic
      abbreviator.

## Paper B: analysis/PDE (791)

1. **Single affiliation.** It is unnumbered and the author line has no superscripts: "Xingyue He
   and Jingjing Wang *". This is `\address[1]{...}` in the template.
2. **Keywords.** Four, one of them with inline math: "(a, η)-type points".
3. **Main theorems.** Theorems 1 and 2 are stated **in the Introduction**, which ends with "The
   rest of this paper is arranged as follows. In Section 2 … In Section 3 …".
4. **Sections.** Introduction, Preliminaries, The Proof of Main Theorems. There is **no
   Conclusions section**, so Axioms does not enforce one.
5. **Environments.**
   1. Definition, Remark, Theorem and Lemma all use a bold head and an italic body.
   2. Attribution is in the head: "**Lemma 5** (Comparison principle, [19])."
   3. Proof heads read "**Proof for Theorem 1.**". The usual form is "Proof of Theorem 1".
6. **Figure 1.** Two panels with the caption **below**, at 9 pt, with a bold label: "**Figure 1.**
   Comparing curves: (a): …; (b): …".
7. **Back matter.**
   1. Author Contributions follows the standard per-role CRediT form ("Conceptualization, X.H.;
      methodology, X.H.; …").
   2. Funding lists three grants with their numbers.
   3. The data statement says the contributions are included in the article.
   4. Acknowledgments thank the referees.
   5. The standard conflicts-of-interest sentence follows.
   6. The **IRB and Informed Consent statements are omitted**, not written as "Not applicable".
8. **References.** 20 entries in MDPI style, but **no [CrossRef] links**, which suggests no DOIs
   were supplied. One entry lacks a period before the journal name, and two 2026 entries look
   off-topic.
9. **Slips that survived copy-editing.** "Monge--Ampère" (a double hyphen) and "points.It" (a
   missing space). `check_paper.py` lints for both kinds (`text.space`; the `--` of LaTeX is fine
   inside the source).

## Paper C: applied statistics (793)

1. **Front matter.**
   1. An ORCID icon follows the corresponding author's name.
   2. "* Correspondence:" gives two alternative e-mails joined by "or".
   3. The 355-word abstract shows that the 200-word guideline is not enforced at acceptance.
2. **Headings.**
   1. Three levels: "1." in bold, "2.1." in italics and "3.3.1." upright.
   2. Unnumbered paragraph heads such as "Random Number Generation".
   3. Every heading is in Title Case.
3. **No theorem environments.** Derivations are in running text. Applied papers are in scope.
4. **Tables.**
   1. Thirteen booktabs-style tables with no vertical rules, captions **above** them, and a bold
      "**Table 1.**" label.
   2. Long tables continue with "**Table 2.** *Cont.*", which the class produces.
5. **Figures.** Six multi-panel R plots, some wider than the text column (the `adjustwidth`
   feature). The panel letters in captions are bold: "(**a**) *p* = 0.5 fixed …".
6. **Back matter.**
   1. **Supplementary Materials** comes first: R code, an Excel file and session info, at
      "https://www.mdpi.com/article/10.3390/axioms15110793/s1".
   2. Author Contributions is per role.
   3. "This research received no external funding."
   4. IRB and Informed Consent read "Not applicable."
   5. The data statement is a long reproducibility paragraph.
   6. **Acknowledgments carry the GenAI disclosure**, naming the tools and versions, the
      specific tasks (literature search, language editing, checking derivations, debugging R
      code), and "the authors have reviewed and edited the output and take full responsibility
      for the content".
7. **Citations.**
   1. "**Ref. [4]** obtained …" at the start of a sentence (6 times).
   2. "Sakthivel and Nandhini [25]".
   3. arXiv entries look like `*arXiv* **2009**, arXiv:0901.0434.`

## What the skill copies (house style)

1. **The official class does the layout.** The page-1 block, the left metadata column, the
   running heads "*Axioms* **2026**, *15*, NNN" and "X of N", heading styles, caption styles,
   continuation captions and the Publisher's Note all come from `mdpi.cls`. The skill never
   recreates them by hand.
2. **Front matter.** The author supplies the title (Title Case), full author names with
   superscripts, `*` and optional ORCID, PubMed-style affiliations with e-mails, the
   correspondence line, a one-paragraph abstract, semicolon-separated keywords, and **MSC2020
   codes separated by semicolons**.
3. **Numbering.**
   1. Every environment type is numbered on its own through the paper (Theorem 1, Lemma 1).
   2. Equations are (1), (2), … with no section prefix.
   3. The importer drops `[section]` numbering and `\numberwithin`, and the checker flags
      hard-coded "Theorem 2.1".
4. **Proofs.** The class `proof` environment, optionally `[Proof of Theorem~\ref{...}]`.
   Attribute cited results in the head: `\begin{Lemma}[\cite{key}, Lemma 1.3]`.
5. **Introduction.** It ends with an outline paragraph ("The rest of this paper is organized as
   follows …"), which all three papers have.
6. **Citations.** `\cite` (compressed to [2,3] or [4–6]), "Ref. [n]" at the start of a sentence,
   and "[n] (p. x)" for locators.
7. **References.** BibTeX with `Definitions/mdpi.bst`, ISO 4 abbreviations in `journal`, and a
   `doi` on every entry that has one, so MDPI can add [CrossRef] links.
8. **Back matter.** The MDPI order and stock sentences: "All authors have read and agreed to the
   published version of the manuscript."; "This research received no external funding."; "Not
   applicable."; the data sentence that fits the paper; "The authors declare no conflicts of
   interest."; and the GenAI sentence in Acknowledgments when it applies.

## What varies (left to the author)

1. Length: 14–33 pages; there is no limit.
2. Number of references: 18–38. Recent (2021 and later): 22–30%. Self-citation: 0–3 references.
3. Keywords: 4–7. Abstract: 71–355 words. The skill still recommends at most 200 words.
4. Conclusions are present in two papers out of three. None has a separate Discussion section
   or an appendix.
5. Environments used, and whether main theorems are stated early in the Introduction.
6. Author Contributions written per role (the MDPI default) or per author.
7. IRB and Informed Consent given as "Not applicable." or omitted.
