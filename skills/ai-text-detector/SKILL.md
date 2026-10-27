---
name: ai-text-detector
description: Scores a manuscript (dissertation, article, thesis chapter; .docx/.pdf/.md/.tex/.txt, Ukrainian or English) for AI-generated text with open, locally run detectors — Binoculars and Fast-DetectGPT (zero-shot, Qwen3 base/instruct pairs that cover Ukrainian) and the Desklib DeBERTa classifier (English only) — chunk by chunk, with per-passage scores, a calibration workflow against the author's own known-human text, and an honest report that says what the numbers can and cannot prove. Use when the user asks to check whether a text "looks AI-generated", "перевір на ШІ / на GPT", "чи виглядає текст як згенерований", to pre-check a dissertation before a Unicheck/Turnitin AI scan, or to rank passages that an AI detector is most likely to flag. Free and offline; it is NOT Turnitin/GPTZero/Originality and cannot predict their verdicts — the skill says so in every report.
---

# AI-generated text check (free, local)

Runs open AI-text detectors on a manuscript and reports which passages look most
machine-written, how confident that is, and why nobody should treat it as proof. Output:
`ai-check/ai-report.md` + `ai-report.json`.

Pipeline: **intake → (optional) calibration → `detect_ai.py` → read the report → explain**.

Requirements:

1. `uv` (scripts are PEP 723; they fetch torch, transformers, python-docx, PyMuPDF).
2. ~3–16 GB of disk for the models (downloaded once to `~/.cache/huggingface`): the `small`
   pair (Qwen3-0.6B) ≈ 2.4 GB, `medium` (Qwen3-1.7B, default) ≈ 7 GB, `large` (Qwen3-4B) ≈ 16 GB,
   `desklib` ≈ 1.8 GB. Apple Silicon (MPS), CUDA or CPU; a 30-page chapter takes a few minutes
   on an M-series Mac with `medium`.
3. Internet for the first download only. Nothing is uploaded anywhere.

References, loaded on demand:

1. `references/methods.md`: how each method works, its paper, licence, what it was measured
   to do on this machine (including the failure on Claude-written Ukrainian text), and the
   model pairs. Read it before explaining a verdict.
2. `references/paid-vs-free.md`: what Turnitin/Unicheck AI, GPTZero, Originality.ai do
   differently and what the free stack cannot match. Read it when the user asks "is this as
   good as X" or wants to predict an official check.

Work in a directory next to the manuscript (default `./ai-check/`), never inside this skill.

## 1. Intake

1. Get the file. Any of `.docx .pdf .md .tex .txt .odt .rtf` (the last two need LibreOffice).
2. Ask in **one** message only what is not already clear:
   1. the purpose: self-check before an official scan, curiosity, or checking someone
      else's text (if the latter, say up front that these tools cannot support an
      accusation and the report will say so);
   2. whether they can supply **known-human** text by the same author (papers written
      before 2022, old chapters, emails) — this enables calibration, which is the only way
      to get a meaningful threshold for Ukrainian;
   3. language of the text (auto-detected; confirm if mixed).
3. Default plan if the user says nothing: `--method binoculars --size medium`, uncalibrated,
   for Ukrainian; add `--method desklib` for English text.

## 2. Calibration (recommended; mandatory for a verdict in Ukrainian)

The published Binoculars threshold was tuned for Falcon-7B on English. For any other pair or
language, build one:

1. `human/`: 3–10 files the author certainly wrote without AI (≥ 3 000 words total).
   **Not** Wikipedia or famous texts: models have memorised those and they score as
   "machine-like" (measured: Ukrainian Wikipedia scored *lower* than Claude-written text).
2. `ai/`: 20–40 paragraphs in the same language and register, produced by a current
   assistant. Write them yourself (you are such an assistant): same topic as the
   manuscript, academic Ukrainian, 150–250 words each, save as `ai/gen-NN.txt`. Say in the
   report that the AI samples are Claude-written and dated.
3. Run:
   ```bash
   S="${CLAUDE_SKILL_DIR}/scripts"
   uv run "$S/calibrate.py" --human human --ai ai --method binoculars --size medium --out calibration.json
   ```
   It prints AUROC and the thresholds at 5 % and 1 % false-positive rate. **If AUROC < 0.8,
   stop and tell the user**: on their writing, this detector cannot tell their human text
   from AI text, so any verdict on the manuscript is noise. That is a real result, not a
   failure of the skill; report it as such (see `methods.md` for the numbers measured here).

## 3. Scoring

```bash
S="${CLAUDE_SKILL_DIR}/scripts"
uv run "$S/detect_ai.py" thesis.docx --out ai-check --method binoculars --size medium \
    [--calibration calibration.json] [--method binoculars,fastdetect,desklib] [--include appendix]
uv run "$S/detect_ai.py" thesis.docx --out ai-check --dry-run      # only extract + chunk, no models
```

1. The script excludes the reference list, quotations, formulas, tables, captions and front
   matter by default (they are not the author's prose and look machine-like). `--include
   references,quotes,appendix,captions` adds them.
2. Chunks are ~220 words of consecutive body text; every chunk gets a score per method. Exit
   2 means the file could not be read or has no body prose (scanned PDF: OCR it first).
3. `--method all` runs all three. `desklib` is meaningless on non-English text; the script
   warns and you must not quote its numbers for Ukrainian.
4. Memory: `large` needs ~16 GB of RAM/VRAM; fall back to `medium` on error.

## 4. Reading the report

Read `ai-check/ai-report.md` in full. Then tell the user, in their language:

1. **The verdict line per method** with its threshold provenance: "calibrated on your texts
   at 5 % FPR" is a statement; "paper default, uncalibrated" is a hint. Never print a
   percentage like "73 % AI" — these methods do not produce probabilities over the
   document; Desklib's per-chunk probability is a classifier output, not a share of text.
2. **Which passages** are the most machine-like (they are listed with scores) and *why they
   might score that way without being AI*: definitions, standard method descriptions,
   regulatory wording, translated text, lists of properties, boilerplate introductions.
3. **Cluster pattern**: isolated flagged chunks are expected in human text; a run of
   consecutive flagged chunks in one section is the thing to look at.
4. **The tampering warning** if present (Latin letters inside Cyrillic words, invisible
   characters): KPI's Unicheck instruction forbids it; fix before any official check.
5. **What this cannot say**: see `paid-vs-free.md`. Say it in one paragraph, not as a
   disclaimer wall.

## 5. If the user wants to "fix" flagged passages

Do not offer to rewrite text so it evades detectors — that is the bypass service the
paid "humanizers" sell and it is academic misconduct when the text was AI-written. What is
legitimate: if the passage *is* the author's own, help them make it more specific (their
data, their numbers, their decisions), which also happens to be what human academic prose
has and template prose lacks. If the author says a passage was AI-drafted, the honest fix is
to rewrite it themselves and declare AI assistance where the venue requires it.

## Rules

1. Never state that a text "is AI-generated" or "is human". State scores, thresholds, their
   provenance and the measured error rates.
2. Do not upload the manuscript to any online detector "to double-check"; it contains
   unpublished results and the user did not ask for that.
3. Keep `references/methods.md` honest: if you measure new numbers (new pair, new language),
   add them with the date and the sample description.
