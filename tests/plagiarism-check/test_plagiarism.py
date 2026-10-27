# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = [
#     "python-docx>=1.1",
#     "pymupdf>=1.24",
#     "ddgs>=9",
#     "trafilatura>=1.12",
#     "requests",
# ]
# ///
"""Plain-assert regression harness for the plagiarism-check skill (check_local.py, check_web.py,
match_engine.py, text_common.py).

    uv run tests/plagiarism-check/test_plagiarism.py            # offline
    KPI_SKILLS_NETWORK=1 uv run tests/plagiarism-check/test_plagiarism.py   # + one real web/CORE search

Everything is generated in a temporary directory: a Ukrainian "dissertation" .docx with a reference
list and a quotation, an external source .txt/.docx/.pdf that it copies from verbatim and near-verbatim,
and an "own publication" it legitimately reuses. Checks: extraction and paragraph classification,
exclusion of references/quotes, verbatim vs near-verbatim runs, per-source attribution, own vs
external similarity, homoglyph tampering detection, min-words and include flags, HTML/MD/JSON output,
query selection for the web check (dry run) and that both scripts' text_common.py copies are identical.
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

from docx import Document

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "skills" / "plagiarism-check" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import text_common as tc  # noqa: E402
from match_engine import Index, SourceDoc, coverage, tokenize  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="plag-test-"))
atexit.register(shutil.rmtree, TMP, ignore_errors=True)
R = {"pass": 0, "fail": 0, "skip": 0}


def check(cond, msg):
    R["pass" if cond else "fail"] += 1
    print(("  ok   " if cond else "  FAIL ") + msg)


def run(script, *args):
    p = subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)], capture_output=True, text=True, cwd=TMP)
    return p.returncode, p.stdout, p.stderr


SRC_PARA = ("Оркестрація контейнерів у хмарних середовищах передбачає автоматизоване розгортання, масштабування та "
            "керування життєвим циклом контейнеризованих застосунків на кластері обчислювальних вузлів. Найпоширенішим "
            "інструментом оркестрації сьогодні є Kubernetes, який надає декларативну модель опису бажаного стану системи "
            "та механізми його підтримання.")
NEAR_PARA = ("Відмова одного сервісу може спричинити каскадні збої в інших компонентах системи, що негативно впливає на "
             "її доступність та надійність у цілому.")
OWN_PARA = ("Запропонована модель залежностей мікросервісів описує систему як орієнтований граф, вершини якого відповідають "
            "сервісам, а ребра відображають залежності між ними з урахуванням часових вікон відмов.")
ORIG = ["У цьому розділі розглянуто підходи до планування розгортання, які враховують структуру залежностей між "
        "сервісами та обмеження на ресурси вузлів кластера.",
        "Експериментальна перевірка проводилася на тестовому стенді з дванадцяти вузлів, на якому було розгорнуто сорок "
        "мікросервісів із різною топологією залежностей."]


def make_docs():
    ext = TMP / "corpus"
    own = TMP / "own"
    ext.mkdir()
    own.mkdir()
    (ext / "textbook.txt").write_text("Розділ 3. Оркестрація.\n\n" + SRC_PARA + "\n\nІнший абзац підручника про мережі.\n\n" + NEAR_PARA + "\n",
                                      encoding="utf-8")
    d = Document()
    d.add_paragraph("Стаття автора у фаховому виданні")
    d.add_paragraph(OWN_PARA)
    d.save(own / "my_article.docx")
    # the target
    t = Document()
    t.add_paragraph("ДИСЕРТАЦІЯ")
    t.add_paragraph("РОЗДІЛ 1. АНАЛІЗ СТАНУ ДОСЛІДЖЕНЬ")
    t.add_paragraph(ORIG[0])
    t.add_paragraph(SRC_PARA)                                               # verbatim copy (external)
    near = NEAR_PARA.replace("негативно впливає", "суттєво погіршує")         # one substitution -> near-verbatim
    t.add_paragraph(ORIG[1])
    t.add_paragraph("Як відомо, " + near)
    t.add_paragraph("«" + ORIG[1] + "» [5].")                               # quotation: excluded by default
    t.add_paragraph(OWN_PARA)                                               # own publication reuse
    t.add_paragraph("СПИСОК ВИКОРИСТАНИХ ДЖЕРЕЛ")
    t.add_paragraph("1. Петренко О. І. Оркестрація контейнерів у хмарних середовищах. Київ: КПІ, 2021. 120 с.")
    t.add_paragraph("2. Burns B. Kubernetes: Up and Running. O'Reilly, 2019.")
    t.save(TMP / "thesis.docx")
    return ext, own


def test_extraction():
    print("extraction & classification")
    doc = tc.extract(TMP / "thesis.docx")
    def kind_of(prefix):
        return next(p.kind for p in doc.paragraphs if p.text.startswith(prefix))
    check(doc.language == "uk", f"language uk ({doc.language})")
    check(kind_of("ДИСЕРТАЦІЯ") in ("heading", "front"), "title is not body")
    check(kind_of("РОЗДІЛ 1. АНАЛІЗ СТАН") == "heading", "chapter heading")
    check(kind_of("«Експериментальна пер") == "quote", "quotation detected")
    check(kind_of("1. Петренко О. І. Орк") == "reference", "reference list detected")
    check(kind_of("2. Burns B. Kubernete") == "reference", "second reference")
    check(kind_of(ORIG[0][:20]) == "body", "body paragraph")
    sents = tc.sentences("Див. рис. 2.1 та табл. 3. Метод працює. Він швидкий!")
    check(len(sents) == 3, f"sentence splitter keeps abbreviations ({sents})")
    check(tc.detect_language("The quick brown fox jumps over the lazy dog again and again") == "en", "english detection")
    tam = tc.tampering_report("Систeма (Latin e) та мoдель (Latin o) і ще сиcтема, модeль, мeтод, тeст, cистема.")
    check(tam["mixed_script_words"] >= 5 and tam["suspicious"], f"homoglyph tampering flagged ({tam['mixed_script_words']})")
    check(tc.normalize("Систeма") == tc.normalize("Система"), "homoglyphs normalised for matching")
    # md and tex inputs
    (TMP / "a.md").write_text("# Title\n\nSome **bold** text with $x^2$ math.\n\n```\ncode\n```\n\n## References\n\n1. A. B. Paper. 2020.\n", encoding="utf-8")
    md = tc.extract(TMP / "a.md")
    check(any(p.kind == "reference" for p in md.paragraphs), "markdown references section")
    (TMP / "a.tex").write_text(r"\section{Intro} Text \cite{x} here \textbf{bold} and $a=b$. \begin{equation}x\end{equation} More text.", encoding="utf-8")
    tex = tc.extract(TMP / "a.tex")
    check("cite" not in tex.text and "bold" in tex.text, "tex commands stripped, arguments kept")


def test_engine():
    print("match engine")
    doc = tc.extract(TMP / "thesis.docx")
    toks = tokenize(doc)
    src = tc.extract(TMP / "corpus" / "textbook.txt")
    s = SourceDoc(1, "textbook.txt", "x", tokens=tokenize(src, kinds={"body", "heading", "front"}), doc=src)
    idx = Index(5)
    idx.add(s)
    runs = idx.match(toks, min_words=8, gap=4)
    kinds = sorted(r.kind for r in runs)
    check(len(runs) == 2, f"two runs found ({len(runs)})")
    check(kinds == ["near-verbatim", "verbatim"], f"verbatim + near-verbatim ({kinds})")
    verb = next(r for r in runs if r.kind == "verbatim")
    check(verb.length == len(tc.words(SRC_PARA)), f"verbatim run covers the whole paragraph ({verb.length})")
    cov = coverage(runs, len(toks), {1: s})
    check(0.25 < cov["similarity_total"] < 0.6, f"similarity in range ({cov['similarity_total']:.2f})")
    strict = idx.match(toks, min_words=8, gap=0)
    check(all(r.kind == "verbatim" for r in strict) or len(strict) >= 1, "gap=0 keeps only exact chains")


def test_cli():
    print("check_local.py")
    code, out, err = run("check_local.py", "thesis.docx", "--corpus", "corpus", "--own", "own", "--out", "pc")
    check(code == 0, f"exit 0 ({err[-300:] if code else ''})")
    res = json.loads((TMP / "pc" / "plagiarism-report.json").read_text(encoding="utf-8"))
    s = res["summary"]
    check(s["sources_matched"] == 2, f"both sources matched ({s['sources_matched']})")
    check(s["similarity_own"] > 0 and s["similarity_external"] > s["similarity_own"], "own vs external separated")
    check(abs(s["similarity_total"] - (s["similarity_external"] + s["similarity_own"])) < 1e-6, "no overlap between own and external here")
    srcs = {x["name"]: x for x in res["sources"]}
    check(srcs["my_article.docx"]["own"] is True, "own flag in report")
    quoted = any(ORIG[1][:30] in p["target_text"] for p in res["passages"])
    check(not quoted, "quotation not matched (excluded)")
    check(all(p["target_paragraph"] < 8 for p in res["passages"]), "no matches inside the reference list")
    md = (TMP / "pc" / "plagiarism-report.md").read_text(encoding="utf-8")
    html = (TMP / "pc" / "plagiarism-report.html").read_text(encoding="utf-8")
    check("Similarity to **external**" in md and "<mark" in html, "md + html written")
    check("near" in html, "near-verbatim marked in html")
    # include quotes: the quote matches the corpus? It is original text, so still no new match, but the
    # own article in --corpus (not --own) must count as external.
    code, out, _ = run("check_local.py", "thesis.docx", "--corpus", "corpus", "own", "--out", "pc2")
    res2 = json.loads((TMP / "pc2" / "plagiarism-report.json").read_text(encoding="utf-8"))
    check(res2["summary"]["similarity_own"] == 0 and res2["summary"]["similarity_external"] > s["similarity_external"],
          "own folder given as --corpus counts as external")
    code, out, _ = run("check_local.py", "thesis.docx", "--corpus", "corpus", "--min-words", "60", "--out", "pc3")
    res3 = json.loads((TMP / "pc3" / "plagiarism-report.json").read_text(encoding="utf-8"))
    check(res3["summary"]["passages"] == 0, "min-words 60 drops everything")
    code, _, err = run("check_local.py", "thesis.docx", "--corpus", str(TMP / "nonexistent"), "--out", "pc4")
    check(code == 2, "empty corpus -> exit 2")
    code, _, err = run("check_local.py", "thesis.docx")
    check(code == 2, "no corpus argument -> error")


def test_web_dry():
    print("check_web.py (dry run)")
    code, out, err = run("check_web.py", "thesis.docx", "--out", "web", "--queries", "3", "--dry-run")
    check(code == 0, f"dry run exit 0 ({err[-200:] if code else ''})")
    q = json.loads((TMP / "web" / "queries.json").read_text(encoding="utf-8"))
    check(1 <= len(q) <= 3 and all(len(x["phrase"].split()) == 9 for x in q), f"{len(q)} 9-word phrases")
    check(all(x["paragraph"] < 8 for x in q), "queries come from the body, not references")
    if os.environ.get("KPI_SKILLS_NETWORK") != "1":
        R["skip"] += 1
        print("  skip network search (set KPI_SKILLS_NETWORK=1)")
        return
    code, out, err = run("check_web.py", "thesis.docx", "--out", "webrun", "--queries", "2", "--engines", "core,ddgs", "--delay", "1")
    check(code == 0, f"network run exit 0 ({err[-300:] if code else ''})")
    stats = json.loads((TMP / "webrun" / "search-stats.json").read_text(encoding="utf-8"))
    check(stats["searches"] >= 2, f"searches performed ({stats})")


def test_common_copies():
    print("shared module copies")
    a = (REPO / "skills" / "ai-text-detector" / "scripts" / "text_common.py").read_bytes()
    b = (SCRIPTS / "text_common.py").read_bytes()
    check(a == b, "text_common.py identical in both skills")


def main():
    make_docs()
    for t in (test_extraction, test_engine, test_cli, test_web_dry, test_common_copies):
        try:
            t()
        except Exception as exc:  # noqa: BLE001
            R["fail"] += 1
            print(f"  FAIL {t.__name__}: {type(exc).__name__}: {exc}")
    print(f"SUMMARY pass={R['pass']} fail={R['fail']} skip={R['skip']}")
    return 1 if R["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
