# Review of three recently published LNNS papers

Purpose: to see how Springer actually typesets accepted LNNS papers, how strictly the author
instructions (`requirements.md`) are enforced, and which choices the skill should copy.

1. **Selection.** Three open-access chapters from 2025-2026, picked through Crossref
   (`issn:2367-3370`, CC BY / CC BY-NC-ND licence). All three are in software engineering, AI or
   platform engineering, and each comes from a different volume and conference.
2. **How they were read.** The full-text PDFs were measured with PyMuPDF for page size, fonts and
   sizes, word counts and reference counts.
3. **Date.** Reviewed 2026-10-25.

| | Paper A | Paper B | Paper C |
|---|---|---|---|
| Title | "SKY CONTROL …" (multi-cloud software architecture) | LLMs for personality-trait prediction (prompt engineering) | The e-DIPLOMA educational platform |
| Authors | C. Baun, H.-N. Cocos, M. Kappes | J. S. John, S. George, D. Mukhopadhyay | V. Burkus, A. Castelli, Á. Sike, L. Szécsi, G. Tomcsányi |
| DOI | 10.1007/978-981-96-9709-0_4 | 10.1007/978-3-032-22911-3_7 | 10.1007/978-3-031-84170-5_4 |
| Volume | LNNS 1440: ICICT 2025 (Springer Singapore) | LNNS 1929: SCIS 2025 (Springer Cham) | LNNS 1274: MIS4TEL / ETELT 2024 (Springer Cham) |
| Online | 2025-10-19 | 2026-04-16 | 2025-03-07 |
| Pages | 49-67 (**19**) | 86-98 (**13**) | 37-48 (**12**) |
| Template | **svmult** (book chapter), *not* llncs | llncs, re-typeset by Springer in Times | llncs, the authors' own LaTeX (Computer Modern) |

All three printed books use a 155 × 235 mm page with a 10 pt body. Springer adds the following
itself:

1. the "© The Author(s)" line;
2. the "Eds.: CONF, LNNS N, pp. x–y, year" and DOI footer;
3. running heads ("J. S. John et al." / the title);
4. the Crossmark logo and the open-access licence block.

## Paper A: SKY CONTROL (LNNS 1440, svmult layout)

1. **Title block.** Bold author names with no superscripts. The affiliation, e-mails and URL sit in
   a block at the foot of page 1 at 8.5 pt. The corresponding author is marked "C. Baun (✉)". No
   ORCIDs.
2. **Abstract and keywords.** "**Abstract**" (no period) introduces 200 unstructured words at
   10 pt. "**Keywords**" introduces 5 keywords separated by "·", in sentence case.
3. **Sections.**
   1. 1 Introduction
   2. 2 Background and Related Works (2.1)
   3. 3 Methodology
   4. 4 Concept of SKY CONTROL (4.1-4.4)
   5. 5 Impact of the Project
   6. 6 Conclusion and Outlook

   Subsections are 12 pt bold italic. "Acknowledgements" (British spelling) is a run-in paragraph.
   There is **no Disclosure of Interests**.
4. **Floats.** 4 figures and 2 tables. Captions read "**Fig. 1** …" and "**Table 1** …" with no
   period after the number, at 8.5 pt. Figure captions are below, table captions above. Tables have
   vertical rules.
5. **References.** 38 entries, numbered and sorted **alphabetically**, in the Springer "basic"
   author–year style ("Li S, Zhou Y, … (2015) Towards … IEEE Trans Serv Comput 8(3):398–409").
   None has a DOI, 39 % are from 2021 or later, and several entries are incomplete.
6. **Against llncs.** The whole layout is different (svmult). At 19 pages it is far above the usual
   10-15.

## Paper B: LLM personality prediction (LNNS 1929, llncs re-typeset by Springer)

1. **Title block.** "Juswin Sajan John, Shiju George(✉), and Debarka Mukhopadhyay". There is one
   affiliation, so no superscripts; it still contains a typo ("AI ans Data Science"), so nobody
   copy-edited it. The e-mails are in monospace, one per line. No ORCIDs.
2. **Abstract and keywords.** "**Abstract.**" introduces 177 unstructured words at 9 pt, as an
   indented block. "**Keywords:**" introduces 5 keywords separated by "·", in Title Case.
3. **Sections.**
   1. 1 Introduction
   2. 2 Literature Review (2.1-2.4)
   3. 3 Methodology (3.1, 3.2, and **numbered level-3 headings 3.2.1-3.2.4**)
   4. 4 Results and Discussions
   5. 5 Conclusions and Future Scope

   There are **no Acknowledgments and no Disclosure of Interests**. A GitHub repository is
   mentioned but not linked.
4. **Floats.** 5 figures, two of them raster screenshots, and 5 tables. Captions read
   "**Fig. 1.** Proposed Methodology" and "**Table 1.** …", at 9 pt, figure below and table above.
   Tables have internal vertical rules. Maths is inline only.
5. **References.** 34 entries, numbered in **citation order**, splncs04 style ("Kernberg, O.F.:
   What is personality? J. Pers. Disord. 30(2), 145–156 (2016)"), cited as "[3–5]". None has a DOI,
   65 % are from 2021 or later, and two are arXiv preprints.
6. **Against llncs.** Numbered level-3 headings, vertical rules in tables, and no Disclosure of
   Interests even though the current template asks for one.

## Paper C: e-DIPLOMA platform (LNNS 1274, the authors' own llncs LaTeX)

1. **Title block.** "Viktória Burkus¹(✉), Andrea Castelli²(✉), Ádám Sike¹, László Szécsi¹(✉), and
   Gergely Tomcsányi¹(✉)": superscript affiliation numbers, and **four** authors marked as
   corresponding. The e-mails are grouped as "{burkus,sike,szecsi,tomcsanyi}@iit.bme.hu". No ORCIDs.
2. **Abstract and keywords.** 193 unstructured words at 9 pt. 6 keywords in Title Case, separated
   by "·".
3. **Sections.**
   1. 1 Introduction
   2. 2 Functionality (2.1-2.3)
   3. 3 User Interface
   4. 4 Asset Management (4.1-4.4)
   5. 5 Results and Discussion

   There is **no separate Conclusion**. "**Acknowledgments.**" names the EU grant number, and
   "**Disclosure of Interests.** The authors have no competing interests to declare that are
   relevant to the content of this article." uses the exact template wording.
4. **Floats.** 5 figures (screenshots and a chart) with captions written as full sentences,
   sometimes several lines long. No tables and no equations.
5. **References.** 10 entries, roughly in citation order. 5 are web pages ("Accessed 12 April
   2024"). One conference entry was left in a non-splncs format ("…(TALE), (pp. 23-30) (2015).
   IEEE"). No DOIs.
6. **Against llncs.** Springer did not normalise the reference list, so whatever authors submit in
   LaTeX is printed as is. There is no Conclusion heading.

## What the skill takes from this

1. **llncs is the default; svmult is the exception.** Both Cham volumes use llncs. The Singapore
   ICICT volume uses svmult. The skill builds llncs and tells the user to check the call for
   papers (`template.flavour`).
2. **Springer does not fix what authors submit.** Typos in affiliations, malformed references,
   numbered level-3 headings and missing Disclosure statements all reached print. This is why the
   checker flags them: the paper is printed as it is submitted.
3. **House style that was consistent across all three:**
   1. numbered "1 Introduction" / "2.1" headings;
   2. one unstructured abstract of 177-200 words;
   3. 5-6 keywords;
   4. figure captions below and table captions above, with a bold label;
   5. numbered [n] citations.

   The builder produces exactly these.
4. **Length.** 12-13 pages is the norm, and 19 is an outlier. The checker uses the conference
   limit from `conference.max_pages` and warns above 15 when no limit is given.
5. **References.** The counts were 10, 34 and 38, and none of the papers gave DOIs. The skill warns
   below 15 references and below 40 % recent ones, and recommends DOIs. That puts the user's paper
   above the published norm, not just at it.
6. **Disclosure of Interests.** It appeared in only 1 of 3 papers, but the current template and
   checklist require it. The checker treats a missing statement as an ERROR, because a missing
   mandatory item can hold up the camera-ready, while including it costs one sentence.
7. **Tables.** All three papers used vertical rules. llncs shows a fully ruled sample. The builder
   uses horizontal rules only (top, under the header, bottom), which is the conservative choice
   that typesetters never need to change.
