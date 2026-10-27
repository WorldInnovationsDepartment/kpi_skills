# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = [
#     "python-docx>=1.1",
#     "pymupdf>=1.24",
# ]
# ///
"""Plain-assert regression harness for the ai-text-detector skill (detect_ai.py, calibrate.py,
ai_models.py, text_common.py).

    uv run tests/ai-text-detector/test_detector.py                 # offline: no models downloaded
    KPI_SKILLS_HEAVY=1 uv run tests/ai-text-detector/test_detector.py   # + a real Binoculars run (Qwen3-0.6B pair)

Offline part: text extraction and chunking of a generated .docx/.pdf/.md (dry run), exclusion of the
reference list / quotes / formulas, calibration maths on synthetic score sets (--scores-only), threshold
direction per method, and that the two text_common.py copies are identical. The heavy part scores a
short Ukrainian text with the small pair, checks the report files and that --calibration is honoured.
Prints a SUMMARY line and exits non-zero on failure.
"""
from __future__ import annotations

import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pymupdf as fitz
from docx import Document

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "skills" / "ai-text-detector" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import text_common as tc  # noqa: E402
from ai_models import BINOCULARS_F1_THRESHOLD, DIRECTION, default_threshold, is_ai  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="aidet-test-"))
atexit.register(shutil.rmtree, TMP, ignore_errors=True)
R = {"pass": 0, "fail": 0, "skip": 0}
UV = shutil.which("uv")


def check(cond, msg):
    R["pass" if cond else "fail"] += 1
    print(("  ok   " if cond else "  FAIL ") + msg)


def run(script, *args, timeout=1800):
    cmd = [UV, "run", "-q", str(SCRIPTS / script), *map(str, args)] if UV else [sys.executable, str(SCRIPTS / script), *map(str, args)]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=TMP, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


BODY = ("Мікросервісна архітектура передбачає декомпозицію застосунку на набір невеликих слабко зв'язаних сервісів, "
        "кожен з яких відповідає за окрему бізнес-функцію та може розгортатися незалежно від інших. ") * 6


def make_docs():
    d = Document()
    d.add_paragraph("ВСТУП")
    for _ in range(4):
        d.add_paragraph(BODY)
    d.add_paragraph("«Цитований фрагмент із іншої роботи, який не є текстом здобувача і має бути виключений» [3].")
    d.add_paragraph("Рис. 2.1. Архітектура системи оркестрації")
    d.add_paragraph("x = y + z = ∑ αβγ ≤ ∞")
    d.add_paragraph("СПИСОК ВИКОРИСТАНИХ ДЖЕРЕЛ")
    d.add_paragraph("1. Іваненко П. П. Назва статті. Журнал. 2020. № 1. С. 1–10.")
    d.save(TMP / "t.docx")
    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_textbox(fitz.Rect(72, 72, 520, 760), "Introduction\n\n" + ("This is a human written sentence about software. " * 30), fontsize=9)
    pdf.save(TMP / "t.pdf")
    (TMP / "t.md").write_text("# Title\n\n" + BODY + "\n\n$$E=mc^2$$\n\n## References\n\n1. Ref.\n", encoding="utf-8")


def test_dry_run():
    print("extraction & chunking (dry run)")
    code, out, err = run("detect_ai.py", "t.docx", "--out", "d1", "--dry-run")
    check(code == 0, f"docx dry run exit 0 ({err[-300:] if code else ''})")
    data = json.loads((TMP / "d1" / "chunks.json").read_text(encoding="utf-8"))
    check(data["language"] == "uk", "language uk")
    kinds = data["kinds_words"]
    check("reference" in kinds and "quote" in kinds and "caption" in kinds and "formula" in kinds, f"kinds detected {kinds}")
    text = " ".join(c["text"] for c in data["chunks"])
    check("Цитований фрагмент" not in text and "Іваненко" not in text and "αβγ" not in text, "quote/references/formula excluded")
    check(sum(c["words"] for c in data["chunks"]) == kinds["body"], "all body words chunked")
    check(all(c["words"] >= 40 for c in data["chunks"]), "no tiny chunks")
    code, out, err = run("detect_ai.py", "t.docx", "--out", "d2", "--dry-run", "--include", "quotes,references")
    data2 = json.loads((TMP / "d2" / "chunks.json").read_text(encoding="utf-8"))
    check(sum(c["words"] for c in data2["chunks"]) > sum(c["words"] for c in data["chunks"]), "--include adds text")
    code, out, err = run("detect_ai.py", "t.pdf", "--out", "d3", "--dry-run")
    check(code == 0 and "language=en" in out, f"pdf dry run ({out.strip()[:80]})")
    code, out, err = run("detect_ai.py", "t.md", "--out", "d4", "--dry-run")
    check(code == 0, "md dry run")
    code, out, err = run("detect_ai.py", "missing.docx", "--out", "d5", "--dry-run")
    check(code == 2, "missing file -> exit 2")


def test_calibration_math():
    print("calibrate.py (--scores-only)")
    # binoculars: lower = AI. Human 0.9..1.1, AI 0.6..0.85 -> perfect separation.
    human = [0.9 + i * 0.005 for i in range(40)]
    ai = [0.6 + i * 0.005 for i in range(40)]
    (TMP / "s1.json").write_text(json.dumps({"method": "binoculars", "models": ["a", "b"], "human": human, "ai": ai}))
    code, out, err = run("calibrate.py", "--scores-only", "s1.json", "--method", "binoculars", "--out", "c1.json")
    check(code == 0, f"exit 0 ({err[-200:] if code else ''})")
    c = json.loads((TMP / "c1.json").read_text())["binoculars"]
    check(abs(c["auroc"] - 1.0) < 1e-9, f"AUROC 1.0 ({c['auroc']})")
    check(c["achieved_fpr"] <= 0.05 and c["recall"] == 1.0, f"threshold keeps FPR<=5% with full recall ({c})")
    check(0.85 <= c["threshold"] <= 0.9125, f"binoculars threshold between the classes ({c['threshold']:.4f})")
    check(all(is_ai("binoculars", x, c["threshold"]) for x in ai) and not any(is_ai("binoculars", x, c["threshold"]) for x in human[2:]),
          "is_ai direction for binoculars")
    # fastdetect: higher = AI; overlapping classes.
    human = [i * 0.1 for i in range(40)]          # 0..3.9
    ai = [2.0 + i * 0.1 for i in range(40)]       # 2..5.9
    (TMP / "s2.json").write_text(json.dumps({"method": "fastdetect", "models": ["a"], "human": human, "ai": ai}))
    code, out, err = run("calibrate.py", "--scores-only", "s2.json", "--method", "fastdetect", "--out", "c2.json", "--target-fpr", "0.1")
    c2 = json.loads((TMP / "c2.json").read_text())["fastdetect"]
    check(0.7 < c2["auroc"] < 0.95, f"partial AUROC ({c2['auroc']:.3f})")
    check(c2["achieved_fpr"] <= 0.1 and c2["threshold"] > 3.5, f"fastdetect threshold respects FPR 10% ({c2['threshold']:.2f}, fpr {c2['achieved_fpr']})")
    check("noisy" not in c2["warning"], "no small-sample warning with 40 chunks")
    th, src = default_threshold("binoculars")
    check(th == BINOCULARS_F1_THRESHOLD and "UNCALIBRATED" in src, "default threshold is marked uncalibrated")
    check(default_threshold("fastdetect")[0] is None, "fastdetect has no default threshold")
    check(DIRECTION["binoculars"] == -1 and DIRECTION["desklib"] == 1, "directions")


def test_heavy():
    print("real scoring (KPI_SKILLS_HEAVY=1)")
    if os.environ.get("KPI_SKILLS_HEAVY") != "1" or not UV:
        R["skip"] += 1
        print("  skip (set KPI_SKILLS_HEAVY=1; downloads Qwen3-0.6B base+instruct, ~2.4 GB)")
        return
    code, out, err = run("detect_ai.py", "t.docx", "--out", "h1", "--size", "small", "--method", "binoculars,fastdetect", "--max-chunks", "2")
    check(code == 0, f"binoculars+fastdetect run exit 0 ({err[-400:] if code else ''})")
    rep = json.loads((TMP / "h1" / "ai-report.json").read_text(encoding="utf-8"))
    sc = [c["scores"]["binoculars"] for c in rep["chunks"]]
    check(len(sc) == 2 and all(0.3 < s < 2.0 for s in sc), f"binoculars scores plausible {sc}")
    check(all(isinstance(c["scores"]["fastdetect"], float) for c in rep["chunks"]), "fastdetect scores present")
    check("UNCALIBRATED" in rep["meta"]["thresholds"]["binoculars"]["source"], "report says uncalibrated")
    md = (TMP / "h1" / "ai-report.md").read_text(encoding="utf-8")
    check("Caveats" in md and "Most machine-like passages" in md, "markdown report sections")
    calib = {"binoculars": {"method": "binoculars", "models": ["Qwen/Qwen3-0.6B-Base", "Qwen/Qwen3-0.6B"], "threshold": 5.0,
                            "date": "2026-01-01", "target_fpr": 0.05}}
    (TMP / "cal.json").write_text(json.dumps(calib))
    code, out, err = run("detect_ai.py", "t.docx", "--out", "h2", "--size", "small", "--max-chunks", "2", "--calibration", "cal.json")
    rep2 = json.loads((TMP / "h2" / "ai-report.json").read_text(encoding="utf-8"))
    check(rep2["meta"]["summary"]["binoculars"]["flagged_chunks"] == 2 and "calibrated" in rep2["meta"]["thresholds"]["binoculars"]["source"],
          "calibration file honoured (absurd threshold flags everything)")


def test_common_copies():
    print("shared module copies")
    a = (SCRIPTS / "text_common.py").read_bytes()
    b = (REPO / "skills" / "plagiarism-check" / "scripts" / "text_common.py").read_bytes()
    check(a == b, "text_common.py identical in both skills")


def main():
    make_docs()
    for t in (test_dry_run, test_calibration_math, test_heavy, test_common_copies):
        try:
            t()
        except Exception as exc:  # noqa: BLE001
            R["fail"] += 1
            print(f"  FAIL {t.__name__}: {type(exc).__name__}: {exc}")
    print(f"SUMMARY pass={R['pass']} fail={R['fail']} skip={R['skip']}")
    return 1 if R["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
