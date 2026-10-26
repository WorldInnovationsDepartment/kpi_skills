# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = [
#     "torch>=2.3",
#     "transformers>=4.51",
#     "sentencepiece",
#     "protobuf",
#     "tiktoken",
#     "safetensors",
#     "huggingface_hub",
#     "python-docx>=1.1",
#     "pymupdf>=1.24",
# ]
# ///
"""Score a document for AI-generated text with open, locally run detectors.

    uv run detect_ai.py thesis.docx --out ai-check [--method binoculars|fastdetect|desklib|all]
                        [--size small|medium|large] [--calibration calib.json] [--chunk-words 220]
                        [--include references,quotes,appendix] [--max-chunks N] [--dry-run]

Reads .docx/.pdf/.md/.tex/.txt/.odt, excludes the reference list, quotations, formulas, tables
and captions by default (they are not the candidate's prose), splits the body into ~220-word chunks,
scores every chunk, and writes <out>/ai-report.json and <out>/ai-report.md with per-chunk scores,
the most machine-like passages and an honest caveat block. Exit code: 0 = ran, 2 = input error.

The verdict depends on a threshold. Without --calibration the script uses the published default of
the method (Binoculars: Falcon-7B/English) and says so in the report; for Ukrainian text or any
non-Falcon pair, build a calibration with calibrate.py first. See ../references/methods.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import statistics
import sys
from pathlib import Path

import text_common as tc
from ai_models import DIRECTION, METHODS, PAIRS, build, default_threshold, hf_offline_hint, is_ai


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", type=Path, default=Path("ai-check"))
    ap.add_argument("--method", default="binoculars", help="binoculars (default), fastdetect, desklib, or all")
    ap.add_argument("--size", default="medium", choices=sorted(PAIRS), help="model pair for zero-shot methods")
    ap.add_argument("--observer", help="override observer / scoring model (HF id or local path)")
    ap.add_argument("--performer", help="override performer model (binoculars only)")
    ap.add_argument("--device", default="auto", help="auto|mps|cuda|cpu")
    ap.add_argument("--calibration", type=Path, help="calibration.json from calibrate.py")
    ap.add_argument("--chunk-words", type=int, default=220)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--max-chunks", type=int, default=0, help="score only the first N chunks (0 = all)")
    ap.add_argument("--include", default="", help="comma list of extra kinds to score: references,quotes,appendix,captions")
    ap.add_argument("--top", type=int, default=10, help="how many most-AI-like passages to list")
    ap.add_argument("--dry-run", action="store_true", help="extract and chunk only; no models")
    ap.add_argument("--json-only", action="store_true")
    return ap.parse_args(argv)


def load_calibration(path: Path | None, method: str) -> dict | None:
    if not path:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    entry = data.get(method) if method in data else (data if data.get("method") == method else None)
    return entry


def select_paragraphs(doc: tc.Document, include: set[str]) -> list[tc.Paragraph]:
    kinds = {"body"}
    if "appendix" in include:
        kinds.add("appendix")
    if "quotes" in include:
        kinds.add("quote")
    if "references" in include:
        kinds.add("reference")
    if "captions" in include:
        kinds.add("caption")
    return [p for p in doc.paragraphs if p.kind in kinds]


def summarize(method: str, chunks: list[dict], threshold: float | None) -> dict:
    scores = [c["scores"][method] for c in chunks if not math.isnan(c["scores"][method])]
    weights = [c["tokens"][method] for c in chunks if not math.isnan(c["scores"][method])]
    if not scores:
        return {"chunks": 0}
    wmean = sum(s * w for s, w in zip(scores, weights)) / max(1, sum(weights))
    out = {
        "chunks": len(scores),
        "mean": statistics.fmean(scores),
        "token_weighted_mean": wmean,
        "median": statistics.median(scores),
        "min": min(scores),
        "max": max(scores),
        "direction": "lower = more AI-like" if DIRECTION[method] < 0 else "higher = more AI-like",
    }
    if threshold is not None:
        flagged = [c for c in chunks if not math.isnan(c["scores"][method]) and is_ai(method, c["scores"][method], threshold)]
        out["threshold"] = threshold
        out["flagged_chunks"] = len(flagged)
        out["flagged_fraction"] = len(flagged) / len(scores)
        out["flagged_words"] = sum(c["words"] for c in flagged)
        out["flagged_words_fraction"] = sum(c["words"] for c in flagged) / max(1, sum(c["words"] for c in chunks))
    return out


def md_report(doc: tc.Document, args, chunks: list[dict], methods: list[str], meta: dict) -> str:
    L: list[str] = []
    L.append(f"# AI-text check: {doc.path.name}")
    L.append("")
    L.append(f"Generated {meta['date']} by kpi-skills:ai-text-detector. Language detected: **{doc.language}**. "
             f"Words in file: {doc.words}; scored words (body prose): {sum(c['words'] for c in chunks)}; chunks: {len(chunks)}.")
    L.append("")
    tamper = meta["tampering"]
    if tamper["suspicious"]:
        L.append(f"> **Warning:** {tamper['mixed_script_words']} words mix Latin and Cyrillic letters and "
                 f"{tamper['invisible_characters']} invisible characters were found. KPI's Unicheck instruction "
                 f"forbids such tampering; fix it before any official check. Examples: {', '.join(tamper['mixed_script_examples'][:8])}")
        L.append("")
    L.append("## Verdict per method")
    L.append("")
    L.append("| Method | Models | Threshold (source) | Flagged chunks | Flagged words | Mean score | Median |")
    L.append("|---|---|---|---|---|---|---|")
    for m in methods:
        s = meta["summary"][m]
        th = meta["thresholds"][m]
        if s.get("chunks", 0) == 0:
            L.append(f"| {m} | {', '.join(meta['models'][m])} | - | no scorable text | | | |")
            continue
        th_txt = f"{th['value']:.4f} ({th['source']})" if th["value"] is not None else f"none ({th['source']})"
        flagged = f"{s['flagged_chunks']}/{s['chunks']} ({s['flagged_fraction']:.0%})" if "flagged_chunks" in s else "n/a"
        fw = f"{s['flagged_words']} ({s['flagged_words_fraction']:.0%})" if "flagged_words" in s else "n/a"
        L.append(f"| {m} | {', '.join(meta['models'][m])} | {th_txt} | {flagged} | {fw} | {s['mean']:.4f} | {s['median']:.4f} |")
    L.append("")
    L.append("Reading the numbers: a *flagged* chunk only means the chunk's statistics look more like text sampled "
             "from a language model than like the calibration set of human text. It is evidence, not proof. "
             "Formal academic prose, text translated from another language, heavily edited or template-like "
             "sections (methods, definitions, standard phrases) score *more* machine-like than conversational text. "
             "A document-level share under about 10-20 % of flagged words is normal for human writing with these "
             "detectors; a cluster of consecutive flagged chunks is the pattern worth looking at.")
    L.append("")
    for m in methods:
        if meta["summary"][m].get("chunks", 0) == 0:
            continue
        th = meta["thresholds"][m]["value"]
        key = (lambda c: c["scores"][m]) if DIRECTION[m] < 0 else (lambda c: -c["scores"][m])
        ranked = sorted((c for c in chunks if not math.isnan(c["scores"][m])), key=key)
        L.append(f"## Most machine-like passages ({m})")
        L.append("")
        for c in ranked[: args.top]:
            flag = "FLAGGED" if th is not None and is_ai(m, c["scores"][m], th) else "below threshold" if th is not None else ""
            snippet = c["text"][:400].replace("\n", " ")
            L.append(f"- **chunk {c['id']}** (paragraphs {c['paragraphs'][0]}-{c['paragraphs'][-1]}, {c['words']} words) "
                     f"score {c['scores'][m]:.4f} {flag}")
            L.append(f"  > {snippet}{'…' if len(c['text']) > 400 else ''}")
        L.append("")
    L.append("## All chunks")
    L.append("")
    L.append("| # | Paragraphs | Words | " + " | ".join(methods) + " | First words |")
    L.append("|---|---|---|" + "---|" * len(methods) + "---|")
    for c in chunks:
        cells = []
        for m in methods:
            s = c["scores"][m]
            th = meta["thresholds"][m]["value"]
            mark = " ⚑" if th is not None and not math.isnan(s) and is_ai(m, s, th) else ""
            cells.append("nan" if math.isnan(s) else f"{s:.4f}{mark}")
        first = " ".join(c["text"].split()[:8])
        L.append(f"| {c['id']} | {c['paragraphs'][0]}-{c['paragraphs'][-1]} | {c['words']} | " + " | ".join(cells) + f" | {first}… |")
    L.append("")
    L.append("## Caveats (read before acting on this)")
    L.append("")
    L.append("1. **No detector is reliable enough to accuse anyone.** Independent evaluations (RAID, ACL 2024; "
             "Mozilla Foundation 2024; the 2025 study of Ukrainian academic texts) show every detector, paid or free, "
             "has false positives on human text and misses edited or paraphrased AI text.")
    L.append("2. **Language.** Only the zero-shot methods (binoculars, fastdetect) see Ukrainian at all; desklib is "
             "English-only. The Qwen3 pairs used here cover Ukrainian, but nobody has published their accuracy on "
             "Ukrainian academic prose; the default Binoculars threshold comes from Falcon-7B on English. "
             "Treat an uncalibrated verdict as a ranking of passages, not a classification.")
    L.append("3. **Calibrate.** Run `calibrate.py` with texts you know are human (your pre-2022 papers) and texts you "
             "know are AI (generate them on the same topic) to get a threshold for this model pair and your writing; "
             "the report then says `calibrated`.")
    L.append("4. **What official tools do differently.** Turnitin/Unicheck AI-detection and GPTZero/Originality use "
             "proprietary supervised models with far more training data, and still publish 1-5 % false-positive "
             "rates; they are *not* available here, so this report cannot predict their output.")
    L.append("5. **Score only prose.** References, formulas, tables, captions and quotations are excluded by default "
             "because they are template-like and make everything look machine-written.")
    L.append("")
    L.append(f"Model/device notes: {meta['device']}; {hf_offline_hint()}")
    return "\n".join(L)


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        doc = tc.extract(args.input)
    except tc.ExtractError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    include = {s.strip() for s in args.include.split(",") if s.strip()}
    paras = select_paragraphs(doc, include)
    chunks = tc.chunks_by_words(paras, target_words=args.chunk_words)
    if args.max_chunks:
        chunks = chunks[: args.max_chunks]
    for i, c in enumerate(chunks, 1):
        c["id"] = i
        c["scores"], c["tokens"] = {}, {}
    args.out.mkdir(parents=True, exist_ok=True)
    kinds = {}
    for p in doc.paragraphs:
        kinds[p.kind] = kinds.get(p.kind, 0) + p.words
    if not chunks:
        print("ERROR: no body prose found to score (check the file; use --include to add other parts)", file=sys.stderr)
        return 2
    if args.dry_run:
        (args.out / "chunks.json").write_text(json.dumps({"language": doc.language, "kinds_words": kinds,
                                                          "chunks": chunks}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{doc.path.name}: language={doc.language}, words by kind={kinds}, chunks={len(chunks)} -> {args.out / 'chunks.json'}")
        return 0

    methods = list(METHODS) if args.method == "all" else [m.strip() for m in args.method.split(",")]
    for m in methods:
        if m not in METHODS:
            print(f"ERROR: unknown method {m}", file=sys.stderr)
            return 2
    if "desklib" in methods and doc.language not in ("en", "unknown"):
        print(f"WARNING: desklib is English-only; the document looks like '{doc.language}'. Its scores are meaningless here.",
              file=sys.stderr)

    meta = {"date": dt.date.today().isoformat(), "input": str(doc.path), "language": doc.language, "kinds_words": kinds,
            "tampering": tc.tampering_report(doc.text), "models": {}, "thresholds": {}, "summary": {}, "device": ""}
    for m in methods:
        scorer = build(m, size=args.size, observer=args.observer, performer=args.performer, device=args.device)
        meta["models"][m] = scorer.models()
        meta["device"] = getattr(scorer, "device", "")
        calib = load_calibration(args.calibration, m)
        if calib and calib.get("models") and sorted(calib["models"]) != sorted(scorer.models()):
            print(f"WARNING: calibration for {m} was made with {calib['models']}, not {scorer.models()}; ignoring it.",
                  file=sys.stderr)
            calib = None
        if calib:
            th, src = calib["threshold"], f"calibrated {calib.get('date', '')}, target FPR {calib.get('target_fpr', '?')}"
        else:
            th, src = default_threshold(m)
        meta["thresholds"][m] = {"value": th, "source": src}
        t0 = __import__("time").time()
        for c in chunks:
            r = scorer.score(c["text"], max_tokens=args.max_tokens)
            c["scores"][m], c["tokens"][m] = r.score, r.tokens
            print(f"[{m}] chunk {c['id']}/{len(chunks)} score={r.score:.4f} tokens={r.tokens}", file=sys.stderr)
        print(f"[{m}] scored {len(chunks)} chunks in {__import__('time').time() - t0:.0f}s", file=sys.stderr)
        meta["summary"][m] = summarize(m, chunks, th)
        del scorer

    (args.out / "ai-report.json").write_text(json.dumps({"meta": meta, "chunks": chunks}, ensure_ascii=False, indent=1),
                                             encoding="utf-8")
    if not args.json_only:
        (args.out / "ai-report.md").write_text(md_report(doc, args, chunks, methods, meta), encoding="utf-8")
    for m in methods:
        s = meta["summary"][m]
        if "flagged_chunks" in s:
            print(f"SUMMARY {m}: {s['flagged_chunks']}/{s['chunks']} chunks flagged ({s['flagged_words_fraction']:.0%} of words), "
                  f"threshold {meta['thresholds'][m]['value']:.4f} [{meta['thresholds'][m]['source']}]")
        else:
            print(f"SUMMARY {m}: {s.get('chunks', 0)} chunks, mean {s.get('mean', float('nan')):.4f} (no threshold)")
    print(f"Report: {(args.out / 'ai-report.md').resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
