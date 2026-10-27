# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-docx>=1.1",
# ]
# ///
"""brick_status.py -- inventory and traceability checks of the WHOLE dissertation (specialty 121,
Igor Sikorsky KPI): are the novelty items identical in анотація / вступ / висновки, do the tasks match the
conclusions, do the numbers of the conclusions occur in the chapters, does the list of abbreviations
match the text.

    uv run brick_status.py brick/                       # a directory of part files (*.md, *.docx, *.txt)
    uv run brick_status.py dissertation.md              # one big file, split by ВСТУП / РОЗДІЛ / ВИСНОВКИ ...
    uv run brick_status.py brick/ --novelty novelty.md --md status.md --json status.json

Prints the inventory table, then findings (`ERROR B01 [..] ...`) and
`SUMMARY: E error(s), W warning(s), I info`. Exits 1 on any ERROR, 2 if the input cannot be read.
Rule codes B01-B07 are described in references/rules.md.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brick_common import (  # noqa: E402
    CHARS_PER_PAGE, GRADATION_RE, KNOWN_ABBR, BrickError, Part, Report, enumerate_items, load_parts, normtext,
    novelty_items, number_tokens, quantities, short, split_sentences, words,
)

ABBR_RE = re.compile(r"(?<![\w])([A-ZА-ЯІЇЄҐ][A-ZА-ЯІЇЄҐ0-9]{1,5})(?![\w'’])")
ROMAN_RE = re.compile(r"^[IVXLCDMХІ]+$")
NORM_SHARES = {"аналітика": 10, "власні результати": 58, "обрамлення": 32}
SKIP_FILES = re.compile(r"^(readme|status|\.|~\$)", re.I)


# ---------------------------------------------------------------- novelty units

def nz(text: str) -> str:
    t = normtext(text)
    t = re.sub(r"^[\s\d.)\-–—•*]+", "", t)
    t = re.sub(r"\s+", " ", t).strip().rstrip(".;,: ")
    return t


def novelty_key(text: str) -> str:
    t = normtext(text)
    m = re.search(GRADATION_RE, t)
    if not m:
        return ""
    ws = words(re.sub(r"^\w*", "", t[m.end():]))  # skip the rest of the marker word («удосконал|ено»)
    if re.match(r"(вперше|уперше)", m.group(0)) and ws and re.search(r"(но|ено|ано|ся)$", ws[0]):
        ws = ws[1:]
    return " ".join(ws[:6])  # compared on the first 4 words in check_novelty_consistency


def grad_units(part: Part) -> list[dict]:
    """Novelty sentences of a part: the items of its «наукова новизна» block if there is one, otherwise the
    sentences carrying a gradation marker (annotation, general conclusions, chapter conclusions)."""
    if part.kind in ("vstup", "anotatsiia", "vysnovky"):
        found, items = novelty_items(part)
        if found:
            return [dict(text=it["text"], para=it["para"]) for it in items if re.search(GRADATION_RE, normtext(it["text"]))]
    paras = part.concl_paras() if part.kind == "rozdil" else [p for p in part.paras if p["kind"] in ("body", "list")]
    out = []
    for p in paras:
        if p["kind"] not in ("body", "list"):
            continue
        for s in split_sentences(p["text"]):
            for piece in re.split(r";\s+", s) if len(re.findall(GRADATION_RE, normtext(s))) >= 2 else [s]:
                if re.search(GRADATION_RE, normtext(piece)):
                    out.append(dict(text=piece, para=p["i"]))
    return out


def check_novelty_consistency(places: list[tuple[str, Part | None, list[dict]]], rep: Report):
    seen = set()
    for ia, (la, pa, ua) in enumerate(places):
        for ib, (lb, pb, ub) in enumerate(places):
            if ib <= ia or not ua or not ub:
                continue
            pairs = {}
            for x, a in enumerate(ua):
                best = max(range(len(ub)), key=lambda y: difflib.SequenceMatcher(None, nz(a["text"]), nz(ub[y]["text"])).ratio())
                pairs[(x, best)] = True
            for y, b in enumerate(ub):
                best = max(range(len(ua)), key=lambda x: difflib.SequenceMatcher(None, nz(ua[x]["text"]), nz(b["text"])).ratio())
                pairs[(best, y)] = True
            matched_a, matched_b = set(), set()
            for (x, y) in pairs:
                a, b = ua[x], ub[y]
                r = difflib.SequenceMatcher(None, nz(a["text"]), nz(b["text"])).ratio()
                ka, kb = novelty_key(a["text"]), novelty_key(b["text"])
                same = r >= 0.9 or (len(ka.split()) >= 4 and ka.split()[:4] == kb.split()[:4])
                if not same:
                    continue
                matched_a.add(x)
                matched_b.add(y)
                if r == 1.0 or (la, x, lb, y) in seen:
                    continue
                seen.add((la, x, lb, y))
                loc = f"{la} п.{a['para']} ↔ {lb} п.{b['para']}"
                msg = (f"новизна «{short(a['text'], 60)}» і «{short(b['text'], 60)}»: схожість {r:.2f}")
                if r >= 0.9:
                    rep.add("WARN", "B01", f"{msg} — майже збігається; зробіть формулювання буквально однаковими", loc)
                else:
                    rep.add("ERROR", "B01", f"{msg} — це той самий результат, але формулювання розходяться", loc)
            # items that have no counterpart (only between the three main places)
            main = ("анотація", "вступ", "загальні висновки", "novelty")
            if la.split(" ")[0] in main and lb.split(" ")[0] in main:
                for x, a in enumerate(ua):
                    if x not in matched_a:
                        rep.add("INFO", "B01", f"новизни «{short(a['text'], 70)}» ({la}) не знайдено в «{lb}»", f"{la} п.{a['para']}")
                for y, b in enumerate(ub):
                    if y not in matched_b:
                        rep.add("INFO", "B01", f"новизни «{short(b['text'], 70)}» ({lb}) не знайдено в «{la}»", f"{lb} п.{b['para']}")


# ---------------------------------------------------------------- loading

def gather(path: Path, cpp: int, exclude: set[Path]) -> list[Part]:
    if path.is_dir():
        files = sorted(f for ext in ("*.md", "*.docx", "*.txt") for f in path.glob(ext)
                       if not SKIP_FILES.match(f.name) and f.resolve() not in exclude)
        if not files:
            raise BrickError(f"{path}: у каталозі немає .md/.docx/.txt")
        files.sort(key=lambda f: f.name)
    else:
        files = [path]
    parts: list[Part] = []
    for f in files:
        parts += load_parts(f, cpp=cpp)
    return parts


def sort_key(p: Part):
    order = {"tytul": 0, "anotatsiia": 1, "zmist": 2, "poznachennia": 3, "vstup": 4, "rozdil": 5, "vysnovky": 6,
             "spysok": 7, "dodatky": 8}
    return (order.get(p.kind, 9), p.chapter or 0)


# ---------------------------------------------------------------- checks

def conclusion_items(part: Part) -> list[str]:
    items = [p["text"] for p in part.paras if p["kind"] == "list"]
    if items:
        return items
    return [p["text"] for p in part.paras if p["kind"] == "body" and re.match(r"^\d{1,2}[.)]\s", p["text"])]


def check_status(parts: list[Part], rep: Report, novelty_file: Path | None, cpp: int) -> dict:
    by = lambda k: [p for p in parts if p.kind == k]  # noqa: E731
    anot, vstup, vys = by("anotatsiia"), by("vstup"), by("vysnovky")
    chapters = sorted(by("rozdil"), key=lambda p: p.chapter or 0)
    extra: dict = {}

    # B01 novelty consistency
    places: list[tuple[str, Part | None, list[dict]]] = []
    if novelty_file:
        src = load_parts(novelty_file, kind="vysnovky", cpp=cpp)[0]
        units = [dict(text=p["text"], para=p["i"]) for p in src.paras if p["kind"] == "list" and re.search(GRADATION_RE, normtext(p["text"]))]
        if not units:
            units = grad_units(src)
        places.append(("novelty", src, units))
    for p in anot:
        places.append(("анотація", p, grad_units(p)))
    for p in vstup:
        places.append(("вступ", p, grad_units(p)))
    for p in vys:
        places.append(("загальні висновки", p, grad_units(p)))
    for p in chapters:
        u = grad_units(p)
        if u:
            places.append((f"висновки до розділу {p.chapter}", p, u))
    check_novelty_consistency(places, rep)
    extra["novelty_places"] = {l: len(u) for l, _, u in places}

    # B02 tasks vs conclusions
    if vstup and vys:
        blk = vstup[0].blocks().get("tasks")
        tasks = enumerate_items(blk["units"]) if blk else []
        concl = conclusion_items(vys[0])
        extra["tasks"], extra["conclusion_items"] = len(tasks), len(concl)
        if not tasks or not concl:
            rep.add("INFO", "B02", f"не вдалося порахувати завдання у вступі ({len(tasks)}) або пронумеровані висновки ({len(concl)})", "вступ ↔ висновки")
        elif not (len(tasks) <= len(concl) <= len(tasks) + 2):
            rep.add("WARN", "B02", f"завдань у вступі {len(tasks)}, пунктів у загальних висновках {len(concl)} "
                    f"(очікується {len(tasks)}…{len(tasks) + 2}: за кожним завданням, плюс «мету досягнуто» і практична цінність)", "вступ ↔ висновки")

    # B03 chapters without conclusions
    for p in chapters:
        if not p.concl_index:
            rep.add("WARN", "B03", "у розділі немає «Висновки до розділу»", p.label)

    # B04 page budget and shares
    real = [p for p in parts if p.kind not in ("zmist", "tytul")]
    total = sum(p.pages(cpp) for p in real) or 1
    shares = {"аналітика": sum(p.pages(cpp) for p in chapters if p.chapter == 1),
              "власні результати": sum(p.pages(cpp) for p in chapters if (p.chapter or 0) >= 2)}
    shares["обрамлення"] = total - shares["аналітика"] - shares["власні результати"]
    extra["shares"] = {k: round(100 * v / total, 1) for k, v in shares.items()}
    extra["total_pages"] = round(total, 1)
    rep.add("INFO", "B04", f"усього ≈{total:.0f} стор.; частки: " + "; ".join(
        f"{k} {extra['shares'][k]:.0f} % (норма ≈{NORM_SHARES[k]} %)" for k in NORM_SHARES), "обсяг")

    # B05 numbers of the general conclusions absent from the chapters
    if vys and chapters:
        body = set()
        for p in chapters:
            body |= number_tokens(p.body_text(p.main_paras()))
        miss: dict[str, int] = {}
        for p in vys[0].concl_paras():
            for tok, val in quantities(p["text"]):
                if val not in body and tok not in miss:
                    miss[tok] = p["i"]
        if miss:
            rep.add("WARN", "B05", "числа з одиницями у загальних висновках, яких немає в жодному розділі: "
                    + ", ".join(f"«{t}»" for t in list(miss)[:10]), vys[0].loc(min(miss.values())))

    # B06 references
    sp = by("spysok")
    if sp:
        entries = [p["text"] for p in sp[0].paras if p["kind"] == "list"]
        if not entries:
            entries = [p["text"] for p in sp[0].paras if p["kind"] == "body"]
        latin = 0
        for e in entries:
            letters = [c for c in e if c.isalpha()]
            if letters and sum(1 for c in letters if c.isascii()) / len(letters) > 0.5:
                latin += 1
        doi = sum(len(re.findall(r"10\.\d{4,9}/\S+", e)) for e in entries)
        extra["references"] = dict(count=len(entries), latin=latin, doi=doi)
        n = len(entries)
        note = " (корпус КПІ: зазвичай 100–160)" if n < 100 else ""
        rep.add("INFO", "B06", f"джерел: {n}{note}; латиницею {latin} ({100 * latin / max(n, 1):.0f} %); з DOI {doi}", sp[0].label)
    else:
        rep.add("INFO", "B06", "частину «Список використаних джерел» не знайдено", "джерела")

    # B07 abbreviations vs the list of symbols
    listed: dict[str, str] = {}
    for p in by("poznachennia"):
        txt = " ".join(x["text"] for x in p.paras if x["kind"] != "heading")
        for m in re.finditer(r"(?<![\w])([A-ZА-ЯІЇЄҐ][\w/+.-]{0,14})\s+[–—-]\s", txt):
            tok = m.group(1).rstrip(".")
            if sum(c.isupper() for c in tok) >= 2 or any(c.isdigit() for c in tok):
                listed[tok] = tok
    used: Counter = Counter()
    text_parts = [p for p in parts if p.kind in ("anotatsiia", "vstup", "rozdil", "vysnovky")]
    for p in text_parts:
        for q in p.paras:
            if q["kind"] in ("body", "list", "caption_fig", "caption_tab"):
                for m in ABBR_RE.finditer(q["text"]):
                    used[m.group(1)] += 1
    if listed:
        unused = [a for a in listed if used.get(a, 0) == 0 and not any(re.search(r"(?<![\w])" + re.escape(a) + r"(?![\w])", q["text"]) for p in text_parts for q in p.paras)]
        if unused:
            rep.add("WARN", "B07", "абревіатури з переліку позначень, яких немає в тексті: " + ", ".join(unused[:30]), "перелік позначень")
    absent = [(a, c) for a, c in used.most_common()
              if c >= 3 and a not in listed and a.upper() not in KNOWN_ABBR and not ROMAN_RE.match(a)]
    if absent:
        where = "перелік позначень" if listed else "перелік відсутній"
        rep.add("WARN", "B07", ("абревіатури ≥ 3 разів, яких немає в «Переліку умовних позначень»: " if listed else
                                "«Переліку умовних позначень» немає, а абревіатури вжито ≥ 3 разів: ")
                + ", ".join(f"{a} ×{c}" for a, c in absent[:30]), where)
    extra["abbreviations"] = dict(listed=sorted(listed), used_ge3=[a for a, c in used.items() if c >= 3 and a.upper() not in KNOWN_ABBR])
    return extra


# ---------------------------------------------------------------- output

def inventory_rows(parts: list[Part]) -> list[dict]:
    rows = []
    for p in parts:
        s = p.stats()
        rows.append(dict(part=p.name, kind=p.kind or "?", label=p.label, headings=s["headings"], pages=s["pages"],
                         figures=s["figures"], tables=s["tables"], formulas=s["formulas"], citations=s["citations"],
                         conclusions="так" if s["has_conclusions"] else "ні"))
    return rows


def inventory_text(rows: list[dict]) -> str:
    hdr = ["частина", "вид", "заголовків", "стор.", "рис.", "табл.", "формул", "посилань", "висновки"]
    data = [[r["part"], r["label"], r["headings"], r["pages"], r["figures"], r["tables"], r["formulas"], r["citations"], r["conclusions"]] for r in rows]
    w = [max(len(str(x)) for x in col) for col in zip(hdr, *data)]
    line = lambda row: "  ".join(str(x).ljust(w[i]) for i, x in enumerate(row))  # noqa: E731
    return "\n".join([line(hdr)] + [line(r) for r in data])


def inventory_md(rows: list[dict], rep: Report, extra: dict) -> str:
    out = ["# Статус дисертації", "", "## Інвентар", "",
           "| Частина | Вид | Заголовків | Стор. | Рис. | Табл. | Формул | Посилань | Висновки |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['part']} | {r['label']} | {r['headings']} | {r['pages']} | {r['figures']} | {r['tables']} | {r['formulas']} | {r['citations']} | {r['conclusions']} |")
    if "shares" in extra:
        out += ["", "## Частки обсягу (B04)", "", "| Блок | Фактично, % | Норма, % |", "|---|---|---|"]
        out += [f"| {k} | {extra['shares'][k]} | ≈{NORM_SHARES[k]} |" for k in NORM_SHARES]
        out.append(f"\nУсього ≈{extra['total_pages']} стор.")
    out += ["", "## Знахідки", ""]
    order = {s: i for i, s in enumerate(Report.SEV)}
    for it in sorted(rep.items, key=lambda x: (order[x["severity"]], x["code"])):
        out.append(f"1. **{it['severity']} {it['code']}** [{it['location']}] {it['message']}")
    c = rep.counts()
    out += ["", f"**{rep.summary_line()}**", ""]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", type=Path, help="каталог із файлами частин (*.md/*.docx/*.txt) або один великий файл")
    ap.add_argument("--novelty", type=Path, help="novelty.md — єдине джерело формулювань новизни (за наявності)")
    ap.add_argument("--md", type=Path, help="записати Markdown-звіт")
    ap.add_argument("--json", type=Path, help="записати інвентар і знахідки в JSON")
    ap.add_argument("--chars-per-page", type=int, default=CHARS_PER_PAGE, help=f"знаків із пробілами на сторінку (default {CHARS_PER_PAGE})")
    args = ap.parse_args(argv)

    exclude = {p.resolve() for p in (args.novelty, args.md, args.json) if p}
    try:
        if not args.path.exists():
            raise BrickError(f"{args.path}: не знайдено")
        parts = gather(args.path, args.chars_per_page, exclude)
        parts.sort(key=sort_key)
        rep = Report()
        extra = check_status(parts, rep, args.novelty, args.chars_per_page)
    except BrickError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    rows = inventory_rows(parts)
    print("INVENTORY:")
    print(inventory_text(rows))
    print()
    rep.print_lines()
    print("\n" + rep.summary_line())
    if args.md:
        args.md.parent.mkdir(parents=True, exist_ok=True)
        args.md.write_text(inventory_md(rows, rep, extra), encoding="utf-8")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps({"inventory": rows, "details": extra, "findings": rep.items,
                                         "summary": rep.counts()}, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if rep.counts()["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main())
