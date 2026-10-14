# Структура звіту (Report Structure) — KPI PhD Semester Report

Generalized content guide for a KPI graduate-school semester attestation
report presentation, derived from a real reference deck's outline. **No
person-specific content from that deck appears here** — every concrete value
below is a `{placeholder}` to be filled per student/semester.

## Placeholder reference

| Placeholder | Meaning |
|---|---|
| `{student_name}` | Student full name (Прізвище Ім'я По батькові / initials) |
| `{student_group}` | Aspirant group code (department-issued PhD-group label, e.g. `XX-00ф`) |
| `{department_name}` | Department / chair name |
| `{supervisor}` | Supervisor name with academic degree/title (д.т.н., проф. …) |
| `{dissertation_topic}` | Full dissertation title (UA, optionally EN) |
| `{semester_no}` | Semester number being reported (does not print by default in the reference deck — maps to the generator's `meta.report_title` field, e.g. `"Звіт про виконання плану аспіранта за {semester_no} семестр"`; see the "1. Title / attestation" slide guide below and `references/spec-schema.md`'s `meta.report_title` section) |
| `{study_year}` | Year of PhD study (рік навчання) |
| `{report_date}` | Date of the attestation/report |
| `{research_object}`, `{research_subject}`, `{research_goal}` | The three canonical framing statements |
| `{tasks[]}` | Numbered tasks for the semester, from the individual plan |
| `{results[]}` | Repeatable block: each result = statement + 0–2 formulas/diagrams + 0–2 tables |
| `{progress_done[]}`, `{progress_in_progress[]}` | What's finished vs. in progress this semester |
| `{publications[]}` | Bibliographic entries (articles) |
| `{conferences[]}` | Conference/school participation entries |
| `{teaching[]}` | Teaching/pedagogical-practice activities (optional) |
| `{conclusions[]}` | Numbered conclusion statements |
| `{next_semester_plan[]}` | Planned tasks for the following semester |

## Recommended slide sequence

Total 12–16 slides is typical; adjust the results block (2–5 slides) and mark
optional slides based on what the student actually has to report.

| # | UA heading (EN gloss) | Generator type | Required? |
|---|---|---|---|
| 1 | Титульний слайд (Title / attestation) | `title` | yes |
| 2 | Об'єкт, предмет, мета дослідження (Object / subject / goal) | `definition` | yes |
| 3 | Завдання на семестр (Tasks for the semester) | `bullets` | yes |
| 4 | Структура дисертації (Dissertation structure) | `bullets` | optional |
| 5…N | Наукові результати (Research results, 2–5 slides) | `table` / `image` / `two_column` / `bullets` | yes |
| N+1 | Стан виконання плану (Progress: done / in progress) | `bullets` | optional |
| N+2 | Публікації (Publications) | `references` | yes if any |
| N+3 | Конференції та школи (Conferences / schools) | `references` | yes if any |
| N+4 | Педагогічна практика (Teaching practice) | `bullets` | optional |
| N+5 | Висновки (Conclusions) | `conclusions` | yes |
| N+6 | План на наступний семестр (Plan for next semester) | `bullets` | yes |
| N+7 | Дякую за увагу! (Thank you) | `thanks` | yes |
| N+8 | Back cover (branding) | `back_cover` | optional |

## Slide-by-slide guide

### 1. Title / attestation — type `title`
- **Purpose:** identifies the student, topic, supervisor and department for the attestation commission; the single most scrutinized slide.
- **Collect:** `{dissertation_topic}`, `{student_name}`, `{student_group}`, `{supervisor}`, `{department_name}`, `{semester_no}`.
- **Volume:** short — report-title/semester line (1 line), topic (1–2 lines), 3–4 attestation lines.
- **Pitfalls:** missing `{semester_no}` (it's easy to omit — the reference deck never printed it on any slide; put it in `meta.report_title`, e.g. `"Звіт про виконання плану аспіранта за {semester_no} семестр"`, not hacked into `student_label_template` or another field); topic text overflowing its box on long titles (keep the title-text box tall enough for 3–4 wrapped lines, don't rely on a 1-line default); truncated/incorrect academic degree abbreviations for the supervisor.

### 2. Object / subject / goal — type `definition`
- **Purpose:** restates the canonical dissertation-proposal framing the commission expects every report to open with.
- **Collect:** `{research_object}`, `{research_subject}`, `{research_goal}` — one paragraph each.
- **Volume:** 3 header+body pairs, 1–3 lines of body text each.
- **Pitfalls:** letting any of the three run past 3–4 lines (cramped, causes header/body overlap if boxes are stacked tightly); default full-justification on short paragraphs stretches word gaps awkwardly — prefer left-aligned body text.

### 3. Tasks for the semester — type `bullets`
- **Purpose:** shows what the individual plan committed to for this semester.
- **Collect:** `{tasks[]}` — phrased as infinitives ("дослідити…", "розробити…"), matching the approved individual plan wording.
- **Volume:** 3–6 numbered items, 1 line each.
- **Pitfalls:** task wording that doesn't match the officially approved individual plan (commissions cross-check this); more than ~6 items forces autofit shrink — split into two slides instead of shrinking text below ~18pt.

### 4. Dissertation structure (optional) — type `bullets`
- **Purpose:** shows the overall dissertation roadmap/chapter plan, for context beyond just this semester.
- **Collect:** `{dissertation_structure[]}` — chapter/stage names in planned order.
- **Volume:** 4–6 numbered items.
- **Pitfalls:** skip this slide if the plan hasn't changed since the last report — repeating it unchanged every semester adds no value and commissions notice filler.

### 5…N. Research results (repeat 2–5 times) — types `table` / `image` / `two_column` / `bullets`
- **Purpose:** the substantive core of the report — what was actually discovered/built this semester.
- **Collect per result:** one clear claim statement; 0–2 supporting formulas or diagrams (as images, since native equation editing is out of scope for a generated deck); 0–2 small tables (comparisons, metrics); optionally 2 connector callouts.
- **Volume:** one result per slide is safest. Use `two_column` when presenting two parallel items (e.g. two proposed indicators, each with its own pros/cons); use `table` when the result is best shown as a comparison/metrics table; use `image` for a pipeline/architecture diagram; use `bullets` for a purely textual result.
- **Pitfalls:** cramming a formula + diagram + table onto one slide (the most common overflow cause) — split into a "(1/2)"/"(2/2)" pair instead; a 2-line title wrapping down into the body content below it (always reserve ≥2 full lines of height for the title box); treating a result as "done" when the underlying chapter is still in draft — flag with `{progress_in_progress[]}` instead.

### N+1. Progress: done vs. in progress (optional) — type `bullets`
- **Purpose:** an explicit checklist view of individual-plan completion, useful when results slides don't map 1:1 onto plan items.
- **Collect:** `{progress_done[]}`, `{progress_in_progress[]}` as two short numbered sub-lists.
- **Volume:** 3–6 items per sub-list.
- **Pitfalls:** vague progress items ("working on chapter") without a concrete deliverable or date; omitting this slide entirely can leave the commission unsure what's actually finished vs. planned.

### N+2. Publications — type `references`
- **Purpose:** demonstrates research output; heavily scrutinized for completeness and correct indexing status (Scopus/WoS/фахове видання).
- **Collect:** `{publications[]}` — full bibliographic entries, in the Ukrainian reference-list format (see below), tagged with index status where applicable.
- **Volume:** all publications to date, but ≤6–7 entries per slide — beyond that, split across two slides rather than shrinking the font.
- **Pitfalls:** the single biggest cause of unreadable slides in the reference deck was cramming 7–9 long entries onto one slide, forcing automatic text shrink down to ~67% scale; incomplete bibliographic data (missing DOI, volume/issue, page range) is also flagged by attestation commissions.

### N+3. Conferences / schools — type `references`
- **Purpose:** demonstrates participation in the scholarly community.
- **Collect:** `{conferences[]}` — conference/school name, location, dates, and (if applicable) the title of the presented work.
- **Volume:** ≤5–6 entries per slide, same overflow risk as publications.
- **Pitfalls:** same as publications — don't rely on autofit shrink to fit everything on one slide; missing dates/location makes an entry unverifiable.

### N+4. Teaching / pedagogical practice (optional) — type `bullets`
- **Purpose:** required only for students with a teaching-load component in their plan (педагогічна практика).
- **Collect:** `{teaching[]}` — course name, role (asst./lecturer), semester, group(s).
- **Volume:** 2–4 items.
- **Pitfalls:** omit the slide entirely (don't leave an empty placeholder) if the student has no teaching duties this semester.

### N+5. Conclusions — type `conclusions`
- **Purpose:** closes the loop with the semester's tasks slide — each task from slide 3 should have a matching, past-tense conclusion.
- **Collect:** `{conclusions[]}`, ideally same count and order as `{tasks[]}`.
- **Volume:** 3–6 numbered statements, 1 line each.
- **Pitfalls:** conclusions that don't map back onto the stated tasks (commissions will ask); full-justification on short lines producing stretched gaps — prefer left alignment.

### N+6. Plan for next semester — type `bullets`
- **Purpose:** sets expectations for the next attestation; shows the work is on a credible trajectory.
- **Collect:** `{next_semester_plan[]}` — concrete, checkable next steps, ideally traceable to `{dissertation_structure[]}`.
- **Volume:** 3–5 items.
- **Pitfalls:** vague or unrealistic plans ("finish the dissertation") without an intermediate, checkable milestone.

### N+7. Thanks — type `thanks`
- **Purpose:** closing slide, invites questions.
- **Collect:** nothing — static "Дякую за увагу!" content.
- **Pitfalls:** none typical; keep it a clean, uncluttered slide (this is a good place for wide-open white space, not more text).

### N+8. Back cover (optional) — type `back_cover`
- **Purpose:** pure institutional branding bookend; reuse the university/KPI brand template as-is.
- **Collect:** nothing — no per-student data.
- **Pitfalls:** don't accidentally add per-student text to this slide; it's purely institutional.

## Pre-generation checklist — questions to ask the student

Ask these before generating, in roughly this order:

1. Which semester and year of study is this report for? (`{semester_no}`, `{study_year}`, `{report_date}`)
2. Full name, group code, department, and supervisor (with academic degree/title)? (`{student_name}`, `{student_group}`, `{department_name}`, `{supervisor}`)
3. Exact dissertation topic as currently approved? (`{dissertation_topic}`)
4. What were the approved individual-plan tasks for this semester, verbatim if possible? (`{tasks[]}`)
5. For each task: is it done, in progress, or not started? Any concrete evidence (a result, a metric, a draft chapter)? (`{results[]}`, `{progress_done[]}`, `{progress_in_progress[]}`)
6. Has the overall dissertation structure/roadmap changed since the last report? (`{dissertation_structure[]}`, only if changed)
7. Any publications since the last report? For each: authors, title, journal/collection, year, volume/issue, pages, DOI, and indexing status (Scopus/WoS/фахове видання). (`{publications[]}`)
8. Any conferences, schools, or seminars attended/presented at? For each: name, location, dates, title of the presented work. (`{conferences[]}`)
9. Any teaching/pedagogical practice this semester? Course, role, group(s). (`{teaching[]}`)
10. What are the 3–6 headline conclusions for this semester, ideally one per task above? (`{conclusions[]}`)
11. What's planned for next semester? (`{next_semester_plan[]}`)

## Ukrainian phrasing conventions for headings

| UA heading | EN gloss |
|---|---|
| Об'єкт дослідження | Object of research |
| Предмет дослідження | Subject of research |
| Мета дослідження | Goal of research |
| Завдання на семестр | Tasks for the semester |
| Часткові наукові завдання | Partial scientific tasks |
| Структура дисертації | Dissertation structure |
| Стан виконання індивідуального плану | Individual-plan progress status |
| Науковий результат | Scientific result |
| Результати | Results |
| Публікації | Publications |
| Конференції | Conferences |
| Педагогічна практика | Teaching practice |
| Висновки | Conclusions |
| План на наступний семестр | Plan for next semester |
| Дякую за увагу! | Thank you for your attention! |

## Typical Ukrainian bibliographic entry formats

**Article:**
`{authors}. {title}. {journal_name}. {year}. Т. {volume}, № {issue}. С. {page_range}. DOI: {doi}.`

**Conference:**
`{authors}. {title}. {conference_name}: матеріали конф. ({city}, {dates}). С. {page_range}.`

## Length and timing

- **Target length:** 12–16 slides (title + framing + tasks + 2–5 results slides + publications/conferences + conclusions + next-semester plan + thanks, with dissertation-structure/progress/teaching/back-cover added only when relevant).
- **Target time:** 7–10 minutes of spoken presentation — roughly 30–45 seconds per slide, less for the title/thanks bookends, more for dense results/reference slides.
- Prefer splitting a dense slide (publications, conferences, multi-part results) over shrinking its font to fit — small, evenly-sized text reads better under time pressure than a large slide auto-shrunk to fit everything.
