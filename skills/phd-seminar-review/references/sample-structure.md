# Sample: a real 121 defence talk at KPI (2024), anonymised

Source: a PhD defence presentation, specialty 121, department ІПЗЕ (ТЕФ), KPI, May 2024,
24 slides, 16:9, Ukrainian. Topic area: query processing in heterogeneous distributed NoSQL
databases. Names and the exact wording are omitted; the structure is what matters.

## Slide sequence

| # | Slide | Notes |
|---|---|---|
| 1 | Title: ministry, KPI, candidate (ПРІЗВИЩЕ Ім'я По батькові), topic, «Спеціальність 121 «Інженерія програмного забезпечення»», «Дисертація на здобуття ступеня доктора філософії», two supervisors with degree + title, «Київ – 2024» | complete |
| 2 | Актуальність теми дослідження: chain of facts (data volume growth, %), leading to the problem | figures without sources |
| 3 | Об'єкт, предмет та мета дослідження + методи дослідження | object = process, subject = means; aim «підвищення ефективності … шляхом розробки …» |
| 4 | Аналіз останніх публікацій та досліджень: schools/authors per sub-problem, the contradiction (протиріччя) between need and existing methods, and the scientific task (наукове завдання) | typo in the title; 13 pt text |
| 5 | Часткові наукові завдання: 6 numbered infinitive tasks | |
| 6 | Основні наукові результати: 4 items, each «Удосконалено/Вперше розроблено …, яка відрізняється …, дозволяє …» | 211 words; item 4 is «вперше розроблено програмне забезпечення…» |
| 7–9 | Result 1 (model): formulas, matrices, diagrams | small fonts |
| 10–11 | Result 2 (method): flowcharts of two algorithms | 7–8 pt labels, unexplained abbreviations |
| 12–14 | Result 3 (method): formulas, probability estimates | |
| 15–17 | Result 4: the integrated software system — structure / components | the de-facto architecture, but never called a scientific architecture result |
| 18–20 | Experimental examples for results 1–3 | |
| 21–22 | Висновки: 9 numbered items | ~300 words per slide |
| 23 | Публікації, апробація та реалізація: summary line (5 articles, category Б, 11 conference papers, 3 in Scopus), 5 references, 4 acts of implementation | dense |
| 24 | Дякую за увагу! | |

## What this skill reports on it

`check_deck.py` on this deck: 1 ERROR, ~32 WARN, ~12 INFO (most WARN are text walls and
small fonts).

1. **A01 ERROR**: none of the four novelty items is an architecture. Item 4 («вперше розроблено
   програмне забезпечення комплексної системи …») and slides 15–17 are an architecture in
   substance; the fix is to formulate it as one: «Удосконалено архітектуру комплексної
   системи …, яка відрізняється …, що дозволило …», and title slide 15 «Архітектура …».
2. N02: item 4 has no distinguishing feature; software «вперше розроблено» is practical
   value, not novelty, unless the architecture itself is new.
3. L01: «об'єм» (→ обсяг), «процентів» (→ відсотків; also «15% процентів» is a pleonasm),
   «даного методу», «в залежності від», «на даний час».
4. L02: abbreviations never expanded (e.g. ОКР; ВОЗ is used in flowcharts and only caught
   manually). F08: figure numbers repeated on different slides. C01: no future-research line.
   C02: conclusions copy the novelty items. A03 points to the slide whose figure caption
   says «Архітектура…».
5. F02/F03: text walls (novelty, conclusions, publications slides) and 7–13 pt fonts on
   diagrams.
6. Manual review adds: typos in titles («ПУБЛКАЦІЙ», «НАУКОВЕ ЗАДАННЯ», «СТАТІ»); relevance
   figures without sources and contradicting each other; part of slide 2 is a picture (text
   not extracted); a task with no matching result; an experiment without a baseline; two
   publications of doubtful topic that bring the credit from 4.5 down to the minimum 3; Oracle
   listed as a non-relational DBMS; garbled OLE formulas in the LibreOffice preview.

## Good patterns to keep

1. Every result has its own block of slides, titled exactly as the novelty item.
2. The analysis slide ends with an explicit contradiction and the scientific task.
3. Publications slide starts with a one-line summary and lists acts of implementation with
   dates.
