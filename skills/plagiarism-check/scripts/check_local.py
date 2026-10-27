# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = [
#     "python-docx>=1.1",
#     "pymupdf>=1.24",
# ]
# ///
"""Check a document for text reuse against a local corpus (your own papers, colleagues' theses,
downloaded sources, the web corpus collected by check_web.py).

    uv run check_local.py thesis.docx --corpus sources/ [--own my-papers/] --out plag-check
                          [--k 5] [--min-words 8] [--gap 4] [--include quotes,references]
                          [--semantic] [--semantic-threshold 0.92]

Writes plagiarism-report.{md,html,json} into --out. --own marks folders with the candidate's own
publications: matches there are reported separately as self-reuse (allowed in a dissertation when
cited) and do not count towards the "external" similarity. --semantic adds a sentence-embedding pass
(needs sentence-transformers; first run downloads intfloat/multilingual-e5-small, ~450 MB).
Exit 0 = ran; 2 = input error. The similarity figures describe only the corpus you supplied.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import text_common as tc
from match_engine import DEFAULT_GAP, DEFAULT_K, DEFAULT_MIN_WORDS, Index, coverage, load_corpus, semantic_matches, tokenize
from plag_report import build_result, write_html, write_json, write_markdown


def run_check(target_path: Path, corpus_dirs: list[Path], own_dirs: list[Path], out: Path, *, k=DEFAULT_K,
              min_words=DEFAULT_MIN_WORDS, gap=DEFAULT_GAP, include=(), semantic=False, semantic_threshold=0.92,
              manifest: dict | None = None, mode: str = "local") -> dict:
    target = tc.extract(target_path)
    tokens = tokenize(target, include_quotes="quotes" in include, include_references="references" in include)
    sources = load_corpus(corpus_dirs, own_dirs, manifest=manifest, skip=target_path)
    if not sources:
        raise tc.ExtractError("the corpus is empty (no readable .docx/.pdf/.md/.tex/.txt files)")
    index = Index(k)
    for s in sources:
        index.add(s)
    runs = index.match(tokens, min_words=min_words, gap=gap)
    src_map = {s.id: s for s in sources}
    cov = coverage(runs, len(tokens), src_map)
    sem = []
    if semantic:
        try:
            sem = semantic_matches(target, tokens, cov["covered_mask"], src_map, threshold=semantic_threshold, min_words=min_words)
        except ImportError:
            print("WARNING: sentence-transformers not installed; run with `uv run --with sentence-transformers` for --semantic",
                  file=sys.stderr)
    settings = {"k": k, "min_words": min_words, "gap": gap, "include": list(include), "semantic": semantic,
                "semantic_threshold": semantic_threshold, "corpus": [str(d) for d in corpus_dirs], "own": [str(d) for d in own_dirs]}
    result = build_result(target, tokens, runs, cov, src_map, sem, settings)
    out.mkdir(parents=True, exist_ok=True)
    write_json(result, out)
    write_markdown(result, out, mode)
    write_html(target, tokens, runs, src_map, result, out)
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", type=Path)
    ap.add_argument("--corpus", type=Path, nargs="*", default=[], help="folders/files with external sources")
    ap.add_argument("--own", type=Path, nargs="*", default=[], help="folders/files with the candidate's own publications")
    ap.add_argument("--out", type=Path, default=Path("plag-check"))
    ap.add_argument("--k", type=int, default=DEFAULT_K, help="shingle length in words")
    ap.add_argument("--min-words", type=int, default=DEFAULT_MIN_WORDS, help="shortest reported match")
    ap.add_argument("--gap", type=int, default=DEFAULT_GAP, help="tolerated gap (missing shingles) inside a near-verbatim run")
    ap.add_argument("--include", default="", help="comma list: quotes,references (match them too)")
    ap.add_argument("--semantic", action="store_true", help="add the sentence-embedding paraphrase pass")
    ap.add_argument("--semantic-threshold", type=float, default=0.92)
    args = ap.parse_args(argv)
    if not args.corpus and not args.own:
        ap.error("give at least one --corpus or --own folder")
    include = {s.strip() for s in args.include.split(",") if s.strip()}
    try:
        res = run_check(args.target, args.corpus, args.own, args.out, k=args.k, min_words=args.min_words, gap=args.gap,
                        include=include, semantic=args.semantic, semantic_threshold=args.semantic_threshold)
    except tc.ExtractError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    s = res["summary"]
    print(f"SUMMARY external={s['similarity_external']:.1%} own={s['similarity_own']:.1%} total={s['similarity_total']:.1%} "
          f"sources={s['sources_matched']}/{s['sources_total']} passages={s['passages']} semantic={s['semantic_candidates']}")
    print(f"Report: {(args.out / 'plagiarism-report.md').resolve()}  (+ .html, .json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
