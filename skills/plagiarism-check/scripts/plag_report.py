"""Report writers for the plagiarism-check skill: JSON, Markdown and an HTML page with the target text
highlighted per source (Unicheck-style). Imported by check_local.py and check_web.py."""
from __future__ import annotations

import datetime as dt
import html
import json
from collections import defaultdict
from pathlib import Path

import text_common as tc
from match_engine import Run, SourceDoc, Token, span_text

COLORS = ["#ffd54f", "#81d4fa", "#a5d6a7", "#f48fb1", "#ce93d8", "#ffab91", "#80cbc4", "#bcaaa4", "#e6ee9c", "#90caf9"]
OWN_COLOR = "#e0e0e0"


def build_result(target: tc.Document, tokens: list[Token], runs: list[Run], cov: dict, sources: dict[int, SourceDoc],
                 semantic: list[dict], settings: dict) -> dict:
    per_src = []
    for sid, share in sorted(cov["per_source"].items(), key=lambda kv: -kv[1]):
        s = sources[sid]
        s_runs = [r for r in runs if r.source == sid]
        per_src.append({"id": sid, "name": s.name, "own": s.own, "url": s.url, "title": s.title, "path": s.path,
                        "similarity": share, "words_matched": sum(r.length for r in s_runs), "passages": len(s_runs),
                        "longest_passage": max((r.length for r in s_runs), default=0), "source_words": s.words})
    passages = []
    for r in sorted(runs, key=lambda r: r.t_start):
        s = sources[r.source]
        passages.append({"source": r.source, "source_name": s.name, "own": s.own, "kind": r.kind, "words": r.length,
                         "target_paragraph": tokens[r.t_start].para, "target_text": span_text(tokens, target, r.t_start, r.t_end),
                         "source_paragraph": s.tokens[r.s_start].para if r.s_start < len(s.tokens) else None,
                         "source_text": span_text(s.tokens, s.doc, r.s_start, r.s_end) if s.doc else ""})
    kinds = defaultdict(int)
    for p in target.paragraphs:
        kinds[p.kind] += p.words
    return {
        "meta": {"date": dt.date.today().isoformat(), "target": str(target.path), "language": target.language,
                 "words_total": target.words, "words_by_kind": dict(kinds), "settings": settings,
                 "tampering": tc.tampering_report(target.text), "notes": target.notes},
        "summary": {"matchable_words": cov["matchable_words"], "similarity_total": cov["similarity_total"],
                    "similarity_external": cov["similarity_external"], "similarity_own": cov["similarity_own"],
                    "originality_external": 1 - cov["similarity_external"], "sources_matched": len(per_src),
                    "sources_total": len(sources), "passages": len(runs), "semantic_candidates": len(semantic)},
        "sources": per_src, "passages": passages, "semantic": semantic,
    }


def write_json(result: dict, out: Path) -> Path:
    p = out / "plagiarism-report.json"
    p.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def write_markdown(result: dict, out: Path, mode: str) -> Path:
    m, s = result["meta"], result["summary"]
    L = [f"# Plagiarism check ({mode}): {Path(m['target']).name}", "",
         f"Generated {m['date']} by kpi-skills:plagiarism-check. Language: **{m['language']}**. Words: {m['words_total']} "
         f"(matchable prose: {s['matchable_words']}; excluded by kind: "
         + ", ".join(f"{k} {v}" for k, v in m["words_by_kind"].items() if k not in ("body", "appendix", "heading", "caption")) + ").", ""]
    if m["tampering"]["suspicious"]:
        L += [f"> **Warning:** {m['tampering']['mixed_script_words']} mixed-script words / {m['tampering']['invisible_characters']} "
              f"invisible characters: the KPI Unicheck instruction forbids this; fix before the official check.", ""]
    L += ["## Summary", "",
          "| Metric | Value |", "|---|---|",
          f"| Similarity to **external** sources | **{s['similarity_external']:.1%}** |",
          f"| Similarity to the candidate's **own** publications | {s['similarity_own']:.1%} |",
          f"| Similarity, any source | {s['similarity_total']:.1%} |",
          f"| Originality (external) | {s['originality_external']:.1%} |",
          f"| Sources matched / checked | {s['sources_matched']} / {s['sources_total']} |",
          f"| Matched passages (>= {m['settings'].get('min_words')} words) | {s['passages']} |",
          f"| Paraphrase candidates (semantic) | {s['semantic_candidates']} |", ""]
    L += ["These percentages are computed only over the prose that was checked, against only the sources that were "
          "available to this run. They are **not** the number Unicheck/Turnitin will show: those systems match against "
          "indexes (other theses, paywalled journals, the whole web) this skill does not have. A 0 % here does not mean "
          "0 % there; a passage flagged here will almost certainly be flagged there too.", ""]
    if result["sources"]:
        L += ["## Sources", "", "| # | Source | Own? | Similarity | Passages | Longest (words) |", "|---|---|---|---|---|---|"]
        for src in result["sources"]:
            name = f"[{src['title'] or src['name']}]({src['url']})" if src.get("url") else src["name"]
            L.append(f"| {src['id']} | {name} | {'yes' if src['own'] else ''} | {src['similarity']:.1%} | {src['passages']} | {src['longest_passage']} |")
        L.append("")
    if result["passages"]:
        L += ["## Matched passages (in document order)", ""]
        for p in result["passages"]:
            tag = "own" if p["own"] else "EXTERNAL"
            L.append(f"- **¶{p['target_paragraph']}** · {p['words']} words · {p['kind']} · source {p['source']} ({p['source_name']}, {tag})")
            L.append(f"  > {p['target_text'][:500]}{'…' if len(p['target_text']) > 500 else ''}")
            if p["source_text"] and p["kind"] != "verbatim":
                L.append(f"  > *source:* {p['source_text'][:300]}{'…' if len(p['source_text']) > 300 else ''}")
        L.append("")
    if result["semantic"]:
        L += ["## Paraphrase candidates (semantic similarity, review manually)", ""]
        for c in result["semantic"]:
            L.append(f"- ¶{c['target_paragraph']} ↔ source {c['source']} ¶{c['source_paragraph']} (cosine {c['cosine']})")
            L.append(f"  > {c['target_sentence'][:300]}")
            L.append(f"  > *source:* {c['source_sentence'][:300]}")
        L.append("")
    L += ["## What to do with this", "",
          "1. Every EXTERNAL passage needs either a citation with quotation marks (verbatim) or a rewrite in your own words "
          "plus a citation of the idea; a bare citation does not cover a verbatim copy.",
          "2. Passages from your OWN publications are allowed in a dissertation when the publication is cited and listed "
          "among the works on the topic; mention them explicitly in the request for the official check so the "
          "operator can exclude them.",
          "3. Standard phrases (definitions, method names, regulatory wording) match everywhere; judge them, do not just "
          "rewrite them into worse Ukrainian.",
          "4. Rerun after edits. Then book the official Unicheck check through the department/library: this report is a "
          "rehearsal, not a certificate.", ""]
    if m["notes"]:
        L += ["Notes: " + " ".join(m["notes"]), ""]
    p = out / "plagiarism-report.md"
    p.write_text("\n".join(L), encoding="utf-8")
    return p


def write_html(target: tc.Document, tokens: list[Token], runs: list[Run], sources: dict[int, SourceDoc], result: dict,
               out: Path) -> Path:
    # Build per-paragraph highlight spans (char offsets) from runs.
    spans: dict[int, list[tuple[int, int, int, str]]] = defaultdict(list)   # para -> (start, end, sid, kind)
    for r in runs:
        for i in range(r.t_start, min(r.t_end, len(tokens))):
            t = tokens[i]
            lst = spans[t.para]
            if lst and lst[-1][2] == r.source and lst[-1][1] >= t.start - 3:
                lst[-1] = (lst[-1][0], t.end, r.source, r.kind)
            else:
                lst.append((t.start, t.end, r.source, r.kind))
    color_of = {}
    ext_ids = [s["id"] for s in result["sources"] if not s["own"]]
    for n, sid in enumerate(ext_ids):
        color_of[sid] = COLORS[n % len(COLORS)]
    for s in result["sources"]:
        if s["own"]:
            color_of[s["id"]] = OWN_COLOR
    s = result["summary"]
    H = ["<!doctype html><html><head><meta charset='utf-8'><title>Plagiarism check: " + html.escape(Path(result["meta"]["target"]).name) + "</title>",
         "<style>body{font-family:Georgia,serif;max-width:900px;margin:2em auto;padding:0 1em;line-height:1.5}"
         ".p{margin:0 0 .8em}.k{color:#888;font-size:.8em;margin-right:.4em}.excl{color:#999}"
         "mark{padding:0 .1em;border-radius:2px}mark.near{outline:1px dashed #555}table{border-collapse:collapse}"
         "td,th{border:1px solid #ccc;padding:.2em .5em;font-size:.9em}.legend span{display:inline-block;padding:.1em .4em;margin:.1em}</style></head><body>",
         f"<h1>Plagiarism check: {html.escape(Path(result['meta']['target']).name)}</h1>",
         f"<p>External similarity <b>{s['similarity_external']:.1%}</b>, own publications {s['similarity_own']:.1%}, "
         f"any source {s['similarity_total']:.1%} of {s['matchable_words']} matchable words. Dashed outline = near-verbatim. "
         f"Grey text = excluded from matching (references, quotes, formulas, tables).</p>", "<div class='legend'>"]
    for src in result["sources"]:
        label = html.escape(src["title"] or src["name"])
        if src.get("url"):
            label = f"<a href='{html.escape(src['url'])}'>{label}</a>"
        H.append(f"<span style='background:{color_of[src['id']]}'>#{src['id']} {label} {src['similarity']:.1%}{' (own)' if src['own'] else ''}</span>")
    H.append("</div><hr>")
    for p in target.paragraphs:
        text = p.text
        if p.kind in ("reference", "quote", "formula", "code", "table", "front"):
            H.append(f"<p class='p excl'><span class='k'>¶{p.index} {p.kind}</span>{html.escape(text)}</p>")
            continue
        pieces, pos = [], 0
        for st, en, sid, kind in sorted(spans.get(p.index, [])):
            if st < pos:
                continue
            pieces.append(html.escape(text[pos:st]))
            cls = " class='near'" if kind != "verbatim" else ""
            pieces.append(f"<mark style='background:{color_of.get(sid, '#eee')}' title='source #{sid}: {html.escape(sources[sid].name)}'{cls}>"
                          f"{html.escape(text[st:en])}</mark>")
            pos = en
        pieces.append(html.escape(text[pos:]))
        tag = "h3" if p.kind == "heading" else "p"
        H.append(f"<{tag} class='p'><span class='k'>¶{p.index}</span>{''.join(pieces)}</{tag}>")
    if result["semantic"]:
        H.append("<hr><h2>Paraphrase candidates</h2><table><tr><th>Target ¶</th><th>Target sentence</th><th>Source</th><th>Source sentence</th><th>cos</th></tr>")
        for c in result["semantic"]:
            H.append(f"<tr><td>{c['target_paragraph']}</td><td>{html.escape(c['target_sentence'])}</td><td>#{c['source']} ¶{c['source_paragraph']}</td>"
                     f"<td>{html.escape(c['source_sentence'])}</td><td>{c['cosine']}</td></tr>")
        H.append("</table>")
    H.append("</body></html>")
    p = out / "plagiarism-report.html"
    p.write_text("\n".join(H), encoding="utf-8")
    return p
