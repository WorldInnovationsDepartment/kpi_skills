# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""renumber_refs.py -- reorder the reference list of paper.md and renumber every citation in the body.

    uv run renumber_refs.py paper.md --order citation       # order of first citation (llncs default)
    uv run renumber_refs.py paper.md --order alphabetical   # by first author, as splncs04 sorts

Rewrites paper.md in place (a copy of the original is kept as paper.md.bak) and
sets `citation_order:` in the front matter to match. Citation groups are
rewritten in Springer's form, e.g. [7, 3, 4] -> [3, 4, 7] and [5, 6, 7] -> [5–7].
Uncited references are kept at the end (citation order) or in their
alphabetical place, so check_paper.py still reports them as `cite.unused`.
Citations inside code blocks and math are left alone.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

import yaml

from lnns_common import (
    CITE_RE,
    SourceError,
    citation_numbers,
    find_citations,
    format_citation,
    load_source,
    references,
    sort_key,
    strip_code,
    strip_math,
)


def new_order(refs: list[str], body: str, order: str) -> list[int]:
    """Old 1-based numbers in their new order."""
    n = len(refs)
    if order == "alphabetical":
        return sorted(range(1, n + 1), key=lambda i: (sort_key(refs[i - 1]), i))
    seen: list[int] = []
    for _, k in find_citations(body):
        if 1 <= k <= n and k not in seen:
            seen.append(k)
    return seen + [i for i in range(1, n + 1) if i not in seen]


def rewrite_body(body: str, mapping: dict[int, int]) -> str:
    clean = strip_math(strip_code(body))
    out, last = [], 0
    for m in CITE_RE.finditer(clean):
        nums = [mapping.get(k, k) for k in citation_numbers(m.group(1))]
        out.append(body[last:m.start()])
        out.append(format_citation(nums))
        last = m.end()
    out.append(body[last:])
    return "".join(out)


def rewrite_front(front_text: str, refs_new: list[str], order: str) -> str:
    """Replace the references: list and citation_order: line, keeping every other line (and comment) as written."""
    lines = front_text.split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if re.match(r"^references\s*:", ln):
            out.append("references:")
            out.extend("  - " + yaml.safe_dump(r, allow_unicode=True, width=10_000, default_style='"').strip()
                       for r in refs_new)
            i += 1
            while i < len(lines) and (lines[i].startswith((" ", "\t", "-")) or not lines[i].strip()) \
                    and not re.match(r"^(---|\.\.\.)\s*$", lines[i]):
                i += 1
            continue
        if re.match(r"^citation_order\s*:", ln):
            comment = re.search(r"\s+#.*$", ln)
            out.append(f"citation_order: {order}" + (comment.group(0) if comment else ""))
            i += 1
            continue
        out.append(ln)
        i += 1
    text = "\n".join(out)
    if not re.search(r"(?m)^citation_order\s*:", text):
        text = re.sub(r"(?m)^references\s*:", f"citation_order: {order}\nreferences:", text, count=1)
    return text


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("source", type=Path)
    ap.add_argument("--order", choices=("citation", "alphabetical"), required=True)
    ap.add_argument("--dry-run", action="store_true", help="print the old -> new mapping only")
    args = ap.parse_args(argv)
    try:
        src = load_source(args.source)
    except (SourceError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    refs = references(src.meta)
    if not refs:
        print("error: no references in the front matter", file=sys.stderr)
        return 1
    order = new_order(refs, src.body, args.order)
    mapping = {old: new for new, old in enumerate(order, 1)}
    changed = {o: n for o, n in mapping.items() if o != n}
    print(f"{len(changed)} of {len(refs)} references change number"
          + ("".join(f"\n  [{o}] -> [{n}]" for o, n in sorted(changed.items())) if changed else ""), file=sys.stderr)
    if args.dry_run:
        return 0
    front = rewrite_front(src.front_text, [refs[o - 1] for o in order], args.order)
    body = rewrite_body(src.body, mapping)
    shutil.copyfile(args.source, args.source.with_suffix(args.source.suffix + ".bak"))
    args.source.write_text(front + body, encoding="utf-8")
    load_source(args.source)  # sanity: the rewritten front matter still parses
    print(f"rewrote {args.source} (backup: {args.source.name}.bak)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
