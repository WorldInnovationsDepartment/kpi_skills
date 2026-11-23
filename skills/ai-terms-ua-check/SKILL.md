---
name: ai-terms-ua-check
description: Use when checking or reviewing how artificial-intelligence / machine-learning terms were translated from English into Ukrainian (paper, dissertation, documentation, slides, policy text), with or without the English source — e.g. «перевір переклад термінів ШІ», «чи відповідає термінологія словнику Мінцифри», «як правильно перекласти prompt / fine-tuning / alignment», "check the AI terminology in my Ukrainian translation".
---

# AI terms EN→UA check (словник Мінцифри)

Checks AI terminology in a Ukrainian text against **«Словник термінів у сфері штучного
інтелекту 2.0»** (Міністерство цифрової трансформації України, 2026, 146 термінів,
[PDF](https://storage.thedigital.gov.ua/files/9/39/18441baf603a192429ecac57b7076394.pdf);
[сторінка Мінцифри з анонсом](https://thedigital.gov.ua/news/technologies/hovoryty-odniyeiu-movoiu-z-tekhnolohiiamy-onovyly-natsionalnyy-slovnyk-terminiv-zi-shtuchnoho-intelektu)),
bundled as `references/dictionary.json`.

**Core rule: every remark has a basis, and the report keeps the two apart.**

| Basis | What it covers | Label in the report |
|---|---|---|
| `mintsyfra` | the recommended Ukrainian form is an entry (or a synonym in brackets) of the dictionary | Частина 1 «На основі словника Мінцифри», with the entry number №N |
| `other` | anything else: calques, style, terms the dictionary lacks, your own judgment | Частина 2 «Поза словником Мінцифри» + the note «не базуються на словнику Міністерства цифрової трансформації» |

A remark is `mintsyfra` only when you can name the entry №N it rests on. Your opinion
about a term the dictionary contains but in a different sense, or about a term it does not
contain, is `other` — even when you are confident.

## Workflow

1. **Intake.** Get the Ukrainian text (`.docx` `.md` `.txt` `.pdf`) and, if available, the
   English source. With a source, the check is far stronger: it sees which English term each
   paragraph used. If paragraph counts differ, the script compares whole documents and the
   findings lose their locations; when locations matter, split both texts into matching
   paragraphs first (one EN paragraph split into two UA ones is enough to break alignment).
2. **Run the script** from the repository root, or replace `S` with the absolute path of this
   skill's `scripts/` folder (needs [`uv`](https://docs.astral.sh/uv/); `pdftotext` for PDF input):
   ```bash
   S=skills/ai-terms-ua-check/scripts
   uv run $S/check_terms.py uk.docx --source en.docx --md review/terms.md --json review/terms.json
   uv run $S/check_terms.py uk.docx --md review/terms.md        # no source: UA-only checks
   ```
   Add `--latin-words` to also list every lower-case English word left in Ukrainian prose
   (noisy; `other` basis).
3. **Verify each script finding in context** (open the paragraph; the JSON has `context`):
   1. drop false positives (an everyday word, a product name, a quotation, a bibliography entry);
   2. keep `caution` variants as questions, not errors (`зміщення` is correct for statistical
     bias of an estimator; `розмітка даних` is widespread);
   3. inflection the light stemmer misses (alternations like «вихід/виходи» are handled, rarer
      ones are not): if the term is there in another form, drop the finding;
   4. a dictionary word used for a different source concept is not a miss: «вибірка» for *split*
      is fine even when the same sentence has *testing data*;
   5. P1 «немає відповідника»: read the paragraph and name what the translator actually wrote —
     the script only knows the dictionary forms and the variants in `references/known_variants.json`.
4. **Read for what the script cannot see** (`mintsyfra` basis, cite №N) — the confusable pairs
   in the dictionary itself:
   1. Accuracy №131 «точність» vs Precision №132 «точність (прецизійність)»;
   2. Recall №99 «повнота (чутливість)» vs Completeness №100 «повнота»;
   3. Alignment: №136 «узгодженість» (властивість) vs №137 «узгодження» (процес);
   4. Robustness №114 «робастність» vs Resilience №124 «стійкість»;
   5. Automated №2 «автоматизоване» vs Automatic №3 «автоматичне» ухвалення рішень;
   6. Validation №95: «оцінювання» (у навчанні моделі) vs «перевірка» (в інженерії систем ШІ);
   7. Model №75 vs Language model №76 vs LLM №19 «велика мовна модель (ВММ)».
   Look up any entry's definition in `references/dictionary.json` before ruling on sense.
   The script flags Robustness→«стійкість» and the other swaps as P4; Accuracy/Precision and
   the Alignment sense (№136 vs №137) still need your reading.
5. **Non-dictionary review** (`other` basis). For AI terms the dictionary lacks (attention,
   embedding layer, guardrails, agentic workflow …), suggest a rendering and say where it comes
   from: a named Ukrainian standard or textbook if you can cite it exactly, otherwise «усталене
   вживання» or «судження рецензента». When no Ukrainian form is settled, recommend the Ukrainian
   rendering with the English term in brackets at first use. Also note calques the style rules caught.
   Never present these as the ministry's position.
6. **Report** in the user's language using the template below: rewrite the script's tables
   into the template columns (code and level go into «Пояснення»), keep the Part 2 note verbatim.
   The script's «вжиті терміни» table is a lexical match; before listing a term as «вжито
   правильно», confirm it is used in the dictionary sense. Severity for your own Part 1 findings:
   wrong dictionary entry or sense swap = WARN, missing precision/clarification = INFO; a bare
   English term in Ukrainian prose = WARN. Do not edit the translation
   unless asked; if asked, change only approved items.

## Report template

```markdown
# Перевірка ШІ-термінології: <файл>
Словник: «Словник термінів у сфері ШІ 2.0», Мінцифра, 2026 (146 термінів; <посилання на сторінку Мінцифри та PDF>). Режим: <з джерелом по абзацах | без джерела>.
Підсумок: <N> зауважень за словником (<E> помилок, <W> попереджень, <I> інформаційних), <M> поза словником.

## Частина 1. На основі словника Мінцифри
| # | Де | У перекладі | Рекомендує словник (№) | Пояснення |

## Частина 2. Поза словником Мінцифри
> Зауваження цієї частини не базуються на словнику Міністерства цифрової трансформації України;
> це рекомендації рецензента (стиль, кальки, терміни, яких у словнику немає).
| # | Де | У перекладі | Пропозиція | Обґрунтування / джерело |

## Терміни словника, вжиті правильно
<коротко: які терміни і скільки разів — щоб автор бачив, що вже узгоджено>
```

## Finding codes

| Code | Basis | Meaning |
|---|---|---|
| P1 | mintsyfra | EN source has dictionary term; translation lacks its UA form (ERROR multi-word, WARN single word, INFO everyday word) — or used a non-dictionary variant / left it in English (WARN) |
| P2 | mintsyfra | translated with a dictionary synonym, not the primary form (INFO) |
| P4 | mintsyfra | translated with the UA form of a *different* entry the dictionary keeps apart (Robustness→«стійкість», Automated↔Automatic, Recall→Completeness) |
| P3 | mintsyfra | confusable pair: Precision without «прецизійність», Recall without «чутливість» |
| M2 | mintsyfra | UA text uses a known non-dictionary variant of an entry (`known_variants.json`) |
| M3 | mintsyfra | dictionary term left in Latin script in UA prose (glosses in brackets, quotes, code are skipped) |
| M4 | mintsyfra | only the bracketed synonym used (e.g. «промпт» without «запит») |
| M5 | mintsyfra | several dictionary forms for one concept in one text — consistency |
| S01–S16 | other | calques and wording (`references/style_rules.json`) |
| X1 | other | English word left in UA prose, not in the dictionary (`--latin-words`) |

## Pitfalls

| Mistake | Instead |
|---|---|
| Calling a non-dictionary form «помилка за Мінцифрою» | The dictionary recommends; say «словник Мінцифри рекомендує …, №N» |
| Mixing your own suggestions into Part 1 | Part 1 = only rows with №N; everything else goes to Part 2 |
| Flagging «модель», «ризик», «підтримка» used in their everyday sense | Check the sentence: only the term usage counts |
| Flagging an English gloss: «велика мовна модель (LLM)» | A UA term followed by the EN original in brackets is good practice |
| Trusting a whole-document run for locations | Align paragraphs or report «весь текст» honestly |
| Using a dictionary older than the user's citation | If the ministry publishes a new version, rebuild (below) and say which version you used |

## When the dictionary changes

```bash
curl -L -o /tmp/mintsyfra-ai.pdf "<new PDF URL>"
uv run skills/ai-terms-ua-check/scripts/build_dictionary.py /tmp/mintsyfra-ai.pdf \
    --out skills/ai-terms-ua-check/references/dictionary.json
uv run tests/ai-terms-ua-check/test_ai_terms.py
```
The builder warns about missing or duplicated numbers; update `OVERRIDES` in
`build_dictionary.py` for rows that are not «термін (синонім)», the entry count in the test, and
`references/sources.md`. Extraction details and caveats: `references/sources.md`.
