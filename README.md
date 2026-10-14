# kpi-skills

A collection of [Claude Code](https://code.claude.com) skills gathered along Danylo Vorvul's PhD path at **Igor Sikorsky Kyiv Polytechnic Institute (KPI)**.

This repository is both a Claude Code **plugin** and its own **marketplace** — the same directory can be loaded directly for development (`--plugin-dir`) or installed permanently by adding it as a local marketplace.

## Skills in this collection

| Skill | Namespaced name | What it does |
|---|---|---|
| `phd-report-presentation` | `kpi-skills:phd-report-presentation` | Generates a KPI-branded PhD semester/attestation report presentation (`.pptx`) from a JSON content spec, using a bundled brand template (navy/Exo 2 KPI style) and a build + preview-render + visual-check loop. Can also update/regenerate an existing deck. |

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

## Repository layout

```
kpi_skills/
├── .claude-plugin/
│   ├── plugin.json          # plugin manifest (name, version, author, keywords)
│   └── marketplace.json     # self-hosted marketplace listing this same plugin via "source": "./"
├── skills/
│   └── phd-report-presentation/
│       ├── SKILL.md         # skill entry point (frontmatter + instructions)
│       ├── scripts/         # build_deck.py, render_preview.py, make_template.py
│       ├── references/      # spec-schema.md, style-guide.md, report-structure.md
│       └── assets/          # template.pptx, example-spec.json, fonts/
├── .gitignore
└── README.md
```

`.claude-plugin/` contains **only** the two manifest files — every other component (skills, commands, agents, hooks, etc.) lives at the repository root per the Claude Code plugin spec.

## Tests

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
