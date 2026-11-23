# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1"]
# ///
"""Check how AI terms were translated EN -> UA against the Mintsyfra AI-terms dictionary.

Dictionary: «Словник термінів у сфері штучного інтелекту 2.0», Міністерство цифрової
трансформації України, 2026 (references/dictionary.json, rebuilt by build_dictionary.py).

Every finding carries `basis`:
  mintsyfra  — the recommended form is taken from the dictionary;
  other      — NOT based on the Mintsyfra dictionary (this skill's own style rules and
               heuristics); reports must say so.

Usage:
  uv run check_terms.py translation.docx                      # UA text only
  uv run check_terms.py translation.docx --source source.docx # EN source + UA translation
  uv run check_terms.py uk.md --source en.md --json out.json --md out.md

Inputs: .txt, .md, .docx, .pdf (pdf needs poppler's pdftotext). If source and translation
have the same number of paragraphs, the EN->UA check runs paragraph by paragraph and
reports locations; otherwise it compares whole documents and says so.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
REF = HERE.parent / "references"

UA_LETTERS = "а-щьюяґєії’"
# Ukrainian inflectional endings, longest first (a light stemmer: enough to match
# «моделі», «моделями», «навчених», not a morphological analyser).
ENDINGS = sorted("""
ями ами ові еві ого ому ими іми ною ною ній ної ним них ні ну на не ий ій ою ею ам ям ах ях ом ем
ів їв ей ую юю ая яя ої єї им ім их іх і и а я у ю о е ь й є ї
""".split(), key=len, reverse=True)
SHORT_WORD = 3

# Entries the dictionary keeps apart although translators often swap them:
# EN term of key -> its UA form must not be replaced by the UA form of value.
CONFUSABLE = {114: 124, 124: 114, 2: 3, 3: 2, 99: 100, 136: 137, 137: 136}

# EN terms that are also everyday English words: a miss is only a question, not an error.
GENERIC_EN = {
    "support", "security", "input", "output", "risk", "model", "agent", "parameter", "compute",
    "temperature", "seed", "sandbox", "token", "metadata", "completeness", "reliability",
    "transparency", "fairness", "accuracy", "precision", "recall", "sensitivity", "validation",
    "orchestration", "regression", "classification", "clustering", "ensemble", "benchmark",
    "alignment", "opacity", "discrimination", "scraping", "robotics", "measurability",
    "resilience", "robustness", "truthfulness", "groundedness", "autonomy", "adaptiveness",
    "observability", "controllability", "explainability", "auditability", "traceability",
    "reproducibility", "replicability", "prompt", "transformer", "chatbot",
}


# Entries whose dictionary synonyms are everyday words (вхід/вхідні дані, оцінювання/перевірка):
# mixing them is normal prose, not inconsistent terminology.
EVERYDAY_SYNONYMS = {28, 29, 95}


def norm(text: str) -> str:
    text = text.replace("'", "’").replace("ʼ", "’").replace("`", "’")
    text = re.sub(r"[‐‑‒–—](?=\w)", "-", text)
    return text.lower()


def stem(word: str) -> str:
    if len(word) <= SHORT_WORD or not re.fullmatch(f"[{UA_LETTERS}-]+", word):
        return word
    for e in ENDINGS:
        if word.endswith(e) and len(word) - len(e) >= max(3, len(word) - 4):
            return word[: -len(e)]
    return word


def ua_regex(phrase: str) -> re.Pattern:
    parts = []
    for w in re.split(r"[\s]+", norm(phrase).strip()):
        sub = []
        for piece in w.split("-"):
            s = stem(piece)
            if s == piece and len(piece) <= SHORT_WORD:
                sub.append(re.escape(piece))
            else:
                # closed-syllable і alternates with о/е in other forms: вихід/виходи, ріст/росту
                k = s.rfind("і", max(0, len(s) - 3))
                body = (re.escape(s[:k]) + "[іое]" + re.escape(s[k + 1:])) if k > 0 else re.escape(s)
                sub.append(body + f"[{UA_LETTERS}]{{0,4}}")
        parts.append(r"[\s-]?".join(sub) if len(sub) > 1 else sub[0])
    return re.compile(r"(?<![\w’])" + r"[\s,]+".join(parts) + r"(?![\w’])")


def en_regex(phrase: str) -> re.Pattern:
    words = re.split(r"[\s-]+", phrase.strip().lower())
    body = r"[\s-]+".join(re.escape(w) for w in words)
    return re.compile(r"(?<![\w-])" + body + r"(?:s|es)?(?![\w-])", re.I)


def abbr_regex(abbr: str) -> re.Pattern:
    return re.compile(r"(?<![\w-])" + re.escape(abbr) + r"s?(?![\w-])")


# ----------------------------------------------------------------------------- input
def read_text(path: Path) -> list[str]:
    suf = path.suffix.lower()
    if suf == ".docx":
        from docx import Document

        doc = Document(str(path))
        paras = [p.text for p in doc.paragraphs]
        for t in doc.tables:
            for row in t.rows:
                for cell in row.cells:
                    paras.extend(p.text for p in cell.paragraphs)
        return [p.strip() for p in paras if p.strip()]
    if suf == ".pdf":
        raw = subprocess.run(["pdftotext", "-layout", str(path), "-"], check=True,
                             capture_output=True, text=True).stdout
    else:
        raw = path.read_text(encoding="utf-8")
    return [re.sub(r"\s*\n\s*", " ", p).strip() for p in re.split(r"\n\s*\n", raw) if p.strip()]


# ----------------------------------------------------------------------------- model
@dataclass
class Finding:
    code: str
    severity: str          # ERROR / WARN / INFO
    basis: str             # mintsyfra / other
    message: str
    entry: int | None = None
    recommended: str = ""
    found: str = ""
    location: str = ""
    context: str = ""


@dataclass
class Entry:
    n: int
    uk: str
    en: str
    uk_variants: list[str]
    uk_abbr: list[str]
    en_variants: list[str]
    en_abbr: list[str]
    note: str = ""
    definition: str = ""
    uk_re: list[re.Pattern] = field(default_factory=list)
    en_re: list[re.Pattern] = field(default_factory=list)

    @property
    def primary(self) -> str:
        return self.uk_variants[0] if self.uk_variants else self.uk.lower()

    @property
    def display(self) -> str:
        return f"№{self.n} {self.uk} — {self.en}"


def load_dictionary(path: Path) -> list[Entry]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for e in data["entries"]:
        ent = Entry(n=e["n"], uk=e["uk"], en=e["en"], uk_variants=e["uk_variants"],
                    uk_abbr=e["uk_abbr"], en_variants=e["en_variants"], en_abbr=e["en_abbr"],
                    note=e.get("note", ""), definition=e.get("definition", ""))
        ent.uk_re = [ua_regex(v) for v in ent.uk_variants]
        ent.uk_re += [re.compile(r"(?<![\w’])" + re.escape(a) + r"(?![\w’])") for a in ent.uk_abbr]
        ent.en_re = [en_regex(v) for v in ent.en_variants] + [abbr_regex(a) for a in ent.en_abbr]
        out.append(ent)
    return out


def mostly_latin(para: str) -> bool:
    """English quotations, reference-list entries, code: not the translation's own prose."""
    cyr = len(re.findall(f"[{UA_LETTERS}]", para.lower()))
    lat = len(re.findall(r"[a-z]", para.lower()))
    return lat > cyr


def in_parens(text: str, start: int) -> bool:
    return re.search(r"\([^()]*$", text[max(0, start - 120): start]) is not None


def codeish(text: str, start: int, end: int) -> bool:
    """Identifiers, file names, URLs, `code`: part of a token with _ . / ` or digits."""
    a, b = text[max(0, start - 1): start], text[end: end + 1]
    return bool(re.match(r"[_./`\\\d]", a or " ") or re.match(r"[_./`\\\d(]", b or " "))


def group(findings: list[Finding]) -> list[Finding]:
    """One finding per (code, entry, found form); locations listed, count in the message."""
    out: dict[tuple, Finding] = {}
    locs: dict[tuple, list[str]] = {}
    for f in findings:
        k = (f.code, f.entry, f.found.lower())
        if k not in out:
            out[k], locs[k] = f, []
        if f.location not in locs[k]:
            locs[k].append(f.location)
    res = []
    for k, f in out.items():
        ls = locs[k]
        if len(ls) > 1:
            f.message += f" Трапляється в {len(ls)} абзацах."
            f.location = ", ".join(ls[:6]) + (" …" if len(ls) > 6 else "")
        res.append(f)
    return res


def snippet(text: str, start: int, end: int, width: int = 60) -> str:
    a, b = max(0, start - width), min(len(text), end + width)
    return ("…" if a else "") + text[a:b].replace("\n", " ") + ("…" if b < len(text) else "")


# ----------------------------------------------------------------------------- checks
def ua_hits(ent: Entry, text_n: str) -> list[tuple[int, re.Match]]:
    """(variant index, match). Index 0 = primary term; >=1 = synonym listed by the dictionary."""
    hits = []
    for i, rx in enumerate(ent.uk_re):
        hits += [(i, m) for m in rx.finditer(text_n)]
    return hits


def check_translation(paras: list[str], entries: list[Entry], variants: list[dict],
                      style: list[dict]) -> tuple[list[Finding], dict]:
    findings: list[Finding] = []
    by_n = {e.n: e for e in entries}
    usage: dict[int, dict[str, int]] = {}
    latin_en = []
    for e in entries:
        for v in e.en_variants:
            latin_en.append((e, en_regex(v), v))
        for a in e.en_abbr:
            latin_en.append((e, abbr_regex(a), a))

    for pi, para in enumerate(paras, start=1):
        loc = f"абз. {pi}"
        t = norm(para)
        latin_para = mostly_latin(para)
        # dictionary inventory + secondary synonyms
        for e in entries:
            for idx, m in ua_hits(e, t):
                form = e.uk_variants[idx] if idx < len(e.uk_variants) else e.uk_abbr[idx - len(e.uk_variants)]
                usage.setdefault(e.n, {}).setdefault(form, 0)
                usage[e.n][form] += 1
        # known non-dictionary variants
        for v in variants:
            for m in re.finditer(v["pattern"], t):
                e = by_n[v["entry"]]
                rec = v.get("recommend", e.primary)
                findings.append(Finding(
                    "M2", "INFO" if v.get("caution") else "WARN", "mintsyfra",
                    f"Нетиповий для словника відповідник. Словник Мінцифри рекомендує «{rec}» ({e.en})."
                    + (f" {v['caution']}" if v.get("caution") else ""),
                    e.n, rec, m.group(0), loc, snippet(para, m.start(), m.end())))
        # English dictionary terms left in Latin script (longest match wins)
        taken: list[tuple[int, int]] = []
        for e, rx, form in sorted(latin_en, key=lambda x: -len(x[2])):
            for m in rx.finditer(para):
                if any(a < m.end() and m.start() < b for a, b in taken):
                    continue
                taken.append((m.start(), m.end()))
                if (latin_para or in_parens(para, m.start()) or codeish(para, m.start(), m.end())
                        or mostly_latin(para[max(0, m.start() - 60): m.end() + 60])):
                    continue  # English quote or title / gloss in brackets / identifier
                before = t[max(0, m.start() - 90): m.start()]
                if re.search(r"\([^()]*$", before) and any(r.search(before) for r in e.uk_re):
                    continue  # «велика мовна модель (LLM)» — UA term with EN gloss: fine
                if form.isupper() and e.uk_abbr:
                    rec = f"{e.uk_abbr[0].upper()} ({e.primary})"
                else:
                    rec = e.primary
                findings.append(Finding(
                    "M3", "WARN", "mintsyfra",
                    f"Англомовний термін у латиниці в українському тексті. Словник Мінцифри: «{rec}».",
                    e.n, rec, m.group(0), loc, snippet(para, m.start(), m.end())))
        # style rules (not Mintsyfra)
        for r in style:
            for m in re.finditer(r["pattern"], t):
                findings.append(Finding(
                    r["id"], "INFO", "other",
                    f"Поза словником Мінцифри: {r['note']} Пропозиція: «{r['suggest']}».",
                    None, r["suggest"], m.group(0), loc, snippet(para, m.start(), m.end())))

    # secondary synonyms and mixed usage across the document
    for n, forms in sorted(usage.items()):
        e = by_n[n]
        used = {f: c for f, c in forms.items() if c}
        secondary = {f: c for f, c in used.items() if f != e.primary}
        if secondary and e.primary not in used:
            findings.append(Finding(
                "M4", "INFO", "mintsyfra",
                f"Вжито лише синонім, який словник подає в дужках / через скісну. Основний термін словника — «{e.primary}».",
                n, e.primary, ", ".join(f"{f}×{c}" for f, c in secondary.items()), "весь текст"))
        if len(used) > 1 and n not in EVERYDAY_SYNONYMS and not (set(used) <= set(e.uk_abbr) | {e.primary}):
            findings.append(Finding(
                "M5", "INFO", "mintsyfra",
                f"Для одного поняття словника вжито кілька форм: {', '.join(f'«{f}»×{c}' for f, c in used.items())}. "
                f"Перевірте послідовність (основна форма словника — «{e.primary}»).",
                n, e.primary, ", ".join(used), "весь текст"))
    return findings, usage


def check_pair(src: list[str], tgt: list[str], entries: list[Entry],
               variants: list[dict] | None = None) -> tuple[list[Finding], bool]:
    """EN source term -> expected UA dictionary term in the corresponding translation part."""
    aligned = len(src) == len(tgt) and len(src) > 1
    pairs = list(zip(src, tgt)) if aligned else [(" ".join(src), " ".join(tgt))]
    findings = []
    longest_first = sorted(entries, key=lambda e: -max((len(v) for v in e.en_variants), default=0))
    for pi, (en, uk) in enumerate(pairs, start=1):
        loc = f"абз. {pi}" if aligned else "весь текст"
        uk_n = norm(uk)
        claimed: list[tuple[int, int]] = []
        seen: dict[int, tuple[int, re.Match]] = {}
        for e in longest_first:
            for rx in e.en_re:
                for m in rx.finditer(en):
                    if any(a <= m.start() < b or a < m.end() <= b for a, b in claimed):
                        continue
                    claimed.append((m.start(), m.end()))
                    seen.setdefault(e.n, (0, m))
                    seen[e.n] = (seen[e.n][0] + 1, seen[e.n][1])
        by_n = {e.n: e for e in entries}
        # «Alignment» maps to two dictionary entries: either satisfies.
        twins = {136: [137], 137: [136]}
        for n, (count, m) in sorted(seen.items()):
            e = by_n[n]
            cand = [e] + [by_n[t] for t in twins.get(n, [])]
            hits = [h for c in cand for h in ua_hits(c, uk_n)]
            src_form = m.group(0)
            ctx = snippet(en, m.start(), m.end())
            base = src_form.lower()
            generic = base in GENERIC_EN or re.sub(r"e?s$", "", base) in GENERIC_EN
            if not hits:
                vs = [v for v in (variants or []) if v["entry"] in [c.n for c in cand]
                      and re.search(v["pattern"], uk_n)]
                alt = sorted({m2.group(0) for v in vs for m2 in re.finditer(v["pattern"], uk_n)})
                twin = by_n.get(CONFUSABLE.get(n, -1))
                if twin and n not in (136, 137) and ua_hits(twin, uk_n):
                    wrong = sorted({h.group(0) for _, h in ua_hits(twin, uk_n)})
                    findings.append(Finding(
                        "P4", "WARN", "mintsyfra",
                        f"«{src_form}» перекладено як «{', '.join(wrong)}» — це відповідник іншого терміна словника "
                        f"(№{twin.n} {twin.en}). Для {e.en} словник рекомендує «{e.primary}» (№{n}).",
                        n, e.primary, ", ".join(wrong), loc, ctx))
                    continue
                left = sorted({m2.group(0) for c in cand for rx in c.en_re for m2 in rx.finditer(uk)})
                if left:
                    findings.append(Finding(
                        "P1", "WARN", "mintsyfra",
                        f"«{src_form}» залишено англійською («{', '.join(left)}»). Словник Мінцифри: «{e.primary}».",
                        n, e.primary, ", ".join(left), loc, ctx))
                    continue
                if alt:
                    caution = " ".join(v["caution"] for v in vs if v.get("caution"))
                    findings.append(Finding(
                        "P1", "INFO" if caution else "WARN", "mintsyfra",
                        f"«{src_form}» перекладено як «{', '.join(alt)}» — цієї форми немає у словнику. "
                        f"Словник Мінцифри рекомендує «{e.primary}»." + (f" {caution}" if caution else ""),
                        n, e.primary, ", ".join(alt), loc, ctx))
                    continue
                findings.append(Finding(
                    "P1", "INFO" if generic else ("WARN" if " " not in src_form else "ERROR"), "mintsyfra",
                    (f"У джерелі «{src_form}» (×{count}), у перекладі немає рекомендованого словником відповідника «{e.primary}»"
                     + (f" або синонімів ({', '.join(e.uk_variants[1:])})" if len(e.uk_variants) > 1 else "")
                     + (". Слово загальновживане — перевірте, чи воно тут терміном." if generic else ".")
                     + (f" {e.note}" if e.note else "")),
                    n, e.primary, src_form, loc, ctx))
                continue
            if all(i > 0 for i, _ in hits) and len(cand) == 1:
                findings.append(Finding(
                    "P2", "INFO", "mintsyfra",
                    f"«{src_form}» перекладено синонімом зі словника; основний термін — «{e.primary}».",
                    n, e.primary, ", ".join(sorted({h.group(0) for _, h in hits})), loc, ctx))
            if n == 132 and not any(i == 1 for i, _ in hits):
                findings.append(Finding(
                    "P3", "WARN", "mintsyfra",
                    "Precision у словнику — «точність (прецизійність)»; без уточнення її легко сплутати з Accuracy (№131, «точність»).",
                    n, "точність (прецизійність)", "точність", loc, ctx))
            if n == 99 and not any(i == 1 for i, _ in hits) and by_n[100].en_re[0].search(en) is None:
                findings.append(Finding(
                    "P3", "INFO", "mintsyfra",
                    "Recall у словнику — «повнота (чутливість)»; «повнота» без уточнення збігається з Completeness (№100).",
                    n, "повнота (чутливість)", "повнота", loc, ctx))
    return findings, aligned


def latin_leftovers(paras: list[str], entries: list[Entry]) -> list[Finding]:
    """Lower-case English words in UA text that the dictionary does not cover (not Mintsyfra)."""
    known = set()
    for e in entries:
        for v in e.en_variants:
            known.update(re.split(r"[\s-]+", v.lower()))
    out = []
    for pi, para in enumerate(paras, start=1):
        if not re.search(f"[{UA_LETTERS}]", para.lower()) or mostly_latin(para):
            continue
        for m in re.finditer(r"(?<![\w./@#-])[a-z][a-z-]{3,}(?![\w./@(-])", para):
            w = m.group(0)
            if w in known or "http" in w or in_parens(para, m.start()) or codeish(para, m.start(), m.end()):
                continue
            out.append(Finding(
                "X1", "INFO", "other",
                "Поза словником Мінцифри: англійське слово в українському тексті, якого немає у словнику. "
                "Перекладіть або дайте український відповідник з англійським у дужках.",
                None, "", w, f"абз. {pi}", snippet(para, m.start(), m.end())))
    return out


# ----------------------------------------------------------------------------- report
SEV_ORDER = {"ERROR": 0, "WARN": 1, "INFO": 2}


def write_md(path: Path, meta: dict, findings: list[Finding], usage: dict, entries: list[Entry]) -> None:
    by_n = {e.n: e for e in entries}
    L = [f"# Перевірка перекладу ШІ-термінів: {meta['translation']}", ""]
    L += [f"Словник: {meta['dictionary']}, {meta['dictionary_entries']} термінів. "
          f"Сторінка Мінцифри: {meta.get('dictionary_page') or '—'}; PDF: {meta['dictionary_url']}", ""]
    if meta.get("source"):
        L += [f"Джерело (EN): {meta['source']}; режим: "
              + ("по абзацах" if meta["aligned"] else "весь документ (кількість абзаців різна)"), ""]
    ms = [f for f in findings if f.basis == "mintsyfra"]
    ot = [f for f in findings if f.basis == "other"]
    L += ["## Частина 1. На основі словника Мінцифри", ""]
    L += _table(ms, by_n)
    L += ["", "### Терміни словника, вжиті в перекладі", ""]
    if usage:
        L += ["| № | Термін словника | Вжиті форми |", "|---|---|---|"]
        for n, forms in sorted(usage.items()):
            L.append(f"| {n} | {by_n[n].uk} | " + ", ".join(f"{f}×{c}" for f, c in forms.items()) + " |")
    else:
        L.append("Не знайдено.")
    L += ["", "## Частина 2. Поза словником Мінцифри", "",
          "> Зауваження цієї частини **не базуються на словнику Міністерства цифрової трансформації**: "
          "це власні правила стилю та евристики skill-а. Вони мають рекомендаційний характер.", ""]
    L += _table(ot, by_n)
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def _table(fs: list[Finding], by_n: dict) -> list[str]:
    if not fs:
        return ["Зауважень немає."]
    rows = ["| # | Код | Рівень | Де | Знайдено | Рекомендовано | Пояснення | Контекст |",
            "|---|---|---|---|---|---|---|---|"]
    for i, f in enumerate(sorted(fs, key=lambda f: (SEV_ORDER[f.severity], f.code, f.location)), 1):
        rec = f.recommended + (f" (№{f.entry})" if f.entry else "")
        cells = [str(i), f.code, f.severity, f.location, f.found, rec, f.message, f.context]
        rows.append("| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("translation", type=Path, help="Ukrainian text (.txt/.md/.docx/.pdf)")
    ap.add_argument("--source", type=Path, help="English source text (optional)")
    ap.add_argument("--dictionary", type=Path, default=REF / "dictionary.json")
    ap.add_argument("--json", type=Path, help="write findings as JSON")
    ap.add_argument("--md", type=Path, help="write a Markdown report")
    ap.add_argument("--no-style", action="store_true", help="skip the non-Mintsyfra style rules")
    ap.add_argument("--latin-words", action="store_true",
                    help="also list every lower-case English word left in UA prose (non-Mintsyfra, noisy)")
    a = ap.parse_args()

    dict_meta = json.loads(a.dictionary.read_text(encoding="utf-8"))
    entries = load_dictionary(a.dictionary)
    variants = json.loads((REF / "known_variants.json").read_text(encoding="utf-8"))["variants"]
    style = [] if a.no_style else json.loads((REF / "style_rules.json").read_text(encoding="utf-8"))["rules"]

    tgt = read_text(a.translation)
    findings, usage = check_translation(tgt, entries, variants, style)
    aligned = None
    if a.source:
        pf, aligned = check_pair(read_text(a.source), tgt, entries, variants)
        # the paired finding already says it with the source context: drop the UA-only twin
        paired = {(f.entry, f.location) for f in pf if f.code == "P1"}
        findings = pf + [f for f in findings
                         if not (f.code in ("M2", "M3") and (f.entry, f.location) in paired)]
    if a.latin_words:
        findings += latin_leftovers(tgt, entries)
    findings = group(findings)

    meta = {
        "translation": str(a.translation), "source": str(a.source) if a.source else None,
        "aligned": aligned, "dictionary": dict_meta["source"], "dictionary_url": dict_meta["url"], "dictionary_page": dict_meta.get("page_url"),
        "dictionary_entries": dict_meta["count"],
    }
    counts = {s: sum(f.severity == s for f in findings) for s in SEV_ORDER}
    by_basis = {b: sum(f.basis == b for f in findings) for b in ("mintsyfra", "other")}
    if a.json:
        a.json.write_text(json.dumps({"meta": meta, "counts": counts, "by_basis": by_basis,
                                      "usage": {str(k): v for k, v in usage.items()},
                                      "findings": [asdict(f) for f in findings]},
                                     ensure_ascii=False, indent=1), encoding="utf-8")
    if a.md:
        write_md(a.md, meta, findings, usage, entries)
    for f in sorted(findings, key=lambda f: (f.basis != "mintsyfra", SEV_ORDER[f.severity])):
        tag = "Мінцифра" if f.basis == "mintsyfra" else "поза словником"
        print(f"{f.severity:5} {f.code} [{tag}] {f.location}: «{f.found}» → {f.recommended or '—'}")
    if a.source and not aligned:
        print("NOTE: paragraph counts differ — EN->UA check ran on whole documents (no locations).")
    print(f"SUMMARY errors={counts['ERROR']} warnings={counts['WARN']} info={counts['INFO']} "
          f"mintsyfra={by_basis['mintsyfra']} other={by_basis['other']} dictionary_terms_used={len(usage)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
