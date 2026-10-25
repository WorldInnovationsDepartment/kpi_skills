# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pypandoc_binary>=1.13",
#     "pymupdf>=1.24",
#     "pillow>=10",
# ]
# ///
"""Plain-assert (no pytest) regression harness for the axioms-paper-format skill
scripts: import_source.py, check_paper.py, build_paper.py, render_preview.py.

    uv run tests/axioms-paper-format/test_axioms.py

Works from any CWD; every path is derived from this file's location or a fresh
temporary directory. The interpreter running this file has every dependency the
skill scripts declare, so it runs them directly (sys.executable).

Covers: the shipped example (0 errors, 0 warnings), the importer on an amsart draft,
an article-class draft with \\and and thebibliography, a Markdown draft via pandoc and
the --new skeleton; every major check_paper.py rule on deliberately broken
manuscripts; log and PDF checks; packaging (zip contents); the preview renderer; and,
when a TeX engine is installed, a real compile of the example. Prints a final SUMMARY
line and exits non-zero if anything failed.
"""
from __future__ import annotations

import atexit
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "skills" / "axioms-paper-format"
SCRIPTS = SKILL_DIR / "scripts"
IMPORT = SCRIPTS / "import_source.py"
CHECK = SCRIPTS / "check_paper.py"
BUILD = SCRIPTS / "build_paper.py"
PREVIEW = SCRIPTS / "render_preview.py"
EXAMPLE = SKILL_DIR / "assets" / "example"
DEFS = SKILL_DIR / "assets" / "mdpi-template" / "Definitions"
TEMPLATE_PDF = SKILL_DIR / "assets" / "mdpi-template" / "template.pdf"
PY = sys.executable

_tmp = tempfile.TemporaryDirectory(prefix="axioms-paper-format-test-")
atexit.register(_tmp.cleanup)
TMP = Path(_tmp.name)

RESULTS: list[tuple[str, bool, str]] = []


def test(fn):
    try:
        fn()
        RESULTS.append((fn.__name__, True, ""))
        print(f"PASS {fn.__name__}")
    except AssertionError as e:
        RESULTS.append((fn.__name__, False, str(e)))
        print(f"FAIL {fn.__name__}: {e}")
    except Exception as e:  # noqa: BLE001
        RESULTS.append((fn.__name__, False, f"{type(e).__name__}: {e}"))
        print(f"FAIL {fn.__name__}: {type(e).__name__}: {e}")
    return fn


def run(script: Path, *args, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run([PY, str(script), *map(str, args)], capture_output=True, text=True, cwd=cwd)


def example_copy(name: str) -> Path:
    d = TMP / name
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(EXAMPLE, d)
    shutil.copytree(DEFS, d / "Definitions")
    return d / "paper.tex"


def findings(tex: Path, *extra) -> tuple[int, list[dict]]:
    js = tex.with_suffix(".json")
    p = run(CHECK, tex, "--json", js, *extra)
    return p.returncode, json.loads(js.read_text())


def codes(items, level=None) -> set[str]:
    return {x["code"] for x in items if level is None or x["level"] == level}


def mutate(name: str, *pairs) -> Path:
    """Copy the example and apply (old, new) replacements to paper.tex."""
    tex = example_copy(name)
    s = tex.read_text()
    for old, new in pairs:
        assert old in s, f"mutation anchor not found: {old[:50]}"
        s = s.replace(old, new, 1)
    tex.write_text(s)
    return tex


# ---------------------------------------------------------------- example

@test
def example_is_clean():
    tex = example_copy("clean")
    code, items = findings(tex)
    errs = [x for x in items if x["level"] in ("ERROR", "WARN")]
    assert code == 0, f"exit {code}: {errs}"
    assert not errs, errs


@test
def example_has_required_parts():
    s = (EXAMPLE / "paper.tex").read_text()
    assert "\\documentclass[axioms,article,submit,moreauthors]{Definitions/mdpi}" in s
    for macro in ("\\Title{", "\\Author{", "\\AuthorNames{", "\\address{", "\\corres{", "\\abstract{",
                  "\\keyword{", "\\MSC{", "\\authorcontributions{", "\\funding{", "\\dataavailability{",
                  "\\conflictsofinterest{", "\\PublishersNote{}"):
        assert macro in s, macro
    assert "\\TitleCitation" not in s and "\\AuthorCitation" not in s


# ---------------------------------------------------------------- importer

AMSART = r"""\documentclass[11pt]{amsart}
\usepackage{amsmath,amssymb,amsthm}
\usepackage[margin=1in]{geometry}
\usepackage{hyperref}
\usepackage{mathtools}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{conj}{Conjecture}
\theoremstyle{definition}
\newtheorem{defn}[theorem]{Definition}
\numberwithin{equation}{section}
\newcommand{\R}{\mathbb{R}}
\title{On contractions in metric spaces}
\author{Ivan Petrenko}
\address{Department of Mathematics, Kyiv University, 01601 Kyiv, Ukraine}
\email{ivan@example.com}
\author{Olena Kovalenko}
\address{Institute of Mathematics, 79000 Lviv, Ukraine}
\email{olena@example.com}
\subjclass[2020]{Primary 47H10; Secondary 54H25}
\keywords{fixed point, contraction, metric space}
\begin{document}
\begin{abstract}
We prove a fixed point theorem.

It is short.
\end{abstract}
\maketitle
\section{Introduction}
Banach \cite{banach} proved $$x=Tx.$$ % a comment that must disappear
\input{sec2}
\section*{Funding}
This research received no external funding.
\section*{Acknowledgments}
We thank the referees.
\bibliographystyle{amsplain}
\bibliography{refs}
\appendix
\section{Extra proof}
Text.
\end{document}
"""
SEC2 = r"""\section{Results}
\begin{theorem}\label{t1} Let $T$ be a contraction. \end{theorem}
\begin{proof} Trivial. \end{proof}
\begin{conj} Something. \end{conj}
\begin{figure}\includegraphics[width=5cm]{figs/plot}\caption{A plot.}\end{figure}
"""
BIB = "@article{banach,author={Banach, S.},title={Sur les op\\'erations},journal={Fundam. Math.}," \
      "year={1922},volume={3},pages={133--181},doi={10.4064/fm-3-1-133-181}}\n"


def make_amsart() -> Path:
    d = TMP / "draft-amsart"
    (d / "figs").mkdir(parents=True, exist_ok=True)
    (d / "draft.tex").write_text(AMSART)
    (d / "sec2.tex").write_text(SEC2)
    (d / "refs.bib").write_text(BIB)
    shutil.copy(EXAMPLE / "fig1.png", d / "figs" / "plot.png")
    return d / "draft.tex"


@test
def import_amsart():
    src = make_amsart()
    out = TMP / "out-amsart"
    p = run(IMPORT, src, "--out", out)
    assert p.returncode == 0, p.stderr
    s = (out / "paper.tex").read_text()
    assert "\\documentclass[axioms,article,submit,moreauthors]{Definitions/mdpi}" in s
    assert (out / "Definitions" / "mdpi.cls").exists()
    assert (out / "refs.bib").exists() and (out / "figs" / "plot.png").exists()
    assert "\\Title{On contractions in metric spaces}" in s
    assert "\\MSC{47H10; 54H25}" in s, re.findall(r"\\MSC\{[^}]*\}", s)
    assert "\\keyword{fixed point; contraction; metric space}" in s
    assert "Ivan Petrenko $^{1}$ and Olena Kovalenko $^{2}$" in s
    assert "Kyiv University, 01601 Kyiv, Ukraine; ivan@example.com" in s
    assert "\\begin{Theorem}" in s and "\\end{Theorem}" in s and "\\begin{theorem}" not in s
    assert "\\theoremstyle{mdpi}\\newtheorem{Conjecture}{Conjecture}" in s and "\\begin{Conjecture}" in s
    assert "\\newtheorem{theorem}" not in s and "numberwithin" not in s and "geometry" not in s.split(
        "\\Title")[0].split("seqsplit")[-1]
    assert "\\usepackage{mathtools}" in s
    assert "a comment that must disappear" not in s
    assert "\\[x=Tx.\\]" in s and "$$" not in s
    assert "\\funding{This research received no external funding.}" in s
    assert "\\acknowledgments{We thank the referees.}" in s
    assert "\\appendixstart" in s and "\\section{Extra proof}" in s
    assert "\\bibliography{refs}" in s and "\\bibliographystyle" not in s
    # abstract became one paragraph
    ab = re.search(r"\\abstract\{([^}]*)\}", s).group(1)
    assert "\n\n" not in ab and "It is short." in ab
    rep = (out / "import-report.md").read_text()
    assert "theorem (Theorem) -> Theorem" in rep and "geometry" in rep
    # the result is only blocked by the TODOs the author must answer
    code, items = findings(out / "paper.tex")
    assert code == 1
    assert "template.todo" in codes(items, "ERROR")
    assert not codes(items, "ERROR") & {"class.mdpi", "math.newtheorem", "math.env", "refs.undefined-cite",
                                        "figure.file", "msc.format", "keywords.count"}, codes(items, "ERROR")


@test
def import_refuses_overwrite():
    src = make_amsart()
    out = TMP / "out-amsart"
    if not (out / "paper.tex").exists():
        run(IMPORT, src, "--out", out)
    p = run(IMPORT, src, "--out", out)
    assert p.returncode == 1 and "exists" in p.stderr
    assert run(IMPORT, src, "--out", out, "--force").returncode == 0


ARTICLE = r"""\documentclass{article}
\usepackage{times}
\newtheorem{thm}{Theorem}
\newtheorem{prop}{Proposition}
\title{Some results}
\author{Anna Shevchenko\\ Department of Algebra, Kharkiv University, 61022 Kharkiv, Ukraine\\ \texttt{anna@example.org}}
\begin{document}
\maketitle
\begin{abstract} Abstract text. \textbf{Keywords:} groups; rings; modules \end{abstract}
\section{Introduction}
See \cite{b} and \cite{a}.
\begin{thm} A. \end{thm} \begin{prop} B. \end{prop}
\begin{thebibliography}{9}
\bibitem{a} A. Author, Paper A.
\bibitem{b} B. Author, Paper B.
\end{thebibliography}
\end{document}
"""


@test
def import_article_single_author():
    d = TMP / "draft-article"
    d.mkdir(exist_ok=True)
    (d / "draft.tex").write_text(ARTICLE)
    out = TMP / "out-article"
    p = run(IMPORT, d / "draft.tex", "--out", out)
    assert p.returncode == 0, p.stderr
    s = (out / "paper.tex").read_text()
    assert "\\documentclass[axioms,article,submit,oneauthor]{Definitions/mdpi}" in s
    assert "\\Author{Anna Shevchenko*}" in s, re.findall(r"\\Author\{[^\n]*", s)
    assert "\\address[1]{%\nDepartment of Algebra, Kharkiv University, 61022 Kharkiv, Ukraine; anna@example.org}" in s
    assert "\\corres{Correspondence: anna@example.org}" in s
    assert "\\keyword{groups; rings; modules}" in s
    assert "\\begin{Proposition}" in s and "\\usepackage{times}" not in s
    assert "\\begin{thebibliography}" in s.split("\\reftitle")[1]
    code, items = findings(out / "paper.tex")
    assert "refs.order" in codes(items, "ERROR"), "thebibliography a,b cited b,a must be flagged"
    assert "msc.missing" in codes(items, "WARN") or "template.todo" in codes(items, "ERROR")


@test
def import_markdown_via_pandoc():
    d = TMP / "draft-md"
    d.mkdir(exist_ok=True)
    (d / "draft.md").write_text("# Introduction\n\nWe study $x^2$.\n\n$$a=b$$\n\n# Conclusions\n\nDone.\n")
    out = TMP / "out-md"
    p = run(IMPORT, d / "draft.md", "--out", out)
    assert p.returncode == 0, p.stderr
    s = (out / "paper.tex").read_text()
    assert "\\section{Introduction}" in s and "\\section{Conclusions}" in s
    assert "a=b" in s
    assert "pandoc" in (out / "import-report.md").read_text()


@test
def import_new_skeleton():
    out = TMP / "out-new"
    p = run(IMPORT, "--new", "--out", out, "--authors", "3")
    assert p.returncode == 0, p.stderr
    s = (out / "paper.tex").read_text()
    assert "moreauthors" in s and (out / "references.bib").exists()
    assert "\\section{Introduction}" in s and "\\section{Conclusions}" in s
    p = run(IMPORT, "--new", "--out", TMP / "out-new1", "--authors", "1")
    assert "oneauthor" in (TMP / "out-new1" / "paper.tex").read_text()


@test
def import_rejects_pdf_and_missing():
    assert run(IMPORT, TMP / "nope.tex", "--out", TMP / "x1").returncode == 1
    (TMP / "x.pdf").write_bytes(b"%PDF-1.4")
    p = run(IMPORT, TMP / "x.pdf", "--out", TMP / "x2")
    assert p.returncode == 1 and "PDF" in p.stderr


# ---------------------------------------------------------------- checker rules

CASES = [
    # (name, replacements, expected codes (level, code))
    ("class", [("{Definitions/mdpi}", "{amsart}")], [("ERROR", "class.mdpi")]),
    ("journal", [("[axioms,article,", "[mathematics,article,")], [("ERROR", "class.journal")]),
    ("oneauthor", [("submit,moreauthors]", "submit,oneauthor]")], [("ERROR", "class.authors")]),
    ("accept", [("submit,moreauthors]", "accept,moreauthors]")], [("ERROR", "class.submit")]),
    ("obsolete", [("\\AuthorNames{", "\\TitleCitation{X}\n\\AuthorNames{")], [("ERROR", "template.obsolete")]),
    ("newtheorem", [("\\newcommand{\\N}", "\\newtheorem{theorem}{Theorem}[section]\n\\newcommand{\\N}")],
     [("ERROR", "math.newtheorem"), ("WARN", "math.numbering")]),
    ("numberwithin", [("\\newcommand{\\N}", "\\numberwithin{equation}{section}\n\\newcommand{\\N}")],
     [("WARN", "math.numbering")]),
    ("lowerenv", [("\\begin{Lemma}\\label{lem:steps}", "\\begin{lemma}\\label{lem:steps}"),
                  ("\\end{Lemma}", "\\end{lemma}")], [("ERROR", "math.env")]),
    ("geometry", [("\\newcommand{\\N}", "\\usepackage[margin=2cm]{geometry}\n\\geometry{a4paper}\n\\newcommand{\\N}")],
     [("WARN", "preamble.package"), ("ERROR", "preamble.layout")]),
    ("forbidden", [("\\newcommand{\\N}", "\\usepackage{times}\n\\newcommand{\\N}")], [("ERROR", "preamble.package")]),
    ("titlecase", [("\\Title{An A Priori Error Bound", "\\Title{An a priori error bound")],
     [("WARN", "front.title.case")]),
    ("nostar", [("$^{2,}$*}", "$^{2}$}")], [("ERROR", "front.corresponding")]),
    ("nocorres", [("\\corres{Correspondence: o.kovalenko@example.com}", "\\corres{Correspondence: TBA}")],
     [("ERROR", "front.corres")]),
    ("orcid", [("{0000-0002-1825-0097}", "{1234}")], [("ERROR", "front.orcid")]),
    ("initials", [("Ivan Petrenko $^{1}$", "I. Petrenko $^{1}$")], [("WARN", "front.author.fullname")]),
    ("abstract-cite", [("\\abstract{Fixed point iterations", "\\abstract{Following \\cite{kirk1965}, fixed point "
                                                             "iterations")], [("ERROR", "abstract.citation")]),
    ("abstract-para", [("This note revisits", "\n\nThis note revisits")], [("ERROR", "abstract.paragraph")]),
    ("abstract-eq", [("The proof uses", "\\[a=b\\] The proof uses")], [("ERROR", "abstract.equation")]),
    ("abstract-long", [("The proof uses", "word " * 120 + "The proof uses")], [("WARN", "abstract.length")]),
    ("kw-comma", [("\\keyword{Banach contraction principle; fixed point; Picard iteration; a priori estimate; "
                   "complete metric space}", "\\keyword{Banach contraction principle, fixed point, Picard iteration}")],
     [("ERROR", "keywords.separator")]),
    ("kw-few", [("\\keyword{Banach contraction principle; fixed point; Picard iteration; a priori estimate; "
                 "complete metric space}", "\\keyword{fixed point; contraction}")], [("ERROR", "keywords.count")]),
    ("msc-bad", [("\\MSC{47H10; 54H25; 65J15}", "\\MSC{Primary 47H10, 54H25, functional analysis}")],
     [("ERROR", "msc.format"), ("WARN", "msc.separator")]),
    ("msc-missing", [("\\MSC{47H10; 54H25; 65J15}", "")], [("WARN", "msc.missing")]),
    ("fig-caption", [("\\caption{Error of the Picard iterates for $Tx=\\tfrac12\\cos x$ and the a priori bound~"
                      "\\eqref{eq:apriori} (logarithmic scale).\\label{fig:error}}", "")],
     [("ERROR", "figure.caption")]),
    ("table-pos", [("\\caption{Picard iterates", "\\begin{tabular}{c}x\\end{tabular}\\caption{Picard iterates")],
     [("WARN", "table.caption.position")]),
    ("vrules", [("\\begin{tabularx}{\\textwidth}{CCCC}", "\\begin{tabularx}{\\textwidth}{|C|C|C|C|}")],
     [("WARN", "table.vrules")]),
    ("uncited-fig", [("Table~\\ref{tab:iterates} and Figure~\\ref{fig:error} compare",
                      "Table~\\ref{tab:iterates} compares"),
                     ("as Figure~\\ref{fig:error} shows", "as the plot shows")], [("WARN", "figure.cited")]),
    ("undefined-ref", [("Section~\\ref{sec:concl} concludes", "Section~\\ref{sec:nope} concludes")],
     [("ERROR", "refs.undefined")]),
    ("fig-abbrev", [("as Figure~\\ref{fig:error} shows", "as Fig.~\\ref{fig:error} shows")],
     [("WARN", "text.abbrev")]),
    ("missing-graphic", [("{fig1}", "{nothere}")], [("ERROR", "figure.file")]),
    ("cite-undefined", [("\\cite{caristi1976}", "\\cite{nokey}")], [("ERROR", "refs.undefined-cite")]),
    ("cite-locator", [("Ref.~\\cite{granas2003} gives", "Ref.~\\cite[p.~10]{granas2003} gives")],
     [("WARN", "cite.locator")]),
    ("cite-start", [("Ref.~\\cite{granas2003} gives", "\\cite{granas2003} gives")],
     [("WARN", "cite.sentence-start")]),
    ("bibstyle", [("\\bibliography{references}", "\\bibliographystyle{plain}\n\\bibliography{references}")],
     [("WARN", "refs.style")]),
    ("no-contrib", [("\\authorcontributions{", "\\iffalse{"), ("manuscript.}\n\n\\funding", "manuscript.}\\fi\n\n\\funding")],
     [("ERROR", "back.contributions")]),
    ("contrib-end", [(" All authors have read and agreed to the published version of the manuscript.", "")],
     [("ERROR", "back.contributions")]),
    ("contrib-initials", [("supervision, O.K.", "supervision, X.Y.")], [("WARN", "back.contributions")]),
    ("no-funding", [("\\funding{This research received no external funding.}", "")], [("ERROR", "back.funding")]),
    ("no-data", [("\\dataavailability{No new data were created or analyzed in this study. Data sharing is not "
                  "applicable to this article.}", "")], [("ERROR", "back.data")]),
    ("no-coi", [("\\conflictsofinterest{The authors declare no conflicts of interest.}", "")], [("ERROR", "back.coi")]),
    ("order", [("\\funding{This research received no external funding.}\n", ""),
               ("\\conflictsofinterest{", "\\funding{This research received no external funding.}\n\n"
                                          "\\conflictsofinterest{")], [("WARN", "back.order")]),
    ("ai", [("\\acknowledgments{The authors thank", "\\acknowledgments{ChatGPT polished the text. The authors thank")],
     [("WARN", "back.ai")]),
    ("leftover", [("\\section{Introduction}", "\\setcounter{section}{-1}\n\\section{How to Use this Template}\n"
                                              "\\section{Introduction}")], [("ERROR", "template.leftover")]),
    ("todo", [("\\funding{This research", "\\funding{TODO This research")], [("ERROR", "template.todo")]),
    ("hardcoded", [("which completes the induction.", "which completes the induction, as in Theorem 2.1.")],
     [("WARN", "refs.hardcoded")]),
    ("dollars", [("For $x_0\\in X$ the", "For $$x_0\\in X$$ the")], [("WARN", "math.display")]),
    ("footnote", [("Throughout, $(X,d)$", "Throughout\\footnote{note}, $(X,d)$")], [("WARN", "text.footnote")]),
    ("space", [("Throughout, $(X,d)$ is a complete metric space.", "Throughout, $(X,d)$ is complete.Hence fine.")],
     [("WARN", "text.space")]),
    ("enotation", [("guarantee $\\varepsilon=10^{-6}$", "guarantee an error of 1e-6")], [("WARN", "text.enotation")]),
    ("proof-for", [("\\begin{proof}\nFor $m>n$", "\\begin{proof}[Proof for Theorem 1]\nFor $m>n$")],
     [("WARN", "math.proof")]),
    ("no-intro", [("\\section{Introduction}", "\\section{Background}")], [("WARN", "body.introduction")]),
    ("starred", [("\\section{Conclusions}\\label{sec:concl}", "\\section*{Conclusions}\\label{sec:concl}")],
     [("WARN", "body.unnumbered")]),
]


@test
def checker_rules():
    failures = []
    for name, pairs, expected in CASES:
        tex = mutate(f"case-{name}", *pairs)
        code, items = findings(tex)
        got = {(x["level"], x["code"]) for x in items}
        miss = [e for e in expected if e not in got]
        if miss:
            failures.append(f"{name}: expected {miss}, got {sorted(c for c in got if c[0] != 'INFO')}")
        if any(lv == "ERROR" for lv, _ in expected) and code != 1:
            failures.append(f"{name}: exit {code}, expected 1")
    assert not failures, "\n  " + "\n  ".join(failures)


@test
def checker_bib_rules():
    tex = example_copy("bib")
    bib = tex.parent / "references.bib"
    s = bib.read_text()
    s = s.replace("journal = {Trans. Am. Math. Soc.},", "journal = {Transactions of the American Mathematical Society},")
    s = s.replace("  doi     = {10.1112/jlms/s1-37.1.74}\n", "")
    s = s.replace("doi     = {10.2307/2313345}", "doi = {https://doi.org/10.2307/2313345}")
    s += "\n@article{dup, author={X, Y}, title={T}, journal={J. Math.}, year={2000}, volume={1}, pages={1--2}," \
         " doi={10.1007/978-0-387-21593-8}}\n@book{nopub, author={Z, Z}, title={B}}\n"
    bib.write_text(s)
    tx = tex.read_text().replace("monographs~\\cite{goebel1990,granas2003}", "monographs~\\cite{goebel1990,granas2003,dup,nopub}")
    tex.write_text(tx)
    code, items = findings(tex)
    got = {(x["level"], x["code"]) for x in items}
    for e in [("WARN", "bib.journal-abbrev"), ("WARN", "bib.doi"), ("ERROR", "refs.duplicate"),
              ("ERROR", "bib.fields")]:
        assert e in got, (e, sorted(got))
    assert code == 1


@test
def checker_missing_definitions_and_bibfile():
    tex = example_copy("nodefs")
    shutil.rmtree(tex.parent / "Definitions")
    (tex.parent / "references.bib").unlink()
    code, items = findings(tex)
    assert {"class.files", "refs.bibfile"} <= codes(items, "ERROR"), codes(items, "ERROR")


@test
def checker_log_and_pdf():
    tex = example_copy("logpdf")
    log = tex.with_suffix(".log")
    log.write_text("! Undefined control sequence.\nLaTeX Warning: Reference `x' on page 2 undefined on input line 4.\n"
                   "Overfull \\hbox (25.3pt too wide) in paragraph at lines 3--4\n")
    code, items = findings(tex, "--log", log, "--pdf", TEMPLATE_PDF)
    got = codes(items)
    assert {"log.error", "log.undefined", "log.overfull", "pdf.pages"} <= got, got
    assert code == 1
    code, items = findings(tex, "--log", TMP / "none.log")
    assert "log.missing" in codes(items, "ERROR")


# ---------------------------------------------------------------- build / zip / preview

@test
def package_zip_no_compile():
    tex = example_copy("zip")
    p = run(BUILD, tex, "--zip", "--no-compile")
    assert p.returncode == 0, p.stderr
    z = tex.parent / "submission.zip"
    names = set(zipfile.ZipFile(z).namelist())
    for n in ("paper.tex", "references.bib", "fig1.png", "Definitions/mdpi.cls", "Definitions/mdpi.bst",
              "Definitions/journalnames.tex"):
        assert n in names, (n, sorted(names))
    assert not any(n.endswith((".aux", ".log", ".json")) for n in names), names
    assert "no compiled PDF" in p.stdout


@test
def build_engine_detection():
    tex = example_copy("compile")
    engine = next((e for e in ("latexmk", "pdflatex", "tectonic") if shutil.which(e)), None)
    p = run(BUILD, tex, "--zip")
    if engine is None:
        assert p.returncode == 3 and "no TeX engine" in p.stderr, (p.returncode, p.stderr)
        print("     (no TeX engine installed: compile test skipped)")
        return
    assert p.returncode == 0, p.stdout + p.stderr
    pdf = tex.with_suffix(".pdf")
    assert pdf.exists()
    code, items = findings(tex, "--log", tex.with_suffix(".log"), "--pdf", pdf)
    assert not codes(items, "ERROR"), [x for x in items if x["level"] == "ERROR"]
    assert "paper.pdf" in zipfile.ZipFile(tex.parent / "submission.zip").namelist()


@test
def build_bad_args():
    assert run(BUILD, TMP / "nope.tex").returncode == 2


@test
def preview_renders():
    out = TMP / "preview"
    p = run(PREVIEW, TEMPLATE_PDF, "--out", out)
    assert p.returncode == 0, p.stderr
    assert (out / "page-01.png").exists() and (out / "contact-sheet.png").exists()
    assert re.search(r"^\d+ page\(s\)", p.stdout)


# ---------------------------------------------------------------- bundled template sanity

@test
def bundled_template_matches_expectations():
    cls = (DEFS / "mdpi.cls").read_text(errors="replace")
    assert "\\DeclareOption{oneauthor}" in cls and "\\newcommand{\\MSC}" in cls
    for env in ("Theorem", "Lemma", "Corollary", "Proposition", "Definition", "Remark", "Example"):
        assert f"\\newtheorem{{{env}}}" in cls, env
    assert "TitleCitation" not in cls
    jn = (DEFS / "journalnames.tex").read_text(errors="replace")
    assert "\\DeclareOption{axioms}" in jn


if __name__ == "__main__":
    failed = [r for r in RESULTS if not r[1]]
    print(f"SUMMARY: {len(RESULTS) - len(failed)} passed, {len(failed)} failed")
    sys.exit(1 if failed else 0)
