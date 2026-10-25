---
name: vottp-paper-format
description: Format and check an author manuscript for «Вимірювальна та обчислювальна техніка в технологічних процесах» (ВОТТП, VOTTP, Measuring and computing devices in technological processes, vottp.khmnu.edu.ua). Produce an editable Word manuscript and a sourced formatting/content compliance report, preserving equations, tables, images and scientific claims. Use for preparation, formatting checks and revised submissions to this journal.
---

# VOTTP paper formatter

Prepare an editable `.docx` and a requirement-by-requirement report. Formatting can
support submission readiness; acceptance depends on editorial and peer review.

Read [requirements.md](references/requirements.md) before formatting. It records
the official rules, unresolved contradictions and their sources, checked
**2026-10-25**. Recheck the linked author and policy pages for a new submission;
record changes in the working report. If unavailable, identify the snapshot date.
Read [published-papers-review.md](references/published-papers-review.md) for three
recent examples and [formatting-workflow.md](references/formatting-workflow.md)
for the helper's role map, layout choices and limitations.

## Intake and content review

1. Work in a submission directory outside the skill. Retain the original input.
   For `.docx`, preserve its OOXML rather than reconstructing paragraphs from text.
   For `.md`/`.tex`/`.odt`, convert a copy with an available Word-capable converter,
   preserving native equations and media, then inspect the result. For PDF-only
   input, request editable source; reconstruction, if necessary, needs explicit
   verification of every formula, table and citation.
2. Inventory the manuscript and review the full content against requirements
   F01–F07, M01–M06, C01–C05 and P01–P05. Distinguish missing material from layout
   defects. Preserve author wording and section order for a formatting-only request;
   propose structural/content changes separately. Never invent research, results,
   references, identity details, UDC, permissions or editorial approval.
3. Verify bilingual titles, names, affiliations, qualifications, ORCIDs, contacts,
   abstracts and keywords. Report absent fields. Ask for missing identity facts in
   one concise request while progressing with layout. Translations may derive only
   from supplied material and must be identified for author review.
4. Map the manuscript to problem/significance, literature analysis, aims, main
   material, and conclusions/future work. Equivalent English headings are acceptable;
   do not impose ASAC's IMRaD or end-page-abstract rules on this journal.
5. Check that claims in abstracts and conclusions match presented evidence;
   inspect tables for missing values, not just presence. Review methods, evaluation
   conditions, comparison baselines and limits appropriate to the article type.
   Identify gaps for the author; do not manufacture experiments to fill them.
6. Preserve either DSTU 8302:2015 or APA consistently. Number references by first
   citation, verify cited/listed correspondence, retain full URLs and verify assigned
   DOIs before adding them. Include the Latin-script References list required by the
   guide. Check the prohibited-source and self-citation rules; report questionable
   entries and any proposed replacements instead of silently deleting them.

## Format and verify

The bundled helper requires Python 3.10+, `uv` and `lxml` (PEP 723 dependency).
Resolve `S` to this skill's actual installed directory; in Claude Code it is
`${CLAUDE_SKILL_DIR}`, while other hosts may expose a different path.

```bash
uv run "$S/scripts/vottp_docx.py" inspect draft.docx --out work/roles.json
# Read roles.json and assign every paragraph its semantic role; see formatting-workflow.md.
uv run "$S/scripts/vottp_docx.py" format draft.docx --roles work/roles.json --out work/paper.docx
uv run "$S/scripts/vottp_docx.py" check work/paper.docx --roles work/roles.json --original draft.docx --out work/layout-report.json
```

The default profile applies the detailed guide: A4 portrait, margins left 25/right
15/top 25/bottom 25 mm, Times New Roman 10 pt, line spacing 1.3. Roles apply alignment
and heading treatment without guessing paragraph meanings. `--profile published`
is an optional imitation of observed front matter, with 12 pt titles/authors and
8 pt metadata/abstracts/references; identify it as an observed convention, not a
replacement for the guide. Never use the generic 12 pt/single-spaced checklist as
the undisclosed default.

The helper preserves text, equations, links, media, tables and unrelated package
parts; it verifies preservation before writing. It does not compose missing front
matter, translate or renumber citations, resize tables/figures, convert floating
images, render pages or judge scientific quality. Resolve reported defects with
an appropriate document editor, preserving native objects, then rerun checks.
Tracked revisions must be resolved by the author before applying this helper.

Render the final DOCX with Word or LibreOffice and inspect **every page**, especially
bilingual front matter, equations, captions, table widths, broken rows and page
breaks. A usable LibreOffice command is:

```bash
soffice --headless --convert-to pdf --outdir work/preview work/paper.docx
pdftoppm -scale-to 1400 -png work/preview/paper.pdf work/preview/page
```

Use a fresh LibreOffice user profile if another instance holds its lock. Verify
fonts are installed; substitution affects layout and length. Record the actual
rendered page count against F04. Without rendering, mark length and visual QA
**NOT VERIFIED**; do not infer pages from DOCX metadata. Keep the PDF as a preview;
deliver the editable Word manuscript for submission.

## Deliver

Deliver the `.docx`, preview if rendered, and a report with rows:
`rule ID | PASS / FAIL / NEEDS AUTHOR / EDITOR CLARIFICATION / NOT VERIFIED |
evidence/location | action`. The automated JSON is only the layout subset of this
report. Include the chosen profile, original/output paths, preservation result,
page count, unresolved source conflicts, content changes/translations, missing
author information, and manual checks still pending.

List the submission materials from P01 and prepare an accurate AI-use disclosure
under P03, including assistance performed during formatting. Do not inherit an
AI-language-editing exemption from another journal. Do not invent model versions.
The journal describes double-blind review while requesting named front matter:
retain an identified master and flag the anonymous-file procedure for clarification;
make an anonymized copy when requested without losing the master.

Call the result **formatted with listed checks complete**, or **ready for author
review** if issues remain. Do not claim acceptance or complete compliance while
an unresolved rule, placeholder, unreviewed translation or unverified check remains.
Submission, editor contact and payment require the user's corresponding request.
