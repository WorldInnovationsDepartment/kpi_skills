# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-docx>=1.1",
# ]
# ///
"""check_chapter.py -- automatic checks of ONE part of a dissertation (анотація, вступ, розділ N,
загальні висновки, ...) for specialty 121 «Інженерія програмного забезпечення» at Igor Sikorsky KPI.

    uv run check_chapter.py 01-vstup.md
    uv run check_chapter.py 02-rozdil-2.docx --chapter 2 --json findings.json
    uv run check_chapter.py 04-vysnovky.md --body chapters/        # numbers of the conclusions vs the chapters
    uv run check_chapter.py 02-rozdil-1.md --first-citation-order --max-ref 120

Accepts .md, .txt (e.g. `pdftotext -layout`) and .docx. Prints one line per finding:

    ERROR S01 [розділ 2] ...   a requirement is violated -> fix before submitting
    WARN  F03 [2.3, п.14: «...»] ...   a likely problem / typical reviewer objection
    INFO  L04 ...              facts and reminders for the manual review

then the detected structure and `SUMMARY: E error(s), W warning(s), I info`. Exits 1 if there is any
ERROR, 2 if the input cannot be read, 0 otherwise. A file that holds several top-level parts
(whole dissertation) is split automatically unless --kind/--chapter is given. Every rule code,
severity and its limits are listed in references/rules.md. These are heuristics: the review decides.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brick_common import (  # noqa: E402
    ARCH_RE, BLOCK_LABELS, CHARS_PER_PAGE, DISTINCT_RE, EFFECT_RE, GRADATION_RE, INFINITIVE_RE, KNOWN_ABBR,
    LANG_CHECKS, PLACEHOLDER_CASE_RE, PLACEHOLDER_EXTRA_RE, PLACEHOLDER_RE, RUS_LETTERS, SE_RE, AUTHOR_YEAR_RE,
    BrickError, Part, Report, enumerate_items, load_parts, load_text, normtext, novelty_items, number_tokens,
    quantities, short, split_sentences, words,
)

BUDGETS = {"vstup": (8, 12), "rozdil1": (15, 25), "rozdil": (25, 50), "vysnovky": (2, 5), "anotatsiia": (2, 4)}
NO_TEXT_CHECKS = {"spysok", "dodatky", "poznachennia", "zmist", "tytul"}
MANDATORY = ["relevance", "link", "aim", "tasks", "object", "subject", "methods", "novelty", "practical",
             "personal", "approbation", "publications", "structure"]
CONCL_COMPARATIVE_RE = r"\bкраще\b|\bкраща\b|\bкращі\b|ефективніш\w*|\bшвидш\w*|підвищ\w*|зменш\w*"
FIRST_PERSON_RE = (r"(?<![\w'.-])я(?![\w'.-])|(?<![\w'-])(?:мною|мій|моя|моє|мої|моїх|мого|моєму|вважаю)(?![\w'-])")
ABBR_RE = re.compile(r"(?<![\w])([A-ZА-ЯІЇЄҐ][A-ZА-ЯІЇЄҐ0-9]{1,5})(?![\w'’])")
ROMAN_RE = re.compile(r"^[IVXLCDMХІ]+$")  # incl. Cyrillic Х and І typed instead of Latin


def n_loc(part: Part, para: int | None) -> str:
    return part.loc(para)


def text_paras(part: Part, kinds=("body", "list")):
    return [p for p in part.paras if p["kind"] in kinds]


# ---------------------------------------------------------------- structure

def check_structure(part: Part, rep: Report, args):
    heads = part.headings
    if part.kind == "rozdil":
        concl = [h for h in heads if h["hkind"] == "concl"]
        n = part.chapter
        if not concl:
            rep.add("ERROR", "S01", f"немає підрозділу «Висновки до розділу {n or 'N'}»", part.label)
        else:
            first = concl[0]
            ttl = normtext(first["htitle"] or first["text"])
            if first.get("loose") or "висновки до розділу" not in ttl:
                rep.add("WARN", "S01", f"заголовок висновків має бути «Висновки до розділу {n}», а не «{short(first['htitle'] or first['text'], 50)}»",
                        part.loc(first["i"]))
            elif not re.search(r"\d", ttl):
                rep.add("INFO", "S01", f"у заголовку «{short(first['htitle'] or first['text'], 50)}» немає номера розділу (очікується «Висновки до розділу {n}»)",
                        part.loc(first["i"]))
            elif n and first["hchapter"] != n:
                rep.add("ERROR", "S01", f"«Висновки до розділу {first['hchapter']}» стоять у розділі {n}", part.loc(first["i"]))
            after = [h for h in heads if h["i"] > first["i"] and h["hkind"] not in ("concl",)]
            if after:
                rep.add("ERROR", "S01", f"«Висновки до розділу» не останні в розділі: далі йде заголовок «{short(after[0]['text'], 60)}»",
                        part.loc(after[0]["i"]))
    if part.kind == "rozdil" and part.chapter:
        N = part.chapter
        last: dict[tuple, int] = {}
        seen: set[tuple] = set()
        stack: dict[int, tuple] = {}
        children: dict[tuple, list[dict]] = defaultdict(list)
        for h in heads:
            if h["hkind"] not in ("sub", "concl") or not h["hnum"]:
                continue
            comps = tuple(int(x) for x in h["hnum"].split("."))
            L = len(comps)
            if comps[0] != N:
                rep.add("ERROR", "S02", f"номер {h['hnum']} не починається з номера розділу {N}", part.loc(h["i"]))
                continue
            if comps in seen:
                rep.add("ERROR", "S02", f"номер {h['hnum']} повторюється", part.loc(h["i"]))
                continue
            seen.add(comps)
            parent = comps[:-1]
            if L >= 3 and stack.get(L - 1) != parent:
                cur = ".".join(map(str, stack[L - 1])) if stack.get(L - 1) else "—"
                rep.add("ERROR", "S02", f"{h['hnum']} стоїть не під своїм {'.'.join(map(str, parent))} (поточний заголовок рівня {L - 1}: {cur})",
                        part.loc(h["i"]))
            exp = last.get(parent, 0) + 1
            if comps[-1] != exp:
                rep.add("ERROR", "S02", f"пропуск у нумерації: очікувався {'.'.join(map(str, parent + (exp,)))}, а знайдено {h['hnum']}",
                        part.loc(h["i"]))
            last[parent] = max(last.get(parent, 0), comps[-1])
            stack[L] = comps
            for k in [k for k in stack if k > L]:
                del stack[k]
            children[parent].append(h)
        for parent, hs in children.items():
            if len(hs) == 1:
                rep.add("WARN", "S05", f"у {'.'.join(map(str, parent))} лише один підпункт ({hs[0]['hnum']}); потрібно ≥ 2 або без підпункту",
                        part.loc(hs[0]["i"]))
        if N == 1:
            ok = any(re.search(r"постановк|завдання дослідження|формулюванн", normtext(h["text"])) for h in heads)
            if not ok:
                rep.add("WARN", "S03", "розділ 1 не містить підрозділу з «постановка / завдання дослідження / формулювання» у назві",
                        part.label)
    # page budget
    key = part.kind
    if part.kind == "rozdil":
        key = "rozdil1" if part.chapter == 1 else "rozdil"
    if key in BUDGETS:
        lo, hi = BUDGETS[key]
        pages = part.pages(args.chars_per_page)
        mult = 1
        if part.kind == "anotatsiia":
            mult = max(1, sum(1 for h in heads if h["hkind"] == "anotatsiia"))
        lo, hi = lo * mult, hi * mult
        per = " на мову" if part.kind == "anotatsiia" else ""
        lang = f" ({mult} мов.)" if mult > 1 else ""
        sev = "WARN" if (pages < 0.5 * lo or pages > 2 * hi) else "INFO"
        rep.add(sev, "S04", f"орієнтовно {pages:.1f} стор. (≈{part.chars()} знаків із пробілами / {args.chars_per_page}); "
                f"типовий обсяг{per}: {lo}–{hi} стор.{lang}", part.label)


# ---------------------------------------------------------------- figures, tables, formulas

def first_comp(num: str) -> str:
    return num.split(".")[0]


def check_figures(part: Part, rep: Report, args):
    N = str(part.chapter) if part.chapter else None
    fcaps = Counter(c["num"] for c in part.fig_caps)
    tcaps = Counter(c["num"] for c in part.tab_caps)
    for num, cnt in fcaps.items():
        if cnt > 1:
            rep.add("WARN", "F01", f"підпис «Рисунок {num}» повторюється {cnt} р.", n_loc(part, next(c["para"] for c in part.fig_caps if c["num"] == num)))
    refs_f = {}
    for r in part.fig_refs:
        refs_f.setdefault(r["num"], r["para"])
    refs_t = {}
    for r in part.tab_refs:
        refs_t.setdefault(r["num"], r["para"])
    for num, para in refs_f.items():
        if num not in fcaps and (N is None or first_comp(num) == N or not num[0].isdigit()):
            rep.add("ERROR", "F01", f"на рисунок {num} є посилання, але підпису «Рисунок {num}» немає", n_loc(part, para))
    for c in part.fig_caps:
        if c["num"] not in refs_f:
            rep.add("WARN", "F01", f"підпис «Рисунок {c['num']}» ніде не згадано в тексті (рис. {c['num']})", n_loc(part, c["para"]))
    for num, para in refs_t.items():
        if num not in tcaps and (N is None or first_comp(num) == N or not num[0].isdigit()):
            rep.add("WARN", "F03", f"на таблицю {num} є посилання, але підпису «Таблиця {num}» немає", n_loc(part, para))
    for c in part.tab_caps:
        if c["num"] not in refs_t:
            rep.add("WARN", "F03", f"таблицю {c['num']} ніде не згадано в тексті (табл. {c['num']})", n_loc(part, c["para"]))
    if N:
        bad = [(f"Рисунок {c['num']}", c["para"]) for c in part.fig_caps if c["num"][0].isdigit() and first_comp(c["num"]) != N]
        bad += [(f"Таблиця {c['num']}", c["para"]) for c in part.tab_caps if c["num"][0].isdigit() and first_comp(c["num"]) != N]
        bad += [(f"формула ({f['num']})", f["para"]) for f in part.formulas if first_comp(f["num"]) != N]
        if bad:
            rep.add("ERROR", "F02", f"номер не починається з номера розділу {N}: " + "; ".join(b for b, _ in bad[:6])
                    + (f" (+{len(bad) - 6})" if len(bad) > 6 else ""), n_loc(part, bad[0][1]))
        fs = [f for f in part.formulas if first_comp(f["num"]) == N]
        ks = [int(f["num"].split(".")[-1]) for f in fs]
        if ks and ks != list(range(1, len(ks) + 1)):
            rep.add("WARN", "F04", "номери формул не йдуть підряд з 1: " + ", ".join(f["num"] for f in fs[:12]) + (" …" if len(fs) > 12 else ""), n_loc(part, fs[0]["para"]))
    else:
        ks = [int(f["num"].split(".")[-1]) for f in part.formulas]
        if ks and ks != list(range(1, len(ks) + 1)):
            rep.add("WARN", "F04", "номери формул не йдуть підряд з 1: " + ", ".join(f["num"] for f in part.formulas[:12]),
                    n_loc(part, part.formulas[0]["para"]))
    bad = [c for c in part.fig_caps + part.tab_caps if not c["canonical"]]
    imgs = part.images_no_caption
    if bad or imgs:
        ex = "; ".join(f"«{short(c['text'], 50)}»" for c in bad[:3])
        msg = f"{len(bad)} підпис(ів) не у формі «Рисунок N.M – Назва» / «Таблиця N.M – Назва» (довге тире, без крапки в кінці)"
        if bad:
            msg += f": {ex}"
        if imgs:
            msg += f"; зображень без підпису: {imgs}"
        rep.add("INFO", "F05", msg, n_loc(part, bad[0]["para"]) if bad else part.label)


# ---------------------------------------------------------------- citations

def check_citations(part: Part, rep: Report, args):
    if part.kind in NO_TEXT_CHECKS:
        return
    cits = part.citations
    pages = max(part.pages(args.chars_per_page), 0.01)
    if part.kind == "rozdil" and part.chapter == 1:
        if not cits:
            rep.add("WARN", "C01", "у розділі 1 немає жодного посилання на джерела [N]", part.label)
        elif len(cits) / pages < 1:
            rep.add("WARN", "C01", f"посилань {len(cits)} на ≈{pages:.1f} стор. ({len(cits) / pages:.2f} на сторінку); "
                    "в аналітичному розділі очікується ≥ 1 на сторінку", part.label)
    elif part.kind == "rozdil" and not cits:
        rep.add("INFO", "C01", "у розділі немає жодного посилання [N]", part.label)
    if args.first_citation_order and cits:
        seen, mx, issues = set(), args.ref_start - 1, []
        for c in cits:
            for n in c["nums"]:
                if n in seen:
                    continue
                if n != mx + 1:
                    issues.append((n, mx + 1, c["para"]))
                seen.add(n)
                mx = max(mx, n)
        if issues:
            n, exp, para = issues[0]
            rep.add("WARN", "C02", f"нумерація джерел не за порядком першої згадки: {len(issues)} відхилень, перше — [{n}] замість [{exp}] "
                    f"(усі: {', '.join(f'[{a}]/[{b}]' for a, b, _ in issues[:6])})", n_loc(part, para))
    if args.max_ref:
        over = sorted({n for c in cits for n in c["nums"] if n > args.max_ref})
        if over:
            c = next(c for c in cits if any(n > args.max_ref for n in c["nums"]))
            rep.add("WARN", "C02", f"посилання на джерела за межами списку (≤ {args.max_ref}): {', '.join(map(str, over[:10]))}",
                    n_loc(part, c["para"]))
    if cits and part.fmt_author_year:
        rep.add("INFO", "C03", f"змішані стилі посилань: [n] ({len(cits)}) і (Автор, рік) ({part.fmt_author_year}); оберіть один", part.label)


# ---------------------------------------------------------------- novelty / content

def grad(text: str) -> bool:
    return bool(re.search(GRADATION_RE, normtext(text)))


def check_novelty(part: Part, rep: Report, args):
    k = part.kind
    if k in ("vstup", "anotatsiia", "vysnovky"):
        found, items = novelty_items(part)
        if not found:
            if k == "vstup":
                rep.add("ERROR", "N01", "у вступі немає блоку «Наукова новизна одержаних результатів»", part.label)
            else:
                sents = [s for s in part.sentences if grad(s["text"])]
                if not sents:
                    rep.add("WARN", "N01", "немає блоку новизни й жодного положення з маркером градації (вперше / удосконалено / набуло подальшого розвитку)",
                            part.label)
                items = [dict(text=s["text"], para=s["para"]) for s in sents]
        else:
            if not items:
                rep.add("ERROR", "N01", "блок «Наукова новизна» порожній", n_loc(part, part.blocks()["novelty"]["first_para"]))
            bad = [it for it in items if not grad(it["text"])]
            if bad:
                rep.add("ERROR", "N01", f"{len(bad)} із {len(items)} пунктів новизни без маркера градації "
                        "(вперше / удосконалено / набуло подальшого розвитку): " + "; ".join(f"«{short(b['text'], 60)}»" for b in bad[:3]),
                        n_loc(part, bad[0]["para"]))
        if found and k in ("vstup", "anotatsiia"):
            no_d = [it for it in items if not re.search(DISTINCT_RE, normtext(it["text"]))]
            no_e = [it for it in items if not re.search(EFFECT_RE, normtext(it["text"]))]
            for lst, what in ((no_d, "відмінності від відомого (відрізняється / на відміну від / полягає)"),
                              (no_e, "ефекту (дозволило / забезпечує / підвищує / зменшує)")):
                if lst:
                    rep.add("WARN", "N02", f"у {len(lst)} із {len(items)} пунктів новизни немає {what}: "
                            + "; ".join(f"«{short(x['text'], 50)}»" for x in lst[:3]), n_loc(part, lst[0]["para"]))
        if found and k == "vstup" and items and not any(re.search(ARCH_RE, normtext(it["text"])) for it in items):
            rep.add("WARN", "N09", "жоден пункт новизни не стосується програмної архітектури (практика КПІ 121: один із результатів — архітектура ПЗ)",
                    part.label)
    if k == "rozdil" and part.chapter and part.chapter >= 2:
        if not any(grad(s["text"]) for s in part.sentences):
            rep.add("WARN", "N03", "у розділі немає жодного речення з маркером градації (вперше / удосконалено / набуло розвитку) — абзац-новизна",
                    part.label)
        body = [p for p in part.paras if p["kind"] in ("body", "list")]
        wc = sum(len(words(p["text"])) for p in body)
        hits = len(re.findall(SE_RE, normtext(" ".join(p["text"] for p in body))))
        dens = hits * 1000 / wc if wc else 0
        if wc and dens < 2:
            rep.add("INFO", "N08", f"густина лексики програмної інженерії {dens:.1f} на 1000 слів (< 2): перевірте відповідність 121", part.label)


def check_vstup(part: Part, rep: Report, args):
    if part.kind != "vstup":
        return
    blocks = part.blocks()
    present = set(blocks)
    missing = [BLOCK_LABELS[k] for k in MANDATORY if k not in present]
    if missing:
        rep.add("ERROR", "N04", f"у вступі немає обов'язкових блоків: {'; '.join(missing)}", part.label)
    txt = normtext(part.body_text())
    ov = (len(re.findall(r"\bу\s+(?:першому|другому|третьому|четвертому|п'ятому|шостому|сьомому)\s+розділі", txt))
          + len(re.findall(r"\b(?:перший|другий|третій|четвертий|п'ятий)\s+розділ\s+(?:присвячен|містить|розкрива)", txt))
          + len(re.findall(r"\bу\s+розділі\s+\d", txt)))
    if ov == 0:
        rep.add("WARN", "N04", "немає опису змісту розділів («У першому розділі … У другому розділі …») у блоці «Структура та обсяг»", part.label)
    # N05 object / N06 aim: looked up by sentence, so that «Мета і завдання» in one paragraph still works
    sents = [s for s in part.sentences]
    obj = next((s for s in sents if re.match(r"(?i)\W*об['’ʼ]єкт", s["text"])), None)
    if obj and "процес" not in normtext(obj["text"]):
        rep.add("WARN", "N05", "об'єкт дослідження сформульовано не як процес (немає слова «процес/процеси»): "
                f"«{short(obj['text'], 90)}»", n_loc(part, obj["para"]))
    for s in sents:
        m = re.match(r"(?i)\W*мет(?:а|ою)\b[^.]{0,80}?(?:\bє\b|\bполягає\s+(?:у|в)\b|[—–:-])\s*([«\"]?[\w'’ʼ-]+)", s["text"])
        if m:
            if re.match(INFINITIVE_RE, m.group(1).lower()):
                rep.add("WARN", "N06", f"мета починається з інфінітива «{m.group(1)}»; формулюйте результат іменником "
                        "(підвищення / зменшення / забезпечення / скорочення …)", n_loc(part, s["para"]))
            break
    # N07 tasks
    blk = blocks.get("tasks")
    if blk:
        items = enumerate_items(blk["units"])
        if not items:
            rep.add("INFO", "N07", "не вдалося виділити перелік завдань (нумерований або марковений список)", n_loc(part, blk["first_para"]))
        else:
            bad = [it for it in items if not re.match(INFINITIVE_RE, normtext(it).lstrip("«\"–—- "))]
            if bad:
                rep.add("WARN", "N07", f"{len(bad)} із {len(items)} завдань починаються не з інфінітива (проаналізувати, розробити, "
                        "удосконалити …): " + "; ".join(f"«{short(b, 50)}»" for b in bad[:4]), n_loc(part, blk["first_para"]))


# ---------------------------------------------------------------- evidence

PLACEHOLDERS = [(PLACEHOLDER_RE, re.I), (PLACEHOLDER_EXTRA_RE, re.I), (PLACEHOLDER_CASE_RE, 0)]


def check_evidence(part: Part, rep: Report, args, extra_numbers: set[float]):
    # E03 placeholders (every paragraph)
    found: dict[str, list[int]] = defaultdict(list)
    for p in part.paras:
        for rx, fl in PLACEHOLDERS:
            for m in re.finditer(rx, p["text"], fl):
                found[m.group(0).strip().upper() if m.group(0).isalpha() else m.group(0).strip()].append(p["i"])
    for ph, paras in found.items():
        rep.add("ERROR", "E03", f"заповнювач «{ph}» залишився в тексті ({len(paras)} р.)", n_loc(part, paras[0]))
    # E01 / E02 conclusions
    concl = part.concl_paras()
    if not concl:
        return
    if part.kind == "rozdil":
        body_nums = number_tokens("\n".join(p["text"] for p in part.main_paras())) | extra_numbers
        have_body = True
    else:
        body_nums = extra_numbers
        have_body = bool(extra_numbers)
        if not have_body:
            rep.add("INFO", "E01", "для звірки чисел висновків із текстом передайте розділи через --body (файли або каталог)", part.label)
    if have_body:
        miss: dict[str, int] = {}
        for p in concl:
            for tok, val in quantities(p["text"]):
                if val not in body_nums and tok not in miss:
                    miss[tok] = p["i"]
        if miss:
            first = min(miss.values())
            rep.add("WARN", "E01", "числа з одиницями у висновках, яких немає в тексті: " + ", ".join(f"«{t}»" for t in list(miss)[:8])
                    + (f" (+{len(miss) - 8})" if len(miss) > 8 else ""), n_loc(part, first))
    n = 0
    for p in concl:
        if p["kind"] not in ("body", "list"):
            continue
        for s in split_sentences(p["text"]):
            if re.search(CONCL_COMPARATIVE_RE, normtext(s)) and not re.search(r"\d", s):
                n += 1
                if n <= 5:
                    rep.add("INFO", "E02", f"порівняльне/ефектне твердження без числа: «{short(s, 90)}»", n_loc(part, p["i"]))
    if n > 5:
        rep.add("INFO", "E02", f"… і ще {n - 5} таких тверджень у висновках", part.label)


# ---------------------------------------------------------------- language

def check_language(part: Part, rep: Report, args):
    if part.kind in NO_TEXT_CHECKS:
        return
    sents = part.sentences
    # L01 calques
    for item in LANG_CHECKS:
        pat, sug = item[0], item[1]
        sev = item[2] if len(item) > 2 else "WARN"
        hits = [s for s in sents if re.search(pat, normtext(s["text"]))]
        if hits:
            total = sum(len(re.findall(pat, normtext(s["text"]))) for s in hits)
            rep.add(sev, "L01", f"{sug} — {total} раз(ів)", n_loc(part, hits[0]["para"]))
    # L02 first person
    fp = []
    for s in sents:
        t = normtext(re.sub(r"«[^»]*»|\"[^\"]*\"|“[^”]*”", " ", s["text"]))
        if re.search(FIRST_PERSON_RE, t):
            fp.append(s)
    if fp:
        rep.add("WARN", "L02", f"перша особа однини в {len(fp)} реч.: у дисертації — безособові форми або «автор», «ми»",
                n_loc(part, fp[0]["para"]))
    # L03 abbreviations
    first_seen: dict[str, tuple[int, str, int]] = {}
    counts: Counter = Counter()
    defined: set[str] = set()
    for p in part.paras:
        if p["kind"] not in ("body", "list", "caption_fig", "caption_tab"):
            continue
        t = p["text"]
        if sum(1 for c in t if c.isalpha()) and sum(c.isupper() for c in t if c.isalpha()) / max(1, sum(c.isalpha() for c in t)) > 0.7:
            continue
        for m in ABBR_RE.finditer(t):
            a = m.group(1)
            if a.upper() in KNOWN_ABBR or ROMAN_RE.match(a) or len(a) < 2 or a.isdigit():
                continue
            counts[a] += 1
            if a not in first_seen:
                first_seen[a] = (p["i"], t, m.start())
                before, after = t[max(0, m.start() - 1):m.start()], t[m.end():m.end() + 40]
                if (before == "(" and after.startswith(")")) or re.match(r"\s*\(", after) or re.match(r"\s*[–—-]\s", after):
                    defined.add(a)
    und = [(a, c) for a, c in counts.most_common() if c >= 3 and a not in defined]
    if und:
        rep.add("INFO", "L03", "абревіатури ≥ 3 разів без розшифрування при першому вживанні (додайте до переліку позначень): "
                + ", ".join(f"{a} ×{c}" for a, c in und[:25]) + (f" (+{len(und) - 25})" if len(und) > 25 else ""),
                n_loc(part, first_seen[und[0][0]][0]))
    # L04 long sentences
    longs = [(len(words(s["text"])), s) for s in sents]
    longs = [x for x in longs if x[0] > 60]
    if longs:
        n, s = max(longs, key=lambda x: x[0])
        rep.add("INFO", "L04", f"{len(longs)} реч. довших за 60 слів; найдовше — {n} слів", n_loc(part, s["para"]))
    # L06 Russian letters
    bad: dict[str, int] = {}
    for p in part.paras:
        if p["kind"] in ("table",) and False:
            continue
        for w in re.findall(r"[А-Яа-яІіЇїЄєҐґЫыЭэЪъЁё'’ʼ-]+", p["text"]):
            if any(c in RUS_LETTERS for c in w) and w not in bad:
                bad[w] = p["i"]
    if bad:
        rep.add("ERROR", "L06", "російські літери (ы э ъ ё) в україномовному тексті: " + ", ".join(list(bad)[:12])
                + (f" (+{len(bad) - 12})" if len(bad) > 12 else ""), n_loc(part, min(bad.values())))
    # L07 typography
    typo = [
        ("дефіс замість тире між пробілами « - »", r"[\wа-яіїєґ»)]\s-\s[А-Яа-яІіЇїЄєҐґA-Za-z«(]"),
        ("подвійні пробіли", r"\S  +\S"),
        ("прямі лапки \"…\" замість «…»", r"\"[^\"\n]{1,80}[А-Яа-яІіЇїЄєҐґ][^\"\n]{0,80}\"|“[^”\n]{1,80}”"),
        ("пробіл перед комою/крапкою/двокрапкою", r"[\wа-яіїєґ»)]\s+[,.;:!?](?=\s|$)"),
        ("кома як роздільник тисяч", r"\b\d{1,3}(?:,\d{3}){2,}\b|\b\d{1,3},000\b"),
    ]
    for label, rx in typo:
        if label.startswith("подвійні") and part.fmt == "txt":
            continue
        hit = [(p["i"], re.search(rx, p["text"])) for p in part.paras if p["kind"] in ("body", "list", "caption_fig", "caption_tab")]
        hit = [(i, m) for i, m in hit if m]
        if hit:
            i, m = hit[0]
            rep.add("INFO", "L07", f"типографіка: {label} — {len(hit)} абз.; напр. «{short(m.group(0), 40)}»", n_loc(part, i))


# ---------------------------------------------------------------- driver

def run_checks(part: Part, rep: Report, args, extra_numbers: set[float]):
    if part.kind == "tytul":
        return
    if part.kind is None:
        rep.add("INFO", "S00", "не вдалося визначити вид частини (анотація / вступ / розділ N / висновки …); "
                "задайте --kind і за потреби --chapter", part.name)
    check_structure(part, rep, args)
    check_figures(part, rep, args)
    check_citations(part, rep, args)
    check_novelty(part, rep, args)
    check_vstup(part, rep, args)
    check_evidence(part, rep, args, extra_numbers)
    check_language(part, rep, args)


def collect_body_numbers(paths: list[Path]) -> set[float]:
    files: list[Path] = []
    for p in paths:
        if p.is_dir():
            files += sorted(f for ext in ("*.md", "*.docx", "*.txt") for f in p.glob(ext))
        else:
            files.append(p)
    nums: set[float] = set()
    for f in files:
        text, _ = load_text(f)
        nums |= number_tokens(text)
    return nums


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", type=Path, help=".md / .txt / .docx with one part of the dissertation (or the whole text)")
    ap.add_argument("--kind", choices=["anotatsiia", "vstup", "rozdil", "vysnovky", "spysok", "dodatky", "poznachennia"],
                    help="вид частини (інакше визначається за заголовком)")
    ap.add_argument("--chapter", type=int, help="номер розділу (для rozdil)")
    ap.add_argument("--chars-per-page", type=int, default=CHARS_PER_PAGE, help=f"знаків із пробілами на сторінку (default {CHARS_PER_PAGE})")
    ap.add_argument("--first-citation-order", action="store_true", help="перевіряти нумерацію джерел за порядком першої згадки")
    ap.add_argument("--ref-start", type=int, default=1, help="перший номер джерела цієї частини (для --first-citation-order)")
    ap.add_argument("--max-ref", type=int, help="кількість джерел у списку; посилання вище — WARN C02")
    ap.add_argument("--body", type=Path, nargs="*", default=[], help="файли/каталоги розділів для звірки чисел загальних висновків (E01)")
    ap.add_argument("--no-split", action="store_true", help="не розбивати файл із кількома частинами")
    ap.add_argument("--json", type=Path, help="записати знахідки та структуру в JSON")
    args = ap.parse_args(argv)

    try:
        parts = load_parts(args.file, args.kind, args.chapter, not args.no_split, args.chars_per_page)
        extra = collect_body_numbers(args.body) if args.body else set()
    except BrickError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    rep = Report()
    multi = len(parts) > 1
    for part in parts:
        rep.prefix = part.label if multi else ""
        run_checks(part, rep, args, extra)
    rep.prefix = ""
    rep.print_lines()

    print("\nSTRUCTURE:")
    for part in parts:
        s = part.stats()
        print(f"  {part.label:<22} {part.name}: {s['pages']} стор., заголовків {s['headings']}, рисунків {s['figures']}, "
              f"таблиць {s['tables']}, формул {s['formulas']}, посилань {s['citations']}, висновки: {'так' if s['has_conclusions'] else 'ні'}")
    print("\n" + rep.summary_line())

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps({
            "file": str(args.file), "parts": [p.to_dict() for p in parts],
            "findings": rep.items, "summary": rep.counts(),
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if rep.counts()["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main())
