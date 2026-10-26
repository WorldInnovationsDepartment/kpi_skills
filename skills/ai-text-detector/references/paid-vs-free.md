# Paid detectors vs this free stack

Last checked: 2026-10-26. Vendor figures are self-reported unless noted.

| | Turnitin AI (and Unicheck's AI module where offered) | GPTZero | Originality.ai | This skill |
|---|---|---|---|---|
| Model | proprietary supervised, trained on millions of documents | proprietary multi-component | proprietary; "2.0.0 multilingual" lists Ukrainian with 98.4 % accuracy, 2.4 % FPR (vendor) | open zero-shot LLM statistics + one open English classifier |
| Ukrainian | Turnitin AI: English, Spanish, Japanese … (Ukrainian not listed) | multi-language claims | yes (vendor claim) | yes, uncalibrated and measured as **not separating** frontier-model prose |
| Independent evaluation | RAID leaderboard (vendors submit): GPTZero ≈ 93 % TPR at 1 % FPR on RAID (Winston's Oct-2026 comparison) | same | ranked itself on RAID | Binoculars: strong in the 2024 paper at low FPR; weak on 2026 models here |
| False positives | Turnitin says < 1 % document-level; independent studies show non-native writers at much higher risk | < 0.5 % (vendor) | 2.4 % (vendor) | depends on calibration; uncalibrated = unknown |
| Can it be used as evidence | universities increasingly say no (several banned AI detection in 2023–2026) | no | no | no |
| Cost | institutional licence (KPI has Unicheck for plagiarism; AI module not confirmed) | paid tiers, small free quota | paid | free |
| Privacy | text uploaded to vendor | uploaded | uploaded | local |

What the paid tools have that cannot be reproduced for free:

1. **Training data**: millions of labelled human/AI documents across domains and current
   models, refreshed as models change. Open supervised detectors are frozen at RAID (2024).
2. **Current-model coverage**: vendors retrain on GPT-5/Claude/Gemini output; the open
   zero-shot methods were validated on 2023-era ChatGPT and fail here on 2026 Claude prose.
3. **Document-level calibration** with large held-out human corpora per language.

What they do *not* have either:

1. Reliability on edited or paraphrased AI text, on translated text, on short texts.
2. Any way to prove authorship. Every vendor's terms say the score is not proof.

Practical reading for a KPI candidate: the official plagiarism check is Unicheck (see the
plagiarism-check skill); an AI check is not part of the mandated procedure as of the sources
in `requirements.md` of that skill. If a reviewer runs GPTZero/Turnitin AI on the
dissertation, this skill cannot predict the result. What it can do is show which passages
*any* perplexity-based detector will dislike (template prose), so the author can make them
more specific — which is good writing advice regardless of detectors.
