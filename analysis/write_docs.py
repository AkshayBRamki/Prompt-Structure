import csv,json,re
OUT='/home/claude/leakfree_experiment'
rows=list(csv.DictReader(open(f'{OUT}/dataset/master_dataset.csv',encoding='utf-8')))
cur={r['case_id']:r for r in json.load(open('rows_cur.json'))}
from collections import Counter
c=Counter(r['leak_status'] for r in rows)
L=[]
L.append('# Leakage report (120-case sample, MedR-Bench oracle diagnosis input)\n')
L.append('Source: MAGIC-AI4Med/MedRBench `diagnosis_957_cases_with_rare_disease_491.json`, field `generate_case.case_summary` (the text the models see).\n')
L.append('Sample: random stratified, 70 rare + 50 common, seed 42, shuffled and relabelled M001-M120. **This is NOT the pilot sample** (the pilot case IDs and sampling code were not recoverable), so results cannot be paired with pilot results.\n')
L.append('## Counts\n')
L.append(f'- Redacted (diagnostic label / organism / gene / entity named in a conclusion or result): **{c["redacted"]}** of 120\n- Full ground-truth label verbatim in the original text: 15 of 120; after redaction: 0\n- Kept, label is itself an imaging/exam finding (cannot be removed without deleting the evidence): {c["kept_irreducible_imaging_label"]}\n- Kept, pre-existing condition in history (not the answer): {c["kept_history_premise"]}\n- Kept, detector false positive: {c["kept_false_positive"]}\n- No match: {c["clean_no_match"]}\n')
L.append('## Redaction rule\n')
L.append('Replaced with `[REDACTED]`: the diagnostic label or its abbreviation when it appears in a conclusion ("confirmed X", "consistent with X", "histology: X"), an identified organism, gene, or tumour type, or a component of the final diagnosis stated as a result. Not redacted: descriptive imaging or exam findings, and conditions listed as pre-existing history when they are only part of the answer. Indirect cues remain (e.g. Hurley stage in a hidradenitis case), so the leak count is a lower bound, as in the earlier audit.\n')
L.append('## Judgement calls to veto before you run\n')
L.append('- Organism and gene names were redacted in result lines (e.g. M041, M060, M067, M068, M105). That removes the decisive finding in those cases, so they become harder than in the original benchmark. If you prefer, restore them from `case_original`.\n- The 9 irreducible cases (M014, M023, M040, M054, M062, M094, M107, M109, M112) still contain imaging findings that essentially state the diagnosis. Report them as a limitation or drop them from the leak-free analysis.\n- The 27.5% (33/120) leak rate in the earlier audit used a looser definition; this sample is not directly comparable.\n')
L.append('## Per-case redactions\n\n| Case | Status | Removed |\n|---|---|---|')
for r in rows:
    if r['leak_status']=='redacted':
        L.append(f"| {r['case_id']} | redacted | "+'; '.join(p[0].replace('|','/') for p in cur[r['case_id']]['applied'])+' |')
    elif r['leak_status']!='clean_no_match':
        L.append(f"| {r['case_id']} | {r['leak_status']} | - |")
open(f'{OUT}/leakage_report.md','w',encoding='utf-8').write('\n'.join(L)+'\n')
R='''# Run protocol (same for every condition)

**Design.** 120 cases, 2 models (Claude, Gemini), 3 prompt styles (S1 bare, S2 stepwise, S3 structured), 15 batches of 8 cases. Batch composition is identical in every condition.
- **Arm A_redacted (required):** 2 models x 3 styles x 15 batches = 90 pastes.
- **Arm B_original (leaky text, for the leakage contrast):** 90 more pastes. If time is short, run S1_bare on both models first (30 pastes).

**Before you start**
1. Use a fresh temporary/incognito chat with memory and personalisation off. Your Claude memory contains this project, which would contaminate the runs.
2. Use the same model and mode for every run in a model's arm. No web search, no deep research. Record the exact model name shown in the app in `run_log.csv`.
3. One new chat per condition (model x arm x style). Paste batch_01, wait for the full answer, then batch_02, and so on in order. Do not edit prompts.
4. Save each raw answer immediately, unedited, as `outputs/<run_id>.txt` (the `save_output_as` column). Never leave an answer only in a chat.
5. If an answer is cut off or skips a case, rerun that batch in a new chat and note it in `run_log.csv`. Do not stitch answers together.
6. Never paste `answer_key_DO_NOT_PASTE.csv` into a model.

**Limits to disclose.** Chat interfaces give no control over temperature or seed. The three prompt texts were written fresh (the pilot prompt files were not recoverable), so S1-S3 are not identical to the pilot wording.

**Scoring plan.** Auto-match diagnoses in Python and flag ambiguous ones for your review. Score reasoning soundness blind to model and style on a 40-60 case subset, with a human as the reference rater.
'''
open(f'{OUT}/README_PROTOCOL.md','w').write(R)
