# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-pptx>=1.0",
#     "pymupdf>=1.24",
# ]
# ///
"""extract_deck.py -- dump a presentation slide by slide for the content review.

    uv run extract_deck.py talk.pptx --out review/
    uv run extract_deck.py talk.ppt  --out review/      # .ppt/.odp/.key need LibreOffice
    uv run extract_deck.py talk.pdf  --out review/

Writes `review/deck.md` (one section per slide: detected title, the parts of
the talk it was recognised as, all text in reading order, speaker notes,
picture/table/shape counts, explicit font sizes) and `review/deck.json` (the
same data, machine-readable). Read deck.md in full before the manual review.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deck_common import SECTIONS, DeckError, classify_slide, load_deck, section_map  # noqa: E402


def to_markdown(deck: dict) -> str:
    sm = section_map(deck)
    by_slide: dict[int, list[str]] = {}
    for k, idx in sm.items():
        for i in idx:
            by_slide.setdefault(i, []).append(SECTIONS[k][2])
    out = [f"# {Path(deck['source']).name}", "",
           f"Слайдів: {deck['slide_count']}; формат: {deck['converted_from'] or deck['format']}; "
           f"розмір: {deck['slide_width_in']}×{deck['slide_height_in']} in", ""]
    for s in deck["slides"]:
        out.append(f"## Слайд {s['index']}: {s['title'] or '(без заголовка)'}")
        meta = [f"слів {s['words']}", f"зображень {s['pictures']}", f"фігур {s['shapes']}"]
        if s["tables"]:
            meta.append(f"таблиць {s['tables']}")
        if s["charts"]:
            meta.append(f"діаграм {s['charts']}")
        if s["font_sizes"]:
            meta.append(f"шрифт {min(s['font_sizes']):g}–{max(s['font_sizes']):g} pt")
        if not s["has_slide_number"]:
            meta.append("без номера")
        out.append("_" + ", ".join(meta) + "_")
        if s["pictures"]:
            out.append("_⚠ на слайді є зображення: текст у них (схеми, SmartArt, скріни) тут не видно — "
                       "дивіться preview/slide-%02d.png_" % s["index"])
        if s["index"] in by_slide:
            out.append(f"_Розпізнано як: {'; '.join(by_slide[s['index']])}_")
        out.append("")
        for p in s["paragraphs"]:
            out.append(f"- {p}")
        if s["notes"]:
            out += ["", "**Нотатки доповідача:**", "", s["notes"]]
        out.append("")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck", type=Path)
    ap.add_argument("--out", type=Path, default=Path("review"), help="output directory (default ./review)")
    args = ap.parse_args(argv)
    try:
        deck = load_deck(args.deck, work_dir=args.out / "converted")
    except DeckError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    args.out.mkdir(parents=True, exist_ok=True)
    for s in deck["slides"]:
        s["sections"] = classify_slide(s)
    (args.out / "deck.json").write_text(json.dumps(deck, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.out / "deck.md").write_text(to_markdown(deck), encoding="utf-8")
    print(args.out / "deck.md")
    print(args.out / "deck.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
