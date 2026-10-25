# Rule codes of `check_deck.py`

Severity: **ERROR** — a regulation or the KPI 121 requirement is violated; **WARN** — a
likely problem or a typical objection of reviewers; **INFO** — a fact or reminder for the
manual review. Sources: see `requirements.md` (§ numbers below refer to it). All rules are
heuristics on extracted text; confirm each one against the slide before reporting it.

## Title slide (T)

| Code | Level | Rule | Source |
|---|---|---|---|
| T01 | ERROR | KPI (НТУУ «КПІ ім. Ігоря Сікорського») named on slide 1 | §3 |
| T02 | ERROR | specialty 121 «Інженерія програмного забезпечення» (or F2) on slides 1–2; another specialty code → ERROR (skill scope) | §2, §5 |
| T03 | WARN | «дисертація на здобуття ступеня доктора філософії» | §2 |
| T04 | ERROR | supervisor present | §3 |
| T05 | WARN | supervisor's degree and title (д.т.н., професор …) | custom |
| T06 | WARN | candidate's name (ПРІЗВИЩЕ Ім'я По батькові) recognised; needed for P03 | custom |
| T07 | WARN | city and year | custom |
| T08 | WARN | topic recognised; > 300 characters is suspicious | §2 |

## Structure (S)

| Code | Level | Rule |
|---|---|---|
| S01 | ERROR | required: актуальність, об'єкт, предмет, мета, завдання, наукова новизна, висновки, публікації (§2: elements of the вступ that the talk must present) |
| S02 | WARN | recommended: методи дослідження, практичне значення/впровадження, апробація |
| S03 | INFO | optional: аналіз стану питання, особистий внесок, зв'язок з програмами, «Дякую за увагу» |
| S04 | WARN | order: актуальність → мета → завдання → новизна → висновки; актуальність at the start, висновки in the second half |

## Object, subject, aim (O)

| Code | Level | Rule |
|---|---|---|
| O01 | ERROR | subject identical to object |
| O02 | WARN | subject shares < 25 % of key notions with object (subject must be a part/aspect of the object) |
| O03 | WARN | subject is a process while object is not (inverted pair) |
| O04 | WARN | aim is an action («розробити…») without a result («підвищення … шляхом …») |

## Tasks, novelty, conclusions (K, N, Q)

| Code | Level | Rule |
|---|---|---|
| K01 | WARN | task not an infinitive |
| K02 | WARN | fewer conclusions than tasks |
| K03 | WARN | more novelty items than tasks |
| N01 | WARN | novelty item without gradation (вперше / удосконалено / набуло подальшого розвитку) (§2) |
| N02 | WARN | no distinguishing feature («відрізняється тим, що…», «на відміну від…») (§2) |
| N03 | WARN | no effect («що дозволило…») |
| N04 | WARN | «вперше» mixed with «удосконалено» in one item |
| N05 | INFO | number of novelty items outside 2–4 |
| N07 | INFO | the effect of a novelty item has no number |
| N06 | WARN | «розроблено програмне забезпечення/застосунок» as novelty without an architecture claim — practical value, not novelty (§4) |
| Q01 | WARN | no quantitative result in novelty and conclusions |
| C01 | WARN | conclusions have no future-research line (наказ № 40, п. 10) |
| C02 | INFO | conclusions copy novelty items almost verbatim (> 85 %) |
| Q02 | WARN | no quantitative result in conclusions |

## Specialty 121 and architecture (A)

| Code | Level | Rule |
|---|---|---|
| A01 | ERROR | no novelty item is a software architecture (KPI requirement for 121, §5) |
| A02 | WARN | the architecture item has no distinguishing feature |
| A03 | WARN | no slide titled «архітектура …» with a diagram (picture or ≥ 6 drawn shapes); names slides where only a figure caption mentions the architecture |
| A04 | WARN | fewer than half of the novelty items are about software development, quality, operation or maintenance (risk of a specialty-fit question) |

## Publications, approbation, implementation (P)

| Code | Level | Rule |
|---|---|---|
| P01 | WARN | no summary line «За темою дисертації опубліковано …» |
| P02 | WARN | estimated credit < 3 under п. 8 Порядку №44 (фахова with > 2 authors = 0.5, Scopus/WoS = 1, Q1–Q3 = 2, theses = 0; an unmarked article is assumed фахова) — verify manually (§1) |
| P03 | WARN | candidate's surname (Cyrillic or Latin transliteration) missing in an entry |
| P04 | INFO | entries marked Scopus/WoS/Q1–Q4 |
| P05 | WARN | no acts/certificates of implementation |
| P06 | WARN | no conferences (approbation) |
| P07 | INFO | per-entry credit estimate and total |
| P08 | WARN | two articles in the same journal issue (п. 9, ред. № 1240: only one counts) |
| P09 | INFO | articles listed without DOI (п. 9: only articles with an active DOI count) |

## Form (F) and language (L)

| Code | Level | Rule |
|---|---|---|
| F01 | WARN | slides vs. minutes outside 0.5–1.5 per minute (`--minutes`, default 20) |
| F02 | WARN | > 160 words on a slide |
| F03 | WARN | explicit font size < 14 pt on a 13.33″ slide (scaled for 4:3) on a text slide |
| F04 | WARN | slides not numbered |
| F05 | ERROR | placeholder text left (TODO, Lorem ipsum, «Клацніть, щоб додати …») |
| F06 | WARN | slides without a title |
| F07 | INFO | no speaker notes (.pptx only) |
| F08 | WARN | the same figure number on different slides |
| L01 | WARN | calques / Russianisms (являється, об'єм, процент, на протязі, даний метод, проектування, …); one finding per calque with every slide |
| L02 | WARN | abbreviation used in running text but never expanded (identifiers in formulas/flowcharts are skipped) |
| L03 | INFO | decimal point and decimal comma mixed |

## Cross-check with the dissertation (X, needs `--dissertation`)

| Code | Level | Rule |
|---|---|---|
| X00 | WARN | the dissertation file could not be read |
| X01 | ERROR/WARN | topic on slide 1 not found verbatim in the dissertation (ERROR below 90 % similarity) |
| X02 | WARN | object / subject / aim differ from the dissertation (< 85 %) |
| X03 | WARN | a novelty item is not found in the dissertation's «Наукова новизна» |

When a rule changes, update `scripts/check_deck.py`, this table and
`tests/phd-seminar-review/test_seminar.py` together.
