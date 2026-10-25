# Manuscript source format (`paper.md`)

`build_paper.py`, `check_paper.py` and `renumber_refs.py` all read **one Markdown file**:

1. the YAML front matter holds everything that is not running text;
2. the Markdown body is the paper, from the Introduction to the Conclusion (plus an optional
   Appendix).

`assets/example/paper.md` uses every feature. Copy it rather than starting from scratch.

## Front matter fields

| Field | Required | Notes |
|---|---|---|
| `title` | yes | Title case, no final period. `*italic*` is allowed |
| `running_title` | no | Abbreviated title for the LaTeX running head (`\titlerunning`). The checker asks for it when the title exceeds 70 characters |
| `conference` | recommended | Mapping with `name`, `min_pages`, `max_pages`, copied from the call for papers. The checker uses them with `--pdf` |
| `citation_order` | no | `citation` (default) or `alphabetical`: the order of `references`. `renumber_refs.py` switches between them |
| `authors` | yes | A list in byline order. See the table below |
| `affiliations` | yes | A list. Each entry is either a full string ("Department, University, Street, City Postcode, Country") or a mapping `{department, organization, address, city, country}`. Authors refer to entries by 1-based number |
| `abstract` | yes | One paragraph of 150-250 words, with no citations. `$math$` and `*italic*` are allowed |
| `keywords` | yes | A list of 3-6 phrases, each starting with a capital letter, with no final period |
| `acknowledgments` | no | Funding and thanks, with grant numbers. Rendered as "**Acknowledgments.**" |
| `disclosure` | checker ERROR | The competing-interests statement, e.g. "The authors have no competing interests to declare that are relevant to the content of this article." Rendered as "**Disclosure of Interests.**" The authors must confirm the wording |
| `ai_disclosure` | no | Springer's end-of-chapter AI statement (tool, developer, version, month and year, plus "carefully reviewed, verified, and endorsed by the authors"). When set, the builder also adds the prescribed first-page footnote |
| `references` | yes | splncs04 strings, **without numbers**, in `citation_order`. `**bold**` marks the volume. DOIs go in as `https://doi.org/…`. See `reference-style.md` |

### Author fields

| Field | Required | Notes |
|---|---|---|
| `given`, `family` | yes | Given name(s) in full. A multi-part family name goes entirely in `family` ("Martinez Perez") |
| `affiliations` | yes | A list of affiliation numbers, e.g. `[1]` or `[1, 2]`. Superscripts are printed only when there are several affiliations |
| `orcid` | recommended | `0000-0000-0000-0000`. Printed as a superscript "[…]" / `\orcidID{…}` |
| `email` | ERROR for the corresponding author | Printed under the author's **first** affiliation |
| `corresponding` | exactly one author | Marked "(✉)". This is the author who signs the Licence to Publish |

## Body syntax

| Element | Write | Result |
|---|---|---|
| Section | `# Introduction` | "1 Introduction": numbered, 12 pt bold. **Do not type the number** |
| Subsection | `## Data Sets` | "2.1 Data Sets": numbered, 10 pt bold |
| Level 3 | `### Acceptance Test` followed by a paragraph | Bold run-in heading: "**Acceptance Test.** The paragraph…" |
| Level 4 | `#### Remark` followed by a paragraph | Italic run-in heading |
| Paragraph | Plain text, with a blank line between paragraphs | Justified, 10 pt. Not indented after a heading, float or equation |
| Citation | `[1]`, `[3–5]`, `[2, 7]` | Word: kept as numbers, with ranges normalised to "[3–5]". LaTeX: `\cite{ref3,ref4,ref5}` |
| Inline math | `$w_i$` | A native Word equation / LaTeX math |
| Display formula | `$$ ... $$` (LaTeX syntax) on its own lines | Centred and numbered "(n)" at the right. **Every** display formula is numbered. End it with "," or "." as the sentence requires |
| Text after a formula | Continue in the next paragraph ("where …") | Not indented |
| Bulleted list | `- item;` | "•" list |
| Numbered list | `1. item;` | "1." list |
| Figure | `![Caption](fig1.png){width=10cm alt="What the figure shows"}` as its own paragraph | Centred image with "**Fig. N.** Caption" below. `alt` becomes the alt text (`\Description` / the Word image description). Mention "Fig. N" **before** the figure |
| Table | A `Table: Caption` line, then a pipe table | "**Table N.** Caption" above a table with horizontal rules only. Mention "Table N" before it |
| Code | A fenced block (```) | 9 pt Courier |
| Emphasis | `*italic*`, `**bold**` | As typed. No colour |

Do **not** put the title, authors, Abstract, Keywords, Acknowledgments, Disclosure or References
in the body. They come from the front matter (`check_paper.py` reports `body.generated`).

Image paths are relative to `paper.md`, and images wider than the 122 mm text width are scaled
down.

1. Prefer vector graphics. For LaTeX, use PDF or EPS. For Word, export PNG at 600-1200 dpi.
2. Photos need at least 300 dpi at the printed width.

## What the builder produces, in order

1. The title, the authors (with affiliation superscripts, the (✉) mark and ORCIDs), the
   affiliations with e-mails, then **Abstract.** and **Keywords:**.
2. The body, with numbered sections, figures, tables and equations.
3. Acknowledgments, Disclosure of Interests and Disclosure of AI Use, as 9 pt run-in paragraphs.
4. The numbered References.

The Word output adds no running heads, page numbers or © line; Springer adds those. The LaTeX
output uses `runningheads` with `\titlerunning` / `\authorrunning`, as the template does.
