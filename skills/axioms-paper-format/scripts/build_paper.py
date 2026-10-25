# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""build_paper.py -- compile an Axioms (MDPI) manuscript and package it for SuSy.

    uv run build_paper.py paper.tex                    # compile -> paper.pdf (+ paper.log)
    uv run build_paper.py paper.tex --zip              # compile, then write submission.zip
    uv run build_paper.py paper.tex --zip --no-compile # package only (no TeX installed, e.g. Overleaf user)
    uv run build_paper.py paper.tex --engine tectonic  # force an engine: latexmk | pdflatex | tectonic

Compilation uses the first engine found: latexmk (-pdf), then pdflatex + bibtex
(pdflatex, bibtex, pdflatex, pdflatex), then tectonic. MDPI's class is written for
pdfLaTeX, so XeLaTeX/LuaLaTeX are not offered. With no engine at all it says so and
exits 3; the manuscript can then be compiled on Overleaf, which is also MDPI's
recommended route ("Submit to an MDPI journal").

The zip contains exactly what the editorial office needs to recompile: the .tex,
Definitions/, every \\includegraphics file, every \\input file, the .bib file(s), the
.bbl if one was produced, and the compiled PDF if present. Paths inside the zip are
the same as on disk, relative to the .tex. Auxiliary files (.aux, .log, .out,
.synctex.gz, ...) are left out.

Exit codes: 0 ok, 1 compile errors (see the printed log excerpt), 2 bad arguments,
3 no TeX engine found.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from axioms_common import (
    bib_files,
    find_macros,
    graphics_paths,
    includegraphics,
    load_manuscript,
    resolve_graphic,
)

ENGINES = ["latexmk", "pdflatex", "tectonic"]


def find_engine(prefer: str | None) -> str | None:
    order = [prefer] if prefer else ENGINES
    for e in order:
        if shutil.which(e) and (e != "pdflatex" or shutil.which("bibtex")):
            return e
    return None


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                       errors="replace")
    return p.returncode, p.stdout


def compile_tex(tex: Path, engine: str, verbose: bool) -> int:
    cwd, name = tex.parent, tex.name
    stem = tex.stem
    if engine == "latexmk":
        steps = [["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", name]]
    elif engine == "pdflatex":
        pl = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", name]
        steps = [pl, ["bibtex", stem], pl, pl]
    else:
        steps = [["tectonic", "--keep-logs", "--keep-intermediates", name]]
    for cmd in steps:
        if verbose:
            print("$ " + " ".join(cmd))
        code, out = run(cmd, cwd)
        if code != 0 and not (cmd[0] == "bibtex" and "I found no" in out):
            print(f"error: `{' '.join(cmd)}` failed (exit {code})", file=sys.stderr)
            excerpt = [ln for ln in out.splitlines() if ln.startswith("!") or ":" in ln and "error" in ln.lower()]
            for ln in (excerpt or out.splitlines())[-15:]:
                print("  " + ln, file=sys.stderr)
            return 1
    pdf = cwd / f"{stem}.pdf"
    if not pdf.exists():
        print("error: no PDF produced", file=sys.stderr)
        return 1
    log = cwd / f"{stem}.log"
    warn = ""
    if log.exists():
        text = log.read_text(errors="replace")
        n_over = len(re.findall(r"Overfull \\hbox", text))
        undef = "undefined" in text and re.search(r"(Reference|Citation) `[^']+' on page \d+ undefined", text)
        warn = f" ({n_over} overfull box(es){', UNDEFINED references/citations' if undef else ''})"
    print(f"compiled {pdf}{warn}")
    return 0


def collect(tex: Path) -> tuple[list[Path], list[str]]:
    """Files the editorial office needs, relative to tex.parent; plus warnings."""
    base = tex.parent
    ms = load_manuscript(tex)
    files: list[Path] = [tex]
    warnings = []
    defs = base / "Definitions"
    if defs.is_dir():
        files += [p for p in sorted(defs.rglob("*")) if p.is_file() and not p.name.startswith(".")]
    else:
        warnings.append("Definitions/ folder missing next to the .tex")
    gpaths = graphics_paths(ms.preamble)
    for g in includegraphics(ms.tex):
        p = resolve_graphic(g.args[0].strip(), base, gpaths)
        if p is None:
            warnings.append(f"graphic '{g.args[0].strip()}' not found")
        else:
            files.append(p)
    for name in ("input", "include"):
        for m in find_macros(ms.body + ms.preamble, name):
            if m.args:
                p = base / m.args[0].strip()
                p = p if p.suffix else p.with_suffix(".tex")
                (files.append(p) if p.exists() else warnings.append(f"\\{name}{{{m.args[0]}}} not found"))
    for b in bib_files(ms.tex, base):
        (files.append(b) if b.exists() else warnings.append(f"{b.name} not found"))
    for extra in (tex.with_suffix(".bbl"), tex.with_suffix(".pdf")):
        if extra.exists():
            files.append(extra)
    seen, out = set(), []
    for f in files:
        r = f.resolve()
        if r not in seen:
            seen.add(r)
            out.append(f)
    return out, warnings


def make_zip(tex: Path, dest: Path) -> int:
    files, warnings = collect(tex)
    base = tex.parent.resolve()
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            rf = f.resolve()
            arc = rf.relative_to(base) if rf.is_relative_to(base) else Path(rf.name)
            z.write(rf, str(arc))
    size = dest.stat().st_size / 1e6
    print(f"wrote {dest} ({len(files)} files, {size:.1f} MB)")
    if not tex.with_suffix(".pdf").exists():
        warnings.append("no compiled PDF in the zip: compile first (or upload the Overleaf PDF separately)")
    if size > 120:
        warnings.append("zip exceeds the 120 MB SuSy limit: contact axioms@mdpi.com")
    for w in warnings:
        print(f"warning: {w}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("tex", type=Path)
    ap.add_argument("--zip", nargs="?", const="submission.zip", help="write the SuSy zip (default submission.zip "
                                                                     "next to the .tex)")
    ap.add_argument("--no-compile", action="store_true")
    ap.add_argument("--engine", choices=ENGINES)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args(argv)
    tex = a.tex
    if not tex.exists() or tex.suffix != ".tex":
        print(f"error: {tex} is not an existing .tex file", file=sys.stderr)
        return 2
    code = 0
    if not a.no_compile:
        engine = find_engine(a.engine)
        if not engine:
            print("error: no TeX engine found (latexmk, pdflatex+bibtex or tectonic). Install TeX Live/MacTeX "
                  "(or `brew install tectonic`), or compile on Overleaf; `--no-compile` still packages the "
                  "sources.", file=sys.stderr)
            return 3
        code = compile_tex(tex, engine, a.verbose)
    if a.zip and code == 0:
        dest = Path(a.zip)
        if not dest.is_absolute() and dest.parent == Path("."):
            dest = tex.parent / dest
        code = make_zip(tex, dest)
    return code


if __name__ == "__main__":
    sys.exit(main())
