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
"""Look for the document's sentences on the open web and in open-access repositories, download what
the searches return, and run the local matcher against that collected corpus.

    uv run check_web.py thesis.docx --out plag-check [--queries 40] [--engines ddgs,core,openalex]
                        [--max-pages 80] [--delay 2] [--own my-papers/] [--dry-run]

Free sources used (no account, no payment):
  ddgs      scrapes public result pages of DuckDuckGo/Bing/Google/Brave/Yandex (MIT library). Unofficial,
            rate-limited, sometimes returns nothing; exact-phrase queries work on some backends only.
  core      api.core.ac.uk v3: ~300 M open-access papers with full text; anonymous use is throttled
            (~5 requests / 10 s). CORE_API_KEY env var (free registration) lifts it.
  openalex  api.openalex.org works search (title/abstract/full-text n-grams); returns abstracts only.
            Set OPENALEX_API_KEY (free) or OPENALEX_MAILTO for the polite pool.

What this cannot do: search Unicheck's/Turnitin's private indexes (other students' theses, the Ukrainian
university database, paywalled journals). Expect to find public web pages, open-access papers and
repositories (institutional DSpace, arXiv, CORE) - and nothing else. --dry-run prints the queries only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

import text_common as tc
from check_local import run_check

UA = "kpi-skills-plagiarism-check/0.1 (+https://github.com/; academic self-check)"
SKIP_HOSTS = ("facebook.com", "twitter.com", "x.com", "instagram.com", "youtube.com", "tiktok.com", "linkedin.com",
              "pinterest.", "amazon.", "google.com/search", "bing.com/search", "duckduckgo.com")


def pick_queries(doc: tc.Document, n: int, phrase_words: int = 9) -> list[dict]:
    """Evenly spaced, distinctive sentences from the body; each becomes an exact-phrase query."""
    cands = []
    for p in doc.paragraphs:
        if p.kind not in ("body", "appendix"):
            continue
        for s in tc.sentences(p.text):
            ws = tc.words(s)
            if not (phrase_words + 2 <= len(ws) <= 60):
                continue
            if sum(1 for w in ws if re.search(r"\d", w)) > len(ws) * 0.25:
                continue
            if "[formula]" in s:
                continue
            # Distinctiveness: average word length and share of long words (content words).
            score = sum(len(w) for w in ws) / len(ws) + sum(1 for w in ws if len(w) > 7) / len(ws)
            cands.append({"paragraph": p.index, "sentence": s, "score": score, "words": ws})
    if not cands:
        return []
    # Keep the more distinctive half, then sample evenly across the document.
    cands.sort(key=lambda c: -c["score"])
    keep = cands[: max(n, len(cands) // 2)]
    keep.sort(key=lambda c: c["paragraph"])
    step = max(1, len(keep) / n)
    picked = [keep[int(i * step)] for i in range(min(n, len(keep)))]
    out = []
    for c in picked:
        ws = c["words"]
        start = max(0, (len(ws) - phrase_words) // 2)
        phrase = " ".join(ws[start:start + phrase_words])
        phrase = re.sub(r"[\"«»“”]", "", phrase)
        out.append({"paragraph": c["paragraph"], "sentence": c["sentence"], "phrase": phrase})
    return out


# ----------------------------------------------------------------------------- search backends

def search_ddgs(phrase: str, region: str, max_results: int = 5) -> list[dict]:
    """Exact phrase on the rotating backends first; then the plain phrase on Yandex (the backend that answered
    Ukrainian queries in tests), then plain on auto. "No results found" is an empty answer, not an error."""
    from ddgs import DDGS
    variants = [(f'"{phrase}"', "auto"), (phrase, "yandex"), (phrase, "auto")]
    last_err = None
    for q, backend in variants:
        try:
            res = DDGS(timeout=12).text(q, max_results=max_results, backend=backend, region=region)
        except Exception as exc:  # DDGSException, timeouts, ratelimits
            msg = str(exc)
            if "No results" in msg:
                continue
            last_err = f"{type(exc).__name__}: {msg[:120]}"
            continue
        hits = [{"url": r.get("href"), "title": r.get("title"), "snippet": r.get("body"), "variant": backend} for r in res if r.get("href")]
        if hits:
            return hits
    return [{"error": last_err}] if last_err else []


def search_core(phrase: str, max_results: int = 5) -> list[dict]:
    headers = {"User-Agent": UA}
    key = os.environ.get("CORE_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"
    try:
        # CORE answers HTTP 500 to quoted phrases (any language, tested 2026-10); the plain phrase is ranked by
        # relevance, so a copied passage still comes first.
        r = requests.get("https://api.core.ac.uk/v3/search/works/", params={"q": phrase, "limit": max_results},
                         headers=headers, timeout=30)
        if r.status_code == 429:
            return [{"error": "CORE rate limit (429); increase --delay or set CORE_API_KEY"}]
        r.raise_for_status()
        data = r.json()
    except Exception as exc:
        return [{"error": f"CORE {type(exc).__name__}: {str(exc)[:120]}"}]
    out = []
    for w in data.get("results", []):
        text = w.get("fullText") or w.get("abstract") or ""
        url = w.get("downloadUrl") or (w.get("sourceFulltextUrls") or [None])[0] or f"https://core.ac.uk/works/{w.get('id')}"
        out.append({"url": url, "title": w.get("title"), "text": text, "core_id": w.get("id"),
                    "doi": w.get("doi"), "year": w.get("yearPublished")})
    return out


def search_openalex(phrase: str, max_results: int = 5) -> list[dict]:
    params = {"search": f'"{phrase}"', "per-page": max_results, "select": "id,doi,title,abstract_inverted_index,primary_location"}
    if os.environ.get("OPENALEX_API_KEY"):
        params["api_key"] = os.environ["OPENALEX_API_KEY"]
    elif os.environ.get("OPENALEX_MAILTO"):
        params["mailto"] = os.environ["OPENALEX_MAILTO"]
    try:
        r = requests.get("https://api.openalex.org/works", params=params, headers={"User-Agent": UA}, timeout=30)
        if r.status_code == 429:
            return [{"error": "OpenAlex daily limit (429); set OPENALEX_API_KEY or wait"}]
        r.raise_for_status()
        data = r.json()
    except Exception as exc:
        return [{"error": f"OpenAlex {type(exc).__name__}: {str(exc)[:120]}"}]
    out = []
    for w in data.get("results", []):
        inv = w.get("abstract_inverted_index") or {}
        positions = sorted((pos, word) for word, poss in inv.items() for pos in poss)
        abstract = " ".join(word for _, word in positions)
        loc = (w.get("primary_location") or {})
        url = loc.get("landing_page_url") or w.get("doi") or w.get("id")
        out.append({"url": url, "title": w.get("title"), "text": abstract, "doi": w.get("doi")})
    return out


# ----------------------------------------------------------------------------- fetching

def fetch_page(url: str, max_bytes: int = 15_000_000) -> tuple[str, str]:
    """Return (text, kind) for a URL: HTML via trafilatura, PDF via PyMuPDF. Empty text on failure."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=40, stream=True)
        r.raise_for_status()
        ctype = r.headers.get("content-type", "").lower()
        buf = bytearray()
        for chunk in r.iter_content(65536):
            buf.extend(chunk)
            if len(buf) > max_bytes:
                break
        data = bytes(buf)
    except Exception:
        return "", "error"
    if "pdf" in ctype or data[:5] == b"%PDF-":
        try:
            import pymupdf as fitz
            with fitz.open(stream=data, filetype="pdf") as pdf:
                return "\n\n".join(page.get_text() for page in pdf), "pdf"
        except Exception:
            return "", "error"
    try:
        import trafilatura
        text = trafilatura.extract(data, include_comments=False, include_tables=False, favor_recall=True) or ""
    except Exception:
        text = ""
    return text, "html"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", type=Path)
    ap.add_argument("--out", type=Path, default=Path("plag-check"))
    ap.add_argument("--queries", type=int, default=40, help="how many sentences to search for")
    ap.add_argument("--phrase-words", type=int, default=9)
    ap.add_argument("--engines", default="ddgs,core", help="comma list of ddgs,core,openalex")
    ap.add_argument("--region", default="", help="ddgs region, e.g. ua-uk, us-en (default: by language)")
    ap.add_argument("--max-pages", type=int, default=80, help="cap on pages to download")
    ap.add_argument("--delay", type=float, default=2.0, help="seconds between search requests")
    ap.add_argument("--own", type=Path, nargs="*", default=[])
    ap.add_argument("--corpus", type=Path, nargs="*", default=[], help="extra local sources to include in the same report")
    ap.add_argument("--min-words", type=int, default=8)
    ap.add_argument("--semantic", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="print the queries, do not search")
    args = ap.parse_args(argv)

    try:
        doc = tc.extract(args.target)
    except tc.ExtractError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    queries = pick_queries(doc, args.queries, args.phrase_words)
    if not queries:
        print("ERROR: no searchable sentences found in the body", file=sys.stderr)
        return 2
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "queries.json").write_text(json.dumps(queries, ensure_ascii=False, indent=1), encoding="utf-8")
    if args.dry_run:
        for q in queries:
            print(f"¶{q['paragraph']}: \"{q['phrase']}\"")
        print(f"{len(queries)} queries -> {args.out / 'queries.json'} (dry run, nothing searched)")
        return 0

    engines = [e.strip() for e in args.engines.split(",") if e.strip()]
    region = args.region or ("ua-uk" if doc.language == "uk" else "us-en")
    corpus_dir = args.out / "web-corpus"
    corpus_dir.mkdir(exist_ok=True)
    cache_path = args.out / "search-cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    manifest_path = corpus_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    seen_urls = {v["url"] for v in manifest.values()}
    stats = {"queries": len(queries), "searches": 0, "errors": 0, "hits": 0, "pages_saved": 0, "by_engine": {}, "disabled": []}
    streak = {e: 0 for e in engines}

    def save(url: str, title: str | None, text: str, query: dict, engine: str) -> None:
        nonlocal seen_urls
        if not text or len(tc.words(text)) < 50 or url in seen_urls:
            return
        name = f"{len(manifest) + 1:04d}.txt"
        (corpus_dir / name).write_text(text, encoding="utf-8")
        manifest[name] = {"url": url, "title": title or url, "engine": engine, "query_paragraph": query["paragraph"],
                          "phrase": query["phrase"]}
        seen_urls.add(url)
        stats["pages_saved"] += 1

    for qi, q in enumerate(queries, 1):
        for engine in engines:
            if stats["pages_saved"] >= args.max_pages or engine in stats["disabled"]:
                continue
            key = f"{engine}|{q['phrase']}"
            if key in cache:
                results = cache[key]
            else:
                if engine == "ddgs":
                    results = search_ddgs(q["phrase"], region)
                elif engine == "core":
                    results = search_core(q["phrase"])
                elif engine == "openalex":
                    results = search_openalex(q["phrase"])
                else:
                    print(f"unknown engine {engine}", file=sys.stderr)
                    continue
                cache[key] = results
                cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
                time.sleep(args.delay)
            stats["searches"] += 1
            errs = [r for r in results if "error" in r]
            hits = [r for r in results if "url" in r]
            eng = stats["by_engine"].setdefault(engine, {"searches": 0, "errors": 0, "hits": 0})
            eng["searches"] += 1
            if errs:
                stats["errors"] += 1
                eng["errors"] += 1
                streak[engine] += 1
                print(f"[{qi}/{len(queries)}] {engine}: {errs[0]['error']}", file=sys.stderr)
                if streak[engine] >= 6:
                    stats["disabled"].append(engine)
                    print(f"{engine}: 6 consecutive errors (rate-limited or down); disabled for the rest of this run. "
                          f"Rerun later to resume (results are cached).", file=sys.stderr)
            else:
                streak[engine] = 0
            eng["hits"] += len(hits)
            stats["hits"] += len(hits)
            print(f"[{qi}/{len(queries)}] {engine}: {len(hits)} hits for \"{q['phrase'][:60]}\"", file=sys.stderr)
            for r in hits:
                url = r["url"]
                if not url or any(h in url for h in SKIP_HOSTS) or url in seen_urls:
                    continue
                if r.get("text"):
                    save(url, r.get("title"), r["text"], q, engine)
                else:
                    text, _ = fetch_page(url)
                    save(url, r.get("title"), text, q, engine)
        if len(stats["disabled"]) == len(engines) or stats["pages_saved"] >= args.max_pages:
            break
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    (args.out / "search-stats.json").write_text(json.dumps(stats, indent=1), encoding="utf-8")
    print(f"Search phase: {stats['searches']} searches, {stats['errors']} errors, {stats['hits']} hits, "
          f"{len(manifest)} pages in {corpus_dir}", file=sys.stderr)
    if not manifest and not args.corpus:
        print("No pages collected: the search backends returned nothing usable. Nothing to compare against. "
              "Try again later, change --engines, or supply --corpus.", file=sys.stderr)
        return 0
    try:
        res = run_check(args.target, [corpus_dir] + list(args.corpus), args.own, args.out, min_words=args.min_words,
                        semantic=args.semantic, manifest=manifest, mode="web")
    except tc.ExtractError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    s = res["summary"]
    print(f"SUMMARY external={s['similarity_external']:.1%} own={s['similarity_own']:.1%} sources={s['sources_matched']}/{s['sources_total']} "
          f"passages={s['passages']} | searches={stats['searches']} errors={stats['errors']} pages={len(manifest)}")
    print(f"Report: {(args.out / 'plagiarism-report.md').resolve()}  (+ .html, .json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
