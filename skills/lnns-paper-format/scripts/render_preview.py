# /// script
# requires-python = ">=3.10"
# dependencies = ["pymupdf>=1.24", "pillow"]
# ///
"""render_preview.py -- render a manuscript .docx (or an existing PDF) to PNG pages for visual review.

    uv run render_preview.py paper.docx --out preview/
    uv run render_preview.py latex/paper.pdf --out preview/    # PDF compiled from the LaTeX project

A .docx is converted with LibreOffice headless (`soffice`) and the PDF is kept
(`preview/<name>.pdf`, usable as `check_paper.py --pdf`); a .pdf is rendered as
is. Writes one PNG per page (`preview/page-NN.png`) and a contact sheet of all
pages (`preview/contact-sheet.png`), and prints every path it wrote.

LibreOffice substitutes fonts that are not installed, so install Times New
Roman for a faithful page count. For a Word submission, Springer wants the
.docx plus a PDF made from it; Word's own "Save as PDF" is the reference.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:  # pragma: no cover - pymupdf < 1.24.3
    import fitz
from PIL import Image


def find_soffice() -> str:
    env = os.environ.get("SOFFICE")
    candidates = ([env] if env else []) + [
        "/opt/homebrew/bin/soffice",
        "/usr/local/bin/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "soffice",
        "libreoffice",
    ]
    for c in candidates:
        if c and (Path(c).is_file() or shutil.which(c)):
            return c
    raise RuntimeError("LibreOffice ('soffice') was not found. Install LibreOffice or set the SOFFICE "
                       "environment variable to its path.")


def docx_to_pdf(docx: Path, outdir: Path) -> Path:
    soffice = find_soffice()
    with tempfile.TemporaryDirectory() as profile:
        # Own profile per run so concurrent soffice processes do not fight over the lock file.
        cmd = [soffice, "--headless", "--norestore",
               f"-env:UserInstallation=file://{urllib.parse.quote(profile)}",
               "--convert-to", "pdf", "--outdir", str(outdir), str(docx)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"LibreOffice timed out after {exc.timeout:.0f}s converting {docx}") from exc
    pdf = outdir / (docx.stem + ".pdf")
    if proc.returncode != 0 or not pdf.is_file():
        raise RuntimeError(f"LibreOffice failed to convert {docx}.\nstdout: {proc.stdout}\nstderr: {proc.stderr}")
    return pdf


def render(pdf: Path, outdir: Path, width: int) -> list[Path]:
    pages = []
    with fitz.open(pdf) as doc:
        for i, page in enumerate(doc, 1):
            zoom = width / page.rect.width
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            out = outdir / f"page-{i:02d}.png"
            pix.save(out)
            pages.append(out)
    return pages


def contact_sheet(pages: list[Path], out: Path, cols: int = 4, thumb_w: int = 420) -> Path:
    thumbs = []
    for p in pages:
        im = Image.open(p).convert("RGB")
        k = thumb_w / im.width
        thumbs.append(im.resize((thumb_w, int(im.height * k))))
    th = max(t.height for t in thumbs)
    rows = (len(thumbs) + cols - 1) // cols
    gap = 12
    sheet = Image.new("RGB", (cols * (thumb_w + gap) + gap, rows * (th + gap) + gap), (200, 200, 200))
    for i, t in enumerate(thumbs):
        r, c = divmod(i, cols)
        sheet.paste(t, (gap + c * (thumb_w + gap), gap + r * (th + gap)))
    sheet.save(out)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("docx", type=Path, metavar="FILE", help=".docx to convert, or a .pdf to render")
    ap.add_argument("--out", type=Path, default=Path("preview"))
    ap.add_argument("--width", type=int, default=1100, help="PNG width in pixels (default 1100)")
    args = ap.parse_args(argv)
    if not args.docx.is_file():
        print(f"error: not found: {args.docx}", file=sys.stderr)
        return 1
    args.out.mkdir(parents=True, exist_ok=True)
    for old in args.out.glob("page-*.png"):
        old.unlink()
    if args.docx.suffix.lower() == ".pdf":
        pdf = args.docx
    else:
        try:
            pdf = docx_to_pdf(args.docx.resolve(), args.out.resolve())
        except RuntimeError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    pages = render(pdf, args.out, args.width)
    print(pdf)
    for p in pages:
        print(p)
    print(contact_sheet(pages, args.out / "contact-sheet.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
