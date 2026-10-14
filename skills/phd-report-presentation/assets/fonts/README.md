# Bundled font: Exo 2

## What this is and why it matters

The KPI PhD semester-report template's OOXML theme (`ppt/theme/theme1.xml` in
the reference deck, font scheme named `"КПІ Презентація"`) declares **"Exo 2"**
as *both* the major and minor theme font (`+mj-lt` = `+mn-lt` = `Exo 2`). Every
heading, body run, footer wordmark, and table cell in the reference deck
resolves to this font.

The font is **not embedded** in the reference `.pptx` — its
`embedTrueTypeFonts="1"` flag only ships leftover Calibri/Cambria Math/SimSun
fonts from an earlier template, not Exo 2 — and it is **not installed** on a
typical macOS, Windows, or Linux machine. When PowerPoint or LibreOffice opens
a deck that references a missing font, it silently substitutes another sans
serif for on-screen display and printing. The substitute almost never has the
same metrics as Exo 2, so **line breaks, autofit shrink percentages, and
text-box overflow all shift** — this is exactly the class of bug flagged in
the source-deck analysis (title-box overflow, `normAutofit` scale drift). The
generator therefore bundles the real font so that:

- anyone previewing/editing the generated `.pptx` can install the exact
  typeface the template was designed around, and
- the generator itself (or any headless renderer such as LibreOffice) can be
  pointed at these files to rasterize accurate previews.

## Files

Downloaded from the Google Fonts repository (OFL-licensed), under
`assets/fonts/exo2/`:

| File | Size (bytes) | SHA-256 |
|---|---|---|
| `Exo2[wght].ttf` | 303940 | `205a448676a2586f9c57c25f3d5c58ca8db7e6cf5edf7506783a010c6fe2bfb5` |
| `Exo2-Italic[wght].ttf` | 302556 | `bad568cea9ed23d6ae4aea41ad3f7747752952aabdd85d7f01474af392a21b32` |
| `OFL.txt` | 4386 | `7f95a8eeecc6904ffc81cd10cc8ebc7fcee72a67922924bf45f02dff03b88127` |
| `METADATA.pb` | 1234 | `465b6e658106342dab756a190234bb03d1d7d3bdcb21e68b6d74f9807a781b43` |

Both `.ttf` files are **variable fonts** with a single `wght` axis:

- Range: **100 (Thin) – 900 (Black)**, default instance 400 (Regular)
- Family name (from the font's `name` table): **"Exo 2"**
- `Exo2[wght].ttf` → subfamily "Regular" / PostScript name `Exo2-Regular`
- `Exo2-Italic[wght].ttf` → subfamily "Italic" / PostScript name `Exo2-Italic`

Verified with `fontTools.ttLib.TTFont` (`fvar` table) and confirmed valid
TrueType containers via `file`. Cyrillic coverage was checked against the
font's best cmap:

- U+0404 Є — present
- U+0406 І — present
- U+0407 Ї — present
- U+0490 Ґ — present
- U+0410–U+044F (basic Cyrillic block) — all 64 codepoints present, 0 missing

`METADATA.pb` additionally declares `subsets: cyrillic` and
`subsets: cyrillic-ext`, corroborating full Ukrainian-alphabet support
(matches the reference deck's UA body text, including Є/І/Ї/Ґ).

## License

**SIL Open Font License, Version 1.1** (OFL). Full text bundled at
`assets/fonts/exo2/OFL.txt`. The OFL permits bundling, embedding in
documents, and redistribution (including commercial use) without royalty;
it does not permit selling the font files by themselves. Copyright per the
font's own metadata: "Copyright 2013 The Exo 2 Project Authors
(https://github.com/googlefonts/Exo-2.0)". Designer: Natanael Gama.

## Provenance

- Upstream project: https://github.com/googlefonts/Exo-2.0
- Mirrored into Google's font collection at:
  https://github.com/google/fonts/tree/main/ofl/exo2
- Files fetched via raw download from:
  `https://raw.githubusercontent.com/google/fonts/main/ofl/exo2/`
  (brackets in `Exo2[wght].ttf` / `Exo2-Italic[wght].ttf` URL-encoded as
  `%5B%5D`)
- `google/fonts` commit that last updated the font binaries:
  [`8445cfa2e5f80a6c91ccc1a86726761421791476`](https://github.com/google/fonts/commit/8445cfa2e5f80a6c91ccc1a86726761421791476)
  ("Exo 2: Version 2.010 added"), itself pulled from the upstream repo at
  commit `f83ea8a02d3e1d6963ab6e910038521f27e283a2` — this matches the
  `source.commit` field recorded in the bundled `METADATA.pb`.
- `METADATA.pb` is kept alongside the fonts as the canonical Google Fonts
  provenance record (designer, license, subsets, axis ranges, source repo
  and commit).

## Installing (optional — for preview fidelity only)

Generating the `.pptx` does **not** require the font to be installed
anywhere; python-pptx only needs to *reference* the font name "Exo 2" in the
XML. Installing it is optional and only affects how accurately the deck
*previews/renders* on the machine used to view or edit it — PowerPoint and
LibreOffice will otherwise substitute a fallback sans serif, which can shift
line breaks and autofit shrink percentages versus the design intent.

**macOS:**
```sh
cp "<skill>/assets/fonts/exo2/"*.ttf ~/Library/Fonts/
```

**Linux:**
```sh
mkdir -p ~/.fonts
cp "<skill>/assets/fonts/exo2/"*.ttf ~/.fonts/
fc-cache -f ~/.fonts
```

(Replace `<skill>` with the actual path to this skill directory, e.g.
`skills/phd-report-presentation`.)

## Font name to use in pptx XML

Use the exact family name **"Exo 2"** (with the space, matching the font's
own `name` table entries and the reference deck's theme) as the
`typeface` attribute value in `a:latin`/`a:ea`/`a:cs` runs and in the theme's
`a:majorFont`/`a:minorFont` — e.g. `<a:latin typeface="Exo 2"/>`. This is
also the exact string PowerPoint/LibreOffice will look for when resolving
against installed fonts, and the exact string that must be substituted
(document the substitute font as a fallback for the `ea`/`cs` slots if you
add one) if the generator wants a documented fallback behavior.

## Local machine check (informational only — nothing was installed)

Checked `~/Library/Fonts`, `/Library/Fonts`, `/System/Library/Fonts`, and
`fc-list` on this Mac for anything matching "exo": **not found in any
location.** Exo 2 is not currently installed on this machine.
