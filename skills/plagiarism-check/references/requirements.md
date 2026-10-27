# Rules for the plagiarism check of a PhD dissertation at Igor Sikorsky KPI

Last checked: 2026-10-26. What is *verified from a source* is marked; the rest is marked
**unverified** and must be confirmed with the department / the KPI library before relying
on it.

## National level

1. Закон України «Про освіту», ст. 42 — defines академічний плагіат, самоплагіат,
   фабрикація, фальсифікація; the academic community sets procedures. (Statute text;
   well known, not re-fetched.)
2. Постанова КМУ № 44 від 12.01.2022 «Порядок присудження ступеня доктора філософії…»
   (with later amendments): the dissertation must not contain академічний плагіат,
   фабрикація, фальсифікація; the разова спеціалізована вчена рада and its reviewers check
   this; a confirmed violation leads to refusal of the degree. The same Порядок sets the
   publication requirements the `phd-seminar-review` skill tracks. **Source**: see
   `skills/phd-seminar-review/references/requirements.md` in this repository, which quotes
   it with dates.
3. The MON/НАЗЯВО recommendations leave the tool and the acceptable level to the
   institution; there is no national percentage threshold. (**unverified** for 2026 wording;
   consistent with all university regulations found.)

## KPI (verified from a KPI document, 2023)

Source: «Перевірка студентських кваліфікаційних робіт на наявність ознак плагіату»
(Department of МАтаТЙ page/PDF, matan.kpi.ua, created 2023-01-28), which restates
«Положення про систему запобігання академічному плагіату у КПІ ім. Ігоря Сікорського» and
its Додаток 1 (Інструкція щодо роботи відповідальної особи в системі Unicheck) and Додаток 2
(розміщення в ELAKPI). Also the KPI Library page «Академічна доброчесність» (library.kpi.ua),
which names the library as moderator of KPI's Unicheck account.

1. **What is checked**: курсові (all or by sampling), магістерські, **дисертації на здобуття
   «доктора філософії» або «доктора наук» — на етапі представлення матеріалів до розгляду
   спеціалізованою вченою радою**, рукописи монографій, підручників, посібників, статей, тез.
2. **System**: Unicheck, under the agreement between KPI and ТОВ «АНТИПЛАГІАТ». Accounts for
   the responsible persons of departments are created by the KPI Library (moderator).
3. **File rules** (Додаток 1):
   1. no deliberate distortion of the text: no replacement of characters by look-alike
      images, no Latin↔Cyrillic look-alike substitution (the instruction lists
      ‘АаВЕеІіКМНОоРрСсТуХх’), no invisible characters — this is what `text_common.
      tampering_report` detects;
   2. the file contains the work **from Вступ to Висновки inclusive**; title page, contents,
      reference list etc. may be removed because they lower the uniqueness without reflecting
      authorship — this is why the scripts exclude the reference list by default;
   3. searchable PDF; file name with surname, group, type of work, year
      (e.g. `KostukSV_KV51_magistr_2022.pdf`);
   4. one check per text; no repeated check — so the rehearsal this skill provides is the
      only "second try" the candidate gets.
4. **Acceptable level**: «визначається на розсуд факультетів, кафедр, залежно від виду
   роботи та її галузевого спрямування» — there is no university-wide percentage.
5. The full text of the Положення (`Pologen_pro_plagiat.pdf` on kpi.ua) and the procedure
   for dissertations specifically (who files the request, who signs the довідка, how
   self-citations are treated) were **not retrieved** in this check — ask the department's
   responsible person or the library.

## Self-reuse (самоплагіат) in a dissertation

1. Law: самоплагіат is publishing one's own earlier results as new without reference. A
   dissertation that presents the content of the candidate's own articles **with those
   articles cited and listed** as publications on the topic is the normal case, not
   самоплагіат. (Interpretation consistent with the Law and with the practice of
   specialized councils; **unverified** against a KPI document.)
2. Practical: Unicheck will still highlight the overlap. The candidate should list their
   publications in the request so the operator can mark them as the author's own sources;
   the `--own` folder of this skill produces that list with the overlap per publication.

## Other universities' regulations (for comparison, found 2026-10-26)

1. Львівська політехніка: thresholds set per specialty by the responsible body.
2. ВНТУ: the acceptable amount of borrowing depends on field, specialty and type of work.
3. УДУНТ (2025): table of ranges with qualitative levels (e.g. 70–85 % satisfactory for
   some work types).
4. ХАІ: dissertation check performed on the candidate's application.

These confirm the pattern: no single national number; the council judges attributed vs
unattributed reuse.
