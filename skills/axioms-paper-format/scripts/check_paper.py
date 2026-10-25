# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pymupdf>=1.24",
#     "pillow>=10",
# ]
# ///
"""check_paper.py -- check an MDPI LaTeX manuscript against the requirements of
*Axioms* (https://www.mdpi.com/journal/axioms).

    uv run check_paper.py paper.tex                                  # source checks (+ .bib, figures)
    uv run check_paper.py paper.tex --log paper.log --pdf paper.pdf  # + compile log and PDF checks
    uv run check_paper.py paper.tex --json findings.json             # also write the findings as JSON

Prints one line per finding:

    ERROR <code> [line N]: ...   violates a stated requirement or breaks compilation -> fix
    WARN  <code> [line N]: ...   a guideline of the MDPI author/layout guide, or a likely problem
    INFO  <code>: ...            reminders that cannot be checked automatically

then `SUMMARY: E error(s), W warning(s), I info`, and exits 1 if there is any ERROR
(0 otherwise). Every rule, its source and its severity are listed in
references/requirements.md.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from axioms_common import (
    ARTICLE_TYPES,
    BACK_ORDER,
    CLASS_COUNTERS,
    CLASS_NAME,
    CLASS_PACKAGES,
    CLASS_THEOREMS,
    DOI_RE,
    EMAIL_RE,
    FORBIDDEN_PACKAGES,
    JOURNAL,
    MSC_CODE_RE,
    ORCID_RE,
    STD_ALL_READ,
    TEMPLATE_LEFTOVERS,
    bib_files,
    bibitems,
    citations,
    detex,
    env_names,
    find_envs,
    find_macros,
    first_cite_order,
    graphics_paths,
    includegraphics,
    labels,
    line_of,
    load_manuscript,
    macro_arg,
    parse_bib,
    read_text,
    refs,
    resolve_graphic,
    section_text,
    sections,
    strip_math,
    words,
)

ABBREV_OK = {"MSC", "MDPI", "DOI", "ORCID", "USA", "UK", "EU", "PDE", "ODE", "PDEs", "ODEs", "II", "III", "IV",
             "VI", "VII", "VIII", "IX", "XI", "XII", "LaTeX", "TeX", "CC", "BY"}
TITLE_SMALL = {"a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet", "as", "at", "by", "in", "of",
               "off", "on", "per", "to", "up", "via", "with", "from", "into", "onto", "over", "than", "vs",
               "versus", "its", "is"}
FULL_JOURNAL_WORDS = re.compile(r"\b(Journal|Mathematics|Mathematical|Proceedings|Transactions|Society|"
                                r"International|Applied|Analysis|Annals|Letters|Communications|Bulletin|"
                                r"Mathematische|Mathematik|Equations|Differential|Theory|Research|Physics)\b")


class Report:
    def __init__(self):
        self.items: list[dict] = []

    def add(self, level, code, msg, line=None):
        self.items.append({"level": level, "code": code, "line": line, "message": msg})

    def error(self, code, msg, line=None):
        self.add("ERROR", code, msg, line)

    def warn(self, code, msg, line=None):
        self.add("WARN", code, msg, line)

    def info(self, code, msg, line=None):
        self.add("INFO", code, msg, line)

    def count(self, level):
        return sum(1 for x in self.items if x["level"] == level)

    def print(self):
        order = {"ERROR": 0, "WARN": 1, "INFO": 2}
        for x in sorted(self.items, key=lambda x: (order[x["level"]], x["line"] or 0)):
            where = f" [line {x['line']}]" if x["line"] else ""
            print(f"{x['level']:<5} {x['code']}{where}: {x['message']}")
        print(f"SUMMARY: {self.count('ERROR')} error(s), {self.count('WARN')} warning(s), {self.count('INFO')} info")


def short(s: str, n: int = 70) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n - 1] + "…"


# ---------------------------------------------------------------- template / class

def check_class(ms, rep: Report, n_authors: int):
    if ms.docclass != CLASS_NAME:
        rep.error("class.mdpi", f"\\documentclass must be {{{CLASS_NAME}}} (found {{{ms.docclass or 'none'}}}); "
                                "the editorial office recompiles with the MDPI class")
        return
    opts = ms.docclass_opts
    if JOURNAL not in opts:
        rep.error("class.journal", f"class options {opts} do not select the journal: add `{JOURNAL}`")
    if not any(o in ARTICLE_TYPES for o in opts):
        rep.error("class.type", "no article-type option (article, review, communication, ...)")
    if "accept" in opts:
        rep.error("class.submit", "option `accept` is for the editorial office; submit with `submit`")
    elif "submit" not in opts:
        rep.warn("class.submit", "add the `submit` option (line numbers for reviewers)")
    if "pdftex" in opts:
        rep.warn("class.pdftex", "`pdftex` is not an option of mdpi.cls v6.5; remove it")
    if n_authors > 1 and "moreauthors" not in opts:
        rep.error("class.authors", f"{n_authors} authors but no `moreauthors` option")
    if n_authors == 1 and "moreauthors" in opts:
        rep.warn("class.authors", "single author: use `oneauthor` instead of `moreauthors`")
    defs = ms.path.parent / "Definitions"
    if not (defs / "mdpi.cls").exists():
        rep.error("class.files", f"{defs}/mdpi.cls missing: copy Definitions/ from the bundled template")


def check_preamble(ms, rep: Report):
    pre = ms.preamble
    for name in ("TitleCitation", "AuthorCitation"):
        if re.search(r"\\" + name + r"\b", pre):
            rep.error("template.obsolete", f"\\{name} is not defined by mdpi.cls v6.5 (\"Undefined control "
                                           "sequence\"); remove it", line_of(ms.tex, pre.find("\\" + name)))
    for m in find_macros(pre, "usepackage"):
        for p in [x.strip() for x in (m.args[0] if m.args else "").split(",") if x.strip()]:
            ln = line_of(ms.tex, m.start)
            if p in FORBIDDEN_PACKAGES:
                rep.error("preamble.package", f"package `{p}` changes the MDPI layout, fonts or citation system; "
                                              "remove it", ln)
            elif p in CLASS_PACKAGES:
                rep.warn("preamble.package", f"package `{p}` is already loaded by the class"
                                             + (f"; the options [{m.opt}] may clash" if m.opt else ""), ln)
    for m in re.finditer(r"\\newtheorem\*?\s*\{([^}]+)\}", pre):
        if m.group(1).strip() in CLASS_COUNTERS:
            rep.error("math.newtheorem", f"\\newtheorem{{{m.group(1)}}} collides with the class counter "
                                         f"`{m.group(1)}` (compile error); use the class environment "
                                         f"{m.group(1).capitalize()} instead", line_of(ms.tex, m.start()))
        elif m.group(1).strip() in CLASS_THEOREMS:
            rep.error("math.newtheorem", f"environment {m.group(1)} is already defined by the class",
                      line_of(ms.tex, m.start()))
    for m in re.finditer(r"\\newtheorem\s*\{[^}]+\}\s*(\[[^\]]+\])?\s*\{[^}]+\}\s*\[([^\]]+)\]", pre):
        rep.warn("math.numbering", f"\\newtheorem ... [{m.group(2)}] numbers per {m.group(2)}; Axioms numbers "
                                   "every type through the whole paper (Theorem 1, Theorem 2)",
                 line_of(ms.tex, m.start()))
    for m in re.finditer(r"\\(numberwithin|counterwithin)\s*\{equation\}", ms.tex):
        rep.warn("math.numbering", "equations must be numbered (1), (2), ... through the paper; remove "
                                   f"\\{m.group(1)}{{equation}}", line_of(ms.tex, m.start()))
    for m in re.finditer(r"\\(geometry|linespread)\b|\\setlength\s*\{?\\(textwidth|textheight|oddsidemargin|"
                         r"topmargin)\b|\\renewcommand\s*\{?\\baselinestretch", pre):
        rep.error("preamble.layout", f"layout command `{short(m.group(0), 30)}` overrides the MDPI page layout",
                  line_of(ms.tex, m.start()))
    for i, line in enumerate(ms.raw.split("\n"), 1):
        if "TODO" in line and not line.lstrip().startswith("%"):
            rep.error("template.todo", f"TODO left: {short(line.strip())}", i)
    seen = set()
    for s in TEMPLATE_LEFTOVERS:
        pos = ms.tex.find(s)
        if pos >= 0 and s not in seen:
            seen.add(s)
            rep.error("template.leftover", f"template placeholder text left: \"{s}\"", line_of(ms.tex, pos))
    if re.search(r"\\setcounter\{section\}\{-1\}", ms.tex):
        rep.error("template.leftover", "\\setcounter{section}{-1} from the template: remove it so that sections "
                                       "start at 1")


# ---------------------------------------------------------------- front matter

def split_authors(author_arg: str) -> list[str]:
    a = re.sub(r"\$\^\{[^}]*\}\$\*?|\$\^[^$]*\$|\\orcid[A-Z]\{\}|\*|\\textsuperscript\{[^}]*\}", "", author_arg)
    a = re.sub(r"\s+and\s+", ",", a)
    return [x.strip() for x in a.split(",") if x.strip()]


def is_title_case(title: str) -> list[str]:
    bad = []
    tokens = re.findall(r"[A-Za-z][A-Za-z'’-]*", strip_math(title, " "))
    for i, w in enumerate(tokens):
        if i and w.lower() in TITLE_SMALL:
            continue
        if w[0].islower():
            bad.append(w)
    return bad


def check_front(ms, rep: Report) -> tuple[list[str], str]:
    pre = ms.preamble
    title = macro_arg(pre, "Title")
    if not title or not title.strip():
        rep.error("front.title", "\\Title{} missing or empty")
    else:
        t = detex(title)
        if t.endswith("."):
            rep.warn("front.title", "the title should not end with a period")
        lower = is_title_case(title)
        if lower:
            rep.warn("front.title.case", f"MDPI titles are in Title Case; lower-case word(s): {', '.join(lower[:6])}")
        abbr = [w for w in re.findall(r"\b[A-Z]{2,}[a-z]?\b", strip_math(title, " ")) if w not in ABBREV_OK]
        if abbr:
            rep.warn("front.title.abbr", f"avoid abbreviations in the title: {', '.join(abbr)}")
        if words(t) > 25:
            rep.warn("front.title.length", f"title has {words(t)} words; keep it concise and specific")
    author = macro_arg(pre, "Author")
    names: list[str] = []
    if not author:
        rep.error("front.author", "\\Author{} missing")
    else:
        names = split_authors(author)
        for n in names:
            if re.match(r"(Prof|Dr|Professor|Mr|Ms|Mrs)\.?\s", detex(n)):
                rep.warn("front.author.title", f"no titles in author names: \"{n}\"")
            first = detex(n).split()[0] if detex(n).split() else ""
            if re.fullmatch(r"[A-Z]\.(-?[A-Z]\.)?", first):
                rep.warn("front.author.fullname", f"MDPI asks for full first names: \"{n}\"")
        if "*" not in author:
            rep.error("front.corresponding", "no corresponding author marked with * in \\Author")
        if re.search(r",\s*and\s", author):
            rep.warn("front.author", "no comma before \"and\" in the author list (MDPI style)")
    if not macro_arg(pre, "AuthorNames"):
        rep.warn("front.authornames", "\\AuthorNames{} missing (PDF metadata)")
    address = [m for m in find_macros(pre, "address") if m.args]
    if not address:
        rep.error("front.address", "\\address{} missing")
    else:
        a = address[-1]
        txt = a.args[0]
        n_aff = len(re.findall(r"\$\^\{?\d+\}?\$", txt))
        if n_aff == 0 and a.opt != "1":
            rep.warn("front.address", "single affiliation: write \\address[1]{...} (template rule)")
        n_mail = len(list(EMAIL_RE.finditer(txt)))
        if names and n_mail < len(names):
            rep.warn("front.email", f"{n_mail} e-mail(s) in \\address for {len(names)} author(s); MDPI publishes "
                                    "the e-mail of every author")
    corres = macro_arg(pre, "corres")
    if not corres or not EMAIL_RE.search(corres):
        rep.error("front.corres", "\\corres{Correspondence: e-mail} missing or without an e-mail")
    for m in re.finditer(r"\\newcommand\{\\orcidauthor([A-Z])\}\{([^}]*)\}", pre):
        if not ORCID_RE.match(m.group(2).strip()):
            rep.error("front.orcid", f"ORCID of author {m.group(1)} is not 0000-0000-0000-000X: {m.group(2)}",
                      line_of(ms.tex, m.start()))
        elif not re.search(r"\\orcid" + m.group(1) + r"\{\}", author or ""):
            rep.warn("front.orcid", f"\\orcidauthor{m.group(1)} defined but \\orcid{m.group(1)}{{}} not used in "
                                    "\\Author")
    if not re.search(r"\\newcommand\{\\orcidauthor", pre):
        rep.info("front.orcid", "no ORCID iDs: MDPI strongly recommends them (\\orcidauthorA + \\orcidA{})")

    # abstract
    abstract = macro_arg(pre, "abstract")
    if not abstract:
        rep.error("abstract.missing", "\\abstract{} missing")
    else:
        w = words(detex(abstract))
        if w > 200:
            rep.warn("abstract.length", f"abstract has {w} words; the limit is about 200 words")
        elif w < 50:
            rep.warn("abstract.length", f"abstract has only {w} words; give background, methods, results and "
                                        "conclusions in one paragraph")
        if re.search(r"\n\s*\n|\\\\|\\par\b", abstract):
            rep.error("abstract.paragraph", "the abstract must be a single paragraph (no blank lines, \\\\ or \\par)")
        if re.search(r"\\cite", abstract):
            rep.error("abstract.citation", "no citations in the abstract")
        if re.search(r"\\\[|\$\$|\\begin\{(equation|align|gather|multline)", abstract):
            rep.error("abstract.equation", "no display equations in the abstract (inline math only)")
        if re.search(r"\\(ref|eqref|cref)\{|\bFigure\s+\d|\bTable\s+\d", abstract):
            rep.warn("abstract.reference", "the abstract must not refer to figures, tables or equations")
        abbr = sorted({w for w in re.findall(r"\b[A-Z]{2,}s?\b", strip_math(abstract, " "))
                       if w not in ABBREV_OK and not re.search(r"\(" + w + r"\)", abstract)
                       and not re.search(w + r"\s*\(", abstract)})
        if abbr:
            rep.warn("abstract.abbr", f"abbreviation(s) not defined in the abstract: {', '.join(abbr[:8])}")
    kw = macro_arg(pre, "keyword")
    if not kw:
        rep.error("keywords.missing", "\\keyword{} missing")
    else:
        items = [x.strip() for x in kw.split(";") if x.strip()]
        if "," in kw and len(items) <= 1:
            rep.error("keywords.separator", "separate keywords with semicolons, not commas")
        elif not 3 <= len(items) <= 10:
            rep.error("keywords.count", f"{len(items)} keyword(s); Axioms asks for three to ten")
        if kw.strip().endswith("."):
            rep.warn("keywords.period", "no final period after the keywords")
    msc = macro_arg(pre, "MSC")
    if msc is None or not msc.strip():
        rep.warn("msc.missing", "no \\MSC{}: Axioms papers (and its Word template) carry MSC2020 codes, "
                                "e.g. \\MSC{47H10; 54H25}")
    else:
        codes = [c.strip() for c in re.split(r"[;,]", detex(msc)) if c.strip()]
        bad = [c for c in codes if not MSC_CODE_RE.match(c)]
        if bad:
            rep.error("msc.format", f"not MSC2020 codes: {', '.join(bad)} (format 35J60, 35Jxx or 35-XX)")
        if "," in msc:
            rep.warn("msc.separator", "separate MSC codes with semicolons: 35J60; 35J96")
        if re.search(r"(?i)primary|secondary", msc):
            rep.warn("msc.format", "Axioms prints the codes without \"Primary/Secondary\"")
    return names, title or ""


# ---------------------------------------------------------------- body

def check_body(ms, rep: Report):
    body = ms.body
    secs = sections(body)
    top = [s for s in secs if s.level == 1 and not s.starred and not s.appendix]
    if not top:
        rep.error("body.sections", "no numbered \\section in the body")
        return secs
    titles = [s.title.lower() for s in top]
    if not titles[0].startswith("introduction"):
        rep.warn("body.introduction", f"the first section is \"{top[0].title}\"; MDPI papers start with "
                                      "\"Introduction\"")
    if not any(t.startswith(("conclusion", "concluding", "discussion", "summary")) for t in titles):
        rep.warn("body.conclusions", "no Conclusions (or Discussion) section; optional for Axioms, but "
                                     "recommended (summary, significance, open problems)")
    for s in secs:
        if s.starred and s.level <= 3 and not s.appendix:
            rep.warn("body.unnumbered", f"unnumbered heading \"{s.title}\": MDPI numbers sections 1., 1.1., "
                                        "1.1.1.; use \\paragraph{} for unnumbered run-in heads",
                     ms.line(s.start))
        if s.level <= 3 and s.title and not s.appendix:
            low = is_title_case(s.title)
            if low and len(s.title.split()) > 1:
                rep.info("body.heading.case", f"heading \"{s.title}\": MDPI uses Title Case", ms.line(s.start))
    intro_i = next((i for i, s in enumerate(secs) if s.level == 1 and s.title.lower().startswith("intro")), None)
    if intro_i is not None:
        intro = section_text(body, secs, intro_i)
        if not re.search(r"(?i)(organi[sz]ed as follows|structured as follows|rest of (this|the) paper|"
                         r"remainder of (this|the) paper|paper is organi[sz]ed|outline of the paper)", intro):
            rep.info("intro.outline", "all three reviewed Axioms papers end the Introduction with \"The rest of "
                                      "this paper is organized as follows ...\"")
        if not citations(intro):
            rep.warn("intro.citations", "the Introduction cites no literature")
    return secs


def check_math(ms, rep: Report):
    body = ms.body
    for m in re.finditer(r"\$\$", body):
        rep.warn("math.display", "use \\[...\\] or equation/align instead of $$...$$", ms.line(m.start()))
        break
    for m in re.finditer(r"\\begin\{eqnarray\*?\}", body):
        rep.warn("math.eqnarray", "eqnarray gives wrong spacing; use align", ms.line(m.start()))
    used = set(env_names(body))
    lower = sorted(u for u in used if u in CLASS_COUNTERS and not re.search(r"\\newtheorem\*?\{" + u + r"\}",
                                                                              ms.preamble))
    for u in lower:
        rep.error("math.env", f"environment `{u}` is not defined by the class; use `{u.capitalize()}`")
    for e in find_envs(body, "proof"):
        if e.opt and re.match(r"\s*Proof\s+for\b", e.opt):
            rep.warn("math.proof", f"write \"Proof of ...\", not \"{e.opt.strip()}\"", ms.line(e.start))
    # hard-coded numbers like "Theorem 2.1" or "(3.4)" left from section-based numbering
    plain = strip_math(re.sub(r"\\(label|ref|eqref|cref|Cref|cite)\{[^}]*\}", " ", body), " ")
    for m in re.finditer(r"\b(Theorem|Lemma|Corollary|Proposition|Definition|Remark|Example|Section|Equation)"
                         r"~?\s+(\d+(\.\d+)+)\b", plain):
        rep.warn("refs.hardcoded", f"hard-coded \"{m.group(0)}\": Axioms numbers results 1, 2, 3 ... through the "
                                   "paper; use \\label/\\ref", ms.line(m.start()))
        break
    hard = len(re.findall(r"\b(Theorem|Lemma|Corollary|Proposition|Definition|Figure|Table)~?\s+\d+\b", plain))
    if hard:
        rep.info("refs.hardcoded", f"{hard} hard-coded cross-reference number(s) such as \"Theorem 2\"; prefer "
                                   "Theorem~\\ref{...} so numbers stay right after edits")


def check_floats(ms, rep: Report):
    body = ms.body
    rset = {k for _, k in refs(body)}
    for kind in ("figure", "table", "figure*", "table*"):
        for e in find_envs(body, kind):
            ln = ms.line(e.start)
            cap = re.search(r"\\caption\b", e.body)
            base = kind.rstrip("*")
            if not cap:
                rep.error(f"{base}.caption", f"{base} without \\caption", ln)
                continue
            lab = re.search(r"\\label\{([^}]+)\}", e.body)
            if not lab:
                rep.warn(f"{base}.label", f"{base} without \\label (cannot be cited as {base.capitalize()} N)", ln)
            elif lab.group(1) not in rset:
                rep.warn(f"{base}.cited", f"{base} \"{lab.group(1)}\" is never referenced in the text; every "
                                          f"{base} must be cited", ln)
            obj = re.search(r"\\includegraphics|\\begin\{tabular|\\begin\{tabularx|\\begin\{tikzpicture|"
                            r"\\subfloat|\\input", e.body)
            if obj:
                if base == "figure" and cap.start() < obj.start():
                    rep.warn("figure.caption.position", "figure caption must be below the figure", ln)
                if base == "table" and cap.start() > obj.start():
                    rep.warn("table.caption.position", "table caption must be above the table", ln)
            if base == "table":
                for spec in re.findall(r"\\begin\{tabularx?\}\s*(?:\{[^}]*\})?\s*\{([^}]*)\}", e.body):
                    if "|" in spec:
                        rep.warn("table.vrules", "MDPI tables have no vertical rules; use booktabs "
                                                 "\\toprule/\\midrule/\\bottomrule", ln)
                        break
                if "\\hline" in e.body:
                    rep.warn("table.hline", "use \\toprule/\\midrule/\\bottomrule instead of \\hline", ln)
    plain = re.sub(r"\\(label|ref|cite)\{[^}]*\}", "", body)
    for m in re.finditer(r"\b(Fig|Figs|Tab|Eq|Eqs)\.\s*(~|\\ref|\d)", plain):
        rep.warn("text.abbrev", f"write \"Figure\", \"Table\", \"Equation\" in full, not \"{m.group(1)}.\"",
                 ms.line(m.start()))
        break
    # undefined references
    all_labels = labels(ms.tex)
    missing = sorted({k for _, k in refs(ms.tex) if k not in all_labels})
    if missing:
        rep.error("refs.undefined", f"\\ref to undefined label(s): {', '.join(missing[:10])}")


def check_graphics(ms, rep: Report):
    base = ms.path.parent
    gpaths = graphics_paths(ms.preamble)
    try:
        from PIL import Image
    except ImportError:  # pragma: no cover
        Image = None
    for g in includegraphics(ms.body):
        name = g.args[0].strip()
        p = resolve_graphic(name, base, gpaths)
        ln = ms.line(g.start)
        if p is None:
            rep.error("figure.file", f"graphic \"{name}\" not found", ln)
            continue
        ext = p.suffix.lower()
        if ext in (".tif", ".tiff"):
            rep.warn("figure.format", f"{p.name}: pdfLaTeX cannot include TIFF; use PNG/JPG/PDF in the "
                                      "source (TIFF only for the separate figure zip)", ln)
        if ext in (".png", ".jpg", ".jpeg") and Image is not None:
            try:
                with Image.open(p) as im:
                    wpx = im.size[0]
            except Exception:
                continue
            m = re.search(r"width\s*=\s*([\d.]+)\s*(cm|mm|in|pt)", g.opt or "")
            if m:
                inch = float(m.group(1)) / {"cm": 2.54, "mm": 25.4, "in": 1, "pt": 72.27}[m.group(2)]
            elif re.search(r"width\s*=\s*([\d.]*)\\(textwidth|linewidth|columnwidth)", g.opt or ""):
                f = re.search(r"width\s*=\s*([\d.]*)\\", g.opt).group(1)
                inch = (float(f) if f else 1.0) * 13.5 / 2.54     # MDPI text block is ~13.5 cm
            else:
                inch = None
            if inch:
                dpi = wpx / inch
                if dpi < 300:
                    rep.warn("figure.dpi", f"{p.name}: about {dpi:.0f} dpi at the printed size; MDPI asks for "
                                           "600 dpi or more (or use a vector PDF)", ln)
                elif dpi < 590:
                    rep.info("figure.dpi", f"{p.name}: about {dpi:.0f} dpi at the printed size (600 preferred)")


# ---------------------------------------------------------------- citations, references

def check_citations(ms, rep: Report):
    body = ms.body
    cites = citations(ms.tex)
    keys_used = first_cite_order(ms.tex)
    items = bibitems(ms.tex)
    bibs = bib_files(ms.tex, ms.path.parent)
    entries = []
    for b in bibs:
        if not b.exists():
            rep.error("refs.bibfile", f"bibliography file {b.name} not found")
            continue
        entries += [(e, b.name) for e in parse_bib(read_text(b))]
    if not items and not bibs:
        rep.error("refs.missing", "no \\bibliography{...} and no thebibliography")
        return
    if re.search(r"\\bibliographystyle\b", ms.tex):
        rep.warn("refs.style", "remove \\bibliographystyle: the class sets Definitions/mdpi itself")
    if re.search(r"\\(printbibliography|addbibresource)\b", ms.tex):
        rep.error("refs.biblatex", "biblatex is not supported by the MDPI class; use \\bibliography{file}")
    defined = [k for k, _, _ in items] + [e.key for e, _ in entries]
    undefined = [k for k in keys_used if k not in defined]
    if undefined:
        rep.error("refs.undefined-cite", f"\\cite key(s) with no reference: {', '.join(undefined[:10])}")
    if items:
        uncited = [k for k, _, _ in items if k not in keys_used]
        if uncited:
            rep.error("refs.uncited", f"reference(s) never cited in the text: {', '.join(uncited[:10])}")
        order = [k for k, _, _ in items if k in keys_used]
        expected = [k for k in keys_used if k in order]
        if order != expected:
            first_bad = next(i for i, (a, b) in enumerate(zip(order, expected)) if a != b)
            rep.error("refs.order", "thebibliography is not in order of first citation (MDPI numbers references "
                                    f"in order of appearance); first mismatch at item {first_bad + 1}: "
                                    f"\"{order[first_bad]}\" vs first-cited \"{expected[first_bad]}\"")
        for k, text, pos in items:
            check_ref_text(k, text, rep, line_of(ms.tex, ms.body_offset + pos) if pos < len(body) else None)
    for e, fname in entries:
        check_bib_entry(e, fname, rep)
    if entries:
        dois = {}
        for e, _ in entries:
            d = e.fields.get("doi", "").lower()
            if d:
                dois.setdefault(d, []).append(e.key)
        for d, ks in dois.items():
            if len(ks) > 1:
                rep.error("refs.duplicate", f"same DOI in {', '.join(ks)}: one work per reference")
        unused = [e.key for e, _ in entries if e.key not in keys_used]
        if unused and not re.search(r"\\nocite\{\*\}", ms.tex):
            rep.info("refs.bib-unused", f"{len(unused)} .bib entr(y/ies) not cited (BibTeX leaves them out): "
                                        f"{', '.join(unused[:6])}")
    # in-text citation style
    for pos, keys, opt in cites:
        if pos < ms.body_offset:
            continue
        ln = line_of(ms.tex, pos)
        if opt and re.search(r"\b(p|pp|page|pages)\b\.?", opt):
            rep.warn("cite.locator", f"\\cite[{opt}]{{...}} prints \"[n, {opt}]\"; MDPI style is "
                                     f"\"[n] ({opt})\": write \\cite{{{keys[0]}}} ({opt})", ln)
        line_start = ms.tex.rfind("\n", 0, pos) + 1
        if (re.search(r"[.!?]\s*$", ms.tex[max(0, pos - 3):pos]) or ms.tex[line_start:pos].strip() == "" and
                re.search(r"\n\s*\n\s*$", ms.tex[max(0, pos - 20):pos])):
            rep.warn("cite.sentence-start", "a citation must not start a sentence: write \"Ref. [n]\" or "
                                            "\"Author [n]\"", ln)
    for m in re.finditer(r"\[\s*\d+\s*\]", strip_math(body, " ")):
        rep.warn("cite.manual", f"hand-typed citation \"{m.group(0)}\": use \\cite so numbering stays in order")
        break


def check_ref_text(key: str, text: str, rep: Report, line):
    t = re.sub(r"\s+", " ", text)
    if not DOI_RE.search(t) and not re.search(r"(?i)arxiv|available online|thesis|book|press|springer|"
                                              r"elsevier|wiley|birkh|cambridge|oxford|ed\.;|eds\.;", t):
        rep.info("refs.doi", f"[{key}] no DOI: include https://doi.org/... wherever one exists")
    if re.search(r"\(\s*\d+\s*\)\s*[:,]", t) or re.search(r"\bno\.\s*\d", t):
        rep.warn("refs.issue", f"[{key}] MDPI style gives no issue number: \"{short(t, 60)}\"", line)
    if not re.search(r"\{\\bf\s*\d{4}\}|\\textbf\{\s*\d{4}\s*\}", t) and re.search(r"\{\\em|\\textit", t) \
            and re.search(r",\s*\d+\s*[-–]+\s*\d+\.?$|, \d+\.$", t) and "In " not in t:
        rep.info("refs.format", f"[{key}] journal pattern is: Author, A.; Title. {{\\em Abbr. J.}} "
                                "{\\bf Year}, {\\em Vol}, pages.")


def check_bib_entry(e, fname: str, rep: Report):
    f = e.fields
    where = f"{fname}:{e.line} [{e.key}]"
    need = {"article": ["author", "title", "journal", "year"], "book": ["title", "publisher", "year"],
            "incollection": ["author", "title", "booktitle", "publisher", "year"],
            "inproceedings": ["author", "title", "booktitle", "year"], "phdthesis": ["author", "title", "school",
                                                                                  "year"]}.get(e.type, [])
    miss = [x for x in need if not f.get(x)]
    if e.type == "book" and not (f.get("author") or f.get("editor")):
        miss.append("author/editor")
    if miss:
        rep.error("bib.fields", f"{where}: missing {', '.join(miss)}")
    if e.type == "article":
        if not f.get("volume") and "arxiv" not in f.get("journal", "").lower():
            rep.warn("bib.volume", f"{where}: no volume")
        if not f.get("pages") and not f.get("eid") and "arxiv" not in f.get("journal", "").lower():
            rep.warn("bib.pages", f"{where}: no pages or article number")
        if not f.get("doi"):
            rep.warn("bib.doi", f"{where}: no doi field (MDPI: include the DOI wherever available)")
        j = f.get("journal", "")
        if FULL_JOURNAL_WORDS.search(j) and len(j.split()) > 1:
            rep.warn("bib.journal-abbrev", f"{where}: journal \"{j}\" looks unabbreviated; give the ISO 4 "
                                           "abbreviation (e.g. Proc. Am. Math. Soc.)")
        if f.get("number"):
            rep.info("bib.number", f"{where}: `number` (issue) is not printed in MDPI style; harmless")
    if f.get("doi", "").lower().startswith(("http", "doi:")):
        rep.warn("bib.doi", f"{where}: doi field must be the bare DOI (10.xxxx/...), not a URL")
    if f.get("url") and not f.get("urldate") and not f.get("doi"):
        rep.warn("bib.urldate", f"{where}: a url needs urldate (\"accessed on ...\")")
    if re.search(r"(?i)arxiv", " ".join(f.values())) and not f.get("eprint") and e.type != "article":
        rep.info("bib.arxiv", f"{where}: for arXiv preprints set eprint = {{XXXX.XXXXX}} (and archiveprefix)")
    title = f.get("title", "")
    if re.search(r"\b[A-Z][a-z]+-[A-Z]", title) and "{" not in title:
        rep.info("bib.case", f"{where}: protect capitals in the title with braces, e.g. {{M}}onge--{{A}}mp\\`ere")


# ---------------------------------------------------------------- back matter

def check_back(ms, rep: Report, names: list[str]):
    tex = ms.tex
    present = {}
    for name in BACK_ORDER:
        m = re.search(r"\\" + name + r"\b", tex)
        if m:
            present[name] = m.start()
    many = len(names) > 1
    for name, code, needed in (("authorcontributions", "back.contributions", many),
                               ("funding", "back.funding", True),
                               ("dataavailability", "back.data", True),
                               ("conflictsofinterest", "back.coi", True)):
        if name not in present and needed:
            rep.error(code, f"\\{name}{{}} missing (required MDPI statement)")
    for name in ("institutionalreview", "informedconsent"):
        if name not in present:
            rep.info("back.ethics", f"\\{name} omitted: fine for work without humans/animals (or write "
                                    "\"Not applicable.\")")
    seq = [n for n in BACK_ORDER if n in present]
    pos = [present[n] for n in seq]
    if pos != sorted(pos):
        actual = [n for n, _ in sorted(present.items(), key=lambda x: x[1])]
        rep.warn("back.order", f"back matter order should be {' > '.join(seq)}; found {' > '.join(actual)}")
    contrib = macro_arg(tex, "authorcontributions")
    if contrib and many:
        txt = detex(contrib)
        if "read and agreed to the published version" not in txt:
            rep.error("back.contributions", f"Author Contributions must end with \"{STD_ALL_READ}\"")
        ini = set(re.findall(r"\b(?:[A-Z][a-z]?\.(?:-?[A-Z]\.)*)+", txt))
        expected = {author_initials(n) for n in names}
        unknown = sorted(i for i in ini if i not in expected and len(i) > 2)
        if unknown and expected:
            rep.warn("back.contributions", f"initials {', '.join(unknown)} do not match the authors "
                                           f"({', '.join(sorted(expected))})")
        missing = sorted(i for i in expected if i not in txt)
        if missing:
            rep.warn("back.contributions", f"author(s) {', '.join(missing)} have no CRediT role")
    funding = macro_arg(tex, "funding")
    if funding is not None and not detex(funding).strip():
        rep.error("back.funding", "\\funding{} is empty: \"This research received no external funding.\" or "
                                  "the funder and grant number")
    data = macro_arg(tex, "dataavailability")
    if data is not None and not detex(data).strip():
        rep.error("back.data", "\\dataavailability{} is empty (a statement is mandatory)")
    coi = macro_arg(tex, "conflictsofinterest")
    if coi is not None and not detex(coi).strip():
        rep.error("back.coi", "\\conflictsofinterest{} is empty")
    if funding and "TODO" not in funding and re.search(r"(?i)funded by|grant|supported by", detex(funding)) and coi and \
            "role" not in detex(coi):
        rep.info("back.coi", "with external funding, MDPI expects the funder-role sentence: \"The funders had no "
                             "role in the design of the study; ...\"")
    ack = macro_arg(tex, "acknowledgments") or ""
    if re.search(r"(?i)chatgpt|gpt-|claude|gemini|copilot|large language model|generative ai|genai|llm", tex):
        if not re.search(r"(?i)take full responsibility for the content", ack):
            rep.warn("back.ai", "GenAI is mentioned: MDPI requires the disclosure sentence in Acknowledgments "
                                "(\"During the preparation of this manuscript/study, the author(s) used ...\")")
    rep.info("back.ai", "GenAI used beyond grammar/formatting? Declare it in SuSy, in the methods, and with the "
                        "fixed Acknowledgments sentence (references/requirements.md section 7)")
    if not re.search(r"\\PublishersNote\b", tex):
        rep.warn("back.publishersnote", "\\PublishersNote{} missing at the end (template)")
    abbr = macro_arg(tex, "abbreviations")
    if abbr is not None and re.search(r"MDPI\s*&\s*Multidisciplinary", tex):
        rep.error("template.leftover", "\\abbreviations still lists the template entries")
    if re.search(r"\\appendix\b", ms.body) and not re.search(r"\\appendixstart\b", ms.body):
        rep.warn("back.appendix", "use \\appendixstart before \\appendix (MDPI appendix numbering A1, (A1))")


def author_initials(name: str) -> str:
    parts = [p for p in re.split(r"[\s~]+", detex(name)) if p]
    out = ""
    for p in parts:
        sub = [s for s in p.split("-") if s and s[0].isalpha()]
        out += "-".join(s[0].upper() + "." for s in sub) if len(sub) > 1 else (p[0].upper() + "." if p[0].isalpha()
                                                                                 else "")
    return out


# ---------------------------------------------------------------- text lint

def check_text(ms, rep: Report):
    body = ms.body
    plain = strip_math(body, " X ")
    plain = re.sub(r"\\(url|href|label|ref|eqref|cite\w*|includegraphics|input)\s*(\[[^\]]*\])?\{[^}]*\}", " ", plain)
    m = re.search(r"(?<![A-Z.])\b[a-z]{2,}\.[A-Z][a-z]+", plain)
    if m:
        rep.warn("text.space", f"missing space after a period: \"{m.group(0)}\"", ms.line(m.start()))
    m = re.search(r"\\end\{(equation|align|gather|multline)\*?\}\s*\n?\s*Where\b", body)
    if m:
        rep.warn("text.where", "after a display, \"where\" continues the sentence: lower case, no indent",
                 ms.line(m.start()))
    m = re.search(r"\b\d+(\.\d+)?[eE][+-]?\d+\b", plain)
    if m:
        rep.warn("text.enotation", f"write a × 10^b, not \"{m.group(0)}\"", ms.line(m.start()))
    m = re.search(r"(?<![\w.])\.\d+\b", plain)
    if m and not re.search(r"\d$", plain[:m.start()]):
        rep.info("text.leadingzero", f"write 0{m.group(0)}, not {m.group(0)}")
    m = re.search(r"(?<!\\)\b(ie|eg)\.\s|\bet\.\s?al\b|\bet al(?!\.)", plain)
    if m:
        rep.info("text.latin", f"check \"{m.group(0).strip()}\" (i.e., e.g., et al.)", ms.line(m.start()))
    if re.search(r"\\footnote\b", body):
        rep.warn("text.footnote", "MDPI uses no footnotes (except journal Laws); move the text into the body or "
                                  "use \\endnote")


# ---------------------------------------------------------------- log / pdf

def check_log(path: Path, rep: Report):
    log = read_text(path)
    errs = re.findall(r"^! (.+)$", log, flags=re.M)
    for e in errs[:5]:
        rep.error("log.error", f"LaTeX error: {e}")
    if re.search(r"There were undefined references|Reference `[^']+' on page \d+ undefined", log):
        rep.error("log.undefined", "undefined references in the log: run BibTeX and LaTeX again, then fix labels")
    if re.search(r"Citation `[^']+' on page \d+ undefined|There were undefined citations", log):
        rep.error("log.undefined", "undefined citations in the log")
    if re.search(r"multiply[- ]defined", log):
        rep.warn("log.multiply", "multiply-defined labels")
    over = [float(x) for x in re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)", log)]
    big = [x for x in over if x > 10]
    if big:
        rep.warn("log.overfull", f"{len(big)} overfull line(s) wider than 10pt (max {max(big):.0f}pt): break long "
                                 "formulas or use adjustwidth for wide displays")
    if re.search(r"File `[^']+' not found|LaTeX Warning: File", log):
        rep.error("log.missing-file", "a file was not found during compilation")


def check_pdf(path: Path, rep: Report):
    import pymupdf as fitz
    try:
        doc = fitz.open(path)
    except Exception as e:
        rep.error("pdf.open", f"cannot open {path}: {e}")
        return
    rep.info("pdf.pages", f"{doc.page_count} page(s) (Axioms has no length limit)")
    first = doc[0].get_text() if doc.page_count else ""
    if "Axioms" not in first and "axioms" not in first:
        rep.warn("pdf.journal", "the first page does not name Axioms: compiled with the axioms class option?")
    if re.search(r"\?\?|\[\?\]", "".join(p.get_text() for p in doc)):
        rep.error("pdf.unresolved", "\"??\" or \"[?]\" in the PDF: unresolved reference or citation")
    t3 = set()
    for p in doc:
        for f in p.get_fonts():
            if f[2] == "Type3":
                t3.add(f[3])
    if t3:
        rep.warn("pdf.type3", f"Type 3 (bitmap) fonts: {', '.join(sorted(t3))[:80]}; usually a raster figure "
                              "font or missing cm-super")


# ---------------------------------------------------------------- main

def run(tex_path: Path, log: Path | None, pdf: Path | None) -> Report:
    rep = Report()
    ms = load_manuscript(tex_path)
    if not ms.body:
        rep.error("tex.structure", "no \\begin{document}")
        return rep
    author = macro_arg(ms.preamble, "Author") or ""
    n_auth = max(1, len(split_authors(author))) if author else 1
    check_class(ms, rep, n_auth)
    check_preamble(ms, rep)
    names, _ = check_front(ms, rep)
    check_body(ms, rep)
    check_math(ms, rep)
    check_floats(ms, rep)
    check_graphics(ms, rep)
    check_citations(ms, rep)
    check_back(ms, rep, names)
    check_text(ms, rep)
    if log:
        check_log(log, rep) if log.exists() else rep.error("log.missing", f"{log} not found")
    if pdf:
        check_pdf(pdf, rep) if pdf.exists() else rep.error("pdf.missing", f"{pdf} not found")
    rep.info("submit.files", "SuSy upload: one .zip with paper.tex, Definitions/, .bib (and .bbl), all figures "
                             "+ the compiled PDF (build_paper.py --zip)")
    rep.info("submit.cover-letter", "cover letter must contain the two fixed sentences and the significance of "
                                    "the work (references/requirements.md section 8)")
    rep.info("submit.reviewers", "suggest 3 reviewers: other institutions, no joint papers in the last 3 years")
    return rep


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("tex", type=Path)
    ap.add_argument("--log", type=Path)
    ap.add_argument("--pdf", type=Path)
    ap.add_argument("--json", type=Path, help="write findings to this JSON file")
    a = ap.parse_args(argv)
    if not a.tex.exists():
        print(f"error: {a.tex} not found", file=sys.stderr)
        return 2
    rep = run(a.tex, a.log, a.pdf)
    rep.print()
    if a.json:
        a.json.write_text(json.dumps(rep.items, ensure_ascii=False, indent=1), encoding="utf-8")
    return 1 if rep.count("ERROR") else 0


if __name__ == "__main__":
    sys.exit(main())
