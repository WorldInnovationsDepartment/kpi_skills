# Sources and provenance

## The dictionary (basis `mintsyfra`)

1. **Title:** Словник термінів у сфері штучного інтелекту 2.0
2. **Publisher:** Міністерство цифрової трансформації України, with the Експертно-консультаційний
  комітет з питань розвитку сфери ШІ при Мінцифрі; Київ, 2026, 37 pp.
3. **Ministry page:** «Говорити однією мовою з технологіями: оновили національний словник термінів
  зі штучного інтелекту», 8 June 2026 — https://thedigital.gov.ua/news/technologies/hovoryty-odniyeiu-movoiu-z-tekhnolohiiamy-onovyly-natsionalnyy-slovnyk-terminiv-zi-shtuchnoho-intelektu
  (links to the PDF below and to a machine-readable version hosted in Google AI Studio).
4. **PDF:** https://storage.thedigital.gov.ua/files/9/39/18441baf603a192429ecac57b7076394.pdf
  (PDF metadata: created 2026-03-31, modified 2026-06-08; downloaded for this skill 2026-11-23).
5. **Status (from its introduction):** aims to align technical and legal AI terminology for the
  professional community, technical and legal documentation and law-making; explicitly *not*
  exhaustive and may be updated. It is a recommendation, not a binding standard — reports
  should say «словник рекомендує».
6. **Structure:** a 5-column table — №, термін українською, термін англійською, визначення,
  пов’язані терміни — 146 rows; synonyms in brackets or after «/» (e.g. «Запит (промпт)»,
  «Набір даних / датасет»).

`references/dictionary.json` fields per entry: `n`, `uk`, `en`, `definition`, `related`, `page`
(verbatim from the PDF cells) and `uk_variants`, `uk_abbr`, `en_variants`, `en_abbr`, `note`
(derived by `build_dictionary.py`).

### Extraction caveats

The PDF uses Type3 fonts: PyMuPDF decodes the Cyrillic wrongly, poppler decodes it right but
draws some glyph pieces 10–20 pt off their line, and `find_tables()` misses two pages. The
builder takes row rectangles from the slide drawings, words from `pdftotext -tsv`, and snaps
every word to the PyMuPDF glyph at the same x. Term names and abbreviations were checked row by
row (the test asserts no scrambled names); definitions are clean for most rows but a few long
multi-line definitions (e.g. №87) still have words out of order — read the PDF page (`page`
field) before quoting a definition. The «пов’язані терміни» column keeps only items that exactly
match an entry name, so it is incomplete.

Splitting into variants is ours where the cell is not «термін (синонім)»: see `OVERRIDES` in
`build_dictionary.py` (№18, 26, 95, 99, 100, 119, 127, 128, 131, 132, 136, 137).

## Our additions (still basis `mintsyfra`, but our judgment that a form names the entry)

`known_variants.json` lists renderings that are *not* in the dictionary but denote one of its
entries (галюцинація → галюцинування №30, файн-тюнінг → тонке налаштування №130, вирівнювання →
узгодженість/узгодження №136/137 …). The recommended form is the ministry's; the mapping is ours.
Variants that are legitimate in another sense carry `caution` and are reported as INFO.

## Not based on the dictionary (basis `other`)

`style_rules.json` — calques and usage (являється, на протязі, у якості, даний, співпадати …),
following general Ukrainian style guides (Б. Антоненко-Давидович «Як ми говоримо»;
О. Пономарів «Культура слова: мовностилістичні поради») and editorial practice. The X1 check
(English words left in Ukrainian prose) and any reviewer judgment about terms absent from the
dictionary are also `other`.
