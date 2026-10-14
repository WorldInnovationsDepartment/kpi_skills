# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = ["pymupdf>=1.24", "pillow"]
# ///
"""render_preview.py -- rasterize a .pptx deck to PNGs for visual review.

    uv run render_preview.py deck.pptx
    uv run render_preview.py deck.pptx --out preview/ --width 1600

Converts the deck to PDF via LibreOffice headless (`soffice`), then
rasterizes each page to a PNG with PyMuPDF, and also stitches all pages
into a single contact-sheet PNG for a quick side-by-side review. Prints
the path of every PNG produced (one per line) followed by the contact
sheet path.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

try:
    import pymupdf as fitz  # PyMuPDF's canonical import name (>=1.24.3);
    # "import fitz" alone still works but is a deprecated compat shim that
    # prints a warning on every run -- importing "pymupdf" and aliasing it
    # to the local name "fitz" keeps every call below unchanged while
    # avoiding that warning.
except ImportError:  # pragma: no cover - only hit on pymupdf < 1.24.3
    import fitz
from PIL import Image


def find_soffice() -> str:
    candidates = [
        "/opt/homebrew/bin/soffice",
        "/usr/local/bin/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "soffice",
        "libreoffice",
    ]
    for c in candidates:
        if Path(c).is_file() or shutil.which(c):
            return c
    raise RuntimeError(
        "LibreOffice ('soffice') was not found. Install LibreOffice or pass its path "
        "via the SOFFICE environment variable / edit find_soffice() in this script."
    )


def convert_to_pdf(pptx_path: Path, workdir: Path, soffice: str, profile_dir: Path) -> Path:
    # Isolate LibreOffice's user profile per invocation (own -env:UserInstallation
    # pointed at a scratch dir). Without this, two renders started at the same
    # time share the default profile and soffice's lock file makes the second
    # one fail (or hang) instead of converting -- a real failure mode when
    # this script and another agent/process both call soffice concurrently.
    profile_uri = "file://" + urllib.parse.quote(str(profile_dir))
    cmd = [
        soffice, "--headless", "--norestore", f"-env:UserInstallation={profile_uri}",
        "--convert-to", "pdf", "--outdir", str(workdir), str(pptx_path),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"LibreOffice timed out converting '{pptx_path}' to PDF after {exc.timeout:.0f}s "
            f"(it may be stuck on a lock from a concurrent soffice process)."
        ) from exc
    pdf_path = workdir / (pptx_path.stem + ".pdf")
    if proc.returncode != 0 or not pdf_path.is_file():
        raise RuntimeError(
            f"LibreOffice failed to convert '{pptx_path}' to PDF.\n"
            f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
        )
    return pdf_path


def rasterize(pdf_path: Path, out_dir: Path, width_px: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    png_paths = []
    for i, page in enumerate(doc, start=1):
        zoom = width_px / page.rect.width
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        out_path = out_dir / f"slide-{i:02d}.png"
        pix.save(str(out_path))
        png_paths.append(out_path)
    doc.close()
    return png_paths


def make_contact_sheet(png_paths: list[Path], out_path: Path, cols: int = 4) -> Path:
    if not png_paths:
        raise RuntimeError("no slides to build a contact sheet from")
    thumb_w = 400
    # Slides in one deck normally share one page size, but don't assume it:
    # size every thumbnail to the SAME (thumb_w, thumb_h) cell via an
    # aspect-preserving fit + centering (like add_picture_fit), instead of
    # resizing each to its own aspect ratio and assuming they all match --
    # a mismatched page size used to either overflow its cell or leave the
    # single global `thumb_h` computed from slide 1 wrong for every other
    # slide.
    raw = []
    max_ratio = 0.0
    for p in png_paths:
        with Image.open(p) as im:
            raw.append(im.convert("RGB").copy())
            max_ratio = max(max_ratio, im.height / im.width)
    thumb_h = max(1, round(thumb_w * max_ratio))
    thumbs = []
    for im in raw:
        scale = min(thumb_w / im.width, thumb_h / im.height)
        w, h = max(1, round(im.width * scale)), max(1, round(im.height * scale))
        resized = im.resize((w, h))
        cell = Image.new("RGB", (thumb_w, thumb_h), (255, 255, 255))
        cell.paste(resized, ((thumb_w - w) // 2, (thumb_h - h) // 2))
        thumbs.append(cell)
        im.close()
    rows = (len(thumbs) + cols - 1) // cols
    pad = 10
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), (255, 255, 255))
    for i, thumb in enumerate(thumbs):
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(thumb, (x, y))
    sheet.save(str(out_path))
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck", type=Path, help="path to the .pptx to preview")
    ap.add_argument("--out", type=Path, default=None, help="output directory (default: <deck-stem>-preview next to the deck)")
    ap.add_argument("--width", type=int, default=1600, help="PNG width in pixels (default 1600)")
    args = ap.parse_args()

    if not args.deck.is_file():
        print(f"error: deck not found: {args.deck}", file=sys.stderr)
        raise SystemExit(2)

    out_dir = args.out or args.deck.with_name(args.deck.stem + "-preview")

    try:
        soffice = find_soffice()
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(3)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        profile_dir = tmp_path / "lo_profile"
        profile_dir.mkdir(parents=True, exist_ok=True)
        try:
            pdf_path = convert_to_pdf(args.deck, tmp_path, soffice, profile_dir)
        except RuntimeError as exc:
            print(f"error: {exc}", file=sys.stderr)
            raise SystemExit(3)
        png_paths = rasterize(pdf_path, out_dir, args.width)

    sheet_path = out_dir / "contact-sheet.png"
    make_contact_sheet(png_paths, sheet_path)

    for p in png_paths:
        print(p)
    print(sheet_path)


if __name__ == "__main__":
    main()
