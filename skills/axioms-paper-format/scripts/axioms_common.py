"""Shared constants and LaTeX/BibTeX parsing helpers for the axioms-paper-format
scripts (import_source.py, check_paper.py, build_paper.py, render_preview.py).

Pure standard library on purpose: every script can import it without extra
dependencies. Parsing is deliberately lightweight (brace matching and regular
expressions, not a TeX engine): good enough to read an MDPI manuscript and
typical amsart/article drafts, and every finding names what it saw so a human
can double-check.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = SKILL_DIR / "assets" / "mdpi-template"
DEFINITIONS_DIR = TEMPLATE_DIR / "Definitions"
SKELETON = SKILL_DIR / "assets" / "skeleton.tex"

JOURNAL = "axioms"
CLASS_NAME = "Definitions/mdpi"
ARTICLE_TYPES = {"article", "review", "communication", "briefreport", "conceptpaper", "hypothesis",
                 "perspective", "tutorial", "technicalnote", "editorial", "comment", "reply", "erratum",
                 "correction", "addendum", "essay", "opinion", "shortnote", "systematicreview"}

# Theorem-like environments defined by mdpi.cls v6.5d (capitalised names, one
# counter each, style "mdpi": bold head, italic body).
CLASS_THEOREMS = ["Theorem", "Lemma", "Corollary", "Proposition", "Characterization", "Property", "Problem",
                  "Example", "Remark", "Definition", "Hypothesis", "Notation", "Assumption", "Algorithm"]
# Counters the class creates; a draft's \newtheorem{theorem}... collides with them.
CLASS_COUNTERS = {n.lower() for n in CLASS_THEOREMS}

# Packages the class already loads (template.tex preamble comment). Loading
# them again is harmless at best and an option clash at worst.
CLASS_PACKAGES = {
    "fontenc", "inputenc", "calc", "indentfirst", "fancyhdr", "graphicx", "epstopdf", "lastpage", "ifthen",
    "float", "amsmath", "amssymb", "lineno", "setspace", "enumitem", "mathpazo", "booktabs", "titlesec",
    "etoolbox", "tabto", "xcolor", "colortbl", "soul", "multirow", "microtype", "tikz", "totcount",
    "changepage", "attrib", "upgreek", "array", "tabularx", "pbox", "ragged2e", "tocloft", "marginnote",
    "marginfix", "enotez", "amsthm", "natbib", "hyperref", "cleveref", "scrextend", "url", "geometry",
    "newfloat", "caption", "draftwatermark", "seqsplit",
}
# Packages that change the page layout or fonts and must not be used with the class.
FORBIDDEN_PACKAGES = {"fullpage", "a4wide", "times", "mathptmx", "newtxtext", "newtxmath", "lmodern",
                      "palatino", "fancyheadings", "subfigure", "biblatex", "cite", "titling", "authblk",
                      "showkeys", "showlabels", "refcheck", "times", "helvet", "vmargin", "anysize"}

# Front-matter macros, in template order.
FRONT_MACROS = ["Title", "Author", "AuthorNames", "address", "corres", "abstract", "keyword", "MSC"]
# Back-matter macros, in the order of the MDPI layout guide / template.
BACK_ORDER = ["supplementary", "authorcontributions", "funding", "institutionalreview", "informedconsent",
              "dataavailability", "durcstatement", "acknowledgments", "conflictsofinterest", "abbreviations",
              "appendixstart", "reftitle", "PublishersNote"]

STD_NO_FUNDING = "This research received no external funding."
STD_NO_COI = "The authors declare no conflicts of interest."
STD_NO_COI_ONE = "The author declares no conflicts of interest."
STD_NO_DATA = ("No new data were created or analyzed in this study. "
               "Data sharing is not applicable to this article.")
STD_IN_ARTICLE = ("The original contributions presented in this study are included in the article. "
                  "Further inquiries can be directed to the corresponding author.")
STD_NA = "Not applicable."
STD_ALL_READ = "All authors have read and agreed to the published version of the manuscript."
STD_AI = ("During the preparation of this manuscript/study, the author(s) used [tool name, version information] "
          "for the purposes of [description of use]. The authors have reviewed and edited the output and "
          "take full responsibility for the content of this publication.")
CREDIT_ROLES = ["conceptualization", "methodology", "software", "validation", "formal analysis", "investigation",
                "resources", "data curation", "writing---original draft preparation",
                "writing---review and editing", "visualization", "supervision", "project administration",
                "funding acquisition"]
COVER_LETTER_SENTENCES = [
    "We confirm that neither the manuscript nor any parts of its content are currently under consideration "
    "for publication with or published in another journal.",
    "All authors have approved the manuscript and agree with its submission to Axioms.",
]

# MSC2020: 35J60, 35Jxx, 35-XX, 05C, 00-01 ...
MSC_CODE_RE = re.compile(r"^\d\d(-XX|-\d\d|[A-Z]xx|[A-Z]\d\d|[A-Z])$")
ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s,;{}]+")

# Text left over from template.tex: if any of these survive, the manuscript is unfinished.
TEMPLATE_LEFTOVERS = [
    "How to Use this Template", "Firstname Lastname", "e-mail@e-mail.com", "Affiliation 1", "keyword 1",
    "A single paragraph of about 200 words maximum", "The title of the cited article", "Journal Abbreviation",
    "+xx-xxxx-xxx-xxxx", "0000-0000-0000-000X", "For research articles with several authors",
    "Please add:", "Please add ``", "NAME OF FUNDER", "NAME OF INSTITUTE", "Three-letter acronym",
    "Linear dichroism", "Directory of open access journals", "This is a figure. Schemes follow",
    "This is a table caption", "Title 1", "Example text of a theorem", "Text of the proof",
    "In this section, you can acknowledge", "Declare conflicts of interest or state",
    "We encourage all authors of articles published in MDPI journals to share", "[tool name, version information]",
]


# ---------------------------------------------------------------- LaTeX text helpers

def read_text(path: Path) -> str:
    raw = Path(path).read_bytes()
    for enc in ("utf-8", "cp1251", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def strip_comments(tex: str) -> str:
    """Drop % comments (not \\%), keep the line breaks so line numbers survive.
    Content of verbatim-like environments is not special-cased (rare in papers)."""
    out = []
    for line in tex.split("\n"):
        i, cut = 0, None
        while i < len(line):
            c = line[i]
            if c == "\\":
                i += 2
                continue
            if c == "%":
                cut = i
                break
            i += 1
        out.append(line if cut is None else line[:cut])
    return "\n".join(out)


def line_of(tex: str, pos: int) -> int:
    return tex.count("\n", 0, pos) + 1


def match_brace(tex: str, start: int, open_ch: str = "{", close_ch: str = "}") -> int:
    """`start` points at an opening brace; return the index just past its partner (or -1)."""
    depth, i, n = 0, start, len(tex)
    while i < n:
        c = tex[i]
        if c == "\\":
            i += 2
            continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def _skip_ws(tex: str, i: int) -> int:
    while i < len(tex) and tex[i] in " \t\r\n":
        i += 1
    return i


@dataclass
class Macro:
    name: str
    start: int
    end: int
    opt: str | None
    args: list[str]


def find_macros(tex: str, name: str, nargs: int = 1, allow_opt: bool = True) -> list[Macro]:
    """Every \\name[opt]{a1}...{an}. A call with fewer brace groups is returned with the args found."""
    res = []
    for m in re.finditer(r"\\" + re.escape(name) + r"(?![A-Za-z@])\*?", tex):
        i = m.end()
        opt = None
        j = _skip_ws(tex, i)
        if allow_opt and j < len(tex) and tex[j] == "[":
            k = match_brace(tex, j, "[", "]")
            if k > 0:
                opt, i = tex[j + 1:k - 1], k
        args = []
        for _ in range(nargs):
            j = _skip_ws(tex, i)
            if j < len(tex) and tex[j] == "{":
                k = match_brace(tex, j)
                if k < 0:
                    break
                args.append(tex[j + 1:k - 1])
                i = k
            else:
                break
        res.append(Macro(name, m.start(), i, opt, args))
    return res


def macro_arg(tex: str, name: str) -> str | None:
    found = [m for m in find_macros(tex, name) if m.args]
    return found[-1].args[0] if found else None


@dataclass
class Env:
    name: str
    start: int          # index of \begin
    body_start: int     # just after \begin{name}[opt]
    body_end: int       # index of \end
    end: int            # just past \end{name}
    opt: str | None
    body: str


def find_envs(tex: str, name: str) -> list[Env]:
    """Every \\begin{name}...\\end{name}, nesting-aware for the same name."""
    res = []
    pat = re.compile(r"\\(begin|end)\{" + re.escape(name) + r"\}")
    stack = []
    for m in pat.finditer(tex):
        if m.group(1) == "begin":
            stack.append(m)
        elif stack:
            b = stack.pop()
            if stack:
                continue
            i, opt = b.end(), None
            j = _skip_ws(tex, i)
            if j < len(tex) and tex[j] == "[":
                k = match_brace(tex, j, "[", "]")
                if k > 0:
                    opt, i = tex[j + 1:k - 1], k
            res.append(Env(name, b.start(), i, m.start(), m.end(), opt, tex[i:m.start()]))
    return res


def env_names(tex: str) -> list[str]:
    return re.findall(r"\\begin\{([A-Za-z*@]+)\}", tex)


MATH_ENVS = r"equation\*?|align\*?|gather\*?|multline\*?|eqnarray\*?|flalign\*?|alignat\*?|displaymath|math"


def strip_math(text: str, repl: str = " X ") -> str:
    text = re.sub(r"\\begin\{(" + MATH_ENVS + r")\}.*?\\end\{\1\}", repl, text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$", repl, text, flags=re.S)
    text = re.sub(r"\\\[.*?\\\]", repl, text, flags=re.S)
    text = re.sub(r"\\\(.*?\\\)", repl, text, flags=re.S)
    text = re.sub(r"(?<!\\)\$.*?(?<!\\)\$", repl, text, flags=re.S)
    return text


def detex(text: str) -> str:
    """Rough plain text for word counts and wording checks."""
    t = strip_math(strip_comments(text), " X ")
    t = re.sub(r"\\(cite[tp]?|ref|eqref|cref|Cref|label|url|href)\*?(\[[^\]]*\])?\{[^}]*\}", " ", t)
    t = re.sub(r"\\(textbf|textit|emph|textrm|textsc|mathrm|text|underline|textsf|texttt)\{", "{", t)
    t = re.sub(r"\\[A-Za-z@]+\*?", " ", t)
    t = t.replace("~", " ").replace("---", "—").replace("--", "–")
    t = re.sub(r"[{}]", "", t)
    t = re.sub(r"\\.", "", t)
    return re.sub(r"\s+", " ", t).strip()


def words(text: str) -> int:
    return len([w for w in re.findall(r"\S+", text) if re.search(r"\w", w)])


# ---------------------------------------------------------------- manuscript structure

@dataclass
class Section:
    level: int          # 1 section, 2 subsection, 3 subsubsection
    title: str
    starred: bool
    start: int
    end: int = 0        # start of the next heading of any level (or end of body)
    appendix: bool = False


SECTION_RE = re.compile(r"\\(section|subsection|subsubsection|paragraph)(\*?)\s*(\[[^\]]*\])?\s*\{")


def sections(body: str) -> list[Section]:
    out: list[Section] = []
    appendix_at = body.find("\\appendix")
    for m in SECTION_RE.finditer(body):
        k = match_brace(body, m.end() - 1)
        title = body[m.end():k - 1] if k > 0 else ""
        level = {"section": 1, "subsection": 2, "subsubsection": 3, "paragraph": 4}[m.group(1)]
        out.append(Section(level, detex(title), bool(m.group(2)), m.start(),
                           appendix=appendix_at >= 0 and m.start() > appendix_at))
    for a, b in zip(out, out[1:]):
        a.end = b.start
    if out:
        out[-1].end = len(body)
    return out


def section_text(body: str, secs: list[Section], idx: int) -> str:
    """Text of a top-level section including its subsections."""
    s = secs[idx]
    end = len(body)
    for t in secs[idx + 1:]:
        if t.level <= s.level:
            end = t.start
            break
    return body[s.start:end]


@dataclass
class Manuscript:
    path: Path
    raw: str
    tex: str                         # comments stripped
    preamble: str
    body: str                        # between \begin{document} and \end{document}
    body_offset: int
    docclass_opts: list[str] = field(default_factory=list)
    docclass: str = ""

    def line(self, pos_in_body: int) -> int:
        return line_of(self.tex, self.body_offset + pos_in_body)


def load_manuscript(path: Path) -> Manuscript:
    raw = read_text(path)
    tex = strip_comments(raw)
    b = tex.find("\\begin{document}")
    e = tex.rfind("\\end{document}")
    if b < 0:
        preamble, body, off = tex, "", len(tex)
    else:
        preamble = tex[:b]
        off = b + len("\\begin{document}")
        body = tex[off:e if e > b else len(tex)]
    ms = Manuscript(Path(path), raw, tex, preamble, body, off)
    m = re.search(r"\\documentclass\s*(\[([^\]]*)\])?\s*\{([^}]*)\}", preamble)
    if m:
        ms.docclass = m.group(3).strip()
        ms.docclass_opts = [o.strip() for o in (m.group(2) or "").split(",") if o.strip()]
    return ms


def flatten_inputs(tex: str, base: Path, seen: set | None = None) -> str:
    """Inline \\input{x} / \\include{x} (relative to `base`), recursively. MDPI wants one
    compilable source tree; a single file is also what the checker reads."""
    seen = seen or set()

    def repl(m):
        name = m.group(2).strip()
        p = (base / name)
        if p.suffix != ".tex":
            p = p.with_suffix(".tex") if not p.exists() else p
        if not p.exists() or p.resolve() in seen:
            return m.group(0)
        seen.add(p.resolve())
        return flatten_inputs(read_text(p), p.parent, seen)

    return re.sub(r"(?<!%)\\(input|include)\{([^}]+)\}", repl, tex)


# ---------------------------------------------------------------- citations, labels

CITE_RE = re.compile(r"\\(cite|citep|citet|citealp|citeauthor|citenum|parencite|autocite)\*?"
                     r"\s*(\[[^\]]*\])?\s*(\[[^\]]*\])?\s*\{([^}]*)\}")


def citations(tex: str) -> list[tuple[int, list[str], str | None]]:
    """(position, keys, optional-arg) for every citation, in text order."""
    out = []
    for m in CITE_RE.finditer(tex):
        keys = [k.strip() for k in m.group(4).split(",") if k.strip()]
        opt = (m.group(3) or m.group(2))
        out.append((m.start(), keys, opt[1:-1] if opt else None))
    return out


def first_cite_order(tex: str) -> list[str]:
    order, seen = [], set()
    for _, keys, _ in citations(tex):
        for k in keys:
            if k not in seen:
                seen.add(k)
                order.append(k)
    return order


def labels(tex: str) -> dict[str, int]:
    return {m.group(1).strip(): m.start() for m in re.finditer(r"\\label\{([^}]+)\}", tex)}


def refs(tex: str) -> list[tuple[int, str]]:
    out = []
    for m in re.finditer(r"\\(ref|eqref|cref|Cref|autoref|pageref)\*?\{([^}]+)\}", tex):
        for k in m.group(2).split(","):
            out.append((m.start(), k.strip()))
    return out


# ---------------------------------------------------------------- BibTeX

@dataclass
class BibEntry:
    type: str
    key: str
    fields: dict[str, str]
    line: int


def parse_bib(text: str) -> list[BibEntry]:
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{", text):
        typ = m.group(1).lower()
        if typ in ("comment", "preamble", "string"):
            continue
        end = match_brace(text, m.end() - 1)
        if end < 0:
            continue
        inner = text[m.end():end - 1]
        key, _, rest = inner.partition(",")
        fields: dict[str, str] = {}
        i = 0
        while i < len(rest):
            fm = re.compile(r"\s*([A-Za-z][\w-]*)\s*=\s*").match(rest, i)
            if not fm:
                i += 1
                continue
            name = fm.group(1).lower()
            j = fm.end()
            if j < len(rest) and rest[j] == "{":
                k = match_brace(rest, j)
                val = rest[j + 1:k - 1] if k > 0 else rest[j + 1:]
                j = k if k > 0 else len(rest)
            elif j < len(rest) and rest[j] == '"':
                k = rest.find('"', j + 1)
                val = rest[j + 1:k]
                j = k + 1
            else:
                k = re.compile(r"[^,]*").match(rest, j).end()
                val = rest[j:k].strip()
                j = k
            fields[name] = re.sub(r"\s+", " ", val).strip()
            i = j
        entries.append(BibEntry(typ, key.strip(), fields, text.count("\n", 0, m.start()) + 1))
    return entries


def bibitems(tex: str) -> list[tuple[str, str, int]]:
    """(key, text, position) of each \\bibitem in an inline thebibliography."""
    out = []
    for env in find_envs(tex, "thebibliography"):
        items = list(re.finditer(r"\\bibitem\s*(\[[^\]]*\])?\s*\{([^}]+)\}", env.body))
        for a, b in zip(items, items[1:] + [None]):
            text = env.body[a.end():b.start() if b else len(env.body)]
            out.append((a.group(2).strip(), text.strip(), env.body_start + a.start()))
    return out


def bib_files(tex: str, base: Path) -> list[Path]:
    out = []
    for m in find_macros(tex, "bibliography"):
        for name in (m.args[0].split(",") if m.args else []):
            p = base / name.strip()
            out.append(p if p.suffix == ".bib" else p.with_suffix(".bib"))
    return out


# ---------------------------------------------------------------- graphics

GRAPHIC_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".eps", ".tif", ".tiff"]


def graphics_paths(preamble: str) -> list[str]:
    m = find_macros(preamble, "graphicspath")
    if not m or not m[-1].args:
        return [""]
    return [""] + re.findall(r"\{([^}]*)\}", m[-1].args[0])


def resolve_graphic(name: str, base: Path, gpaths: list[str]) -> Path | None:
    for gp in gpaths:
        p = base / gp / name
        if p.suffix.lower() in GRAPHIC_EXTS and p.exists():
            return p
        for ext in GRAPHIC_EXTS:
            q = p.with_name(p.name + ext)
            if q.exists():
                return q
    return None


def includegraphics(tex: str) -> list[Macro]:
    return [m for m in find_macros(tex, "includegraphics") if m.args]
