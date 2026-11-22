import json,csv,os,re,sys
sys.path.insert(0,'.')
SRC='/tmp/medrbench_src/MedRBench/data/MedRBench/diagnosis_957_cases_with_rare_disease_491.json'
D=json.load(open(SRC)); rows=json.load(open('rows_cur.json'))
OUT='/home/claude/leakfree_experiment'
for sub in ['packs','outputs','dataset']: os.makedirs(f'{OUT}/{sub}',exist_ok=True)
IRREDUCIBLE=['M014','M023','M040','M054','M058','M062','M084','M094','M107','M109','M112']
HISTORY=['M008','M038','M090','M095','M110','M116']
FALSEPOS=['M026','M028','M043','M097','M101','M119']
def status(r):
    c=r['case_id']
    if r['applied']: return 'redacted'
    if c in IRREDUCIBLE: return 'kept_irreducible_imaging_label'
    if c in HISTORY: return 'kept_history_premise'
    if c in FALSEPOS: return 'kept_false_positive'
    return 'clean_no_match'
for r in rows: r['status']=status(r)
# 1. master dataset
with open(f'{OUT}/dataset/master_dataset.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['case_id','pmc_id','stratum','leak_status','n_patterns_applied','case_original','case_redacted'])
    for r in rows: w.writerow([r['case_id'],r['pmc_id'],r['stratum'],r['status'],len(r['applied']),r['case_original'],r['case_redacted']])
# 2. answer key (do NOT paste into any model)
with open(f'{OUT}/dataset/answer_key_DO_NOT_PASTE.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['case_id','pmc_id','ground_truth_diagnosis','reference_final_diagnosis_text','reference_differential_reasoning'])
    for r in rows:
        g=D[r['pmc_id']]['generate_case']
        w.writerow([r['case_id'],r['pmc_id'],g['diagnosis_results'].strip(),g['final_diagnosis'].strip(),g['differential_diagnosis'].strip()])
# 3. prompts
COMMON_HEAD=("You will be given 8 clinical cases. Use only the information in each case. Do not search the web or use any tools. "
 "Answer all 8 cases, in order, and use exactly the output format below for every case.\n\n")
STYLES={
'S1_bare':("Give the most likely final diagnosis for each case.\n\nOutput format for every case:\nCASE: <case id>\nFINAL DIAGNOSIS: <diagnosis>\n"),
'S2_stepwise':("For each case, think step by step, then give the most likely final diagnosis.\n\nOutput format for every case:\nCASE: <case id>\nREASONING: <your step-by-step reasoning>\nFINAL DIAGNOSIS: <diagnosis>\n"),
'S3_structured':("For each case, complete this structured diagnostic work-up.\n\nOutput format for every case:\nCASE: <case id>\n1. KEY FINDINGS: the clinically decisive findings, with their significance\n2. DIFFERENTIAL: 3-5 candidate diagnoses, ranked\n3. EVIDENCE FOR AND AGAINST: for each candidate, the findings that support it and the findings that argue against it\n4. EXCLUSIONS AND COMMITMENT: which candidates you exclude and why, and which you commit to by that reasoning\n5. FINAL DIAGNOSIS: <diagnosis>\n"),
}
batches=[rows[i:i+8] for i in range(0,120,8)]
assert len(batches)==15 and all(len(b)==8 for b in batches)
def case_block(r,arm): return f"=== CASE {r['case_id']} ===\n"+(r['case_original'] if arm=='B_original' else r['case_redacted']).strip()+"\n"
log=[]
for arm in ['A_redacted','B_original']:
    for sty,instr in STYLES.items():
        os.makedirs(f'{OUT}/packs/{arm}/{sty}',exist_ok=True)
        for bi,b in enumerate(batches,1):
            txt=COMMON_HEAD+instr+"\n"+"\n".join(case_block(r,arm) for r in b)
            fn=f'{OUT}/packs/{arm}/{sty}/batch_{bi:02d}.txt'
            open(fn,'w',encoding='utf-8').write(txt)
            for model in ['Claude','Gemini']:
                rid=f'{model}_{arm}_{sty}_B{bi:02d}'
                log.append([rid,model,arm,sty,bi,';'.join(r['case_id'] for r in b),f'packs/{arm}/{sty}/batch_{bi:02d}.txt',f'outputs/{rid}.txt','','','','',''])
with open(f'{OUT}/run_log.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['run_id','model','arm','style','batch','case_ids','prompt_file','save_output_as','status','date_run','exact_model_version','chat_id_or_url','notes']); w.writerows(log)
print('files:',sum(len(fs) for _,_,fs in os.walk(OUT)),' log rows:',len(log))
import collections
print(collections.Counter(r['status'] for r in rows))
