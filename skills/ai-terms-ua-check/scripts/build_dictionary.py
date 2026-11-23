# /// script
# requires-python = ">=3.10"
# dependencies = ["pymupdf>=1.24"]
# ///
"""Rebuild references/dictionary.json from the Mintsyfra AI-terms dictionary PDF.

Ministry page: https://thedigital.gov.ua/news/technologies/hovoryty-odniyeiu-movoiu-z-tekhnolohiiamy-onovyly-natsionalnyy-slovnyk-terminiv-zi-shtuchnoho-intelektu
Source: «Словник термінів у сфері штучного інтелекту 2.0», Міністерство цифрової
трансформації України, 2026,
https://storage.thedigital.gov.ua/files/9/39/18441baf603a192429ecac57b7076394.pdf

Why two extractors: the PDF uses Type3 fonts. PyMuPDF finds the table grid
correctly but decodes Cyrillic wrongly; poppler (`pdftotext -tsv`) decodes text
correctly but places some glyphs ~10 pt above their line. We take cell
rectangles from PyMuPDF and words from poppler, then re-join the glyph pieces.

Usage:
  uv run build_dictionary.py dict.pdf --out ../references/dictionary.json
Requires poppler's `pdftotext` on PATH.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import subprocess
import sys
from pathlib import Path

import pymupdf

PAGE_URL = "https://thedigital.gov.ua/news/technologies/hovoryty-odniyeiu-movoiu-z-tekhnolohiiamy-onovyly-natsionalnyy-slovnyk-terminiv-zi-shtuchnoho-intelektu"
SOURCE_URL = "https://storage.thedigital.gov.ua/files/9/39/18441baf603a192429ecac57b7076394.pdf"
SMALL_GLYPH_H = 45.0   # poppler height of displaced glyph pieces (13.7–37.2 vs ~50.6)
LINE_TOL = 3.0
SPACE_GAP = 2.5


def poppler_words(pdf: Path) -> dict[int, list[dict]]:
    out = subprocess.run(["pdftotext", "-tsv", str(pdf), "-"], check=True,
                         capture_output=True, text=True).stdout
    pages: dict[int, list[dict]] = {}
    for r in csv.DictReader(io.StringIO(out), delimiter="\t", quoting=csv.QUOTE_NONE):
        if r["level"] != "5" or not r["text"].strip():
            continue
        x0, y0 = float(r["left"]), float(r["top"])
        w, h = float(r["width"]), float(r["height"])
        # visual glyph centre: poppler boxes of normal words start ~30 pt above
        # it, displaced pieces roughly 0.45*height above (measured on the 2026 PDF)
        cy = y0 + (0.45 * h if h < SMALL_GLYPH_H else 30.0)
        pages.setdefault(int(r["page_num"]), []).append(
            {"x0": x0, "x1": x0 + w, "y1": cy + 10, "cy": cy, "t": r["text"],
             "small": h < SMALL_GLYPH_H})
    return pages


def snap_to_lines(words: list[dict], page) -> None:
    """Replace poppler's (sometimes displaced) y with PyMuPDF's glyph geometry.

    PyMuPDF mis-decodes the Type3 Cyrillic text but its glyph boxes are right,
    so each poppler word takes the line y of the PyMuPDF glyph that starts at
    the same x.
    """
    glyphs = []
    for b in page.get_text("rawdict")["blocks"]:
        for ln in b.get("lines", []):
            for sp in ln["spans"]:
                for c in sp["chars"]:
                    cy = (c["bbox"][1] + c["bbox"][3]) / 2
                    glyphs.append((c["bbox"][0], cy, round(c["bbox"][3], 1)))
    for w in words:
        best = None
        for gx, gcy, ly in glyphs:
            # displaced pieces can sit up to ~1.5 lines off; whole words are close
            if abs(gx - w["x0"]) <= 1.2 and abs(gcy - w["cy"]) <= (40 if w["small"] else 9):
                d = abs(gcy - w["cy"])
                if best is None or d < best[0]:
                    best = (d, ly)
        if best:
            w["y1"] = best[1]
            w["cy"] = best[1] - 10


def row_cells(page) -> list[list[tuple]]:
    """Table rows from the cell background rectangles the slides are drawn with.

    `find_tables()` misses whole pages of this PDF, but every cell is a filled
    rectangle: a row is a rect in the №-column (x≈32–97) and its four siblings
    share the same y-span.
    """
    rects = [d["rect"] for d in page.get_drawings() if d["rect"].height > 25]
    rows = []
    for r in rects:
        if abs(r.x0 - 32) < 3 and abs(r.x1 - 97) < 3 and r.y0 > 40:
            sib = sorted((q for q in rects if abs(q.y0 - r.y0) < 2 and abs(q.y1 - r.y1) < 2
                          and q.x0 >= 90 and q.width < 1000), key=lambda q: q.x0)
            if len(sib) >= 4:
                cells = [tuple(r)] + [tuple(q) for q in sib[:4]]
                if cells not in rows:
                    rows.append(cells)
    return rows


def join_cell(words: list[dict]) -> str:
    words = sorted(words, key=lambda w: (w["y1"], w["x0"]))
    lines: list[list[dict]] = []
    for w in words:
        if lines and abs(lines[-1][0]["y1"] - w["y1"]) <= LINE_TOL:
            lines[-1].append(w)
        else:
            lines.append([w])
    parts = []
    for ln in lines:
        ln.sort(key=lambda w: w["x0"])
        s, prev = "", None
        for w in ln:
            if prev is not None and w["x0"] - prev["x1"] > SPACE_GAP:
                s += " "
            s += w["t"]
            prev = w if prev is None or w["x1"] > prev["x1"] else prev
        parts.append(s)
    text = " ".join(parts)
    text = re.sub(r"(\w)- (\w)", r"\1-\2", text)          # "decision- making"
    text = re.sub(r"\s+([,.;:)])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    return re.sub(r"\s+", " ", text).strip()


def split_related(s: str) -> list[str]:
    out, depth, cur = [], 0, ""
    for ch in s:
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            out.append(cur.strip()); cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return [x for x in out if x]


# Rows whose cell text does not follow the "term (synonym)" pattern. Values are
# taken verbatim from the PDF cells; only the split into variants is ours.
OVERRIDES: dict[int, dict] = {
    18: {"en_variants": ["validation data", "development data"]},
    26: {"uk_variants": ["вузький ші", "слабкий ші"], "en_variants": ["narrow ai", "weak ai"]},
    128: {"uk_variants": ["тестові дані", "випробувальні дані"]},
    95: {"uk_variants": ["оцінювання", "перевірка", "валідація"],
         "note": "Словник розрізняє: «оцінювання» — у навчанні моделі; «перевірка» — в інженерії систем ШІ."},
    119: {"en_variants": ["system prompt", "developer message"]},
    127: {"uk_variants": ["температура"], "note": "Уточнення в дужках: параметр моделі ШІ."},
    99: {"note": "Recall = повнота (чутливість); не плутати з №100 Completeness = повнота."},
    100: {"note": "Completeness = повнота; не плутати з №99 Recall."},
    131: {"note": "Accuracy = точність; Precision (№132) = точність (прецизійність)."},
    132: {"note": "Precision = точність (прецизійність); Accuracy (№131) = точність."},
    136: {"note": "Alignment має два відповідники: узгодженість (властивість, №136) і узгодження (процес, №137)."},
    137: {"note": "Alignment має два відповідники: узгодженість (властивість, №136) і узгодження (процес, №137)."},
}
QUALIFIER_PREFIX = re.compile(r"^(іноді|інакше|також)\s+", re.I)


def _split_alts(s: str, seps: str) -> list[str]:
    return [x.strip(" .") for x in re.split(seps, s) if x.strip(" .")]


def variants(entry: dict) -> dict:
    """Primary term first, then the synonyms the dictionary lists in brackets."""
    uk, en = entry["uk"], entry["en"]
    uk_v, uk_abbr = [], []
    head = re.sub(r"\s+", " ", re.sub(r"\(.*?\)", "", uk)).strip()
    uk_v += _split_alts(head, r"\s+/\s+")
    for par in re.findall(r"\((.*?)\)", uk):
        for alt in _split_alts(par, r",\s*|\s+або\s+"):
            alt = QUALIFIER_PREFIX.sub("", alt)
            (uk_abbr if alt.isupper() and len(alt) <= 5 else uk_v).append(alt.lower())
    en_v, en_abbr = [], []
    en_head = re.sub(r"\s+", " ", re.sub(r"\(.*?\)", "", en))
    for alt in _split_alts(en_head, r"\s+/\s+|\s+or\s+|,\s*|\.\s+"):
        (en_abbr if alt.isupper() and len(alt) <= 6 else en_v).append(alt)
    for par in re.findall(r"\((.*?)\)", en):
        for alt in _split_alts(par, r",\s*"):
            (en_abbr if alt.replace("-", "").isupper() and len(alt) <= 6 else en_v).append(alt)
    out = {
        "uk_variants": [v.lower() for v in uk_v],
        "uk_abbr": uk_abbr,
        "en_variants": [v.lower() for v in en_v],
        "en_abbr": en_abbr,
    }
    out.update(OVERRIDES.get(entry["n"], {}))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    pw = poppler_words(a.pdf)
    doc = pymupdf.open(a.pdf)
    entries = []
    for pno, page in enumerate(doc, start=1):
        snap_to_lines(pw.get(pno, []), page)
        for cells in row_cells(page):
            texts = []
            for x0, y0, x1, y1 in cells:
                ws = [w for w in pw.get(pno, [])
                      if x0 - 1 <= (w["x0"] + w["x1"]) / 2 <= x1 + 1 and y0 - 1 <= w["cy"] <= y1 + 1]
                texts.append(join_cell(ws))
            num = re.sub(r"\D", "", page.get_textbox(pymupdf.Rect(cells[0])))
            if not num:
                continue  # header row
            entries.append({
                "n": int(num), "uk": texts[1], "en": texts[2],
                "definition": texts[3], "related": split_related(texts[4]), "page": pno,
            })
    entries.sort(key=lambda e: e["n"])
    known = {e["uk"] for e in entries}
    for e in entries:
        e.update(variants(e))
        # the related-terms column is the least clean extraction; keep only exact term names
        e["related"] = [r for r in e["related"] if r in known]
    nums = [e["n"] for e in entries]
    missing = sorted(set(range(1, max(nums) + 1)) - set(nums)) if nums else []
    dups = sorted({n for n in nums if nums.count(n) > 1})
    payload = {
        "source": "Словник термінів у сфері штучного інтелекту 2.0 — Міністерство цифрової трансформації України, 2026",
        "url": SOURCE_URL,
        "page_url": PAGE_URL,
        "count": len(entries),
        "entries": entries,
    }
    a.out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(entries)} entries -> {a.out}", file=sys.stderr)
    if missing or dups:
        print(f"WARNING missing numbers: {missing}  duplicates: {dups}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
