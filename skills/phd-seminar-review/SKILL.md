---
name: phd-seminar-review
description: Verifies the CONTENT of a PhD (доктор філософії) talk for specialty 121 «Інженерія програмного забезпечення» (F2) at Igor Sikorsky KPI before the department seminar (фаховий семінар, попередня експертиза дисертації), the faculty academic council (вчена рада) or the defence before a разова спеціалізована вчена рада, and produces a slide-by-slide review report with ERROR/WARN/INFO findings and concrete rewrite suggestions. Checks the title slide, relevance, object/subject/aim, tasks, scientific novelty (gradation «вперше/удосконалено/набуло подальшого розвитку», distinction, effect), the KPI 121 rule that one scientific result must be a software architecture, tasks↔novelty↔conclusions traceability, quantitative results, publications and approbation against Постанова КМУ №44, implementation acts, Ukrainian scientific style (calques, abbreviations) and readability. Use when the user asks to check, review, verify or перевірити a seminar/defence presentation (.ppt, .pptx, .odp, .key, .pdf), "перевір презентацію на семінар", "чи готова презентація до вченої ради", "рецензія на презентацію дисертації", optionally against the dissertation text. Reviews only; never invents results, numbers or publications, and does not edit the deck unless asked.
---

# PhD seminar talk review (KPI, specialty 121)

Checks whether a dissertation talk will survive the seminar or the council: is everything
the regulations require on the slides, is the scientific novelty formulated so that it can be
defended, does it fit **121 «Інженерія програмного забезпечення»**, and will the slides be
readable from the back of the room. Output: `review/report.md` for the candidate.

Pipeline: **intake → `check_deck.py` (automatic rules) → `extract_deck.py` + full read
(content review) → `render_preview.py` (visual check) → report → (optional) fixes**.

Requirements:

1. `uv`. The scripts are PEP 723 and fetch python-pptx, python-docx, PyMuPDF and Pillow.
2. LibreOffice (`soffice`) for `.ppt`/`.odp`/`.key` input and for the preview. Without it,
   ask for `.pptx` or `.pdf`, and skip the visual check (say so in the report).

References, loaded on demand:

1. `references/rules.md`: every rule code `check_deck.py` prints, its severity and its
   source. Read it before writing the report.
2. `references/requirements.md`: the regulations (Порядок №44, Вимоги до оформлення
   дисертації, KPI procedure, 121 scope, the architecture rule) with sources and dates.
3. `references/review-checklist.md`: the manual content review, slide by slide, plus the
   questions council members typically ask. This is the core of the review.
4. `references/sample-structure.md`: the slide sequence of a real 121 KPI defence talk
   (2024), anonymised, with what it did well and what this skill flags. Use it as an example
   of the expected structure; if the user's deck *is* that talk, don't copy the findings —
   review it independently.

Work in a directory next to the user's deck (default `./review/`), never inside this skill.

## 1. Intake

1. Get the deck path. Never modify the original; all outputs go to `review/`.
2. Ask in **one** message, only if not already clear:
   1. the event: department seminar (попередня експертиза), faculty council, or defence
      before the разова рада; and the talk length in minutes (default 20 for a seminar,
      15–20 for a defence);
   2. the dissertation or its autoabstract / анотація (`.docx`/`.pdf`), if they have it:
      it enables the topic/object/novelty cross-check;
   3. the approved topic wording (from the наказ) if the dissertation is not available.
   Proceed with defaults if the user does not know; record the assumption in the report.
3. If the deck is not for specialty 121 (e.g. 122, 126, F3), say that this skill's
   architecture and specialty-fit rules do not apply, and ask before continuing.
4. Judge against the rules in force on the event date (`requirements.md` lists recent
   changes). For an old deck (e.g. a past defence used as a sample), say which findings come
   from rules that did not exist then.

## 2. Automatic checks

```bash
S="${CLAUDE_SKILL_DIR}/scripts"
uv run "$S/extract_deck.py" talk.ppt --out review     # also writes review/converted/talk.pptx for .ppt/.odp/.key
D=review/converted/talk.pptx                          # or the original if it is already .pptx/.pdf
uv run "$S/check_deck.py" "$D" --minutes 20 --json review/findings.json \
    [--dissertation dissertation.docx] [--candidate Прізвище]
uv run "$S/render_preview.py" "$D" --out review/preview
```

Converting once and passing the `.pptx` to the other scripts saves two LibreOffice runs.

1. `check_deck.py` prints `ERROR`/`WARN`/`INFO` lines with rule codes and slide numbers,
   then the detected structure and a `SUMMARY`. Exit 1 = there are ERRORs; exit 2 = the
   file could not be read (fix the input, e.g. re-save as .pptx).
2. Check the `STRUCTURE` block first. If a section was not detected (`—`) but exists
   (unusual title), or the candidate/topic is wrong, the related findings are false:
   rerun with `--candidate`, or note the false positive and drop it. The script is a
   heuristic; **you** decide what goes into the report.
3. The script cannot judge meaning. Every finding it does not make (logic, wording,
   specialty fit, numbers that contradict each other) comes from step 3.

## 3. Content review (the main part)

Read `review/deck.md` **in full**. It holds only the text of text boxes and tables: text
inside pictures (SmartArt saved as an image, screenshots, charts as images, OLE formulas) is
missing. For every slide marked «⚠ на слайді є зображення», read `review/preview/slide-NN.png`
for **content**, not only layout. Then go through `references/review-checklist.md`
section by section. For every problem record: slide, what is wrong, why the council will
care (the rule or the typical question), and a concrete fix — a rewritten sentence where
the fix is wording. Key points that always get checked:

1. **Title slide** matches the approved topic **verbatim**, specialty «121 Інженерія
   програмного забезпечення», supervisor with degree and title, KPI, city and year.
2. **Object ⊃ subject**, aim as a result (not an action), tasks as infinitives that lead to
   the aim, methods named and tied to the tasks.
3. **Scientific novelty**: every item has a gradation, says what it is (model / method /
   architecture …), how it differs from the known ones, and what this gives (ideally a
   number). Nothing is «вперше» if it is a modification of a known method.
4. **Architecture rule (KPI, 121)**: at least one novelty item is a software architecture
   (of a system, platform, framework …) with its distinguishing feature, and a dedicated
   slide shows it as a diagram (components, connectors, deployment or data flow) — not a
   block-diagram of an algorithm. If missing, this is an ERROR; propose how the
   candidate's existing software result can be formulated as an architecture result, but
   do not invent properties the work does not have.
5. **Specialty fit (121)**: results are about how software is built, analysed, verified or
   operated (architecture, models and methods of software development, quality, testing,
   requirements, DevOps …), not only about the application domain or a mathematical
   algorithm. Flag items a reviewer would call 122/124/126/151 work.
6. **Traceability**: each task → a result slide → a novelty item and/or a conclusion; the
   same numbers everywhere (27 % on a result slide must not become 30 % in conclusions).
7. **Evidence**: experiments with a baseline, metrics, data set/conditions; the effect is
   quantified. Practical value: acts of implementation (акти впровадження), repository,
   deployed system.
8. **Publications and approbation** satisfy Порядок №44 (see `requirements.md`): count,
   journal categories, candidate's authorship, conferences. Do not decide the count rule
   from memory; use `requirements.md` and say if the user's case is borderline.
9. **Language and style**: scientific Ukrainian, no calques (L01 list is not exhaustive),
   typos (especially in titles — they are projected large), abbreviations expanded on
   first use, consistent terminology.
10. **Form**: ≈1 slide per minute, ≤ ~100–150 words per slide, readable fonts (≥ 14–16 pt
    on 16:9), numbered slides, diagrams legible, no slide that only the speaker understands.

Then open `review/preview/contact-sheet.png` and every slide the review flagged
(`review/preview/slide-NN.png`): text overflow, overlaps, unreadable diagrams/formulas,
low-contrast colours, cut-off tables.

## 4. Report

Write `review/report.md` in Ukrainian (if you run as a subagent that may not write report
files, return the full report text instead and say so) (the user's language if they wrote otherwise):

1. **Вердикт** in one line: «готова», «готова після дрібних правок» or «потребує
   доопрацювання», with the count of ERROR/WARN.
2. **Критичні зауваження** (ERROR): must be fixed before the event (seminar, council or
   defence — name it).
3. **Зауваження** (WARN), grouped: structure, novelty & architecture, evidence,
   publications, language, form. Each: `слайд N` — problem — why — proposed fix.
4. **Рекомендації** (INFO and nice-to-have).
5. **Ймовірні запитання ради** (5–10) tailored to *this* talk, each with a hint of what a
   good answer must contain.
6. **Що не перевірялось** (no dissertation provided, no LibreOffice, PDF without notes …).

Keep it concrete: quote the slide text you criticise and give the rewrite. Do not pad the
report with generic advice that does not apply to this deck. Give the user the absolute
path of `report.md` and a 5–10 line summary in chat.

## 5. Fixes (only if asked)

If the user asks to apply the fixes, edit a **copy** of the deck (`*_reviewed.pptx`) with
python-pptx, changing text only (no layout redesign unless asked), rerun step 2 on the copy
and report what changed. Wording for novelty, aim or conclusions is a proposal the candidate
and supervisor must approve; list it as such.

## Rules

1. Never invent results, numbers, publications, acts, conferences or properties of the
   architecture. If something is missing, say what must be added and leave a placeholder
   in proposed text (`[N %]`, `[назва організації]`).
2. Requirements change: if the user has a newer KPI/department document or the rules on
   `requirements.md`'s sources differ, the newer document wins — tell the user and update
   `requirements.md`.
3. Don't upload the deck or dissertation anywhere; they contain unpublished results and
   personal data.
4. Respect the candidate's work: separate «порушує вимогу» from «рада може спитати» from
   «смак». Only the first is an ERROR.
