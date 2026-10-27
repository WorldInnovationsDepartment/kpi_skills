"""Text-reuse matching engine for the plagiarism-check skill (imported by check_local.py / check_web.py).

Method (the same family of techniques Unicheck/Turnitin/MOSS use, without their indexes):
  1. normalise text (case, apostrophes, quotes, Latin/Cyrillic homoglyphs, invisible chars);
  2. tokenise into words and hash every k-word shingle (k = 5 by default);
  3. index the corpus shingles; look every target shingle up;
  4. chain hits that lie on the same diagonal (target pos - source pos) into runs, tolerating small gaps
     so that a substituted word or a dropped article does not break a copied passage ("near-verbatim");
  5. keep runs of at least --min-words words, merge overlapping runs per source, and report
     similarity = share of the target's matchable words covered by at least one run.
Optionally (--semantic) sentence embeddings (intfloat/multilingual-e5-small, MIT) flag sentences
whose meaning is nearly identical to a corpus sentence although the words differ (paraphrase).

Everything is exact and deterministic except the semantic pass. Quotations, the reference list,
formulas, tables and captions are excluded from the matchable text by default, like a checker
operator would do, and can be included with flags.
"""
from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import text_common as tc

DEFAULT_K = 5
DEFAULT_MIN_WORDS = 8
DEFAULT_GAP = 4           # tolerated missing shingles inside a run (1 substituted word kills k shingles)
MATCH_KINDS = {"body", "appendix", "heading", "caption"}   # what is matchable by default


@dataclass
class Token:
    norm: str
    para: int
    start: int
    end: int


@dataclass
class SourceDoc:
    id: int
    name: str
    path: str
    own: bool = False
    url: str | None = None
    title: str | None = None
    tokens: list[Token] = field(default_factory=list)
    doc: tc.Document | None = None

    @property
    def words(self) -> int:
        return len(self.tokens)


@dataclass
class Run:
    source: int
    t_start: int      # inclusive token index in target
    t_end: int        # exclusive
    s_start: int
    s_end: int
    kind: str = "verbatim"   # verbatim | near-verbatim | paraphrase

    @property
    def length(self) -> int:
        return self.t_end - self.t_start


def shingle_hash(words: list[str]) -> int:
    return int.from_bytes(hashlib.blake2b(" ".join(words).encode("utf-8"), digest_size=8).digest(), "big")


def tokenize(doc: tc.Document, kinds: set[str] = MATCH_KINDS, include_quotes: bool = False,
             include_references: bool = False) -> list[Token]:
    """Tokens of the paragraphs whose kind is matchable; quotes/references on request."""
    kinds = set(kinds)
    if include_quotes:
        kinds.add("quote")
    if include_references:
        kinds.add("reference")
    out: list[Token] = []
    for p in doc.paragraphs:
        if p.kind not in kinds:
            continue
        for w, s, e in tc.word_spans(p.text):
            n = tc.normalize(w)
            if not n or n.isdigit() and len(n) < 2:
                continue
            if "[formula]" in w or "[code]" in w:
                continue
            out.append(Token(n, p.index, s, e))
    return out


def shingles(tokens: list[Token], k: int) -> list[int]:
    words = [t.norm for t in tokens]
    return [shingle_hash(words[i:i + k]) for i in range(0, max(0, len(words) - k + 1))]


class Index:
    def __init__(self, k: int = DEFAULT_K):
        self.k = k
        self.table: dict[int, list[tuple[int, int]]] = defaultdict(list)
        self.sources: dict[int, SourceDoc] = {}

    def add(self, src: SourceDoc) -> None:
        self.sources[src.id] = src
        for i, h in enumerate(shingles(src.tokens, self.k)):
            self.table[h].append((src.id, i))

    def match(self, target: list[Token], min_words: int = DEFAULT_MIN_WORDS, gap: int = DEFAULT_GAP,
              skip_self_path: str | None = None) -> list[Run]:
        k = self.k
        hits: dict[int, dict[int, list[int]]] = defaultdict(lambda: defaultdict(list))   # src -> diag -> [i]
        for i, h in enumerate(shingles(target, k)):
            for sid, j in self.table.get(h, ()):
                if skip_self_path and self.sources[sid].path == skip_self_path:
                    continue
                hits[sid][j - i].append(i)
        runs: list[Run] = []
        for sid, diags in hits.items():
            for d, positions in diags.items():
                positions.sort()
                start = prev = positions[0]
                exact = True
                for i in positions[1:]:
                    if i - prev <= 1 + k + gap:
                        if i - prev > 1:
                            exact = False
                        prev = i
                    else:
                        runs.append(Run(sid, start, prev + k, start + d, prev + k + d, "verbatim" if exact else "near-verbatim"))
                        start = prev = i
                        exact = True
                runs.append(Run(sid, start, prev + k, start + d, prev + k + d, "verbatim" if exact else "near-verbatim"))
        runs = _merge_per_source(runs, slack=gap + 2)
        return [r for r in runs if r.length >= min_words]


def _merge_per_source(runs: list[Run], slack: int) -> list[Run]:
    """Merge runs of the same source that overlap or nearly touch in the target (different diagonals)."""
    by_src: dict[int, list[Run]] = defaultdict(list)
    for r in runs:
        by_src[r.source].append(r)
    out: list[Run] = []
    for sid, rs in by_src.items():
        rs.sort(key=lambda r: (r.t_start, r.t_end))
        cur = rs[0]
        for r in rs[1:]:
            if r.t_start <= cur.t_end + slack and abs((r.s_start - r.t_start) - (cur.s_start - cur.t_start)) <= slack * 3:
                kind = "verbatim" if cur.kind == r.kind == "verbatim" and r.t_start <= cur.t_end else "near-verbatim"
                cur = Run(sid, cur.t_start, max(cur.t_end, r.t_end), min(cur.s_start, r.s_start), max(cur.s_end, r.s_end), kind)
            else:
                out.append(cur)
                cur = r
        out.append(cur)
    return out


# ----------------------------------------------------------------------------- coverage & stats

def coverage(runs: list[Run], n_tokens: int, sources: dict[int, SourceDoc]) -> dict:
    covered_any = bytearray(n_tokens)
    covered_ext = bytearray(n_tokens)
    covered_own = bytearray(n_tokens)
    per_source: dict[int, bytearray] = {}
    for r in runs:
        mask = per_source.setdefault(r.source, bytearray(n_tokens))
        for i in range(r.t_start, min(r.t_end, n_tokens)):
            covered_any[i] = 1
            mask[i] = 1
            if sources[r.source].own:
                covered_own[i] = 1
            else:
                covered_ext[i] = 1
    n = max(1, n_tokens)
    return {
        "matchable_words": n_tokens,
        "similarity_total": sum(covered_any) / n,
        "similarity_external": sum(covered_ext) / n,
        "similarity_own": sum(covered_own) / n,
        "per_source": {sid: sum(m) / n for sid, m in per_source.items()},
        "covered_mask": covered_any,
    }


def longest_runs(runs: list[Run], top: int = 15) -> list[Run]:
    return sorted(runs, key=lambda r: -r.length)[:top]


def span_text(tokens: list[Token], doc: tc.Document, start: int, end: int) -> str:
    """Original text covered by tokens[start:end] (may span paragraphs)."""
    if start >= end or start >= len(tokens):
        return ""
    end = min(end, len(tokens))
    parts: list[str] = []
    cur_para = tokens[start].para
    seg_start = tokens[start].start
    for i in range(start, end):
        t = tokens[i]
        if t.para != cur_para:
            parts.append(doc.paragraphs[cur_para].text[seg_start:tokens[i - 1].end])
            cur_para, seg_start = t.para, t.start
    parts.append(doc.paragraphs[cur_para].text[seg_start:tokens[end - 1].end])
    return " / ".join(parts)


# ----------------------------------------------------------------------------- semantic (optional)

def semantic_matches(target_doc: tc.Document, target_tokens: list[Token], covered: bytearray, sources: dict[int, SourceDoc],
                     threshold: float = 0.92, min_words: int = 8, model_name: str = "intfloat/multilingual-e5-small",
                     max_source_sentences: int = 60000) -> list[dict]:
    """Sentences of the target whose embedding is within `threshold` cosine of a corpus sentence, and that
    are not already mostly covered by exact matches. Returns dicts, not Runs (no token alignment)."""
    import numpy as np
    from sentence_transformers import SentenceTransformer

    def sent_items(doc: tc.Document, kinds=("body", "appendix")):
        items = []
        for p in doc.paragraphs:
            if p.kind not in kinds:
                continue
            for s in tc.sentences(p.text):
                if len(tc.words(s)) >= min_words:
                    items.append((p.index, s))
        return items

    # Map target sentences to token coverage to skip the ones already matched verbatim.
    para_cov: dict[int, list[int]] = defaultdict(list)
    for i, t in enumerate(target_tokens):
        para_cov[t.para].append(covered[i])
    t_items = []
    for p_idx, s in sent_items(target_doc):
        cov = para_cov.get(p_idx)
        if cov and sum(cov) / len(cov) > 0.6:
            continue
        t_items.append((p_idx, s))
    s_items: list[tuple[int, int, str]] = []
    for sid, src in sources.items():
        if src.doc is None:
            continue
        for p_idx, s in sent_items(src.doc):
            s_items.append((sid, p_idx, s))
        if len(s_items) > max_source_sentences:
            break
    if not t_items or not s_items:
        return []
    model = SentenceTransformer(model_name)
    te = model.encode(["query: " + s for _, s in t_items], normalize_embeddings=True, batch_size=64, show_progress_bar=False)
    se = model.encode(["query: " + s for _, _, s in s_items], normalize_embeddings=True, batch_size=64, show_progress_bar=False)
    sims = np.asarray(te) @ np.asarray(se).T
    out = []
    for ti, (p_idx, s) in enumerate(t_items):
        j = int(sims[ti].argmax())
        score = float(sims[ti, j])
        if score >= threshold:
            sid, sp, ss = s_items[j]
            out.append({"target_paragraph": p_idx, "target_sentence": s, "source": sid, "source_paragraph": sp,
                        "source_sentence": ss, "cosine": round(score, 4)})
    return out


# ----------------------------------------------------------------------------- corpus loading

def load_corpus(dirs: list[Path], own_dirs: list[Path], start_id: int = 1, manifest: dict | None = None,
                skip: Path | None = None) -> list[SourceDoc]:
    """Every supported file under the given directories becomes a SourceDoc. `manifest` (web corpus)
    maps file name -> {url, title}."""
    out: list[SourceDoc] = []
    sid = start_id
    for own, roots in ((False, dirs), (True, own_dirs)):
        for root in roots:
            files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
            for f in files:
                if f.suffix.lower() not in tc.SUPPORTED or f.name.startswith(".") or f.name == "manifest.json":
                    continue
                if skip and f.resolve() == skip.resolve():
                    continue
                try:
                    d = tc.extract(f)
                except tc.ExtractError as exc:
                    print(f"skip {f}: {exc}")
                    continue
                # For sources, everything is matchable (a quotation in a source is still text one can copy).
                toks = tokenize(d, kinds=MATCH_KINDS | {"quote", "front"}, include_references=False)
                meta = (manifest or {}).get(f.name, {})
                out.append(SourceDoc(sid, f.name, str(f), own=own, url=meta.get("url"), title=meta.get("title"),
                                     tokens=toks, doc=d))
                sid += 1
    return out
