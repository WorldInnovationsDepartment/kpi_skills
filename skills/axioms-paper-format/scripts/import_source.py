# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pypandoc_binary>=1.13",
# ]
# ///
"""import_source.py -- turn a draft into an Axioms (MDPI) LaTeX submission folder.

    uv run import_source.py draft.tex  --out axioms-submission       # LaTeX draft (amsart, article, elsarticle...)
    uv run import_source.py draft.docx --out axioms-submission       # .docx/.odt/.md/.rtf/.html via pandoc
    uv run import_source.py --new      --out axioms-submission [--authors 2]   # empty skeleton

The folder gets:

    paper.tex          the manuscript on the official MDPI class, with \\documentclass[axioms,...]
    Definitions/       mdpi.cls, mdpi.bst, journalnames.tex, logos (copied from the bundled template)
    *.bib, figures     copied from the draft, keeping their relative paths
    import-report.md   what was mapped, moved, dropped, and every TODO left

What it does mechanically (the rest is the content pass in SKILL.md):

1. flattens \\input/\\include and removes % comments;
2. extracts title, authors (amsart \\author/\\address/\\email or article \\author{A \\and B}),
   abstract, keywords, MSC (\\subjclass) and acknowledgments into the MDPI front/back matter;
3. maps the draft's theorem environments onto the class ones (thm -> Theorem, lem -> Lemma,
   ...); the class already owns the counters `theorem`, `lemma`, ..., so a draft's own
   \\newtheorem{theorem}{Theorem} would not compile;
4. drops packages the class loads itself, layout/font packages and commands (geometry,
   \\linespread, \\numberwithin{equation}{section}, \\bibliographystyle, ...);
5. moves Funding / Conflicts of interest / Data availability / Author contributions /
   Acknowledgments sections into the class statements, the bibliography into the
   reference block, and anything after \\appendix into the MDPI appendix;
6. writes TODO wherever it could not fill a field. Nothing is invented.

Exits 1 with `error: ...` (and writes nothing) if the input cannot be read or the
output folder already contains a paper.tex (use --force to overwrite).
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

from axioms_common import (
    CLASS_PACKAGES,
    CLASS_THEOREMS,
    DEFINITIONS_DIR,
    EMAIL_RE,
    FORBIDDEN_PACKAGES,
    SKELETON,
    STD_ALL_READ,
    STD_NA,
    STD_NO_COI,
    STD_NO_COI_ONE,
    STD_NO_DATA,
    STD_IN_ARTICLE,
    STD_NO_FUNDING,
    detex,
    find_envs,
    find_macros,
    flatten_inputs,
    graphics_paths,
    includegraphics,
    match_brace,
    read_text,
    resolve_graphic,
    strip_comments,
)

PANDOC_INPUTS = {".docx", ".odt", ".md", ".markdown", ".rtf", ".html", ".htm"}
CLASS_BY_LOWER = {t.lower(): t for t in CLASS_THEOREMS}
ALIASES = {"thm": "Theorem", "theo": "Theorem", "lem": "Lemma", "lemm": "Lemma", "cor": "Corollary",
           "coro": "Corollary", "prop": "Proposition", "defn": "Definition", "dfn": "Definition",
           "def": "Definition", "rem": "Remark", "rmk": "Remark", "ex": "Example", "exa": "Example",
           "exmp": "Example", "hyp": "Hypothesis", "nota": "Notation", "ass": "Assumption",
           "assum": "Assumption", "prob": "Problem", "alg": "Algorithm"}
LAYOUT_CMDS = ["geometry", "linespread", "pagestyle", "thispagestyle", "hypersetup", "numberwithin",
               "bibliographystyle", "theoremstyle", "setcitestyle", "date", "allowdisplaybreaks"]
LAYOUT_LENGTHS = {"textwidth", "textheight", "oddsidemargin", "evensidemargin", "topmargin", "headheight",
                  "headsep", "footskip", "hoffset", "voffset", "marginparwidth", "parindent", "parskip"}
FRONT_CMDS = ["title", "author", "address", "curraddr", "email", "urladdr", "thanks", "keywords", "subjclass",
              "dedicatory", "affil", "affiliation", "institute", "orcid", "corresp", "ead", "cortext",
              "fntext", "tnotetext", "date"]
BACK_SECTIONS = [
    ("funding", r"funding|financial support|financial disclosure"),
    ("conflictsofinterest", r"conflicts? of interests?|competing interests?|declaration of competing interest"),
    ("dataavailability", r"data availability( statement)?|availability of data( and materials)?"),
    ("authorcontributions", r"author(s'?|'s)? contributions?|credit author(ship)? statement"),
    ("acknowledgments", r"acknowledge?ments?"),
]


class ImportError_(Exception):
    pass


# ---------------------------------------------------------------- helpers

def remove_spans(text: str, spans: list[tuple[int, int]]) -> str:
    for a, b in sorted(spans, reverse=True):
        text = text[:a] + text[b:]
    return text


def clean(s: str) -> str:
    s = re.sub(r"\\\\(\[[^\]]*\])?", " ", s)
    s = re.sub(r"\\(thanks|footnote|footnotemark|thanksref)\s*(\[[^\]]*\])?(\{([^{}]|\{[^{}]*\})*\})?", "", s)
    s = re.sub(r"\\(and|And|AND|newline|par)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip(" ,;")


def initials(name: str) -> str:
    parts = [p for p in re.split(r"[\s~]+", detex(name)) if p]
    out = []
    for p in parts:
        for piece in p.split("-"):
            if piece and piece[0].isalpha():
                out.append(piece[0].upper() + ".")
    return "".join(out)


# ---------------------------------------------------------------- authors

def parse_authors(pre: str) -> list[dict]:
    """amsart style: each \\author{} followed by its own \\address/\\curraddr/\\email.
    article style: \\author{A \\and B} with affiliations after \\\\ (or \\thanks)."""
    calls = []
    for name in ("author", "address", "curraddr", "email", "affil", "affiliation", "institute", "orcid"):
        for m in find_macros(pre, name):
            if m.args:
                calls.append((m.start, name, m.opt, m.args[0]))
    calls.sort()
    authors: list[dict] = []
    for _, name, opt, arg in calls:
        if name == "author":
            pieces = re.split(r"\\and\b|\\And\b|\\AND\b", arg)
            if len(pieces) == 1 and not re.search(r"\\\\|\\thanks", arg) and " and " in arg and "," not in arg:
                pieces = arg.split(" and ")
            for piece in pieces:
                lines = [x for x in re.split(r"\\\\(?:\[[^\]]*\])?", piece) if x.strip()]
                if not lines:
                    continue
                name_txt = clean(re.sub(r"\$\^\{?[^$]*\}?\$|\\textsuperscript\{[^}]*\}|\\inst\{[^}]*\}", "",
                                        lines[0]))
                thanks = [t for t in re.findall(r"\\thanks\{([^{}]*)\}", piece)]
                aff = [clean(x) for x in lines[1:] if clean(x)] + [clean(t) for t in thanks if clean(t)]
                emails = [mm.group(0) for mm in EMAIL_RE.finditer(piece)]
                aff = [re.sub(r"(?i)\be-?mails?\s*:?|\\[A-Za-z]+\s*\{\s*\}", "", EMAIL_RE.sub("", x)).strip(" ,;{}")
                       for x in aff]
                authors.append({"name": name_txt, "aff": [x for x in aff if x], "email": emails, "orcid": None})
        elif authors:
            a = authors[-1]
            if name in ("address", "affil", "affiliation", "institute"):
                txt = clean(arg)
                if txt:
                    a["aff"].append(txt)
            elif name == "curraddr":
                a.setdefault("current", clean(arg))
            elif name == "email":
                a["email"] += [m.group(0) for m in EMAIL_RE.finditer(arg)]
            elif name == "orcid":
                a["orcid"] = arg.strip()
    for a in authors:
        a["name"] = re.sub(r"^(Prof\.?|Dr\.?|Professor|Mr\.?|Ms\.?|Mrs\.?)\s+", "", a["name"])
    return [a for a in authors if a["name"]]


def build_author_block(authors: list[dict], todos: list[str]) -> dict[str, str]:
    if not authors:
        todos.append("authors: none found in the draft (\\Author, \\AuthorNames, \\address, \\corres)")
        return {
            "AUTHOR": "TODO Firstname Lastname $^{1}$, TODO Firstname Lastname $^{2,}$*",
            "AUTHORNAMES": "TODO Firstname Lastname and TODO Firstname Lastname",
            "ADDRESS": "\\address{%\n$^{1}$ \\quad TODO Department, Institution, City Postcode, Country; "
                       "TODO e-mail\\\\\n$^{2}$ \\quad TODO Department, Institution, City Postcode, Country; "
                       "TODO e-mail}",
            "CORRES": "Correspondence: TODO e-mail",
            "ORCIDS": "% \\newcommand{\\orcidauthorA}{0000-0000-0000-0000} % then \\orcidA{} after the name",
            "NOTES": "",
        }
    affs: list[str] = []
    for a in authors:
        if not a["aff"]:
            a["aff"] = ["TODO Department, Institution, City Postcode, Country"]
        a["nums"] = []
        for x in a["aff"]:
            if x not in affs:
                affs.append(x)
            a["nums"].append(affs.index(x) + 1)
    single_aff = len(affs) == 1
    names = [a["name"] for a in authors]

    def join_names(items):
        return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]

    orcid_lines, parts = [], []
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, a in enumerate(authors):
        part = a["name"] if single_aff else f"{a['name']} $^{{{','.join(map(str, a['nums']))}}}$"
        if a.get("orcid") and i < len(letters):
            orcid_lines.append(f"\\newcommand{{\\orcidauthor{letters[i]}}}{{{a['orcid']}}}")
            part += f"\\orcid{letters[i]}{{}}"
        parts.append(part)
    if not orcid_lines:
        orcid_lines.append("% \\newcommand{\\orcidauthorA}{0000-0000-0000-0000} % then \\orcidA{} after the name"
                           " -- TODO ask each author for their ORCID iD (strongly recommended)")
    many = len(authors) > 1
    shared_initials = {}
    for a in authors:
        for n in a["nums"]:
            shared_initials.setdefault(n, []).append(a)
    lines = []
    for idx, aff in enumerate(affs, 1):
        mails = []
        for a in shared_initials.get(idx, []):
            if a["nums"][0] != idx:
                continue
            for e in a["email"]:
                mails.append(f"{e} ({initials(a['name'])})" if many and len(shared_initials[idx]) > 1 else e)
            if not a["email"]:
                mails.append(f"TODO e-mail of {a['name']}")
        tail = ("; " + "; ".join(mails)) if mails else ""
        lines.append((aff + tail) if single_aff else f"$^{{{idx}}}$ \\quad {aff}{tail}")
    address = ("\\address[1]{%\n" + lines[0] + "}") if single_aff else \
        "\\address{%\n" + "\\\\\n".join(lines) + "}"
    if any("TODO" in x for x in lines):
        todos.append("affiliations/e-mails: MDPI publishes every author's e-mail; fill the TODOs in \\address")
    if many:
        todos.append("corresponding author: add * after that author's superscript in \\Author "
                     "(e.g. $^{2,}$*) and give the e-mail in \\corres")
        corres = "Correspondence: TODO e-mail of the corresponding author"
    else:
        parts[0] = parts[0] + ("*" if single_aff else "")
        if not single_aff:
            parts[0] = parts[0].replace("}$", ",}$*", 1)
        corres = "Correspondence: " + (authors[0]["email"][0] if authors[0]["email"] else "TODO e-mail")
    notes = []
    cur = [a for a in authors if a.get("current")]
    if cur:
        notes.append("\\firstnote{Current address: " + "; ".join(f"{a['current']} ({initials(a['name'])})"
                                                               for a in cur) + ".}")
    return {"AUTHOR": join_names(parts), "AUTHORNAMES": join_names(names), "ADDRESS": address,
            "CORRES": corres, "ORCIDS": "\n".join(orcid_lines), "NOTES": "\n".join(notes)}


# ---------------------------------------------------------------- preamble

def process_preamble(pre: str, report: dict) -> tuple[str, dict[str, str]]:
    """Return (kept preamble lines, env map old->new)."""
    envmap: dict[str, str] = {}
    spans = []
    newthm_lines = []
    # documentclass
    for m in find_macros(pre, "documentclass"):
        spans.append((m.start, m.end))
    # packages
    for m in find_macros(pre, "usepackage"):
        spans.append((m.start, m.end))
        if not m.args:
            continue
        keep = []
        for p in [x.strip() for x in m.args[0].split(",") if x.strip()]:
            if p in CLASS_PACKAGES:
                report["dropped_packages"].append(f"{p} (loaded by the class)" + (f" [options: {m.opt}]"
                                                                                 if m.opt else ""))
            elif p in FORBIDDEN_PACKAGES:
                report["dropped_packages"].append(f"{p} (changes the MDPI layout/fonts or citation system)")
            else:
                keep.append(p)
        if keep:
            report["kept_packages"].append(",".join(keep))
            newthm_lines.append(f"\\usepackage{'[' + m.opt + ']' if m.opt else ''}{{{','.join(keep)}}}")
    # theorem declarations
    for m in find_macros(pre, "newtheorem", nargs=0, allow_opt=False):
        star = pre[m.start:m.start + 12] == "\\newtheorem*"
        i = m.start + len("\\newtheorem") + (1 if star else 0)
        groups, j = [], i
        while True:
            k = j
            while k < len(pre) and pre[k] in " \t\n":
                k += 1
            if k < len(pre) and pre[k] in "{[":
                close = "}" if pre[k] == "{" else "]"
                e = match_brace(pre, k, pre[k], close)
                if e < 0:
                    break
                groups.append((pre[k], pre[k + 1:e - 1]))
                j = e
            else:
                break
        spans.append((m.start, j))
        braces = [g for t, g in groups if t == "{"]
        if len(braces) < 2:
            continue
        env, title = braces[0].strip(), detex(braces[1]).strip()
        opts = [g for t, g in groups if t == "["]
        if opts and not star:
            report["notes"].append(
                f"\\newtheorem{{{env}}} used [{'] ['.join(opts)}] (shared or per-section numbering); with the "
                "MDPI class every type has its own counter through the whole paper (Theorem 1, Lemma 1, "
                "Definition 1), as in published Axioms papers -- fix any hard-coded numbers in the text")
        cls = CLASS_BY_LOWER.get(title.lower()) or CLASS_BY_LOWER.get(env.lower()) or ALIASES.get(env.lower())
        if star:
            new = env if env.lower() not in CLASS_BY_LOWER else env + "Star"
            newthm_lines.append(f"\\theoremstyle{{mdpi}}\\newtheorem*{{{new}}}{{{title}}}")
            envmap[env] = new
            report["envs"].append(f"{env} -> {new} (unnumbered, kept with the mdpi style)")
        elif cls:
            envmap[env] = cls
            report["envs"].append(f"{env} ({title}) -> {cls} (class environment, own counter)")
        else:
            new = re.sub(r"[^A-Za-z]", "", title.title()) or env.capitalize()
            if new.lower() in CLASS_BY_LOWER or new in envmap.values():
                new = new + "X"
            newthm_lines.append(f"\\theoremstyle{{mdpi}}\\newtheorem{{{new}}}{{{title}}}")
            envmap[env] = new
            report["envs"].append(f"{env} ({title}) -> {new} (new environment, mdpi style, own counter)")
    # layout commands and lengths
    for name in LAYOUT_CMDS:
        nargs = 2 if name == "numberwithin" else 1
        for m in find_macros(pre, name, nargs=nargs):
            spans.append((m.start, m.end))
            report["dropped_cmds"].append(pre[m.start:m.end].strip()[:80])
    for m in re.finditer(r"\\(setlength|addtolength)\s*\{?\\(\w+)\}?\s*\{[^}]*\}", pre):
        if m.group(2) in LAYOUT_LENGTHS:
            spans.append((m.start(), m.end()))
            report["dropped_cmds"].append(m.group(0)[:80])
    for m in re.finditer(r"\\renewcommand\s*\{?\\baselinestretch\}?\s*\{[^}]*\}", pre):
        spans.append((m.start(), m.end()))
        report["dropped_cmds"].append(m.group(0))
    # front-matter commands are read elsewhere; remove them here
    for name in FRONT_CMDS:
        for m in find_macros(pre, name):
            spans.append((m.start, m.end))
    # abstract env in the preamble (amsart allows it)
    for e in find_envs(pre, "abstract"):
        spans.append((e.start, e.end))
    kept = remove_spans(pre, merge(spans))
    kept = re.sub(r"\n\s*\n+", "\n", kept).strip()
    out = "\n".join(x for x in [kept] + newthm_lines if x.strip())
    return out, envmap


def merge(spans):
    spans = sorted(spans)
    out = []
    for a, b in spans:
        if out and a < out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


# ---------------------------------------------------------------- front/back extraction

def extract_keywords_msc(tex: str) -> tuple[str | None, str | None, list[tuple[int, int]]]:
    spans = []
    kw = msc = None
    for m in find_macros(tex, "keywords"):
        if m.args:
            kw = m.args[0]
            spans.append((m.start, m.end))
    for m in find_macros(tex, "subjclass"):
        if m.args:
            msc = m.args[0]
            spans.append((m.start, m.end))
    for m in find_macros(tex, "MSC"):
        if m.args:
            msc = m.args[0]
            spans.append((m.start, m.end))
    for pat, which in ((r"\\(?:textbf|textit|emph)\{\s*(?:Key\s*words|Keywords)\s*:?\s*\}\s*:?\s*", "kw"),
                       (r"\\(?:textbf|textit|emph)\{\s*(?:MSC|Mathematics Subject Classification)[^}]*\}\s*:?\s*",
                        "msc"),
                       (r"(?m)^\s*(?:\\noindent\s*)?(?:Key\s*words|Keywords)\s*:\s*", "kw")):
        m = re.search(pat, tex)
        if m:
            end = re.compile(r"\n\s*\n|\\par\b|\\end\{abstract\}|\\(sub)?section").search(tex, m.end())
            stop = end.start() if end else len(tex)
            val = tex[m.end():stop].strip()
            spans.append((m.start(), stop))
            if which == "kw" and not kw:
                kw = val
            elif which == "msc" and not msc:
                msc = val
    if kw:
        items = [detex(x).strip(" .") for x in re.split(r"[;,·]|\\and\b|\\sep\b", kw) if detex(x).strip(" .")]
        kw = "; ".join(items)
    if msc:
        msc = re.sub(r"(?i)\b(primary|secondary|msc\s*\d*|\d{4}\s*mathematics subject classification)\b[:.]?",
                      " ", detex(msc))
        codes = re.findall(r"\b\d\d(?:-XX|-\d\d|[A-Z]xx|[A-Z]\d\d|[A-Z])\b", msc)
        msc = "; ".join(dict.fromkeys(codes)) if codes else None
    return kw, msc, spans


def pull_back_sections(body: str, report: dict) -> tuple[str, dict[str, str]]:
    """Move unnumbered/numbered Funding, COI, Data, Contributions, Acknowledgments sections
    (and acknowledgment environments) out of the body."""
    found: dict[str, str] = {}
    for env in ("acknowledgments", "acknowledgements", "acknowledgment", "acknowledgement", "acks"):
        for e in find_envs(body, env):
            found["acknowledgments"] = e.body.strip()
            body = body[:e.start] + body[e.end:]
            report["moved"].append(f"\\begin{{{env}}} -> \\acknowledgments")
    heads = list(re.finditer(r"\\(section|subsection)\*?\s*\{([^}]*)\}", body))
    cut = []
    for i, h in enumerate(heads):
        title = detex(h.group(2)).strip().rstrip(".:").lower()
        for macro, pat in BACK_SECTIONS:
            if re.fullmatch(pat, title):
                nxt = heads[i + 1].start() if i + 1 < len(heads) else len(body)
                for stop_pat in (r"\\bibliography\b", r"\\begin\{thebibliography\}", r"\\appendix\b",
                                 r"\\printbibliography"):
                    s = re.search(stop_pat, body[h.end():nxt])
                    if s:
                        nxt = h.end() + s.start()
                found[macro] = body[h.end():nxt].strip()
                cut.append((h.start(), nxt))
                report["moved"].append(f"section \"{h.group(2).strip()}\" -> \\{macro}")
                break
    body = remove_spans(body, cut)
    return body, found


def rename_envs(body: str, envmap: dict[str, str]) -> str:
    for old, new in envmap.items():
        body = re.sub(r"\\(begin|end)\{" + re.escape(old) + r"\}", lambda m: f"\\{m.group(1)}{{{new}}}", body)
    return body


# ---------------------------------------------------------------- main conversion

def convert_tex(src_text: str, src_dir: Path, out_dir: Path, report: dict, todos: list[str]) -> dict[str, str]:
    tex = strip_comments(flatten_inputs(src_text, src_dir))
    b = tex.find("\\begin{document}")
    e = tex.rfind("\\end{document}")
    if b < 0:
        pre, body = "", tex
    else:
        pre, body = tex[:b], tex[b + len("\\begin{document}"):e if e > b else len(tex)]
    whole = pre + "\n" + body
    fill: dict[str, str] = {}
    m = re.search(r"\\documentclass\s*(\[[^\]]*\])?\s*\{([^}]*)\}", pre)
    report["source_class"] = m.group(2) if m else "(none)"

    # title
    t = [x for x in find_macros(whole, "title") if x.args]
    fill["TITLE"] = clean(t[0].args[0]) if t else "TODO Title in Title Case"
    if not t:
        todos.append("title: not found")

    # authors (may sit in the preamble or right after \begin{document})
    front_end = body.find("\\maketitle")
    authors = parse_authors(pre + "\n" + (body[:front_end] if front_end >= 0 else ""))
    fill.update(build_author_block(authors, todos))
    report["authors"] = [a["name"] for a in authors]

    # abstract
    abs_envs = find_envs(whole, "abstract")
    kw, msc, kw_spans = extract_keywords_msc(abs_envs[0].body if abs_envs else "")
    if abs_envs:
        abstract_body = remove_spans(abs_envs[0].body, kw_spans)
        fill["ABSTRACT"] = re.sub(r"\s*\n\s*\n\s*", " ", abstract_body).strip()
        fill["ABSTRACT"] = re.sub(r"\\(noindent|par)\b\s*", "", fill["ABSTRACT"]).strip()
    else:
        fill["ABSTRACT"] = "TODO one-paragraph abstract (at most about 200 words)"
        todos.append("abstract: not found")
    kw2, msc2, _ = extract_keywords_msc(whole)
    kw, msc = kw or kw2, msc or msc2
    fill["KEYWORDS"] = kw or "TODO keyword; keyword; keyword"
    fill["MSC"] = msc or "TODO MSC2020 codes, e.g. 47H10; 54H25"
    if not kw:
        todos.append("keywords: not found (3-10, separated by semicolons)")
    if not msc:
        todos.append("MSC: no \\subjclass / MSC line found; choose MSC2020 codes with the author")

    # preamble
    extra, envmap = process_preamble(pre, report)
    # body: drop everything up to \maketitle (front matter), the abstract, keyword lines
    if front_end >= 0:
        body = body[front_end + len("\\maketitle"):]
    spans = [(x.start, x.end) for x in find_envs(body, "abstract")]
    body = remove_spans(body, spans)
    _, _, kspans = extract_keywords_msc(body)
    body = remove_spans(body, merge(kspans))
    for name in FRONT_CMDS + ["tableofcontents", "maketitle", "bibliographystyle", "newpage", "clearpage"]:
        body = remove_spans(body, [(x.start, x.end) for x in find_macros(body, name)])
    for name in ("numberwithin",):
        body = remove_spans(body, [(x.start, x.end) for x in find_macros(body, name, nargs=2)])
    body = rename_envs(body, envmap)
    n_dollar = len(re.findall(r"\$\$", body)) // 2
    body = re.sub(r"\$\$(.+?)\$\$", lambda mm: "\\[" + mm.group(1) + "\\]", body, flags=re.S)
    if n_dollar:
        report["notes"].append(f"{n_dollar} $$...$$ display(s) rewritten as \\[...\\]")

    # back matter
    body, back = pull_back_sections(body, report)
    # bibliography
    bib_block = None
    for x in find_envs(body, "thebibliography"):
        bib_block = body[x.start:x.end]
        body = body[:x.start] + body[x.end:]
        report["notes"].append("inline thebibliography moved to the reference block; check the order and the "
                               "MDPI entry format (references/reference-style.md)")
    bibs = [x for x in find_macros(body, "bibliography") if x.args]
    for x in find_macros(body, "printbibliography") + find_macros(pre, "addbibresource"):
        report["notes"].append("biblatex detected: MDPI uses BibTeX + Definitions/mdpi.bst; the .bib was kept, "
                               "replace \\autocite/\\textcite etc. by \\cite")
    biblatex_res = [x.args[0] for x in find_macros(pre, "addbibresource") if x.args]
    if bibs or biblatex_res:
        names = []
        for x in bibs:
            names += [n.strip() for n in x.args[0].split(",") if n.strip()]
        names += biblatex_res
        body = remove_spans(body, [(x.start, x.end) for x in bibs + find_macros(body, "printbibliography")])
        copied = []
        for n in names:
            p = src_dir / (n if n.endswith(".bib") else n + ".bib")
            if p.exists():
                dest = out_dir / p.name
                shutil.copy2(p, dest)
                copied.append(p.stem)
                report["copied"].append(p.name)
            else:
                todos.append(f"bibliography file {p.name}: not found next to the draft")
                copied.append(Path(n).stem)
        bib_block = "\\bibliography{" + ",".join(copied) + "}"
    if not bib_block:
        bib_block = "% TODO no bibliography found\n\\begin{thebibliography}{999}\n\\bibitem{TODO}\nTODO\n" \
                    "\\end{thebibliography}"
        todos.append("references: none found")
    fill["BIB"] = bib_block

    # appendix
    appendix = ""
    a = re.search(r"\\appendix\b", body)
    if a:
        app = body[a.end():]
        body = body[:a.start()]
        appendix = "\\appendixtitles{yes} % show the titles of the appendix sections\n\\appendixstart\n" \
                   "\\appendix\n" + app.strip() + "\n"
        report["moved"].append("material after \\appendix -> MDPI appendix (\\appendixstart\\appendix)")
    fill["APPENDIX"] = appendix
    fill["BODY"] = re.sub(r"\n{3,}", "\n\n", body.strip())
    fill["PREAMBLE_EXTRA"] = extra
    fill["_back"] = back
    fill["_n_authors"] = str(max(1, len(authors)))

    # graphics
    gpaths = graphics_paths(pre)
    for g in includegraphics(fill["BODY"] + fill["APPENDIX"]):
        name = g.args[0].strip()
        p = resolve_graphic(name, src_dir, gpaths)
        if p is None:
            todos.append(f"figure file '{name}': not found")
            continue
        rel = p.relative_to(src_dir) if p.is_relative_to(src_dir) else Path(p.name)
        dest = out_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if p.resolve() != dest.resolve():
            shutil.copy2(p, dest)
        report["copied"].append(str(rel))
    return fill


def convert_pandoc(src: Path, out_dir: Path, report: dict, todos: list[str]) -> dict[str, str]:
    import pypandoc
    media = out_dir / "media"
    body = pypandoc.convert_file(str(src), "latex", extra_args=["--wrap=preserve", f"--extract-media={out_dir}",
                                                                "--top-level-division=section"])
    body = body.replace(str(out_dir) + "/", "")
    pre = []
    if "\\tightlist" in body:
        pre.append("\\providecommand{\\tightlist}{\\setlength{\\itemsep}{0pt}\\setlength{\\parskip}{0pt}}")
    if "\\pandocbounded" in body:
        pre.append("\\providecommand{\\pandocbounded}[1]{#1}")
    if "longtable" in body:
        pre.append("\\usepackage{longtable}")
    report["source_class"] = f"{src.suffix} via pandoc"
    report["notes"].append("converted with pandoc: rebuild tables as tabularx/booktabs floats, turn theorem "
                           "paragraphs into Theorem/Lemma/... environments, captions into \\caption, and "
                           "manual numbers into \\label/\\ref (see references/latex-conversion.md)")
    if media.exists():
        report["copied"].append("media/ (images extracted from the document)")
    fake = "\\documentclass{article}\n" + "\n".join(pre) + "\n\\begin{document}\n" + body + "\n\\end{document}\n"
    fill = convert_tex(fake, out_dir, out_dir, report, todos)
    todos.append("title/authors/abstract/keywords: a word-processor draft has no markup for them; move them "
                 "from the top of the body into \\Title, \\Author, \\address, \\abstract, \\keyword")
    return fill


def statements(fill: dict, n_authors: int, todos: list[str]) -> None:
    back = fill.pop("_back", {})
    many = n_authors > 1
    fill["CONTRIB"] = back.get("authorcontributions") or (
        "TODO CRediT roles with author initials, e.g. Conceptualization, A.B. and C.D.; methodology, A.B.; "
        "formal analysis, A.B.; writing---original draft preparation, A.B.; writing---review and editing, C.D.; "
        "supervision, C.D. " + STD_ALL_READ if many else
        "TODO single author: MDPI prescribes no wording; either delete this command or use the CRediT list "
        "with the author's initials.")
    fill["FUNDING"] = back.get("funding") or (
        f"TODO either ``{STD_NO_FUNDING}'' or ``This research was funded by NAME OF FUNDER grant number XXX.''")
    fill["IRB"] = STD_NA
    fill["CONSENT"] = STD_NA
    fill["DATA"] = back.get("dataavailability") or (
        f"TODO for purely theoretical work: ``{STD_NO_DATA}'' -- otherwise e.g. ``{STD_IN_ARTICLE}''")
    ack = back.get("acknowledgments")
    fill["ACK"] = f"\\acknowledgments{{{ack}}}\n" if ack else \
        "%\\acknowledgments{} % optional; also the place for a GenAI-use disclosure (see references/requirements.md)\n"
    std = STD_NO_COI if many else STD_NO_COI_ONE
    fill["COI"] = back.get("conflictsofinterest") or f"TODO confirm with the author(s): ``{std}''"
    fill["SUPPLEMENTARY"] = "%\\supplementary{The following supporting information can be downloaded at " \
                            "\\linksupplementary{s1}, ...} % optional\n"
    fill["ABBREV"] = "%\\abbreviations{Abbreviations}{The following abbreviations are used in this manuscript:\\\\" \
                     " \\noindent\\begin{tabular}{@{}ll} ABC & Full name\\end{tabular}} % optional\n"
    for key, label in (("CONTRIB", "author contributions"), ("FUNDING", "funding"), ("DATA", "data availability"),
                       ("COI", "conflicts of interest")):
        if fill[key].startswith("TODO"):
            todos.append(f"{label}: statement needed from the author(s)")


def render(fill: dict, article_type: str) -> tuple[str, list[str]]:
    n = int(fill.pop("_n_authors", "1"))
    statements(fill, n, fill.setdefault("_todos", []))
    todos = fill.pop("_todos")
    fill["DOCCLASS_OPTS"] = f"axioms,{article_type},submit,{'moreauthors' if n > 1 else 'oneauthor'}"
    text = SKELETON.read_text(encoding="utf-8")
    for k, v in fill.items():
        text = text.replace(f"<<{k}>>", v)
    return text, todos


def write_report(path: Path, report: dict, todos: list[str], src: str) -> None:
    lines = [f"# Import report: {src}", "", f"Source class/format: {report['source_class']}", ""]
    sections_ = [("Authors found", report["authors"]),
                 ("Theorem environments mapped", report["envs"]),
                 ("Moved into MDPI front/back matter", report["moved"]),
                 ("Packages dropped", report["dropped_packages"]),
                 ("Packages kept", report["kept_packages"]),
                 ("Layout commands dropped", report["dropped_cmds"]),
                 ("Files copied", report["copied"]),
                 ("Notes", report["notes"]),
                 ("TODO (resolve before submission)", todos)]
    for title, items in sections_:
        lines += [f"## {title}", ""]
        lines += [f"{i}. {x}" for i, x in enumerate(items, 1)] if items else ["(none)"]
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("source", nargs="?", help="draft .tex/.docx/.odt/.md (omit with --new)")
    ap.add_argument("--out", required=True, help="output folder (created)")
    ap.add_argument("--new", action="store_true", help="write an empty Axioms skeleton")
    ap.add_argument("--authors", type=int, default=2, help="with --new: number of authors (1 = oneauthor)")
    ap.add_argument("--type", default="article", help="MDPI article type option (article, review, communication)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing paper.tex")
    a = ap.parse_args(argv)

    out = Path(a.out)
    if (out / "paper.tex").exists() and not a.force:
        print(f"error: {out / 'paper.tex'} exists (use --force to overwrite)", file=sys.stderr)
        return 1
    if not a.new and not a.source:
        print("error: give a source file or --new", file=sys.stderr)
        return 1
    report = {k: [] for k in ("authors", "envs", "moved", "dropped_packages", "kept_packages", "dropped_cmds",
                              "copied", "notes")}
    todos: list[str] = []
    out.mkdir(parents=True, exist_ok=True)
    try:
        if a.new:
            report["source_class"] = "(new skeleton)"
            fake_authors = "\n".join(f"\\author{{TODO Author {i + 1}}}" for i in range(max(1, a.authors)))
            fill = convert_tex(f"\\documentclass{{article}}\n{fake_authors}\n\\begin{{document}}\n"
                               "\\section{Introduction}\n\nTODO\n\n\\section{Preliminaries}\n\nTODO\n\n"
                               "\\section{Main Results}\n\nTODO\n\n\\section{Conclusions}\n\nTODO\n\n"
                               "\\bibliography{references}\n\\end{document}\n", out, out, report, todos)
            todos[:] = [t for t in todos if "bibliography file" not in t]
            bib = out / "references.bib"
            if not bib.exists():
                bib.write_text("% BibTeX database: ISO 4 journal abbreviations in `journal`, a `doi` field "
                               "wherever one exists.\n", encoding="utf-8")
        else:
            src = Path(a.source)
            if not src.exists():
                raise ImportError_(f"{src} not found")
            if src.suffix.lower() == ".tex":
                fill = convert_tex(read_text(src), src.parent, out, report, todos)
            elif src.suffix.lower() in PANDOC_INPUTS:
                fill = convert_pandoc(src, out, report, todos)
            elif src.suffix.lower() == ".pdf":
                raise ImportError_("PDF cannot be converted reliably; ask for the .tex/.docx source")
            else:
                raise ImportError_(f"unsupported input type {src.suffix}")
    except ImportError_ as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    fill["_todos"] = todos
    text, todos = render(fill, a.type)
    defs = out / "Definitions"
    if defs.exists():
        shutil.rmtree(defs)
    shutil.copytree(DEFINITIONS_DIR, defs)
    (out / "paper.tex").write_text(text, encoding="utf-8")
    write_report(out / "import-report.md", report, todos, a.source or "--new")
    print(f"wrote {out / 'paper.tex'} (+ Definitions/, import-report.md)")
    print(f"{len(report['envs'])} theorem environment(s) mapped, {len(report['moved'])} block(s) moved, "
          f"{len(report['dropped_packages'])} package(s) dropped, {len(todos)} TODO(s)")
    for t in todos:
        print(f"TODO  {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
