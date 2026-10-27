# How the matcher works, and how commercial checkers differ

Last checked: 2026-10-26.

## Algorithm (`match_engine.py`)

1. **Normalisation**: NFKC, lower case, one apostrophe/quote/dash form, `ё→е`, invisible
   characters removed, Latin look-alike letters inside Cyrillic words mapped back to Cyrillic
   (so homoglyph tampering does not hide a match; the tampering is reported separately).
2. **Tokens**: words (`\w` runs with internal apostrophes/hyphens). Paragraph kinds come from
   `text_common.classify`: body, heading, caption and appendix are matchable; reference list,
   quotations («…» followed by a citation), formulas, code, tables and front matter are not
   (flags `--include quotes,references` add the first two).
3. **Shingles**: every `k` consecutive words (`k = 5`) hashed with BLAKE2b-64. The corpus
   shingles go into a dictionary; every target shingle is looked up. This is the
   fingerprinting family used by MOSS (winnowing), PAN text-alignment baselines, Sherlock,
   Copyfind and noplag-engine; with a corpus of tens of documents there is no need to
   subsample (winnow) the fingerprints, so matching is exact.
4. **Runs**: hits with the same source and the same diagonal (source position − target
   position) are chained if the gap between them is ≤ `1 + k + gap` shingles (`gap = 4`),
   which survives one substituted or inserted word per ~10 words. Runs of one source that
   overlap or nearly touch in the target are merged; a run with gaps or merged from several
   diagonals is labelled *near-verbatim*, an unbroken chain *verbatim*.
5. **Filter**: runs shorter than `--min-words` (8) are dropped. Unicheck's default
   sensitivity is of the same order (it ignores short coincidental matches; operators can
   change it per check).
6. **Coverage**: similarity = share of matchable target words covered by at least one run.
   Reported three ways: external sources only, own publications only, any source. Per-source
   similarity is coverage by that source alone (sources overlap, so they do not sum).
7. **Semantic pass** (`--semantic`): `intfloat/multilingual-e5-small` sentence embeddings;
   target body sentences (≥ 8 words, not already ≥ 60 % covered) are compared with every
   corpus sentence; cosine ≥ 0.92 is listed as a paraphrase candidate. This is the
   mechanism "AI-powered paraphrase detection" marketing refers to; it has many false
   positives on definitions and standard statements and must be read by a person.

## What Unicheck / StrikePlagiarism / Turnitin have that this does not

| Capability | Commercial | This skill |
|---|---|---|
| Index of the open web | own crawler indexes (billions of pages) | 40–100 live search queries through unofficial scrapers + what they return |
| Other students' theses | institutional repositories of all client universities (Unicheck: Ukrainian universities since 2015, KPI among them) | only files the user supplies |
| Paywalled journals | publisher agreements (Turnitin: Crossref/major publishers; Unicheck: partial) | none; open access via CORE/OpenAlex only |
| Previous submissions of the same author | yes (institution's archive) | `--own` folder |
| Translation plagiarism | some (Turnitin, limited) | no |
| Citation/quote exclusion | operator-configurable | automatic heuristics + flags |
| Report | highlighted text, per-source %, PDF certificate | highlighted HTML, per-source %, no certificate |
| Cost | institutional licence | free |

So the external similarity from this skill is a **lower bound** of what the official check
can find, and a passage this skill flags will be flagged there too. The web phase is the
weak part: when the scrapers return nothing (frequent for Ukrainian phrases), the report
can only say "not found", not "original".

## Reading similarity numbers

1. There is no legal threshold in Ukraine; KPI leaves the acceptable level to the faculty/
   department by type of work (`requirements.md`). Numbers like "≥ 90 % originality for a
   dissertation" circulate on commercial sites and are not normative.
2. A dissertation built on the candidate's own articles will show high *own* similarity;
   that is expected and must be explained in the request to the operator, not hidden.
3. Standard wording (definitions, regulation names, methods) matches across thousands of
   documents; the official report will show it too, and the operator/council judges it.
   Do not "fix" it by distorting the language.
4. What matters for the council is *unattributed* external text. One verbatim paragraph
   without a citation is a bigger problem than 15 % of scattered standard phrases.

## Open-source projects reviewed

| Project | Verdict |
|---|---|
| [noplag-engine](https://github.com/NoplagLabs/noplag-engine) (Apache-2.0, Python/FastAPI/PostgreSQL) | the closest open engine (winnowing, PAN benchmark harness); local corpus only, needs a database server — the same algorithm is implemented here without the server |
| cu-sanjay/Free-Turnitin-Plagiarism-Checker | archived |
| JPlag, MOSS, copydetect | source-code plagiarism; winnowing idea reused |
| PAN text-alignment task software | research code, English benchmark; same ideas |
| "free online plagiarism checkers" (Quetext, SmallSEOTools, …) | upload your text to a vendor; limited free words; not open source |
