# /// script
# requires-python = ">=3.10"
# dependencies = ["pymupdf>=1.24", "pillow"]
# ///
"""render_preview.py -- render a presentation to PNGs for the visual check.

    uv run render_preview.py talk.pptx --out review/preview
    uv run render_preview.py talk.pdf  --out review/preview --width 1280

Converts .pptx/.ppt/.odp/.key to PDF with LibreOffice (a .pdf is used as is),
writes `slide-NN.png` for every slide and `contact-sheet.png` with all of them,
and prints every path. Needs LibreOffice (soffice) unless the input is a PDF.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deck_common import DeckError, soffice_convert  # noqa: E402

try:
    import pymupdf as fitz
except ImportError:  # pragma: no cover
    import fitz
from PIL import Image


def contact_sheet(pngs: list[Path], out: Path, cols: int = 4, thumb_w: int = 480) -> Path:
    thumbs = []
    for p in pngs:
        im = Image.open(p)
        thumbs.append(im.resize((thumb_w, round(im.height * thumb_w / im.width))))
    th = max(t.height for t in thumbs)
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (thumb_w + 8) + 8, rows * (th + 8) + 8), "white")
    for k, t in enumerate(thumbs):
        sheet.paste(t, (8 + (k % cols) * (thumb_w + 8), 8 + (k // cols) * (th + 8)))
    sheet.save(out)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck", type=Path)
    ap.add_argument("--out", type=Path, default=Path("review/preview"))
    ap.add_argument("--width", type=int, default=1600, help="PNG width in pixels (default 1600)")
    args = ap.parse_args(argv)
    if not args.deck.is_file():
        print(f"error: {args.deck}: no such file", file=sys.stderr)
        return 2
    args.out.mkdir(parents=True, exist_ok=True)
    try:
        if args.deck.suffix.lower() == ".pdf":
            pdf = args.out / "deck.pdf"
            if args.deck.resolve() != pdf.resolve():
                shutil.copyfile(args.deck, pdf)
        else:
            pdf = soffice_convert(args.deck, "pdf", args.out)
    except DeckError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    doc = fitz.open(str(pdf))
    pngs = []
    for i, page in enumerate(doc, 1):
        zoom = args.width / page.rect.width
        p = args.out / f"slide-{i:02d}.png"
        page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)).save(str(p))
        pngs.append(p)
        print(p)
    if pngs:
        print(contact_sheet(pngs, args.out / "contact-sheet.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
