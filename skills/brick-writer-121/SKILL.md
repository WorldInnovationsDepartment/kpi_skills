---
name: brick-writer-121
description: Writes and reviews a PhD (доктор філософії) dissertation — the user calls it «brick» — for specialty 121 «Інженерія програмного забезпечення» (F2) at Igor Sikorsky KPI, part by part. Write mode drafts анотація, вступ, розділ N, висновки до розділу, загальні висновки, список джерел or додатки from the project's concept, novelty statements and facts, following the genre of defended KPI 121 dissertations (two full examples and their analysis are bundled) and the normative requirements (Постанова КМУ №44, наказ МОН №40, Стандарт №481). Analyse mode reviews a written part or the whole dissertation: automatic ERROR/WARN/INFO checks (structure, numbering of figures/tables/formulas, citations, novelty formula «вперше/удосконалено/дістало подальшого розвитку … відрізняється … дозволяє», mandatory вступ blocks, object = process, aim = result, 121 fit, architecture result, numbers traceable to tables, calques, placeholders) plus a manual opponent-style review with a written report. Use when the user says «brick», «напиши/перевір/проаналізуй розділ|вступ|анотацію|висновки дисертації», «write chapter N of my dissertation», «review my PhD chapter», «чи збирається дисертація», or asks anything about writing or checking a 121 PhD dissertation text. Never invents results, numbers, sources or acts; marks what the author must supply.
---

# Brick writer / reviewer (PhD 121, KPI)

«Brick» = the dissertation. This skill drafts it one part at a time and reviews what is
written, against (a) the normative requirements and (b) the genre of defended 121
dissertations at KPI. Everything it writes is a *draft for the candidate and the supervisor*;
every fact it does not have is marked `TODO(число|джерело|рішення|рисунок): …`, never invented.

Three modes, chosen from the request:

1. **Write** a part (анотація, вступ, розділ N or one of its subsections, висновки до розділу,
   загальні висновки, список джерел, додаток, перелік умовних позначень).
2. **Analyse** a written part: scripts + manual opponent-style review → report.
3. **Status** of the whole brick: inventory, page budget, traceability
   (завдання → розділ → новизна → публікація → висновок), «чи збирається дисертація».

Requirements: `uv` (the scripts are PEP 723; python-docx is fetched automatically). Input
parts are Markdown (preferred), `.docx` or `.txt`; for `.pdf` run `pdftotext -layout` first.

## References (load on demand, in this order)

1. `references/requirements.md` — the law and the KPI practice with rule codes `R-…`:
   structure and volume, the mandatory вступ blocks, Стандарт №481 object of specialty, the
   novelty triad, Порядок №44 publication rules, наказ №40 formatting, the architecture
   rule, typical council remarks. Read before writing or reviewing anything.
2. `references/chapter-playbook.md` — the recipe for each part: block order, sentence
   templates with slots, page budget, pitfalls, the per-result scheme for chapters 2–4, the
   experiment subsection, the session protocol. Read the section for the part in hand.
3. `references/review-checklist.md` — analyse mode: questions per part, severities, fix
   patterns, whole-dissertation traceability checks, typical opponent questions, the report
   template.
4. `references/style-guide.md` — scientific Ukrainian: register, terminology table,
   calques, sentence mechanics, micro-typography, the self-edit pass. Apply to every draft.
5. `references/dissertation-examples.md` — the two bundled defended dissertations (Барабаш
   2024, Бочок 2026): паспорти, skeletons with page budgets, novelty wording verbatim, how
   the architecture result is phrased, experiment reporting, weaknesses not to copy, and
   line pointers into the full texts.
6. `references/rules.md` — every rule code the scripts print, severity, trigger, what the
   script cannot judge.
7. `references/sources/` — the raw material: three gathered requirement documents
   (`sources/requirements/`) and the full texts of the two example dissertations plus the
   expert conspectus of Барабаш (`sources/examples/`). Open them when a distilled file is
   not enough: e.g. to model an анотація on a real one, or to quote the Standard.

## 0. Project intake (every mode)

The dissertation lives in the user's project, never inside this skill. Before anything:

1. Read the project's instructions (`AGENTS.md`, `CLAUDE.md`, `README`) and whatever they
   name as the concept document, the single source of novelty statements, and the facts /
   numbers file. These override the generic playbook: approved topic wording, decided
   object/subject/aim/tasks, the novelty items and their gradation, the agreed experiment
   design and metrics, publication list and co-author arithmetic.
2. Find the parts already written (one file per part is the convention: e.g.
   `00-anotatsiia.md`, `01-vstup.md`, `02-rozdil-1.md`, … `99-dodatky.md`; or one `.docx`).
   Read the «Висновки до розділу» of every finished chapter and the вступ's tasks: they are
   the contract the next part must honour.
3. If the project has no single-source file for the verbatim-repeated sentences (novelty
   items, aim, object, subject, tasks), propose creating `brick/novelty.md` (or the name the
   user prefers) and a `brick/traceability.md` table *before* drafting a results chapter —
   the genre repeats these sentences word for word in 5–6 places, so they must be fixed
   first (`chapter-playbook.md` §1).
4. Ask in **one** message only what is missing and blocks the work (the part to write or
   review, the chapter number and which scientific result it carries, the facts file). Make
   routine decisions yourself and state them. Default language of all output: Ukrainian
   (the dissertation language); answer in the user's language if they write otherwise.
5. Specialty check: if the project is not 121/F2, say that the architecture rule and the
   121-fit checks do not apply and continue only on request.

## 1. Write mode

1. **Fundament check.** Before chapter text, confirm the «фундамент» exists in the project:
   суперечність, наукове завдання, мета (a result: «підвищення/зменшення … шляхом …»),
   об'єкт (a process in the wording of Стандарт №481), предмет, 3–6 завдання (perfective
   infinitives, one per chapter/result), положення новизни with the triad formula. If any is
   missing or violates `requirements.md`, write that part first (or propose wording and get
   it approved); a chapter written on a shaky fundament is wasted.
2. **Outline first.** Propose the part's outline: numbered subsections with a one-line
   purpose each, the page budget (from `chapter-playbook.md` and `dissertation-examples.md`),
   which task and novelty item the chapter carries, which figures/tables/formulas it needs
   and which numbers from the facts file it will cite. Wait for approval unless the user
   asked for a fast track (`-y`, «пиши одразу»).
3. **Draft** section by section, following the recipe for that part in
   `chapter-playbook.md`, in the register of `style-guide.md`:
   1. Results chapters: per result — мотивація → означення → формальна постановка («Задано
      / Потрібно отримати») → твердження/властивості → метод/алгоритм по кроках → приклад →
      абзац-новизна (verbatim from the single source).
   2. The software-implementation chapter maps modules ↔ scientific results explicitly and
      shows the architecture as a diagram (components, connectors, deployment or data flow),
      with its distinguishing feature stated.
   3. The experiment subsection: design, baselines, metrics, dataset, conditions,
      statistical treatment, threats to validity; a table for every number that will appear
      in any conclusions.
   4. Chapter 1 is comparative, not descriptive: ≥ 1–2 tables «метод × критерій», ends with
      постановка завдання and «Висновки до розділу 1».
   5. Every chapter ends with «Висновки до розділу N»: impersonal perfective openers, one
      numbered item per result, the same numbers as in the body, the novelty sentence
      verbatim.
   6. Figures, tables and formulas are numbered within the chapter (`Рисунок 2.1 – Назва`,
      `Таблиця 2.1 – Назва`, `(2.1)`), each referenced in the text before it appears;
      citations as `[n]` against the project's reference list (ask for its numbering or keep
      `[@key]` placeholders consistently and say so).
   7. Numbers come only from the facts file / experiment logs, with their provenance in a
      comment or footnote; otherwise `TODO(число): <що виміряти>`. Sources only from the
      project's list or ones the user supplied; otherwise `TODO(джерело): …`; never
      fabricate a reference.
4. **Self-check.** Run the checker on the draft and fix what is mechanical; then do the
   self-edit pass from `style-guide.md` §8:

   ```bash
   S="${CLAUDE_SKILL_DIR}/scripts"
   uv run "$S/check_chapter.py" 03-rozdil-2.md --chapter 2 --json review/rozdil-2.json
   ```

5. **Hand back** (`chapter-playbook.md` §10.3): the file path; a numbered list «Що треба
   від автора» (every `TODO(…)`, with what exactly is needed and where); which sentences
   are proposals that the supervisor must approve (novelty, aim, conclusions wording); the
   traceability row(s) this part fills or changes; and the remaining checker findings you
   chose not to fix, with why.

Write the whole part the user asked for. If a subsection depends on facts you do not have,
write it with placeholders rather than skipping it, and list them.

## 2. Analyse mode

1. Automatic checks first (never modify the user's file in this step):

   ```bash
   S="${CLAUDE_SKILL_DIR}/scripts"
   uv run "$S/check_chapter.py" path/to/part.md [--kind rozdil --chapter 2] [--max-ref 154] [--first-citation-order] --json review/part.json
   uv run "$S/check_chapter.py" path/to/vysnovky.md --body path/to/parts-dir    # conclusions' numbers vs the chapters (E01)
   uv run "$S/brick_status.py" path/to/parts-dir [--novelty brick/novelty.md] --md review/status.md   # when > 1 part exists
   ```

   A single file holding the whole dissertation is split into parts automatically (ВСТУП /
   РОЗДІЛ N / ВИСНОВКИ …); `scripts/README.md` lists every option.

   The scripts print `ERROR`/`WARN`/`INFO` lines with rule codes (`references/rules.md`),
   a `SUMMARY`, exit 1 on errors, exit 2 when the input cannot be read. Check the detected
   part kind and chapter number first; if wrong, rerun with `--kind`/`--chapter`, otherwise
   the structural findings are noise. The scripts are heuristics: **you** decide what goes
   into the report, and everything about meaning, logic, 121 fit and evidence quality comes
   from the next step.
2. Read the part **in full**, then go through `references/review-checklist.md` for that part
   (and the whole-dissertation section when more than one part exists). For each problem
   record: location (підрозділ / абзац), what is wrong, why an opponent will care (the `R-…`
   requirement or the typical question), and a concrete fix — a rewritten sentence when the
   fix is wording. Always check:
   1. the part does what its slot in the genre requires (`chapter-playbook.md`), with the
      expected blocks in the expected order and a plausible page budget;
   2. novelty: gradation marker, object type, «відрізняється», «дозволяє», quantified effect,
      verbatim identity with the single source / other parts; nothing «вперше» that is a
      modification of a known method;
   3. 121 fit and the architecture rule (`requirements.md`), object = process, aim = result;
   4. evidence: experiment tests *the proposed* model/method against a baseline with named
      metrics and data; every number in conclusions traceable to a table/figure; no
      comparative claim without a number;
   5. language and typography per `style-guide.md`.
   Compare with the bundled examples where it helps («у Бочка цей блок виглядає так …»),
   using the pointers in `dissertation-examples.md`; do not hold the user to the examples'
   weaknesses.
3. Write `review/<part>-review.md` (Ukrainian unless the user writes otherwise) using the
   template in `review-checklist.md`: **Вердикт** (one line: «готовий», «готовий після
   правок», «потребує доопрацювання», with ERROR/WARN counts), **Критичні зауваження**,
   **Зауваження** grouped (структура, новизна і відповідність 121, доказовість, джерела,
   мова, оформлення), **Рекомендації**, **Ймовірні запитання опонента** (5–10, tailored),
   **Що не перевірялось**. Quote the text you criticise and give the rewrite. No generic
   advice that does not apply to this part. If you run as a subagent that cannot write
   files, return the full report text and say so.
4. Give the user the absolute path of the report and a 5–10 line summary in chat.
5. **Fixes only if asked.** Then edit the part in place if it is under version control
   (say so), otherwise write `<name>_reviewed.md`; change wording and mechanics only, never
   results; rerun the checker; list every change. Novelty, aim and conclusions rewrites are
   proposals for the supervisor — mark them.

## 3. Status mode (the whole brick)

1. Run `brick_status.py` on the parts directory (or the single `.docx`/`.md`), with
   `--novelty` when the single-source file exists. It prints the inventory (part, kind,
   headings, estimated pages, figures/tables/formulas/citations, conclusions present), the
   page-budget shares vs the genre norm (аналітика ≈ 10 %, власні результати ≈ 58 %,
   обрамлення ≈ 32 %), and the `B…` findings: novelty wording drift, tasks ↔ conclusions
   mapping, chapters without conclusions, conclusion numbers not found in chapters,
   reference count and Latin share, abbreviation list vs usage.
2. Build or update the traceability table (`chapter-playbook.md` §1) from the text itself:
   завдання (вступ) → розділ/підрозділ → науковий результат and gradation → публікація →
   пункт загальних висновків. Every empty cell is a finding.
3. Check the formal set from `requirements.md` §5–§7 against the project's publication list
   and co-author arithmetic, acts of implementation, апробація, перелік умовних позначень —
   only from documents the user has; otherwise list what must be collected.
4. Report `review/brick-status.md`: verdict («збирається» / «збирається після …» / «не
   збирається, бо …»), the table, missing parts with their page budgets, the ordered to-do
   list (fundament issues first, then results chapters, then обрамлення), and what was not
   checked.

## Working with subagents

For a whole-brick review or several chapters at once, fan out one reviewer per part in
parallel, each briefed with this skill's paths, the part, the single-source novelty file and
the tasks from the вступ; then merge the reports and run the cross-part checks yourself.
Match the model to the work: the hardest reasoning (novelty wording, results chapters, the
cross-part verdict) to the strongest model; summaries of literature and analytic prose to a
mid-tier model; mechanical passes (running the scripts, abbreviation lists, reference
formatting) to a small one.

## Rules

1. Never invent results, numbers, sources, acts, conferences, co-authors or properties of
   the architecture. Placeholders with what is needed, every time.
2. The project's decisions win over the generic playbook; the newest normative document wins
   over `requirements.md` — say so and update `requirements.md` when the user has a newer
   one.
3. Keep novelty, aim, object, subject and tasks verbatim across parts; when one must change,
   change the single source and list every place to update.
4. Separate «порушує вимогу» (ERROR) from «опонент спитає» (WARN) from «смак» (INFO).
5. Do not upload the dissertation anywhere; it holds unpublished results and personal data.
6. Do not restructure or rewrite parts the user did not ask about; report what you noticed.
