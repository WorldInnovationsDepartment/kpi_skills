# Reference list: DSTU 8302:2015 as used by ASAC

The journal requires **ДСТУ 8302:2015 «Бібліографічне посилання. Загальні положення та
правила складання»**. The official sample (`assets/official/sample_*.docx`) uses its
classic full form, with the heading author in italics. Write every entry in that form:

```
*Surname, I.* Title of the work / I. Surname, I. Surname, I. Surname // Source. – Year. – Vol. N, No. N. – P. N–N. – DOI: 10.xxxx/xxxxx.
```

## Punctuation rules

1. The elements are separated by **". – "** (full stop, space, en dash, space). The
   sample writes this with an en dash "–". Use the same character throughout.
2. **" / "** separates the title from the statement of responsibility, which lists
   **all** authors with initials first ("R. Xu, D. Wunsch"). With **four or more**
   authors, list the first three and add "[et al.]" (UA: "[та ін.]").
3. **" // "** introduces the host document: the journal, proceedings or collection.
4. In the YAML, the heading author ("*Xu, R.*") is wrapped in `*...*`, and the builder
   sets it in italics as in the sample. A work with no author starts directly with the
   title.
5. Use the language of the source. Do not translate the titles of English sources into
   Ukrainian or the other way round. Volume and page abbreviations follow the source
   language: "Vol. / No. / P." for English, "Т. / № / С." for Ukrainian.
6. Add "– DOI: 10.xxxx/..." whenever the work has a DOI (look it up on doi.org or
   Crossref and **never invent one**). If there is no DOI, give a stable URL with the
   access date: "– URL: https://... (дата звернення: 12.08.2025)" or "(accessed:
   12.08.2025)".
7. Page ranges use an en dash: "P. 645–678". The sample's "645-678" is also accepted.
8. Each entry ends with a full stop. **Do not number the entries.** The builder numbers
   them "1.", "2.", ... in citation order.

## Templates

### Journal article

```
*Xu, R.* Survey of clustering algorithms / R. Xu, D. Wunsch // IEEE Transactions on Neural Networks. – 2005. – Vol. 16, iss. 3. – P. 645–678. – DOI: 10.1109/TNN.2005.845141.
*Прізвище, І.* Назва статті / І. Прізвище, І. Прізвище // Адаптивні системи автоматичного управління. – 2025. – Т. 1, № 46. – С. 10–20. – DOI: 10.20535/1560-8956.46.2025.xxxxxx.
```

### Four or more authors

```
*Ke, G.* LightGBM: A highly efficient gradient boosting decision tree / G. Ke, Q. Meng, T. Finley [et al.] // Advances in Neural Information Processing Systems 30. – 2017. – P. 3146–3154.
```

### Conference paper (from the sample)

```
*Gavrilenko, O.* Analysis of the feasibility of implementing service portfolios / O. Gavrilenko, O. Zhurakovska, O. Khomenko // «Unusual methods of development of science and thoughts» : The XXVIII International Scientific and Practical Conference, 17-19 July 2023. – Madrid : [s. n.], 2023. – URL: https://eu-conf.com/ua/events/unusual-methods-ofdevelopment-of-science-and-thoughts/ (accessed: 01.09.2023).
```

### Book

```
*Goodfellow, I.* Deep learning / I. Goodfellow, Y. Bengio, A. Courville. – Cambridge, MA : MIT Press, 2016. – N p.
*Прізвище, І. І.* Назва книги / І. І. Прізвище, І. І. Прізвище. – Київ : Видавництво, 2023. – N с.
```

### Chapter in a book

```
*Surname, I.* Chapter title / I. Surname // Book title / ed. by I. Editor. – City : Publisher, 2021. – P. 10–25. – DOI: ...
```

### Preprint (arXiv)

```
*Vaswani, A.* Attention is all you need / A. Vaswani, N. Shazeer, N. Parmar [et al.] // arXiv preprint. – 2017. – arXiv:1706.03762. – DOI: 10.48550/arXiv.1706.03762.
```

### Standard / patent / thesis

```
ДСТУ 8302:2015. Інформація та документація. Бібліографічне посилання. Загальні положення та правила складання. – Київ : ДП «УкрНДНЦ», 2016. – 16 с.
Пат. 123456 Україна, МПК G06N 3/08. Спосіб ... / І. І. Іваненко ; заявник і власник НТУУ «КПІ ім. Ігоря Сікорського». – № a2023 01234 ; заявл. 01.02.2023 ; опубл. 01.03.2024, Бюл. № 9.
*Іваненко, І. І.* Назва дисертації : дис. ... д-ра філософії : 121 / Іваненко Іван Іванович ; КПІ ім. Ігоря Сікорського. – Київ, 2025. – 180 с.
```

### Web page (use sparingly)

```
Fuzzy logic | Introduction // GeeksforGeeks. – URL: https://www.geeksforgeeks.org/fuzzy-logic-introduction (accessed: 27.05.2025).
```

## Quality rules (checked by check_paper.py)

1. **10-15 papers from international journals of the last 5 years** are recommended in
   the introduction (`refs.recent`). Prefer peer-reviewed journal and conference papers
   to web pages.
2. Give a **DOI wherever one exists** (`refs.doi`).
3. **No unpublished data or personal communications** in the list (`refs.unpublished`).
   Cite them in the text instead, e.g. "(Журавель І., 2026, неопубліковані дані)".
4. Number the entries **in order of first citation**, and cite every entry (`cite.order`,
   `cite.unused`, `cite.range`).
5. Citing earlier ASAC papers is welcome, but self-citation should stay proportionate.

## Converting from other styles

1. **APA / IEEE / BibTeX**: rebuild each entry from its fields (authors, year, title,
   container, volume, issue, pages, DOI) in the order above.
2. **Never guess a missing field.** If the volume, pages or DOI cannot be found, leave
   the entry without it, and list it for the author at delivery.
3. **Renumbering**: when the order of first citation changes, renumber the YAML list
   **and** every `[n]` in the body together. Then re-run `check_paper.py` until
   `cite.order` is clean.
