# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1"]
# ///
"""Plain-assert regression harness for the ai-terms-ua-check skill.

    uv run tests/ai-terms-ua-check/test_ai_terms.py

Checks: the committed dictionary.json (146 entries, numbering 1..146, variants present,
the Mintsyfra source URL), every known variant / style regex compiles and points to a real
entry, a correct translation produces no dictionary findings, a faulty translation produces
the expected codes (P1/P3 with source, M2/M3 without), .docx input, paragraph alignment
fallback, and that every finding from style_rules / Latin leftovers is labelled basis=other.
Prints a SUMMARY line and exits non-zero on failure.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skills" / "ai-terms-ua-check"
SCRIPT = SKILL / "scripts" / "check_terms.py"
REF = SKILL / "references"

passed = failed = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global passed, failed
    if cond:
        passed += 1
        print(f"PASS {name}")
    else:
        failed += 1
        print(f"FAIL {name} {detail}")


def run(tmp: Path, uk: Path, en: Path | None = None) -> dict:
    out = tmp / "r.json"
    cmd = [sys.executable, str(SCRIPT), str(uk), "--json", str(out), "--md", str(tmp / "r.md")]
    if en:
        cmd += ["--source", str(en)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(p.stderr)
    return json.loads(out.read_text(encoding="utf-8"))


EN = """Large language models (LLMs) are trained on massive training data and then adapted by fine-tuning.

Retrieval augmented generation reduces hallucinations, but prompt injection remains a risk.

We report precision and recall of the classifier.

Alignment of the model with human values is achieved via reinforcement learning with human feedback.

The context window limits how many tokens the chatbot can see."""

UK_GOOD = """Великі мовні моделі (LLM) навчаються на величезних тренувальних даних, а потім адаптуються за допомогою тонкого налаштування.

Генерування, доповнене пошуком, зменшує галюцинування, але ін'єкція запиту залишається ризиком.

Ми наводимо точність (прецизійність) і повноту (чутливість) класифікатора.

Узгодження моделі з людськими цінностями досягається навчанням з підкріпленням на основі зворотного зв’язку від людини.

Контекстне вікно обмежує, скільки токенів бачить чатбот."""

UK_BAD = """Великі мовні моделі навчаються на величезній навчальній вибірці, а потім адаптуються за допомогою файн-тюнінгу.

Генерація, доповнена пошуком, зменшує галюцинації, але prompt injection залишається ризиком.

Ми наводимо точність і повноту класифікатора.

Вирівнювання моделі з людськими цінностями досягається навчанням з підкріпленням на основі зворотного зв’язку від людини.

Контекстне вікно обмежує, скільки токенів бачить чат-бот. Даний підхід являється стандартним."""


def main() -> int:
    d = json.loads((REF / "dictionary.json").read_text(encoding="utf-8"))
    nums = [e["n"] for e in d["entries"]]
    check("dict: 146 entries numbered 1..146", nums == list(range(1, 147)), str(len(nums)))
    check("dict: source URL is the Mintsyfra PDF", "storage.thedigital.gov.ua" in d["url"])
    check("dict: every entry has UA and EN variants",
          all(e["uk_variants"] and (e["en_variants"] or e["en_abbr"]) for e in d["entries"]))
    garbled = [e["n"] for e in d["entries"]
               if re.search(r"(^|\s)[а-яіїєґa-z](\s|$)", e["uk"].lower() + " " + e["en"].lower())
               and not re.search(r"\s[ввуз]\s|\sз\s", e["uk"].lower())]
    check("dict: no glyph-scrambled term names", not garbled, str(garbled))
    by_n = {e["n"]: e for e in d["entries"]}
    check("dict: known rows", by_n[30]["uk"] == "Галюцинування" and by_n[133]["en"] == "Training data"
          and by_n[84]["en_abbr"] == ["RLHF"] and by_n[46]["uk_variants"] == ["запит", "промпт"])

    var = json.loads((REF / "known_variants.json").read_text(encoding="utf-8"))["variants"]
    ok = all(re.compile(v["pattern"]) and v["entry"] in by_n for v in var)
    check("variants: regexes compile, entries exist", ok)
    # a variant must never match the dictionary's own primary term
    clash = [v["entry"] for v in var if re.search(v["pattern"], by_n[v["entry"]]["uk_variants"][0])]
    check("variants: never match the recommended term itself", not clash, str(clash))
    sty = json.loads((REF / "style_rules.json").read_text(encoding="utf-8"))["rules"]
    check("style: regexes compile", all(re.compile(r["pattern"]) for r in sty))

    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        (tmp / "en.md").write_text(EN, encoding="utf-8")
        (tmp / "good.md").write_text(UK_GOOD, encoding="utf-8")
        (tmp / "bad.md").write_text(UK_BAD, encoding="utf-8")

        r = run(tmp, tmp / "good.md", tmp / "en.md")
        mf = [f for f in r["findings"] if f["basis"] == "mintsyfra" and f["severity"] in ("ERROR", "WARN")]
        check("good translation: no dictionary errors/warnings", not mf,
              json.dumps(mf, ensure_ascii=False)[:600])
        check("good translation: aligned by paragraphs", r["meta"]["aligned"] is True)

        r = run(tmp, tmp / "bad.md", tmp / "en.md")
        got = {(f["code"], f["entry"]) for f in r["findings"]}
        for code, n in [("P1", 130), ("P1", 133), ("P1", 30), ("P1", 32), ("P1", 53), ("P1", 136),
                        ("P1", 140), ("P3", 132)]:
            check(f"bad translation with source: {code} for №{n}", (code, n) in got)
        check("bad translation: no M2/M3 duplicates of P1",
              not any(f["code"] in ("M2", "M3") and ("P1", f["entry"]) in got for f in r["findings"]))
        other = [f for f in r["findings"] if f["code"].startswith("S")]
        check("style findings exist and are basis=other",
              other and all(f["basis"] == "other" for f in other))
        md = (tmp / "r.md").read_text(encoding="utf-8")
        check("report: two labelled parts", "На основі словника Мінцифри" in md
              and "не базуються на словнику Міністерства цифрової трансформації" in md)

        (tmp / "en2.md").write_text("Robustness of the model matters.\n\nThe outputs are filtered.", encoding="utf-8")
        (tmp / "uk2.md").write_text("Стійкість моделі важлива.\n\nВиходи фільтруються.", encoding="utf-8")
        r = run(tmp, tmp / "uk2.md", tmp / "en2.md")
        got2 = {(f["code"], f["entry"]) for f in r["findings"]}
        check("P4: robustness rendered as стійкість (resilience)", ("P4", 114) in got2, str(got2))
        check("inflection: «виходи» satisfies «вихід»", ("P1", 29) not in got2, str(got2))

        r = run(tmp, tmp / "bad.md")
        got = {(f["code"], f["entry"]) for f in r["findings"]}
        check("UA only: M2 галюцинації", ("M2", 30) in got)
        check("UA only: M3 prompt injection kept in Latin", ("M3", 53) in got)
        check("UA only: no P-codes", not any(c.startswith("P") for c, _ in got))

        doc = Document()
        for p in UK_BAD.split("\n\n"):
            doc.add_paragraph(p)
        doc.save(tmp / "bad.docx")
        r = run(tmp, tmp / "bad.docx", tmp / "en.md")
        check("docx input aligned", r["meta"]["aligned"] is True and ("P1", 30) in
              {(f["code"], f["entry"]) for f in r["findings"]})

        (tmp / "bad1.md").write_text(UK_BAD.replace("\n\n", " "), encoding="utf-8")
        r = run(tmp, tmp / "bad1.md", tmp / "en.md")
        check("misaligned input falls back to whole document",
              r["meta"]["aligned"] is False and all(f["location"] == "весь текст"
                                                    for f in r["findings"] if f["code"].startswith("P")))

    print(f"SUMMARY passed={passed} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
