# ASAC requirements for submitted papers

Journal: **Міжвідомчий науково-технічний збірник «Адаптивні системи автоматичного
управління»** (Interdepartmental scientific-technical journal «Adaptive Systems of
Automatic Control», ASAC). ISSN 1560-8956, Igor Sikorsky Kyiv Polytechnic Institute.
Site: <https://asac.kpi.ua> (OJS).

Sources, as captured on 2026-10-23:

1. "Подання" / "Керівництво для авторів": <https://asac.kpi.ua/about/submissions>
   (Wayback snapshot 2026-10-03; the live site was unreachable from outside Ukraine).
2. Official samples: `sample_ua_.docx` and `sample_eng_.docx`, bundled as
   `assets/official/sample_ua.docx` and `assets/official/sample_eng.docx`
   (snapshots 2026-05-08).
3. "Політика використання ШІ": <https://asac.kpi.ua/AIpolicy> (snapshot 2026-06-12).
4. Published papers in № 1 (48) 2026 and № 2 (49) 2026; see
   `published-papers-review.md`.

The "Rule" column is what `scripts/check_paper.py` enforces (E = ERROR, W = WARN,
I = INFO reminder). Where the guide, the sample and published practice disagree,
see "Conflicts" at the end.

## 1. Submission

| # | Requirement (source 1 unless noted) | Rule |
|---|---|---|
| 1.1 | Submit only through the online system at asac.kpi.ua, with a registered account | I `submit.channel` |
| 1.2 | Accepted types: original (experimental or theoretical) papers, reviews, short communications. Reviews are mostly invited; uninvited reviews follow the "Пропозиція оглядової статті" procedure | `article_type` |
| 1.3 | Language: Ukrainian or English | E `meta.required` (`language`) |
| 1.4 | File: Word .doc/.docx. **PDF is not accepted** | E `docx.format`; builder refuses non-.docx output |
| 1.5 | The author confirms the work is unpublished (except as an abstract, part of a lecture, review or thesis), not under review elsewhere, and approved by all co-authors and by the institution where it was done | I `submit.confirm` |
| 1.6 | Attach an expert-commission act on the possibility of open publication (акт експертизи, sealed, 1 copy) for authors from Ukraine | I `submit.attachments` |
| 1.7 | Attach a permission letter from the rights holder for any borrowed tables or figures | I `submit.attachments` |
| 1.8 | Declare all financial support and any relationship that could be a conflict of interest | I `submit.attachments`; `funding` / `conflict_of_interest` fields |
| 1.9 | Revised resubmission: (1) the revised text with changes marked; (2) a cover letter answering each reviewer comment point by point | SKILL.md "Revisions" |
| 1.10 | Licence: CC BY. Authors keep copyright and may self-archive (arXiv, personal site), before or after submission | (info) |
| 1.11 | AI (source 3): an LLM cannot be an author. Generative-AI use must be documented in "Materials and methods". AI language editing need not be declared | I `ai.policy` |

## 2. Structure

| # | Requirement | Rule |
|---|---|---|
| 2.1 | Length: **5-10 pages**, up to 15 by decision of the editorial board | `--pdf`: E <5 or >15, W 11-15 |
| 2.2 | Original paper / short communication: authors' surnames and initials; title; Introduction; Materials and methods; Results; Discussion; Conclusions; acknowledgements and funding (optional); references; structured abstracts and keywords in Ukrainian and English | E no Introduction/Conclusions; W no Methods/Results/Discussion (synonyms accepted, e.g. "Results and discussion" as in the sample) |
| 2.3 | Review: authors; title; Introduction; text divided into parts; Conclusions; **disclosure of interests**; references; structured abstracts and keywords (UA and EN) | E `review.disclosure` |
| 2.4 | Title: short and informative, without atypical acronyms or abbreviations | W `title.*` |
| 2.5 | Introduction: principles of the study, history, previous work, aims. Summarise the significant literature; **10-15 references to international papers from the last 5 years are recommended**. It must **end with the problem statement** and **contain no figures or tables** | E `intro.floats`; W `intro.citations`, `intro.problem`, `refs.recent` |
| 2.6 | Materials and methods: objects and methods detailed enough to reproduce; known methods by reference; new or modified methods with justification and limits. Human or animal studies state compliance with ethical standards at the end of the section | I `ethics` |
| 2.7 | Results: representative results only, without evaluation (it may point to the Discussion). Tables and figures numbered in order, each placed right after its first mention. Statistical treatment for experimental work | W `figure.ref`, `table.ref` |
| 2.8 | Discussion: interpret the results against what is known, compare with other work, explain the new understanding | W `body.discussion` |
| 2.9 | Conclusions: what is new and how it is better than existing solutions, and the significance for researchers in the field, in other fields and in practice. **Usually 5-10 sentences.** End with directions for further research | W `conclusions.length`, `conclusions.future` |
| 2.10 | Disclosure of interests (optional, mandatory for reviews): starts with "Ця робота була підтримана..." / "This work was supported..."; the full official name of the funder; full grant numbers separated by commas; organisations separated by semicolons | W `funding.prefix` |
| 2.11 | Acknowledgements (optional): as short as possible, with the consent of those named | `acknowledgements` field |

## 3. References

| # | Requirement | Rule |
|---|---|---|
| 3.1 | Format: **DSTU 8302:2015** (the sample links `dstu-8302-2015.pdf`). Use EndNote or an online generator | W `refs.format`; see `reference-style.md` |
| 3.2 | Give the **DOI** of every reference that has one | W `refs.doi` |
| 3.3 | No unpublished data or personal communications in the list. Cite them in the text instead, e.g. (Журавель І., 2026, неопубліковані дані) | E `refs.unpublished` |
| 3.4 | Every citation in text, tables and captions must be in the list | E `cite.range`, `cite.unused` |
| 3.5 | In-text citations: **Arabic numerals in square brackets, numbered in order of first appearance** | E `cite.order`, `cite.style` |
| 3.6 | The literature review must be current and closely related to the topic | W `refs.recent`, `refs.count` |

## 4. Abstracts, keywords, author information (at the end of the file, on separate pages)

| # | Requirement | Rule |
|---|---|---|
| 4.1 | Two abstracts, Ukrainian and English, **200-250 words, at most 1800 characters** each | E >1800 chars; W outside 200-250 words |
| 4.2 | Structured, with named parts: **Проблематика, Мета, Методика реалізації, Результати, Висновки** (EN: Background, Objective, Methods, Results, Conclusions). The purpose is 1-2 sentences | E missing part; W plain-text abstract |
| 4.3 | No references in the abstract; no abbreviations except the most common | E `abstract.*.citations`; W `abstract.*.abbreviations` |
| 4.4 | Keywords in Ukrainian and English: **5-20 words or phrases** (submission checklist); "up to ten, in addition to those in the title" (author guide); avoid single words and polysemous terms | E <5 or >20; W >10, single words; I repeats the title |
| 4.5 | Author information in **both languages**: (1) article title; (2) full name (surname, given name, patronymic); (3) ORCID (mandatory); (4) degree; (5) academic rank; (6) place of work and position; (7) e-mail; (8) contact phone, and the corresponding author must be marked; (9) ScopusID, ResearcherID if any | E ORCID, e-mail, position, corresponding author with phone; W degree, patronymic; I Scopus/ResearcherID |
| 4.6 | Sample end-matter layout (source 2): UDC; bibliographic line "**Title** / Surname I.I., ... // Міжвідомчий науково-технічний збірник «Адаптивні системи автоматичного управління». – year. – № N (NN). – с."; counts "Бібл. N, іл. N, табл. N"; Анотація; Ключові слова. Then the same in English ("Ref. N, fig. N, tab. N"). Then "Про авторів" | builder generates it |

## 5. Layout (author guide + official sample)

| # | Requirement | Value used by build_paper.py | Rule |
|---|---|---|---|
| 5.1 | Paper | A4 | E `docx.page` |
| 5.2 | Margins | 25 mm on every side | E `docx.margins` |
| 5.3 | Main text | Times New Roman 13 pt | E `docx.font`, `docx.size` |
| 5.4 | Line spacing | 1.3 (multiple) | E `docx.spacing` |
| 5.5 | Automatic hyphenation | **off** | E `docx.hyphenation` |
| 5.6 | Paragraph indent (sample) | 12.5 mm first line, justified | builder |
| 5.7 | Title block (sample) | "UDC 004.05" / "УДК 004.05" flush left; authors as initial + surname, **bold, right-aligned**; TITLE **bold, centred, upper case**; *Abstract:* / *Анотація:* paragraph; *Keywords:* / *Ключові слова:* paragraph | builder |
| 5.8 | Section headings (sample "Heading 1") | bold, centred, 13 pt, 6 pt before / 3 pt after; "REFERENCES" / "СПИСОК ВИКОРИСТАНИХ ДЖЕРЕЛ" in capitals | builder |
| 5.9 | Sub-headings (sample "Heading 2") | bold, justified with the 12.5 mm indent | builder |
| 5.10 | Formulas | MathType or Microsoft Equation, fonts Symbol / MT Extra; never images. Number in parentheses at the right margin; "where ..." / "де ..." flush left after the formula | builder (native Word equations); W `equations.images` |
| 5.11 | Tables | inside the text, after the first mention, numbered in Arabic numerals; "*Table 1.*" / "*Таблиця 1.*" italic, right-aligned, then the title centred on the next line; self-explanatory with notes; all abbreviations explained in the notes | builder; E `table.caption` |
| 5.12 | Figures | inside the text, referred to as "Fig. 1" / "рис. 1" in order; caption below, centred: "*Figure 1.* Title" / "*Рисунок 1.* Назва"; sub-figures (а), (б), (в); high quality and legible; a figure drawn in Word must be grouped into one object | builder; E `figure.caption`, `figure.file` |
| 5.13 | Lists (sample) | bullets "–" or "1." at the paragraph indent, items ending with ";" and the last with "." | builder |
| 5.14 | Reference list (sample) | numbered "1." at the paragraph indent; heading author in *italics* ("*Xu, R.* Survey of ... / R. Xu, D. Wunsch // IEEE ... – 2005. – Vol. 16, iss. 3. – P. 645-678.") | builder + `reference-style.md` |

## Conflicts between the sources and how the skill resolves them

1. **Short abstract under the title.** The sample asks for "150-300 знаків, включаючи
   ключові слова". Every paper published in 2026 that we reviewed carries a full
   (≈100-250-word) abstract there instead. Default: repeat the full abstract in the
   article's language. Set `abstract_top` to follow the sample literally. Either choice
   is reported as INFO.
2. **Keyword count.** The checklist says 5-20 and the author guide says up to 10. Fewer
   than 5 or more than 20 is an ERROR, more than 10 a WARN.
3. **Minimum length.** The sample says "не менше 5 сторінок (вимога ВАК)" and the guide
   says 5-10 (15). Both give a minimum of 5.
4. **Figure/table caption style.** Published papers vary: some use "Table 3. **Title**"
   on one centred line, and some captions are not italic. The builder follows the
   official sample, which is the stated template.
5. **Reference style.** Published lists mix DSTU 8302:2015, APA-like and ad-hoc formats.
   The guide requires DSTU 8302:2015, so the skill normalises every entry to the
   sample's DSTU form (`reference-style.md`).
6. **IMRaD headings.** The guide prescribes Introduction / Materials and methods /
   Results / Discussion / Conclusions. Recent papers often use descriptive headings
   instead ("Постановка задачі", "Experimental study"). The checker accepts synonyms
   and only WARNs when the methods, results or discussion part is absent.
