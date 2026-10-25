# LNNS requirements for submitted papers

Series: **Lecture Notes in Networks and Systems** (LNNS), Springer. ISSN 2367-3370,
eISSN 2367-3389. Series editor: Janusz Kacprzyk. Series page:
<https://link.springer.com/bookseries/15179>
(mirror: <https://www.springerprofessional.de/en/lecture-notes-in-networks-and-systems/10076406>).
The series page lists indexing in Scopus, EI Compendex, INSPEC, WTI, zbMATH and SCImago.
Volumes are "submitted for consideration" to Web of Science, which does not guarantee inclusion.

LNNS is a proceedings series. Papers reach it through a conference, and **the conference sets
the page limit, the deadline and sometimes the citation style.** Springer sets everything else.

Sources (captured 2026-10-25; "B" is the document that governs LNNS):

| ID | Source |
|---|---|
| A | Springer Nature, "Conference proceedings" author hub: <https://www.springernature.com/gp/authors/publish-a-book/step-by-step-conference-proceedings> |
| B | "Instructions for Authors of Papers to be published in Springer Engineering/Physics/Mathematics Proceedings", 9 Mar 2026. **Names LNNS in its scope**: <https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/26362278/data/v2> |
| C | The same instructions for Computer Science Proceedings (LNCS, CCIS…), 23 Feb 2026. Nearly identical to B; used for context: <https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/27841326/data/v2> |
| D | LaTeX proceedings template (llncs.cls, samplepaper.tex v2.25, 2026-09-03, llncsdoc): <https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/26361882/data/v8>; CTAN `llncs` v2.26: <https://ctan.org/pkg/llncs> |
| E | Word proceedings template `splnproc2510.docm` (2025-10-15) with its technical instructions: <https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/27841328/data/v1> |
| F | "Disclosing AI use in manuscripts – Books and Proceedings", v.2, Oct 2026: <https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/53830640/data/v3> |
| G | Springer Nature book policies (preprints, self-archiving): <https://www.springernature.com/gp/open-science/policies/book-policies> |
| P | Three published LNNS papers, 2025-2026: see `published-papers-review.md` |

The "Rule" column gives the `scripts/check_paper.py` code: E = ERROR, W = WARN,
I = INFO reminder. "builder" means `build_paper.py` produces it automatically.

## 1. Template and file

| # | Requirement | Source | Rule |
|---|---|---|---|
| 1.1 | Use Springer's proceedings templates: LaTeX `llncs` (`\documentclass[runningheads]{llncs}`) or the Word template `splnproc`. Use the conference's copy if it ships one. A few LNNS volumes (e.g. ICICT, Springer Singapore) use the `svmult` chapter layout instead, so check the call for papers | B, D, E, P | I `template.flavour` |
| 1.2 | Word: submit **.docx without macros**. "On no account should docm files be submitted" | B, E | E `docx.format`, `docx.macros` |
| 1.3 | LaTeX: send all sources (.tex, .bib/.bbl, images); no self-defined environments; avoid `fancyhdr`, `a4wide`, `enumitem`, `\enlargethispage`, `\pagebreak` and changes to `\textheight`, `\vspace` or `\baselinestretch` | B, D | builder (generated preamble uses none) |
| 1.4 | Final PDF that corresponds exactly to the sources. **No Type 3 fonts** ("their characters will be omitted") | B, D | E `pdf.type3`, W `pdf.fonts` |
| 1.5 | No page numbers or running heads in Word. Springer adds them. LaTeX keeps `runningheads` with `\titlerunning` / `\authorrunning` | B §3.4, D | E `docx.header` |
| 1.6 | Short file names, e.g. `Smith_TitleOfPaper.docx` | E | I `submit.package` |

## 2. Page layout

| # | Requirement | Value used by build_paper.py | Rule |
|---|---|---|---|
| 2.1 | Text area **122 × 193 mm** | Word: A4, margins top and bottom 52 mm, left and right 44 mm (header 42 mm, footer 41 mm), copied from splnproc2510. LaTeX: llncs.cls | E `docx.textarea`, W `pdf.textarea` |
| 2.2 | Font: Times (Word) / Times via newtx (LaTeX sample 2026; Computer Modern is also accepted) | Times New Roman; `newtxtext` + `newtxmath` | E `docx.font` |
| 2.3 | Body 10 pt, justified; Word line height "at least 12 pt"; first-line indent 0.4 cm (LaTeX 15 pt). **No indent** for the first paragraph after a heading, table, figure or equation | builder | E `docx.size` |
| 2.4 | Title 14 pt bold, centred, 24 pt after | builder | — |
| 2.5 | Authors 10 pt centred; affiliations 9 pt centred, each on a new line | builder | — |
| 2.6 | "**Abstract.**" run-in, 9 pt, indented 1 cm on both sides; "**Keywords:**" 9 pt | builder | E `docx.abstract`, `docx.keywords` |
| 2.7 | Level 1 heading: 12 pt bold, numbered "1 Introduction". Level 2: 10 pt bold, "2.1 Printing Area". Level 3: bold run-in "Heading. Text", unnumbered. Level 4: italic run-in, unnumbered. **At most four levels.** Never number from "0". Title case, left-aligned | builder | E `headings.depth`, `headings.numbered`; W `headings.case`, `docx.headings` |
| 2.8 | Captions 9 pt; "**Fig. 1.**" **below** figures, "**Table 1.**" **above** tables (bold label). Short captions centred, long ones justified. A caption that is not a full sentence has no final period | builder | E `figure.caption`, `table.caption`; I `figure.caption` |
| 2.9 | Equations centred, numbered consecutively "(1)" at the right margin, with no section counter; punctuated like text; editable, never images | builder (native Word equations / `equation` environment) | E `equations.images` |
| 2.10 | References 9 pt, numbered list | builder | — |
| 2.11 | "**Acknowledgments.**" and "**Disclosure of Interests.**": 9 pt bold run-in paragraphs after the text and before the references (LaTeX `credits` environment) | builder | E `docx.disclosure` |
| 2.12 | No colour in text, tables or equations | B | E `body.color` |

## 3. Title block

| # | Requirement | Source | Rule |
|---|---|---|---|
| 3.1 | **Title case**: capitalise all words except articles, conjunctions and short prepositions; no final punctuation. For hyphenated words, capitalise the second part if it can stand alone | B, D §7.1 | W `title.case`, E `title.period` |
| 3.2 | Abbreviated running title if the title is too long for the running head (`\titlerunning`) | D | W `title.running` |
| 3.3 | Authors: **given name(s) in full, then family name(s)**. Affiliations marked with superscript numbers (`\inst{1,2}`), used only when there are several | B §4.2, D §7.2 | W `authors.initials` |
| 3.4 | **ORCID encouraged**: `\orcidID{0000-…}` / superscript "[0000-…]". In print it is replaced by an icon | B §4.3, D | W `authors.orcid` (missing), E malformed |
| 3.5 | **Exactly one corresponding author**, whose e-mail is mandatory. Published papers mark the author "(✉)", and source B allows an asterisk | B §3.1, P | E `authors.corresponding`, `authors.email` |
| 3.6 | Affiliation includes the town/city and the country | C (2023) | W `affiliations.place`; E `affiliations.unused` |
| 3.7 | Abstract **150-250 words**, one paragraph, no footnotes. Published LNNS abstracts: 177-200 words, unstructured | D, B §3.7, P | E `abstract.words`; W `abstract.citations`, `abstract.paragraphs`, `abstract.structured` |
| 3.8 | Keywords: first letter capitalised. Separated by `\and` in LaTeX (printed "·"), by commas in Word. **No official count**: the samples show 3, published papers use 5-6, and conferences commonly ask for 3-5 | D, E, P | W `keywords.count` (outside 3-6), `keywords.case` |

## 4. References and citations

| # | Requirement | Source | Rule |
|---|---|---|---|
| 4.1 | Citation style. Source B (LNNS) defaults to author–year ("Harvard"), but numbered citations "[3, 7, 12]" are allowed "if customary in your field". The llncs template "prefer[s] square brackets and consecutive numbers" ([9], [4–6, 9]). **Follow the conference.** The skill builds numbered citations, which is what LNNS CS conferences use in practice | B §3.9, D, P | W `cite.style` |
| 4.2 | Numbered lists are ordered **by order of citation or alphabetically** (alphabetical is "preferred" in C 2026; `splncs04.bst` sorts alphabetically; published LNNS papers use both). The skill supports both via `citation_order` + `renumber_refs.py` | B, C, D, P | E `cite.order` |
| 4.3 | Every reference is cited and every citation is in the list | B | E `cite.range`, `cite.unused` |
| 4.4 | splncs04 format, e.g. "Author, F., Author, S.: Title. Journal **2**(5), 99–110 (2016)". See `reference-style.md` | D | W `refs.format` |
| 4.5 | DOIs "strongly encouraged" (`\doi{}` in LaTeX) | B, D | W `refs.doi` |
| 4.6 | Lists of more than six authors are shortened to "et al." | B | W `refs.etal` |
| 4.7 | **Latin alphabet only**. Transliterate, and add "(in Russian)"-style language notes | B | E `refs.latin` |
| 4.8 | Web pages give an access date, e.g. "last accessed 2026/10/25" | D | W `refs.url`, `refs.web` |
| 4.9 | Not in Springer's rules, but taken from published practice (P): 10-38 references (median about 34), 39-65 % from the last 5 years | P | W `refs.count` (<15), `refs.recent` (<40 %) |

## 5. Figures and tables

| # | Requirement | Source | Rule |
|---|---|---|---|
| 5.1 | Numbered, captioned and **cited in the text** | B | E `figure.ref`, `table.ref` |
| 5.2 | Vector graphics preferred. Line art at least 800 dpi (preferably 1200). Lettering at least 6 pt. No official value for photos; the skill warns below 300 dpi | B | W `figure.resolution` |
| 5.3 | Printed in black and white unless arranged otherwise, so colour figures must stay clear in greyscale. Do not rely on colour alone | B, A | I `submit.figures` |
| 5.4 | **Alt text for every figure** (EU Accessibility Act). LaTeX `\Description{}`; for Word, an Excel list is acceptable. If missing, typesetters or AI create it and authors check it in the proofs | A, B, D | W `figure.alt`; builder writes `\Description` and the Word image description |
| 5.5 | Tables and equations editable, not images. No `wrapfigure` / `subfigure` | B, D | E `equations.images` |
| 5.6 | Third-party material needs permission (Springer Nature Permissions Checklist) | A | I `submit.package` |

## 6. Ethics, licence, policies

| # | Requirement | Source | Rule |
|---|---|---|---|
| 6.1 | Original work, not published or under review elsewhere. COPE / Springer Nature policies apply. Volume editors may run a plagiarism check; Springer publishes **no similarity threshold** | A, B | I `submit.original` |
| 6.2 | **Disclosure of Interests is mandatory** (since llncs v2.23, 2023), e.g. "The authors have no competing interests to declare that are relevant to the content of this article." (Published papers do not always show it, but the current templates and checklist require it.) | B §9, D | E `credits.disclosure` |
| 6.3 | Funding goes in Acknowledgments with the grant number ("This study was funded by X (grant number Y)") | B, D | W `credits.funding` |
| 6.4 | Licence to Publish: one corresponding author signs for all, **by hand**, unmodified. Authorship cannot change after submission | A, B | I `submit.ltp` |
| 6.5 | AI cannot be an author. AI-generated text must be human-verified and disclosed: a first-page footnote ("This chapter was prepared with the assistance of AI. See disclosure at the end of chapter…") plus an end-of-chapter statement naming the tool, version and date | F | I `ai.policy`, `ai.disclosure`; builder adds both when `ai_disclosure` is set |
| 6.6 | Preprints may be posted at any time (not under a CC licence). The accepted manuscript has a 12-month embargo, except on the author's own site | G | (info) |
| 6.7 | Data availability statement only if the conference uses Springer Nature figshare | B §4.5 | (info) |
| 6.8 | Appendix: before the references, headed "Appendix", numbered continuously with the main text | B §10 | W `body.order` |

## 7. Length

| # | Requirement | Source | Rule |
|---|---|---|---|
| 7.1 | **Set by the conference**: "Please follow instructions provided by the conference organisers". No Springer minimum or maximum for LNNS | B §3.2, A | `conference.max_pages` / `min_pages` → E `pages` with `--pdf`; W `conference.pages` if unset |
| 7.2 | For comparison, LNCS full papers are 12-15 pages and papers under 4 pages may go to the back matter. Published LNNS papers ran 12, 13 and 19 pages | C §4.2, P | W `pages` (>15 or <4 when no limit is given) |

## Conflicts and how the skill resolves them

1. **Citation style.** B (LNNS) names Harvard as the default, while the llncs template and every
   reviewed LNNS paper use numbered citations. The skill builds numbered citations and warns if it
   finds author–year citations. If a conference asks for author–year, the reference list stays
   valid, but the in-text citations must be rewritten by hand.
2. **Reference order.** Citation order and alphabetical order are both allowed. The default is
   `citation`, because that matches a hand-numbered draft. Switch with
   `renumber_refs.py --order alphabetical` if the conference prefers it or uses splncs04 with BibTeX.
3. **Paragraph indent.** Word uses 0.4 cm and LaTeX 15 pt (0.53 cm). Each output follows its own
   template.
4. **Keyword separators.** Word uses commas and LaTeX `\and` (printed "·"). Again, each output
   follows its own template. Springer re-typesets the final version anyway.
5. **Template version.** Springer's 2026 zip carries llncs "v2.25 (2026-09-03)", which adds
   `\Description`. CTAN carries v2.26 (2025-02-25). The CTAN file is bundled because it is CC BY 4.0,
   and the generated preamble defines `\Description` as a fallback, so the output compiles with
   either.
6. **Corresponding-author mark.** Published papers show "(✉)", and B also allows an asterisk. The
   builder writes "(✉)": `\Envelope` from `bbding` in LaTeX, the U+2709 symbol in Word.
