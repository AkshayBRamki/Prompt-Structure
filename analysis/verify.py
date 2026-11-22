import json,csv,re,os,glob,sys
sys.path.insert(0,'.')
import build
OUT='/home/claude/leakfree_experiment'
rows=list(csv.DictReader(open(f'{OUT}/dataset/master_dataset.csv',encoding='utf-8')))
key={r['case_id']:r for r in csv.DictReader(open(f'{OUT}/dataset/answer_key_DO_NOT_PASTE.csv',encoding='utf-8'))}
print('cases',len(rows),'rare',sum(r['stratum']=='rare' for r in rows),'common',sum(r['stratum']=='common' for r in rows),'unique pmc',len({r['pmc_id'] for r in rows}))
# full-label survival in redacted text
def n(s): return re.sub(r'[^a-z0-9]+',' ',s.lower()).strip()
sur=[]
for r in rows:
    gt=re.sub(r'\([^)]*\)','',key[r['case_id']]['ground_truth_diagnosis']).strip(' .'); 
    if len(n(gt))>=6 and n(gt) in n(r['case_redacted']): sur.append((r['case_id'],r['leak_status'],gt[:60]))
print('full GT label still present in redacted text:',len(sur)); [print(' ',s) for s in sur]
sur0=[r['case_id'] for r in rows if n(re.sub(r'\([^)]*\)','',key[r['case_id']]['ground_truth_diagnosis']).strip(' .')) in n(r['case_original'])]
print('full GT label present in ORIGINAL text:',len(sur0),'cases')
# packs: file counts and answer-key contamination
packs=glob.glob(f'{OUT}/packs/**/*.txt',recursive=True); print('pack files',len(packs))
bad=[p for p in packs if re.search(r'ground.truth|reference_|answer key',open(p,encoding='utf-8').read(),re.I)]
print('packs mentioning answer-key words:',bad[:3])
# each batch has 8 cases and same case ids across styles
import collections
ids=collections.defaultdict(set)
for p in packs:
    t=open(p,encoding='utf-8').read(); m=re.findall(r'=== CASE (M\d{3}) ===',t); assert len(m)==8,(p,len(m))
    ids[(p.split('/')[-1])].add(tuple(m))
print('batch composition identical across arms/styles:',all(len(v)==1 for v in ids.values()))
a=open(f'{OUT}/packs/A_redacted/S3_structured/batch_01.txt',encoding='utf-8').read(); b=open(f'{OUT}/packs/B_original/S3_structured/batch_01.txt',encoding='utf-8').read()
print('arm A vs B differ in batch_01:',a!=b)
# redacted placeholder count
print('total [REDACTED] tokens in master:',sum(r['case_redacted'].count('[REDACTED]') for r in rows))
# anchor recall of the detector over the full 957 for the 13 cases the earlier audit named
D=json.load(open('/tmp/medrbench_src/MedRBench/data/MedRBench/diagnosis_957_cases_with_rare_disease_491.json'))
anch=['dyggve','biermer','gist|gastrointestinal stromal','fava|fibro-adipose','myoepithelioma','hydatidiform','testicular ectopia','hemangiopericytoma','hepatoblastoma','bia-alcl|breast implant','hemangioendothelioma','lissencephaly|heterotopia','cysticercosis']
hit=0;tot=0
for p in anch:
    for i,v in D.items():
        g=v['generate_case']
        if re.search(p,g['diagnosis_results'],re.I):
            red,fl=build.process(g['case_summary'],g['diagnosis_results']); tot+=1; hit+= bool(fl)
print(f'detector flags {hit}/{tot} dataset cases matching the 13 earlier-audit diagnoses (some of these are not the same cases)')
