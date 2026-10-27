# Скрипти brick-writer-121

Усі скрипти мають PEP 723-заголовок: запускайте через `uv run` (залежність лише `python-docx`).
Перевіряється текст дисертації у `.md`, `.txt` (зокрема `pdftotext -layout`) або `.docx`; `.pdf` напряму не читається.

1. `check_chapter.py` — перевірка однієї частини (анотація, вступ, розділ N, висновки):

   ```
   uv run scripts/check_chapter.py brick/01-vstup.md
   uv run scripts/check_chapter.py brick/03-rozdil-2.docx --chapter 2 --json out.json
   uv run scripts/check_chapter.py brick/04-vysnovky.md --body brick/        # звірка чисел висновків із розділами
   uv run scripts/check_chapter.py brick/02-rozdil-1.md --first-citation-order --max-ref 130
   ```

   Параметри: `--kind {anotatsiia,vstup,rozdil,vysnovky,spysok,dodatky,poznachennia}`, `--chapter N`, `--chars-per-page 1800`,
   `--first-citation-order`, `--ref-start N`, `--max-ref N`, `--body FILE_OR_DIR...`, `--no-split`, `--json FILE`.
   Вивід: `ERROR|WARN|INFO <код> [розташування] повідомлення`, далі `STRUCTURE` і
   `SUMMARY: E error(s), W warning(s), I info`. Код виходу: 1 — є ERROR, 2 — вхід не прочитано, 0 — інакше.

2. `brick_status.py` — інвентар і наскрізні перевірки всієї дисертації (B01–B07):

   ```
   uv run scripts/brick_status.py brick/                     # каталог файлів частин
   uv run scripts/brick_status.py dissertation.md            # один файл: ділиться за ВСТУП / РОЗДІЛ / ВИСНОВКИ …
   uv run scripts/brick_status.py brick/ --novelty novelty.md --md status.md --json status.json
   ```

3. `brick_common.py` — спільне завантаження й розбір (не запускається окремо): `load_parts()`, `Part`, регулярні вирази
   й списки (GRADATION_RE, LANG_CHECKS, KNOWN_ABBR …), `Report`, константа `CHARS_PER_PAGE = 1800`.

Усі коди правил, серйозність, межі застосування й відповідність вимогам — у `../references/rules.md`.
Перевірки евристичні: вони знаходять кандидатів, а рішення ухвалює рецензування.

Тести: `uv run tests/brick-writer-121/test_brick.py` (з кореня репозиторію або з будь-якого каталогу).
