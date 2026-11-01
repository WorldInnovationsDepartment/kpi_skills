---
name: review-paper-language
description: Review academic papers for grammar and style, present numbered before-and-after corrections, and apply only approved changes while preserving scientific content and document formatting. Use for manuscript proofreading, approval-first editing, applying a selected correction list, or producing a DOCX table of changes.
---

# Review Paper Language

## Workflow and authorization

Use three stages: review, approved editing, and optional change reporting. Follow the user's current request and existing authorization. By default, show proposals before modifying a manuscript. If the user explicitly authorizes direct editing or approves an existing list, proceed without asking again.

Treat approval as scoped. Approval of a numbered list authorizes only that list, not separate suggestions about the title, terminology, citations, scientific claims, or disclosures. Never expand a narrow request into a general rewrite.

## Read the source

- Identify the exact manuscript and version. Use an available attachment or the current resolved file; do not substitute an unrelated or older paper.
- Read all relevant text, including abstracts, captions, tables, conclusions, and author information. Preserve equations and non-text objects during extraction.
- For DOCX work, use the available document skill and inspect the rendered document where layout or embedded text matters. Use the Library workflow when required for accessing or saving files.
- If a source is unavailable, explain the limitation. A change table may still be generated from an exact approved list or verified edit record in the conversation; state that basis and do not claim a fresh file inspection.

## Review without editing

Respond in the user's language and keep manuscript excerpts in their original language. Present a stable, numbered table:

| ID | Location | Original | Proposed | Reason |
| --- | --- | --- | --- | --- |

Quote exact excerpts and give a concise explanation. Use section names and distinctive phrases as locations. Add page numbers only after verifying them against the source render. Mark omissions with an ellipsis; do not present shortened text as a complete sentence.

Distinguish three categories:

1. **Language corrections:** grammar, articles, agreement, punctuation, awkward syntax, and clear usage errors.
2. **Optional style suggestions:** concision, sentence restructuring, title wording, or terminology preferences.
3. **Meaning-dependent questions:** changes affecting claims, definitions, experimental status, uncertainty, citations, or author declarations.

Do not label a valid stylistic choice as a grammatical error. Follow the established English variety; remember that British English may use Oxford -ize spelling. Preserve formal terminology unless its intended meaning is clear. Do not automatically equate computational cost with complexity, or gameplay difficulty with complexity.

Flag apparent internal inconsistencies separately. Do not silently change results, equations, references, names, affiliations, or disclosures. Do not imply that bibliography entries were externally verified when only the supplied text was inspected. Browse authoritative sources if external verification is requested or needed to support an external factual claim.

Finish with a concrete approval question identifying the proposed batch. State that the manuscript has not been edited. Skip this question when the user has already authorized the requested changes.

## Apply the approved changes

1. Resolve the approved IDs and their exact original/proposed text. Retain stable IDs when the user approves only a subset.
2. Confirm each original excerpt still matches the intended location in the current manuscript. If a revision makes a match ambiguous, clarify that item rather than guessing.
3. Patch only the approved text. Preserve formatting, paragraph and run structure, hyperlinks, citations, tables, drawings, embedded objects, and equation representations. Avoid replacing whole paragraphs when that would discard mixed formatting or objects.
4. Handle text split across runs and formulas explicitly. Do not flatten an equation to insert adjacent punctuation. Distinguish text edits from labels embedded in images; report any approved edit that cannot be applied reliably.
5. Keep an edit record containing ID, location, exact original text, replacement text, and status. Do not equate the number of changed paragraphs with the number of approved corrections.
6. Compare source and output to verify that all approved corrections were applied and no unapproved content changes were introduced. Where practical, verify that unrelated DOCX package parts are unchanged.
7. Render the final DOCX and inspect every page. Fix layout regressions caused by the edits while preserving the journal's existing formatting. Re-render after further changes.
8. Save the result through the applicable file workflow and return the updated DOCX with a concise completion message. Do not send it to third parties unless explicitly requested.

## Produce a change table when requested

Create a separate DOCX containing a clear title, a short scope statement, and one row per applied correction:

| ID | Location | Before | After |
| --- | --- | --- | --- |

Use the verified edit record. If only the conversation's list is available, identify that limitation in the response and do not imply independent verification. Exclude rejected or unapplied suggestions, or clearly label their status if the user requests them.

Include reasons only when requested or useful. Show exact changed excerpts; mark omitted surrounding text. Keep the table readable with sensible column widths, repeated headers across pages, and rows that do not split unnecessarily. Avoid a nearly empty final page without making the text cramped. Render and inspect the document before delivery.

## Completion checks

- Correct source and approved scope used.
- Every authorized correction accounted for.
- Scientific meaning and unapproved content preserved.
- Formatting and embedded content checked.
- Change report, if requested, matches the applied edits.
- Final deliverables saved and linked; no unsupported completion claims.
