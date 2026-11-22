# Beyond Accuracy: Answer Leakage and Prompt Structure in LLM Diagnostic Reasoning on MedR-Bench

Code, data and outputs for the CISS 2027 submission by Akshay Bhuvaneswari Ramakrishnan and Meenalosini Vimal Cruz (School of Computing, Georgia Southern University).

## Study in brief
- **Cases:** 120 diagnosis cases from MedR-Bench (Qiu et al., Nat. Commun. 2025), oracle setting. 70 rare and 50 common, sampled with seed 42 and relabelled M001–M120, in 15 batches of 8.
- **Arm A (redacted text):** statements of the diagnosis replaced by `[REDACTED]`. 56 cases redacted, 42 with no match, 22 kept (see `dataset/leakage_report.md`).
- **Arm B (original text):** the bare prompt only.
- **Prompts:** S1 bare, S2 stepwise, S3 structured (`prompts/packs/`).
- **Models:** Claude Opus 5.5 (medium effort) and Gemini 4 Neon (medium thinking), run through their chat interfaces in November 2026. Each batch went into a new temporary chat. That gives 90 Arm A runs plus 30 Arm B runs.
- **Endpoints:**
  - **Accuracy:** strict and lenient scores on a 0/1/2 rubric, graded blind to condition.
  - **Explanation coverage:** the share of the clinician's reference reasoning steps covered, corrected for length with a permutation null.
  - **Reasoning soundness:** rated 0/1/2 by two LLM judges (ChatGPT and DeepSeek, free web versions) on 40 cases.

## Folder layout
| Folder | Contents |
|---|---|
| `paper/` | LaTeX source (`main.tex`), figure, and the compiled draft (`main.pdf`) |
| `dataset/` | `master_dataset.csv` (original and redacted text per case), `answer_key.csv` (reference diagnosis and reasoning from MedR-Bench), `post_dx_cue_flags.csv`, `leakage_report.md`, `README_PROTOCOL.md`, run order and run log |
| `prompts/packs/` | The exact text pasted into each chat (arm, style, batch) |
| `raw_outputs/` | Unedited model outputs: 120 files |
| `grading/` | `grades.txt` (anonymised grades a–h per case), `mapping_frozen.json` (letter-to-condition key), `graded_long.csv` (decoded, 960 rows), `graded_auto.csv` (with scripted graders G1/G2) |
| `grading/accuracy_audit/` | Blinded 180-item cross-family audit: the paste files, DeepSeek's grades, and the key |
| `soundness/` | 10 judge packs and the key, ChatGPT and DeepSeek scores (160 items each), scored items, and a 30-item anchor file for a human rater (pending) |
| `analysis/` | Scripts for case selection and redaction, pack building, grade decoding, statistics, explanation coverage, the soundness analysis, tables and the figure |

## Rubrics
- **Accuracy:**
  - 2: same primary entity as the reference.
  - 1: right disease family, or one component of a multi-part diagnosis.
  - 0: anything else.
- **Soundness:** this is the pilot rubric.
  - 2: decisive findings identified, valid logic, main alternatives excluded with evidence, and no material error.
  - 1: partial.
  - 0: unsound.

  A wrong diagnosis cannot score 2.

## Reproducing the analysis
The scripts were run in the original working environment and contain absolute paths (`/home/claude/...` and a scratch directory). Change these to point at this repository's folders before rerunning. Python 3 with `scipy`, `scikit-learn` and `matplotlib` is enough.

## Notes and limitations
- **Redaction is not complete.** The redaction is a lower bound on leakage, and it also removed some legitimate findings.
- **Single runs.** Chat interfaces expose no temperature or seed, so each condition was run once.
- **Accuracy grader.** Accuracy was graded by a Claude-family LLM and audited on 180 items by DeepSeek.
- **Soundness judges.** Soundness was rated by LLM judges whose model versions the free interfaces did not display. Human anchor ratings are pending.
- **Data licence.** MedR-Bench case text belongs to its original sources; check the MedR-Bench licence before making this repository public.
