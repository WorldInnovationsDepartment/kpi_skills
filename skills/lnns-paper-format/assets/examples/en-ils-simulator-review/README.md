# Real example: an open-access LNNS chapter as `paper.md`

The fictional manuscript in `assets/example/` only exercises the builder. This folder holds a
**real, published** Springer LNNS chapter converted to the skill's source format, so a user can
see what a finished llncs paper looks like in `paper.md`.

## Source and licence

1. **Chapter:** Odéen, M., Sellberg, C., Praetorius, G., Lindwall, O., Englund, L., Andersson, A.:
   "Intelligent Learning Systems for Simulator-Based Professional Training: A Systematic
   Literature Review". In: Kim, T.E., et al. (eds.) MIS4TEL 2024 (2nd ETELT workshop), Lecture Notes
   in Networks and Systems, vol. 1274, pp. 109-119. Springer, Cham (2025).
2. **DOI:** <https://doi.org/10.1007/978-3-031-84170-5_10> (the volume is 10.1007/978-3-031-84170-5).
3. **Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0), "© The Author(s) 2025".
   Crossref lists the licence as `https://creativecommons.org/licenses/by/4.0` for this chapter, and
   the licence statement is also printed on the last page of the PDF. CC BY permits adaptation, so
   converting the text to Markdown and redistributing it is allowed with this attribution.
4. **Full text used:** the Springer-typeset PDF of the chapter (11 pages, "© The Author(s) 2025"
   footer, DOI printed) from the open repository of the authors' institute (VTI, DiVA portal
   `diva2:1966774`). It is the published version, not an accepted manuscript. link.springer.com
   itself was not used.
5. **Changes made (CC BY "indicate if changes were made"):** the text was retyped into Markdown/YAML
   for this skill; headings lost their numbers (the builder numbers them), the reference list was
   re-marked for `paper.md` (bold volume numbers), and Fig. 1 was cropped from the PDF page at
   600 dpi. No wording was changed.

## Authors and affiliations (as printed)

Martina Odéen (1), Charlott Sellberg (2), Gesa Praetorius (1, 3; corresponding, gesa.praetorius@vti.se),
Oskar Lindwall (2), Linn Englund (1), Anders Andersson (1).
1. The Swedish National Road and Transport Research Institute (VTI), Gothenburg, Sweden.
2. University of Gothenburg, Sweden.
3. University of South-Eastern Norway, Borre, Norway.

## What it demonstrates

1. The llncs/splnproc title block with several affiliations and one corresponding author.
2. A single-paragraph abstract and three keywords, numbered sections 1-6 with three-level
   numbering (3.1, 5.1), a bulleted list, a one-column table with a caption above, and a figure
   with a caption below and alt text.
3. 24 splncs04 references cited by number, with ranges such as `[8–11]` and `[7–9]`.
4. A real conference paper of 11 pages (the builder's Word output also comes to 11 pages).

## Differences from the printed chapter, and genuine checker findings

1. **No ORCIDs.** The chapter prints none, so none are given (the checker warns, as it should).
2. **No Disclosure of Interests.** The chapter has no such statement, and the skill never invents
   one, so `check_paper.py` reports `ERROR credits.disclosure` and `ERROR docx.disclosure`. These
   are real: a camera-ready LNNS paper needs the statement, and the authors would have to supply it.
3. **`ERROR cite.order`.** The chapter cites [8] before [7] in Sect. 3.1 (the numbers are not in
   order of first citation). The numbering is kept as published rather than renumbered. Running
   `renumber_refs.py --order citation` would fix it.
4. Other WARNs are also from the chapter: none of the 24 references has a DOI, only 9 are from
   2021 or later, and the Conclusion has no explicit future-work sentence.
5. **Table 1** is printed without a header row. Because pipe tables need one, the first line of the
   search string is the header row.
6. The chapter prints no page limit, so `conference:` holds only the name.
7. The chapter's own typos are kept ("EduZing", "d Baker, R.S.", "main comments").
8. Layout details Springer adds (running heads, the © and DOI footer, the open-access logo) are not
   reproduced; the skill never adds them.

## Build and check

```bash
S=skills/lnns-paper-format/scripts
E=skills/lnns-paper-format/assets/examples/en-ils-simulator-review
uv run "$S/build_paper.py" "$E/paper.md" --docx /tmp/ils.docx --latex /tmp/ils-latex --verbose
uv run "$S/render_preview.py" /tmp/ils.docx --out /tmp/ils-preview
uv run "$S/check_paper.py" "$E/paper.md" --docx /tmp/ils.docx --pdf /tmp/ils-preview/paper.pdf
```
