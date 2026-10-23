# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6",
#     "pypandoc_binary>=1.13",
# ]
# ///
"""import_source.py -- turn an existing draft (.docx, .odt, .tex, .md, .rtf, .html)
into a paper.md skeleton for build_paper.py.

    uv run import_source.py draft.docx --out work/paper.md [--language uk]

What it does (and only this -- the editorial work stays with you):

1. converts the draft to pandoc Markdown with display math as $$...$$ (Word
   equations and MathType/OMML become LaTeX), extracting images to
   `<out dir>/media/`;
2. removes the reference-list section (a heading like References / Список
   використаних джерел / Література) from the body and puts its entries into
   the `references:` list of the front matter, stripping their leading
   numbers;
3. removes an Abstract/Анотація and Keywords/Ключові слова block if it is a
   heading of its own, putting the text into abstract_<lang> / keywords_<lang>;
4. writes a YAML front matter with every other field set to "TODO" so that
   check_paper.py reports exactly what still has to be filled in.

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

REF_HEAD = re.compile(r"(?i)^(references|bibliography|literature|список\s+(використаних\s+)?(джерел|літератури)|"
                      r"література|джерела)\b")
ABS_HEAD = re.compile(r"(?i)^(abstract|анотація|summary|резюме)\b")
KW_HEAD = re.compile(r"(?i)^(keywords|key words|ключові слова)\b")
KW_LINE = re.compile(r"(?im)^\**\s*(?:keywords|key words|ключові слова)\s*\**\s*[:.—–-]\s*\**(.+)$")
ABS_LINE = re.compile(r"(?im)^\**\s*(?:abstract|анотація)\s*\**\s*[:.—–-]\s*\**(.+)$")

SKELETON_AUTHOR = {
    "surname_en": "TODO", "name_en": "TODO", "surname_uk": "TODO", "name_uk": "TODO", "patronymic_uk": "TODO",
    "degree_en": "TODO", "degree_uk": "TODO", "rank_en": "", "rank_uk": "",
    "position_en": "TODO", "position_uk": "TODO", "interests_uk": "TODO",
    "orcid": "TODO", "email": "TODO", "phone": "TODO", "corresponding": True,
}


def to_markdown(src: Path, media_dir: Path) -> str:
    pandoc = pypandoc.get_pandoc_path()
    cmd = [pandoc, str(src), "-t", "markdown-smart-raw_html-native_divs-native_spans-fenced_divs-bracketed_spans"
           "-header_attributes-simple_tables-multiline_tables-grid_tables+pipe_tables",
           "--wrap=none", f"--extract-media={media_dir.parent}"]  # pandoc adds the media/ level itself
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=media_dir.parent)
    if proc.returncode != 0:
        print(f"error: pandoc failed: {proc.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    md = proc.stdout
    # Pandoc escapes brackets that could start a link; numeric citations must stay plain [1].
    md = re.sub(r"\\([\[\]'\"])", r"\1", md)
    md = re.sub(r"(?m)^(\s*\d+)\\\.", r"\1.", md)  # '1\. text' -- a paragraph that merely starts with a number
    # A line holding only a formula and its number -- the usual "<tab>formula<tab>(n)" layout -- is a
    # display equation; build_paper.py renumbers display equations itself.
    md = re.sub(r"(?m)^[ \t]*\$([^$\n]+)\$[ \t]*[,.;]?[ \t]*\(\s*\d+(?:\.\d+)?\s*\)[ \t]*$", r"$$\1$$", md)
    # Drafts often bold their headings by hand: '# **Introduction**' -> '# Introduction'.
    md = re.sub(r"(?m)^(#{1,6}[ \t]+)\*\*(.+?)\*\*[ \t]*$", r"\1\2", md)
    # ...or use a bold paragraph instead of a heading for References/Abstract/Keywords.
    md = re.sub(r"(?m)^\*\*([^*\n]+?)\*\*[ \t]*$",
                lambda m: f"# {m.group(1)}" if REF_HEAD.match(m.group(1)) or ABS_HEAD.match(m.group(1))
                or KW_HEAD.match(m.group(1)) else m.group(0), md)
    # Display math: pandoc writes $$x$$ inline in a paragraph; put each on its own line for readability.
    md = re.sub(r"[ \t]*\$\$(.+?)\$\$[ \t]*", lambda m: f"\n\n$${m.group(1).strip()}$$\n\n", md, flags=re.S)
    md = re.sub(r"\n{3,}", "\n\n", md)
    # Media paths relative to the output file.
    md = md.replace(str(media_dir.parent) + "/", "")
    return md


def split_sections(md: str) -> list[tuple[str | None, str]]:
    """[(heading text or None for preamble, full chunk text)] on '#'-level headings of any depth."""
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
    """(entries, leftover): list items at the start of the section; whatever follows the list
    (e.g. the end matter of a journal template) is returned as leftover text."""
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
    else:  # not a list: one paragraph per entry, as long as paragraphs look numbered
        paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
        numbered = [p for p in paras if re.match(r"^\s*\[?\d+[.)\]]\s", p)]
        if len(numbered) >= len(paras) / 2:
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
    ap.add_argument("--language", choices=("uk", "en"), help="language of the article (default: guessed)")
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
    md = to_markdown(args.draft.resolve(), args.out.parent.resolve() / "media")

    lang = args.language or ("uk" if len(re.findall(r"[а-яіїєґ]", md, re.I)) > len(re.findall(r"[a-z]", md, re.I))
                             else "en")
    refs, abstract, keywords, kept, udc = [], "", [], [], ""
    m = re.search(r"(?m)^(?:#{1,6}[ \t]+)?\**(?:UDC|УДК)\**[ \t]+([\d.:()\-+/\" ]+?)\**[ \t]*$", md)
    if m:
        udc = m.group(1).strip()
        md = md[:m.start()] + md[m.end():]
    for head, chunk in split_sections(md):
        if head and REF_HEAD.match(head):
            refs, leftover = parse_refs(body_of(chunk))
            if leftover:
                kept.append("\n\n# TODO: material that followed the reference list in the draft -- move what is "
                            "needed into the front matter, then delete this section\n\n" + leftover + "\n")
        elif head and ABS_HEAD.match(head):
            abstract = body_of(chunk)
        elif head and KW_HEAD.match(head):
            keywords = [k.strip(" .") for k in re.split(r"[,;]", body_of(chunk)) if k.strip(" .")]
        else:
            kept.append(chunk)
    body = "".join(kept)
    m = KW_LINE.search(body)
    if m and not keywords:
        keywords = [k.strip(" .*") for k in re.split(r"[,;]", m.group(1)) if k.strip(" .*")]
        body = body[:m.start()] + body[m.end():]
    m = ABS_LINE.search(body)
    if m and not abstract:
        abstract = m.group(1).strip(" *")
        body = body[:m.start()] + body[m.end():]

    other = "en" if lang == "uk" else "uk"
    meta = {
        "language": lang,
        "article_type": "original",
        "udc": udc or "TODO",
        f"title_{lang}": "TODO",
        f"title_{other}": "TODO",
        "authors": [dict(SKELETON_AUTHOR)],
        f"abstract_{lang}": {k: "TODO" for k in ("problem", "purpose", "methods", "results", "conclusions")},
        f"abstract_{other}": {k: "TODO" for k in ("problem", "purpose", "methods", "results", "conclusions")},
        f"keywords_{lang}": keywords or ["TODO"],
        f"keywords_{other}": ["TODO"],
        "references": refs or ["TODO"],
    }
    header = ("# Imported by import_source.py. Fill every TODO (check_paper.py lists them).\n"
              + (f"# Original abstract (restructure it into the five parts below):\n#   "
                 + "\n#   ".join(abstract.splitlines()) + "\n" if abstract else ""))
    text = "---\n" + header + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=110) + "---\n\n" \
        + body.strip() + "\n"
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out} (language={lang}, references={len(refs)}, keywords={len(keywords)}, "
          f"abstract={'found' if abstract else 'not found'})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
