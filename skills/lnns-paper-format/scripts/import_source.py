# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6",
#     "pypandoc_binary>=1.13",
# ]
# ///
"""import_source.py -- turn an existing draft (.docx, .odt, .tex, .md, .rtf, .html)
into a paper.md skeleton for build_paper.py.

    uv run import_source.py draft.docx --out work/paper.md

What it does (and only this -- the editorial work stays with you):

1. converts the draft to pandoc Markdown with display math as $$...$$ (Word
   equations become LaTeX), extracting images to `<out dir>/media/`;
2. strips hand-made heading numbers ('1 Introduction', '2.1. Data') because
   build_paper.py numbers sections itself;
3. moves the reference list (a heading like References / Bibliography) into
   the `references:` list of the front matter, stripping the leading numbers;
4. moves an Abstract and a Keywords block (heading or 'Keywords:' line) into
   `abstract:` / `keywords:`; a LaTeX source's \\title, \\begin{abstract} and
   \\keywords{a \\and b} are picked up too;
5. writes every other field as "TODO" so that check_paper.py lists exactly
   what is still missing.

It never overwrites an existing --out file unless --force is given.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import pypandoc
import yaml

REF_HEAD = re.compile(r"(?i)^(references|bibliography|literature|works cited)\b")
ABS_HEAD = re.compile(r"(?i)^(abstract|summary)\b")
KW_HEAD = re.compile(r"(?i)^(keywords|key words|index terms)\b")
KW_LINE = re.compile(r"(?im)^(?:>\s*)?\**\s*(?:keywords|key words|index terms)\s*\**\s*[:.—–-]\s*\**(.+)$")
ABS_LINE = re.compile(r"(?im)^(?:>\s*)?\**\s*abstract\s*\**\s*[:.—–-]\s*\**(.+)$")

SKELETON_AUTHOR = {"given": "TODO", "family": "TODO", "affiliations": [1], "orcid": "TODO", "email": "TODO",
                   "corresponding": True}


def to_markdown(src: Path, media_dir: Path, tex_text: str | None = None) -> str:
    """Draft -> Markdown. A LaTeX draft is passed as (pre-cleaned) text on stdin."""
    pandoc = pypandoc.get_pandoc_path()
    inp = ["-f", "latex", "--resource-path", str(src.parent)] if tex_text is not None else [str(src)]
    cmd = [pandoc, *inp, "-t", "markdown-smart-raw_html-raw_tex-native_divs-native_spans-fenced_divs"
           "-bracketed_spans-header_attributes-simple_tables-multiline_tables-grid_tables+pipe_tables",
           "--wrap=none", f"--extract-media={media_dir.parent}"]
    proc = subprocess.run(cmd, input=tex_text, capture_output=True, text=True, encoding="utf-8",
                          cwd=media_dir.parent)
    if proc.returncode != 0:
        print(f"error: pandoc failed: {proc.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    md = proc.stdout
    md = re.sub(r"\\([\[\]'\"])", r"\1", md)  # pandoc escapes brackets; numeric citations must stay plain [1]
    md = re.sub(r"(?m)^(\s*\d+)\\\.", r"\1.", md)
    # "formula<tab>(n)" lines from Word drafts are display equations; the builder renumbers them.
    md = re.sub(r"(?m)^[ \t]*\$([^$\n]+)\$[ \t]*[,.;]?[ \t]*\(\s*\d+(?:\.\d+)?\s*\)[ \t]*$", r"$$\1$$", md)
    md = re.sub(r"(?m)^(#{1,6}[ \t]+)\*\*(.+?)\*\*[ \t]*$", r"\1\2", md)
    # Hand-numbered headings: '# 1 Introduction', '## 2.1. Data' -> numbering is the builder's job.
    md = re.sub(r"(?m)^(#{1,6}[ \t]+)(?:\d+(?:\.\d+)*\.?|[IVX]+\.)[ \t]+", r"\1", md)
    md = re.sub(r"(?m)^\*\*([^*\n]+?)\*\*[ \t]*$",
                lambda m: f"# {m.group(1)}" if REF_HEAD.match(m.group(1)) or ABS_HEAD.match(m.group(1))
                or KW_HEAD.match(m.group(1)) else m.group(0), md)
    md = re.sub(r"[ \t]*\$\$(.+?)\$\$[ \t]*", lambda m: f"\n\n$${m.group(1).strip()}$$\n\n", md, flags=re.S)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.replace(str(media_dir.parent) + "/", "")


def tex_to_md_inline(s: str) -> str:
    """Bibliography/credits LaTeX -> paper.md inline text (bold/italic markup, DOIs and URLs as plain links)."""
    s = re.sub(r"\\doi\{([^{}]*)\}", r"https://doi.org/\1", s)
    s = re.sub(r"\\url\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\textbf\{([^{}]*)\}", r"**\1**", s)
    s = re.sub(r"\\(?:emph|textit)\{([^{}]*)\}", r"*\1*", s)
    s = s.replace("---", "—").replace("--", "–").replace("~", " ").replace("\\&", "&").replace("\\_", "_")
    s = re.sub(r"\\newblock\s*", "", s)
    return " ".join(s.split())


def latex_extras(src: Path) -> tuple[dict, str]:
    """(title/abstract/keywords/references/credits found in an llncs source, the source with those parts removed)."""
    tex = src.read_text(encoding="utf-8", errors="replace")
    out = {}
    m = re.search(r"\\begin\{thebibliography\}.*?\n(.*?)\\end\{thebibliography\}", tex, re.S)
    if m:
        out["cite_keys"] = re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^{}]*)\}", m.group(1))
        items = re.split(r"\\bibitem(?:\[[^\]]*\])?\{[^{}]*\}", m.group(1))[1:]
        out["references"] = [tex_to_md_inline(i) for i in items if i.strip()]
    m = re.search(r"\\begin\{credits\}(.*?)\\end\{credits\}", tex, re.S)
    if m:
        for key, macro in (("acknowledgments", "ackname"), ("disclosure", "discintname")):
            c = re.search(r"\\subsubsection\*?\{\\%s\}(.*?)(?=\\subsubsection|\Z)" % macro, m.group(1), re.S)
            if c:
                out[key] = tex_to_md_inline(re.sub(r"\\footnote\{[^{}]*\}", "", c.group(1)))
    m = re.search(r"\\title\{((?:[^{}]|\{[^{}]*\})*)\}", tex)
    if m:
        out["title"] = re.sub(r"\\\\|\s+", " ", m.group(1)).strip()
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
    if m:
        abstract = re.sub(r"\\keywords\{.*?\}", "", m.group(1), flags=re.S)
        out["abstract"] = " ".join(abstract.split())
    m = re.search(r"\\keywords\{(.*?)\}", tex, re.S)
    if m:
        out["keywords"] = [k.strip(" .\n") for k in re.split(r"\\and|·|,", m.group(1)) if k.strip(" .\n")]
    for env in ("thebibliography", "credits", "abstract"):
        tex = re.sub(r"\\begin\{%s\}.*?\\end\{%s\}" % (env, env), "", tex, flags=re.S)
    tex = re.sub(r"\\(?:bibliography|bibliographystyle)\{[^{}]*\}", "", tex)
    return out, tex


def split_sections(md: str) -> list[tuple[str | None, str]]:
    parts, last, last_head = [], 0, None
    for m in re.finditer(r"(?m)^#{1,6}[ \t]+(.+?)[ \t]*$", md):
        parts.append((last_head, md[last:m.start()]))
        last, last_head = m.start(), re.sub(r"[*_]", "", m.group(1)).strip()
    parts.append((last_head, md[last:]))
    return parts


def body_of(chunk: str) -> str:
    return re.sub(r"(?m)^#{1,6}[ \t]+.*$", "", chunk, count=1).strip()


_ITEM = re.compile(r"^\s{0,3}(?:\d+[.)]|\[\d+\]|[-*+])\s+")


def parse_refs(text: str) -> tuple[list[str], str]:
    lines = text.split("\n")
    entries: list[str] = []
    i = 0
    if any(_ITEM.match(ln) for ln in lines[:3]):
        while i < len(lines):
            ln = lines[i]
            if _ITEM.match(ln):
                entries.append(_ITEM.sub("", ln, count=1))
            elif ln.strip() and ln.startswith((" ", "\t")) and entries:
                entries[-1] += " " + ln.strip()
            elif ln.strip():
                break
            i += 1
        leftover = "\n".join(lines[i:])
    else:
        paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
        numbered = [p for p in paras if re.match(r"^\s*\[?\d+[.)\]]\s", p)]
        if paras and len(numbered) >= len(paras) / 2:
            k = 0
            while k < len(paras) and re.match(r"^\s*\[?\d+[.)\]]\s", paras[k]):
                k += 1
            entries = [re.sub(r"^\s*\[?\d+[.)\]]\s+", "", p) for p in paras[:k]]
            leftover = "\n\n".join(paras[k:])
        else:
            entries, leftover = paras, ""
    clean = [re.sub(r"<(https?://[^>]+)>", r"\1", re.sub(r"\s+", " ", e)).strip() for e in entries]
    return [c for c in clean if c], leftover.strip()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("draft", type=Path)
    ap.add_argument("--out", type=Path, default=Path("paper.md"))
    ap.add_argument("--force", action="store_true", help="overwrite --out if it exists")
    args = ap.parse_args(argv)
    if not args.draft.is_file():
        print(f"error: not found: {args.draft}", file=sys.stderr)
        return 1
    if args.draft.suffix.lower() == ".pdf":
        print("error: PDF cannot be converted reliably; ask for the .docx/.tex source or paste the text",
              file=sys.stderr)
        return 1
    if args.out.exists() and not args.force:
        print(f"error: {args.out} exists; pass --force to overwrite", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    extras, tex_text = latex_extras(args.draft) if args.draft.suffix.lower() == ".tex" else ({}, None)
    md = to_markdown(args.draft.resolve(), args.out.parent.resolve() / "media", tex_text)
    if extras.get("cite_keys"):
        # pandoc writes \cite{a,b} as [@a; @b]; numbered citations follow the \bibitem order.
        num = {k: n for n, k in enumerate(extras["cite_keys"], 1)}
        md = re.sub(r"\[(@[^\]]+)\]", lambda m: ("[" + ", ".join(str(num[k]) for k in re.findall(r"@([\w:.\-/]+)", m.group(1)))
                                                + "]") if all(k in num for k in re.findall(r"@([\w:.\-/]+)", m.group(1)))
                    else m.group(0), md)

    refs, abstract, keywords, kept = extras.get("references", []), extras.get("abstract", ""), extras.get("keywords", []), []
    for head, chunk in split_sections(md):
        if head and REF_HEAD.match(head):
            parsed, leftover = parse_refs(body_of(chunk))
            refs = refs or parsed
            if leftover:
                kept.append("\n\n# TODO: material that followed the reference list in the draft -- move what is "
                            "needed into the front matter (acknowledgments, disclosure), then delete this "
                            "section\n\n" + leftover + "\n")
        elif head and ABS_HEAD.match(head):
            abstract = abstract or body_of(chunk)
        elif head and KW_HEAD.match(head):
            keywords = keywords or [k.strip(" .") for k in re.split(r"[,;·]", body_of(chunk)) if k.strip(" .")]
        else:
            kept.append(chunk)
    body = "".join(kept)
    m = KW_LINE.search(body)
    if m:
        keywords = keywords or [k.strip(" .*") for k in re.split(r"[,;·]", m.group(1)) if k.strip(" .*")]
        body = body[:m.start()] + body[m.end():]
    m = ABS_LINE.search(body)
    if m:
        abstract = abstract or m.group(1).strip(" *")
        body = body[:m.start()] + body[m.end():]

    meta = {
        "title": extras.get("title") or "TODO",
        "conference": {"name": "TODO", "min_pages": None, "max_pages": None},
        "citation_order": "citation",
        "authors": [dict(SKELETON_AUTHOR)],
        "affiliations": ["TODO: Department, Institution, Street, City Postcode, Country"],
        "abstract": " ".join(abstract.split()) or "TODO",
        "keywords": keywords or ["TODO"],
        **({"acknowledgments": extras["acknowledgments"]} if extras.get("acknowledgments") else {}),
        "disclosure": extras.get("disclosure") or "TODO",
        "references": refs or ["TODO"],
    }
    header = ("# Imported by import_source.py. Fill every TODO (check_paper.py lists them), remove the title,\n"
              "# author and affiliation lines left in the body, and convert the references to splncs04 style.\n")
    text = "---\n" + header + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=110) + "---\n\n" \
        + body.strip() + "\n"
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out} (references={len(refs)}, keywords={len(keywords)}, "
          f"abstract={'found' if abstract else 'not found'})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
