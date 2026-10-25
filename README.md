# kpi-skills

A collection of [Claude Code](https://code.claude.com) skills gathered along Danylo Vorvul's PhD path at **Igor Sikorsky Kyiv Polytechnic Institute (KPI)**.

This repository is both a Claude Code **plugin** and its own **marketplace** — the same directory can be loaded directly for development (`--plugin-dir`) or installed permanently by adding it as a local marketplace.

## Skills in this collection

| Skill | Namespaced name | What it does |
|---|---|---|
| `phd-report-presentation` | `kpi-skills:phd-report-presentation` | Generates a KPI-branded PhD semester/attestation report presentation (`.pptx`) from a JSON content spec, using a bundled brand template (navy/Exo 2 KPI style) and a build + preview-render + visual-check loop. Can also update/regenerate an existing deck. |
| `asac-paper-format` | `kpi-skills:asac-paper-format` | Formats and checks a paper for the KPI journal «Адаптивні системи автоматичного управління» ([asac.kpi.ua](https://asac.kpi.ua)): Markdown+YAML source → journal-compliant `.docx` (A4, TNR 13, 1.3, native numbered equations, DSTU 8302:2015 references, UA+EN structured abstracts and author info on separate end pages), plus a rule-by-rule compliance report. Can import an existing `.docx`/`.tex` draft. |
| `lnns-paper-format` | `kpi-skills:lnns-paper-format` | Formats and checks a paper for Springer's **Lecture Notes in Networks and Systems** (LNNS, [series page](https://link.springer.com/bookseries/15179)) in the proceedings template (llncs): Markdown+YAML source → Word `.docx` in the splnproc layout (122 × 193 mm, Times 10 pt, numbered headings, run-in level 3/4, bold "Fig. N."/"Table N." captions, numbered equations, Acknowledgments + Disclosure of Interests, splncs04 references) and/or an Overleaf-ready llncs LaTeX project, plus a rule-by-rule compliance report (abstract 150-250 words, title case, ORCID, one corresponding author, citation order, DOIs, alt text, conference page limit, Type 3 fonts). Sourced from Springer's 2026 instructions and a review of three 2025-2026 LNNS papers. |
| `vottp-paper-format` | `kpi-skills:vottp-paper-format` | Formats and checks manuscripts for «Вимірювальна та обчислювальна техніка в технологічних процесах» ([vottp.khmnu.edu.ua](https://vottp.khmnu.edu.ua)): sourced requirements, three recent paper reviews, DOCX layout with content preservation, and a manual formatting/content compliance report. Records conflicting journal instructions explicitly. |

### `phd-report-presentation`

- **Triggers:** "report presi" / "report presentation", "презентація звіту",
  "звіт за семестр", "атестація", "PhD progress report slides", or any
  request for a semester/attestation `.pptx` deck for a KPI PhD student
  (including updating or regenerating one that already exists).
- **Requirements:** [`uv`](https://docs.astral.sh/uv/) (runs the skill's
  scripts and auto-installs their Python dependencies — no project install
  needed); LibreOffice (`soffice`) — optional, only needed to render a PNG
  preview of the deck for visual review; the **Exo 2** font — optional,
  only affects preview/editing fidelity (see
  `skills/phd-report-presentation/assets/fonts/README.md`).
- **Quick start:**
  ```bash
  claude plugin marketplace add /path/to/kpi_skills && claude plugin install kpi-skills@kpi-skills
  claude   # start a normal session with the plugin installed
  # then just ask, e.g.:
  # "зроби презентацію звіту за 4 семестр аспірантури"
  ```
- **Internal layout** (`skills/phd-report-presentation/`):
  ```
  SKILL.md              # entry point Claude reads (this is what to edit/extend)
  scripts/
  ├── build_deck.py      # JSON spec -> .pptx (PEP 723, run via `uv run`)
  ├── render_preview.py  # .pptx -> PNG contact sheet + per-slide PNGs (needs soffice)
  ├── make_template.py   # rebuilds assets/template.pptx from a reference deck (see below)
  └── README.md          # usage reference for all three scripts
  references/
  ├── spec-schema.md      # full JSON spec field reference
  ├── style-guide.md       # the design system build_deck.py implements (palette/fonts/geometry)
  └── report-structure.md  # recommended slide sequence + pre-generation question checklist
  assets/
  ├── template.pptx        # the brand template (master/layouts/theme; no slides)
  ├── example-spec.json    # a complete, realistic example spec exercising every slide type
  ├── example/              # sample chart/equation images the example spec references
  └── fonts/exo2/           # bundled Exo 2 font files (OFL-licensed) + README
  ```
- **Regenerating the template:** if the KPI brand deck changes, rebuild
  `assets/template.pptx` from the new reference deck:
  ```bash
  uv run skills/phd-report-presentation/scripts/make_template.py \
    --source /path/to/new-reference.pptx \
    --out skills/phd-report-presentation/assets/template.pptx
  ```
  This strips every slide and scrubs personal metadata while keeping the
  slide master, all layouts, and the theme intact — see
  `skills/phd-report-presentation/scripts/README.md` for details and the
  re-verification steps to run afterward.

### `vottp-paper-format`

- **Triggers:** "format my paper for VOTTP", "оформи статтю для ВОТТП", or preparation,
  checks and revisions for `vottp.khmnu.edu.ua`.
- **Requirements:** Python 3.10+ and `uv` (the helper resolves `lxml`); Word or
  LibreOffice plus a PDF renderer for visual verification and actual page counts.
- **Workflow:** read `skills/vottp-paper-format/references/requirements.md`, inventory
  a DOCX, classify paragraph roles, format a copy, render every page, then complete
  the manual content/policy report. The automated report covers layout only.
- **Quick start:**
  ```bash
  S=skills/vottp-paper-format
  uv run "$S/scripts/vottp_docx.py" inspect draft.docx --out work/roles.json
  # Review work/roles.json and assign semantic paragraph roles.
  uv run "$S/scripts/vottp_docx.py" format draft.docx --roles work/roles.json --out work/paper.docx
  uv run "$S/scripts/vottp_docx.py" check work/paper.docx --roles work/roles.json --original draft.docx --out work/layout-report.json
  ```
- **Sources:** requirements checked 2026-10-25; three papers from №3 (2026), published
  2026-09-10. The detailed guide's TNR 10 / spacing 1.3 is the default; the optional
  `--profile published` approximates observed production typography. Author-count,
  abstract-length and other conflicting instructions remain visible in the report.
- **Validation:** `uv run tests/vottp-paper-format/test_vottp.py` checks both profiles,
  preservation of equations/media/links/tables, and failure handling.

### `lnns-paper-format`

- **Triggers:** "format my paper for LNNS", "Lecture Notes in Networks and Systems",
  "prepare the camera-ready for the Springer LNNS proceedings", "check my paper against the
  llncs template", or a draft for any conference that publishes in LNNS.
- **Requirements:** [`uv`](https://docs.astral.sh/uv/) (PEP 723 scripts: python-docx, PyYAML,
  PyMuPDF, Pillow, and pandoc via `pypandoc_binary`); LibreOffice (`soffice`), optional, for the
  PDF preview of the `.docx`; a TeX engine, optional, for `--compile` (otherwise upload the LaTeX
  folder to Overleaf).
- **Quick start:**
  ```bash
  S=skills/lnns-paper-format/scripts
  uv run $S/import_source.py draft.docx --out work/paper.md   # or copy skills/lnns-paper-format/assets/example/paper.md
  uv run $S/renumber_refs.py work/paper.md --order citation   # or alphabetical
  uv run $S/build_paper.py work/paper.md --docx work/paper.docx --latex work/latex --verbose
  uv run $S/render_preview.py work/paper.docx --out work/preview
  uv run $S/check_paper.py work/paper.md --docx work/paper.docx --pdf work/preview/paper.pdf
  ```
- **Internal layout** (`skills/lnns-paper-format/`):
  ```
  SKILL.md                     # workflow: conference intake -> content pass -> build/check loop -> deliver
  scripts/
  ├── build_paper.py           # paper.md -> splnproc-layout .docx and/or llncs LaTeX project (pandoc + Lua filter)
  ├── check_paper.py           # ERROR/WARN/INFO report against every rule (source, .docx, final PDF)
  ├── renumber_refs.py         # reorder references (citation/alphabetical) and renumber every [n] in the body
  ├── import_source.py         # .docx/.tex/.odt/.md draft -> paper.md skeleton with TODOs
  ├── render_preview.py        # .docx (via soffice) or .pdf -> page PNGs + contact sheet
  └── lnns_common.py           # shared layout constants, source parsing, citations
  references/
  ├── requirements.md          # every Springer/LNNS rule, its source (2026-10-25) and its checker code
  ├── published-papers-review.md  # three 2025-2026 LNNS papers: house style vs. the instructions
  ├── reference-style.md       # splncs04 with templates and conversions from DSTU/APA/IEEE
  └── manuscript-format.md     # paper.md front-matter fields and body syntax
  assets/
  ├── latex/                   # llncs.cls v2.26 + splncs04.bst (CTAN, CC BY 4.0)
  └── example/paper.md, fig1.png  # complete worked example (fictional authors)
  ```
- **When Springer changes its template:** update `references/requirements.md`, the constants in
  `scripts/lnns_common.py` / `scripts/build_paper.py`, `assets/latex/` and
  `tests/lnns-paper-format/test_lnns.py` together.

### `asac-paper-format`

- **Triggers:** "format my paper for ASAC", "підготуй статтю до «Адаптивні системи
  автоматичного управління»", "asac.kpi.ua", "check my article against the journal's
  requirements", or a revised resubmission for that journal.
- **Requirements:** [`uv`](https://docs.astral.sh/uv/) (the scripts are PEP 723 and
  bring their own python-docx, PyYAML, PyMuPDF and a bundled pandoc via
  `pypandoc_binary`); LibreOffice (`soffice`) optional, only for the PDF preview and
  the exact page count; Times New Roman installed for a faithful preview.
- **Quick start:**
  ```bash
  S=skills/asac-paper-format
  uv run $S/scripts/import_source.py draft.docx --out work/paper.md   # or copy $S/assets/example/paper.md
  uv run $S/scripts/build_paper.py work/paper.md --out work/paper.docx --verbose
  uv run $S/scripts/render_preview.py work/paper.docx --out work/preview
  uv run $S/scripts/check_paper.py work/paper.md --docx work/paper.docx --pdf work/preview/paper.pdf
  ```
- **Internal layout** (`skills/asac-paper-format/`):
  ```
  SKILL.md                     # workflow Claude follows (intake -> content pass -> build/check loop -> deliver)
  scripts/
  ├── build_paper.py           # paper.md -> journal-formatted .docx (pandoc + python-docx post-processing)
  ├── check_paper.py           # ERROR/WARN/INFO report against every journal rule (source, .docx, PDF)
  ├── import_source.py         # .docx/.tex/.odt/.md draft -> paper.md skeleton with TODOs
  ├── render_preview.py        # .docx -> PDF + page PNGs + contact sheet (needs soffice)
  └── asac_common.py           # shared parsing/labels for the scripts above
  references/
  ├── requirements.md          # every journal rule, its source (asac.kpi.ua, 2026-10-23) and its checker code
  ├── published-papers-review.md  # review of three 2026 papers: house style vs. the guide
  ├── reference-style.md       # DSTU 8302:2015 in the journal's form, with templates
  └── manuscript-format.md     # paper.md front-matter fields and body syntax
  assets/
  ├── official/sample_{eng,ua}.docx   # the journal's own templates (as published on asac.kpi.ua)
  └── example/paper.md, fig1.png      # complete worked example (fictional authors)
  ```
- **When the journal changes its rules:** update `references/requirements.md`, the
  constants/labels in `scripts/asac_common.py` and `scripts/build_paper.py`, and
  `tests/asac-paper-format/test_asac.py` together.

## Repository layout

```
kpi_skills/
├── .claude-plugin/
│   ├── plugin.json          # plugin manifest (name, version, author, keywords)
│   └── marketplace.json     # self-hosted marketplace listing this same plugin via "source": "./"
├── skills/
│   ├── phd-report-presentation/
│   │   ├── SKILL.md         # skill entry point (frontmatter + instructions)
│   │   ├── scripts/         # build_deck.py, render_preview.py, make_template.py
│   │   ├── references/      # spec-schema.md, style-guide.md, report-structure.md
│   │   └── assets/          # template.pptx, example-spec.json, fonts/
│   ├── asac-paper-format/
│   │   ├── SKILL.md
│   │   ├── scripts/         # build_paper.py, check_paper.py, import_source.py, render_preview.py
│   │   ├── references/      # requirements.md, published-papers-review.md, reference-style.md, ...
│   │   └── assets/          # official journal templates, worked example
│   └── vottp-paper-format/
│       ├── SKILL.md
│       ├── scripts/         # vottp_docx.py: inspect, format and layout/preservation checks
│       └── references/      # requirements, three-paper review, formatting workflow
├── .gitignore
└── README.md
```

`.claude-plugin/` contains **only** the two manifest files — every other component (skills, commands, agents, hooks, etc.) lives at the repository root per the Claude Code plugin spec.

## Tests

`tests/vottp-paper-format/test_vottp.py` checks both VOTTP layout profiles and
preservation of native equations, media, tables, links, symbols and emphasis,
including stale role maps and deliberately damaged output:

```bash
uv run tests/vottp-paper-format/test_vottp.py
```

`tests/lnns-paper-format/test_lnns.py` checks the `lnns-paper-format` skill the same way:
the Word layout against Springer's splnproc template, the generated llncs LaTeX, build errors,
every major checker rule, reference renumbering, the importer (.docx and .tex) and, with
LibreOffice, rendering and the PDF checks (a TeX engine, if present, also compiles the LaTeX):

```bash
uv run tests/lnns-paper-format/test_lnns.py
```

`tests/asac-paper-format/test_asac.py` is the same kind of plain-assert suite for the
`asac-paper-format` skill (build layout against the journal rules, a Ukrainian
manuscript, build errors, every major checker rule, the importer, and, with
LibreOffice installed, rendering and the page count):

```bash
uv run tests/asac-paper-format/test_asac.py
```

`tests/phd-report-presentation/test_build.py` is a plain-assert (no pytest)
regression suite for the `phd-report-presentation` skill scripts
(`build_deck.py`, `render_preview.py`, `make_template.py`). Run it from the
repository root:

```bash
uv run tests/phd-report-presentation/test_build.py
```

It resolves its own dependencies from a PEP 723 header, so no project
install or virtualenv setup is needed. It also works with any interpreter
that already has `python-pptx`, `pillow`, `pymupdf`, and `lxml` installed
(`python tests/phd-report-presentation/test_build.py`), and from any working
directory — every path it uses is derived from the test file's own location
or a temporary directory, never hardcoded.

It covers: building the shipped example spec end-to-end plus a battery of
adversarial/malformed specs (clean errors vs. WARN-and-succeed), zip-level
OOXML sanity of generated `.pptx` files (well-formed XML, `[Content_Types]`
coverage, no dangling relationships), `uv run` invocation from outside the
repo, `make_template.py` idempotency and metadata scrubbing, and several
fidelity/regression checks (bold text, overflow heuristics, the
`meta.report_title` field). LibreOffice (`soffice`) is optional: the
`render_preview.py` checks need it to rasterize a deck and are skipped
cleanly (printed as `[SKIP]`) when it isn't found on `PATH`. The script
prints a final `SUMMARY: N passed, M failed, K skipped` line and exits
non-zero if anything failed.

## Installing / trying this plugin locally

### Option A — quick iteration, no install (recommended while developing)

Run Claude Code with the plugin loaded for a single session:

```bash
claude --plugin-dir /path/to/kpi_skills
```

Then try the skill:

```
/kpi-skills:phd-report-presentation
```

If you edit files while a session is open, run `/reload-plugins` to pick up the changes without restarting.

### Option B — permanent install via local marketplace

Register this repository as a marketplace, then install the plugin from it:

```bash
claude plugin marketplace add /path/to/kpi_skills
claude plugin install kpi-skills@kpi-skills
```

(Interactive-session equivalents: `/plugin marketplace add /path/to/kpi_skills` and `/plugin install kpi-skills@kpi-skills`.)

To pull in future updates after pushing changes to this repo:

```bash
claude plugin marketplace update
```

### Validating the manifests

```bash
claude plugin validate /path/to/kpi_skills
```

## Adding a new skill to the collection

1. Create a new directory under `skills/`, named exactly like the skill (kebab-case), e.g. `skills/my-new-skill/`.
2. Add `skills/my-new-skill/SKILL.md` with YAML frontmatter at minimum:
   ```yaml
   ---
   name: my-new-skill
   description: One or two sentences — lead with the concrete trigger ("use when the user asks to...").
   ---

   Skill instructions go here.
   ```
3. Keep `SKILL.md` under ~500 lines. Move detailed reference material to a sibling `reference.md` (or similar) and link to it from `SKILL.md`; Claude loads it on demand.
4. Put any bundled scripts in `skills/my-new-skill/scripts/` and any bundled data/templates in `skills/my-new-skill/assets/`.
5. Reference those bundled files from `SKILL.md` using `${CLAUDE_SKILL_DIR}` (e.g. `${CLAUDE_SKILL_DIR}/scripts/render.sh`, `${CLAUDE_SKILL_DIR}/assets/template.pptx`) so paths resolve correctly regardless of the current working directory. Use `${CLAUDE_PLUGIN_ROOT}` instead only for resources shared across more than one skill in this plugin.
6. The skill will be addressable as `kpi-skills:my-new-skill` once the plugin is (re)loaded.
7. Run `claude plugin validate /path/to/kpi_skills` and smoke-test with `claude --plugin-dir /path/to/kpi_skills` before committing.

## Author

Danylo Vorvul — PhD student, Igor Sikorsky Kyiv Polytechnic Institute (KPI).
