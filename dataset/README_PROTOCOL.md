# Run protocol (same for every condition)

**Design.** 120 cases, 2 models (Claude, Gemini), 3 prompt styles (S1 bare, S2 stepwise, S3 structured), 15 batches of 8 cases. Batch composition is identical in every condition.
- **Arm A_redacted (required):** 2 models x 3 styles x 15 batches = 90 pastes.
- **Arm B_original (leaky text, for the leakage contrast):** 90 more pastes. If time is short, run S1_bare on both models first (30 pastes).

**Before you start**
1. Use a fresh temporary/incognito chat with memory and personalisation off. Your Claude memory contains this project, which would contaminate the runs.
2. Use the same model and mode for every run in a model's arm. No web search, no deep research. Record the exact model name shown in the app in `run_log.csv`.
3. **One new chat per batch** (revised: both Hassanein 2026 and Moleka 2026 ran every query in a fresh session to prevent carry-over). Paste one batch file, wait for the full answer, save it, close the chat, open a new one for the next batch. Do not edit prompts. Run the 6 conditions in a randomised order (note the order and date in `run_log.csv`) so model drift or fatigue is not confounded with style.
4. Save each raw answer immediately, unedited, as `outputs/<run_id>.txt` (the `save_output_as` column). Never leave an answer only in a chat.
5. Regenerate only after a technical failure (answer cut off, case skipped, wrong format), never because the answer looks clinically wrong or right. Record every regeneration in `run_log.csv`. Do not stitch answers together.
6. Never paste `answer_key_DO_NOT_PASTE.csv` into a model.

**Limits to disclose.** Chat interfaces give no control over temperature or seed. The three prompt texts were written fresh (the pilot prompt files were not recoverable), so S1-S3 are not identical to the pilot wording.

**Scoring plan.** Auto-match diagnoses in Python and flag ambiguous ones for your review. Score reasoning soundness blind to model and style on a 40-60 case subset, with a human as the reference rater.

## Pre-specified analysis plan (write this down before the first paste)

- **Primary outcome:** final-diagnosis correctness per case, graded blind to model, style and arm; one fixed rubric (state strict vs lenient before grading).
- **Primary contrasts (per model, Arm A):** S2 vs S1 and S3 vs S1, exact McNemar on paired cases, Holm correction across the contrasts. Report Wilson 95% CIs.
- **Leakage contrast:** Arm B vs Arm A, same model and style, exact McNemar, plus accuracy on the 56 redacted cases vs the 64 others.
- **Per-case instability (from Alkaeed 2026, worst-case instability):** for each case and model, max minus min correctness across the three styles; report the share of cases that flip.
- **Reasoning soundness:** 40-60 case subset, scored blind to model, style, arm and the answer key (Savage 2024 blinded raters to the gold answer and to correctness, and counted logic errors per rationale). Two raters, report Cohen's kappa. Record word count per response and include length as a covariate, because in Hassanein 2026 the prompt with the highest explanation scores also produced the longest outputs (length and quality moved together, so length is a possible confounder).
- **Sensitivity analysis (added after literature review):** `dataset/post_dx_cue_flags.csv` lists 34 cases with therapy/outcome phrases (21 in the redacted set). Report Arm A accuracy on these 34 vs the other 86 (counts unchanged after the round-2 redactions; the 34 are flagged on the original text). Yang 2026 found treatment text inflates recall, so this is a sensitivity check, not an exclusion. The flag is a crude regex, so describe it that way.
- **Null results are valid:** prior work found no significant differences between prompt techniques (Zwanzig 2026) and mixed or adverse effects (Chai 2025). If S2/S3 do not beat S1, report that and the size of the leakage and protocol effects instead.
- **Reasoning scoring is human only:** two blinded raters. Do not use an LLM judge for reasoning quality (Liu 2026 found an AI evaluator missed differences clinicians saw). Diagnosis matching may be auto-scored in Python, with ambiguous cases reviewed by a human.
- **Exclusions and regeneration:** none for clinical reasons; technical-failure regeneration only, logged.
- **Reporting:** STARD-AI style flow (cases, runs, regenerations), exact model names and dates, no temperature control in chat interfaces.
