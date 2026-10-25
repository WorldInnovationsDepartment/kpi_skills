# Bundled Springer LaTeX files

`llncs.cls` (v2.26, 2025-02-25) and `splncs04.bst` come unchanged from the CTAN package
[`llncs`](https://ctan.org/pkg/llncs) (<https://mirrors.ctan.org/macros/latex/contrib/llncs.zip>).

> Copyright (c) 1996-2025 Springer. This work may be distributed and/or modified under the
> conditions of the CC BY license, version 4.0 or later.

Springer's own proceedings zip (checked 2026-10-25) ships a branch it labels "v2.25
(2026-09-03)". That branch adds `\Description{...}` for figure alt text, and its
`samplepaper.tex` loads Times through `newtxtext`/`newtxmath`. `build_paper.py --latex` does
both of these on top of the CTAN class: `\providecommand{\Description}[1]{}` plus the newtx
packages. The output therefore compiles with either class file. If the conference ships its own
`llncs.cls`, use that one instead.

`build_paper.py --latex` copies both files into the output folder. The folder then compiles as is
with `latexmk -pdf paper.tex`, or after uploading it to Overleaf.
