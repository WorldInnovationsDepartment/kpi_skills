# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pymupdf>=1.24",
#     "pillow>=10",
# ]
# ///
"""render_preview.py -- PDF -> page PNGs + one contact sheet, for the visual check.

    uv run render_preview.py paper.pdf --out preview [--dpi 110] [--cols 4]

Writes preview/page-01.png, page-02.png, ... and preview/contact-sheet.png, and prints
the page count. Works on any PDF (the compiled manuscript, or a published Axioms
paper for comparison).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pymupdf as fitz
from PIL import Image, ImageDraw


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--out", type=Path, default=Path("preview"))
    ap.add_argument("--dpi", type=int, default=110)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--max-pages", type=int, default=40, help="pages on the contact sheet")
    a = ap.parse_args(argv)
    if not a.pdf.exists():
        print(f"error: {a.pdf} not found", file=sys.stderr)
        return 2
    a.out.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(a.pdf)
    pages = []
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=a.dpi)
        p = a.out / f"page-{i:02d}.png"
        pix.save(p)
        if i <= a.max_pages:
            pages.append(p)
    if pages:
        ims = [Image.open(p).convert("RGB") for p in pages]
        tw = 360
        th = int(ims[0].height * tw / ims[0].width)
        cols = min(a.cols, len(ims))
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (tw + 12) + 12, rows * (th + 30) + 12), "white")
        d = ImageDraw.Draw(sheet)
        for k, im in enumerate(ims):
            x = 12 + (k % cols) * (tw + 12)
            y = 12 + (k // cols) * (th + 30)
            sheet.paste(im.resize((tw, th)), (x, y + 18))
            d.rectangle([x - 1, y + 17, x + tw, y + 18 + th], outline="#999999")
            d.text((x, y), f"page {k + 1}", fill="black")
        sheet.save(a.out / "contact-sheet.png")
    print(f"{doc.page_count} page(s) -> {a.out}/page-NN.png, {a.out}/contact-sheet.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
