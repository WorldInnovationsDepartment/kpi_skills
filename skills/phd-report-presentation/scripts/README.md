# scripts/ -- usage

Three standalone scripts, each runnable either with `uv run` (uses the PEP
723 inline metadata block at the top of the file to fetch its own
dependencies into an ephemeral environment -- no project install needed) or
with a plain `python` that already has the listed dependencies installed.

## build_deck.py -- generate a deck from a JSON spec

```bash
uv run scripts/build_deck.py --spec assets/example-spec.json --out /tmp/deck.pptx --verbose
```

```bash
python scripts/build_deck.py \
  --spec path/to/spec.json \
  --out path/to/deck.pptx \
  [--template assets/template.pptx] \
  [--assets-dir assets/] \
  [--verbose]
```

- `--template` / `--assets-dir` default to the `assets/` directory shipped
  next to this `scripts/` directory -- pass them only to point at a
  different brand template or asset set.
- Image paths inside the spec are resolved relative to the **spec file's
  own directory**, not the current working directory.
- Exits non-zero with a one-line `error: ...` message on stderr for any
  spec problem (unknown slide type, missing field, bad table shape, missing
  image). Prints `WARN: ...` lines to stderr (exit code stays 0) when a
  slide's text is estimated to overflow its box -- it never silently
  shrinks text below a readable size.

## render_preview.py -- rasterize a deck for visual review

```bash
uv run scripts/render_preview.py /tmp/deck.pptx --out /tmp/deck-preview --width 1600
```

```bash
python scripts/render_preview.py deck.pptx [--out DIR] [--width 1600]
```

Requires LibreOffice (`soffice`) on PATH or at one of the common macOS
install locations. Converts the deck to PDF headlessly, rasterizes every
page to `slide-NN.png` with PyMuPDF, and also writes a single
`contact-sheet.png` grid of every slide for a quick side-by-side look.
Prints every PNG path (one per line), contact sheet last.

## make_template.py -- rebuild assets/template.pptx from a reference deck

```bash
uv run scripts/make_template.py --source /path/to/reference.pptx --out assets/template.pptx [--quiet]
```

- `--quiet` suppresses the per-step `[make_template] ...` progress lines
  this script otherwise prints to stderr (useful when calling it from
  another script/CI step that only cares about the exit code).

Only needed if the reference/brand deck changes. Strips every slide (and
their notes/rels), scrubs `docProps` personal metadata, and drops any media
file no longer referenced by a surviving part (master/layouts/theme). Keeps
the slide master, ALL slide layouts, and the theme untouched. Re-run and
re-verify (see the QUALITY LOOP checklist in the skill's task notes: grep
the unzipped output for every person-specific string, load with
python-pptx, convert with LibreOffice) any time this script or its source
deck changes.

## Typical end-to-end loop

```bash
uv run scripts/build_deck.py --spec assets/example-spec.json --out /tmp/deck.pptx --verbose
uv run scripts/render_preview.py /tmp/deck.pptx --out /tmp/deck-preview
open /tmp/deck-preview/contact-sheet.png   # or view individual slide-NN.png files
```
