---
name: plagiarism-check
description: Rehearses the academic-plagiarism check of a dissertation, article or thesis (.docx/.pdf/.md/.tex/.txt, Ukrainian or English) with free, local tools before the official Unicheck/StrikePlagiarism/Turnitin scan — exact and near-verbatim text reuse against a local corpus (the candidate's own publications, colleagues' theses, downloaded sources), against pages found on the open web and in open-access repositories (DuckDuckGo-family scraping, CORE, OpenAlex), optional paraphrase detection with multilingual sentence embeddings, Unicheck-style highlighted HTML report, self-reuse reported separately, reference list and quotations excluded, and detection of the text-tampering tricks the KPI Unicheck instruction forbids. Use when the user asks to check a text for plagiarism / запозичення / унікальність / самоплагіат, "перевір на плагіат", "перевір на антиплагіат", to compare a dissertation with the author's own articles, or to find where a passage came from. Free and local; it does not have Unicheck's or Turnitin's private indexes and says so in every report.
---

# Plagiarism check rehearsal (free, local)

Finds copied and lightly edited passages the way a checker does (word shingles, run
chaining, coverage %), reports them per source with a highlighted HTML page, and is
explicit about the gap to the official check: no access to other students' theses,
Ukrainian university databases or paywalled journals. Output: `plag-check/plagiarism-report.md`,
`.html`, `.json`.

Pipeline: **intake → build the corpus (own papers + local sources + web/CORE harvest) →
`check_local.py` / `check_web.py` → read the report → advise → rerun after edits**.

Requirements:

1. `uv` (PEP 723 scripts: python-docx, PyMuPDF; `check_web.py` adds ddgs, trafilatura,
   requests; `--semantic` adds sentence-transformers and downloads
   `intfloat/multilingual-e5-small`, ~450 MB, MIT).
2. Internet for `check_web.py` only. The search phase scrapes public result pages and calls
   two free academic APIs; it is slow (2 s per query by default) and rate-limited; see
   `references/sources.md`. Nothing is uploaded: only short 9-word phrases leave the machine
   as search queries. Tell the user that before running it on an unpublished dissertation,
   and skip the web phase if they object.

References, loaded on demand:

1. `references/methods.md`: the matching algorithm, parameters, what Unicheck/Turnitin do
   differently, how to read similarity %.
2. `references/sources.md`: the free search sources, their limits and keys, measured
   behaviour from this machine.
3. `references/requirements.md`: the KPI / MON rules for dissertation checks (what is
   verified from sources and what is not), file preparation rules, self-reuse.

Work in a directory next to the manuscript (default `./plag-check/`), never inside this skill.

## 1. Intake

1. Get the manuscript. Ask in **one** message only what is missing:
   1. the candidate's **own publications** on the topic (folder of .pdf/.docx): a dissertation
      legitimately reuses them, and the report separates that from external similarity;
   2. any **local sources** they suspect or want checked against (a colleague's thesis, the
      supervisor's monograph, downloaded papers, the previous version of the text);
   3. whether the **web/open-access search** may run (short phrases leave the machine);
   4. the venue's rule, if known (KPI leaves the acceptable level to the department; see
      `requirements.md`).
2. Note the file kind: a `.pdf` without a text layer must be OCRed first; `.doc`/`.odt`
   need LibreOffice.

## 2. Local check

```bash
S="${CLAUDE_SKILL_DIR}/scripts"
uv run "$S/check_local.py" thesis.docx --corpus sources/ --own my-papers/ --out plag-check \
    [--min-words 8] [--k 5] [--gap 4] [--include quotes,references] [--semantic]
```

1. `--own` folders are the candidate's publications: matches count as *self-reuse*, not as
   external similarity. `--corpus` folders are everything else.
2. Defaults match a checker's usual sensitivity: 5-word shingles, runs ≥ 8 words, small gaps
   tolerated (one substituted word does not break a copied sentence). `--min-words 5` is
   stricter; 12 is looser.
3. Quotations («…» [n]) and the reference list are excluded like an operator would exclude
   them; `--include quotes,references` checks them too (useful to see if quotes are marked).
4. `--semantic` adds the paraphrase pass; it lists sentence pairs with cosine ≥ 0.92 that
   are *not* already matched verbatim. Review them by hand: standard definitions in the same
   field score high without being copied.
5. Exit 2 = unreadable input or empty corpus.

## 3. Web and open-access check

```bash
uv run "$S/check_web.py" thesis.docx --out plag-check --queries 40 --engines ddgs,core \
    [--own my-papers/] [--corpus sources/] [--max-pages 80] [--delay 2] [--dry-run]
```

1. `--dry-run` prints the 9-word phrases that would be searched; show them to the user if
   they are cautious about what leaves the machine.
2. The script picks evenly spaced, distinctive body sentences, searches each phrase, downloads
   the hits (HTML via trafilatura, PDF via PyMuPDF, CORE full texts directly) into
   `plag-check/web-corpus/` with a `manifest.json`, then runs the same matcher. Results are
   cached (`search-cache.json`), so a rerun resumes after a rate-limit stop.
3. Expect many "No results" lines: the scraping backends are unofficial and the Ukrainian
   web is thin in these indexes. 40 queries ≈ 2–5 minutes. CORE finds open-access papers
   (institutional repositories, arXiv mirrors); OpenAlex (`--engines ddgs,core,openalex`)
   adds abstracts only.
4. Set `CORE_API_KEY` (free registration) if CORE returns 429; `OPENALEX_API_KEY` or
   `OPENALEX_MAILTO` for OpenAlex.
5. If nothing was collected, the script says so and writes no report; that is "no
   evidence", not "0 % similarity".

## 4. Reading the report

Read `plagiarism-report.md` in full; open `plagiarism-report.html` for the highlighted text.
Then tell the user, in their language:

1. **External similarity %** and **own-publication similarity %**, with the sentence "over
   the N matchable words, against only the sources available to this run". Never present the
   external figure as the Unicheck/StrikePlagiarism figure.
2. **Every external passage**: paragraph, source, verbatim or near-verbatim, and the fix:
   quotation marks + citation for a short verbatim quote; rewrite in own words + citation of
   the idea otherwise; delete if it is filler. A citation alone does not legitimise a
   verbatim copy.
3. **Own-publication passages**: allowed when the publication is cited and listed among the
   candidate's works on the topic (`requirements.md`); advise listing them in the request to
   the operator so they are excluded from the official report.
4. **Standard phrases** (definitions, regulation text, method names) that match everywhere:
   say which ones are fine as they are.
5. **Tampering warning** if present: mixed-script words / invisible characters are banned by
   the KPI instruction and get a file rejected; fix before submission.
6. **What was not checked**: no web phase, few pages collected, scanned PDF, etc.

## 5. After edits

Rerun step 2/3 on the new file (the web cache makes it fast) and report the delta. Then book
the official check through the department's responsible person / the KPI library
(`requirements.md`); this skill is a rehearsal, not a certificate.

## Rules

1. Never help remove detectability of copied text without fixing the copying itself (no
   "spin" rewriting, no homoglyph substitution, no invisible characters). The legitimate
   outcomes are: quote and cite, paraphrase and cite, or delete.
2. Do not upload the manuscript to online "free plagiarism checkers": they keep the text,
   and an unpublished dissertation is confidential.
3. Report numbers only with their scope (which corpus, which exclusions). If the user asks
   "what will Unicheck show", answer "unknown; what this run found is a lower bound".
