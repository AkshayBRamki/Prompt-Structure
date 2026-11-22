import csv,re,glob,random,json
R=random.Random(2026)
base='/home/claude/leakfree_experiment/'
mast={r['case_id']:r for r in csv.DictReader(open(base+'dataset/master_dataset.csv',encoding='utf-8'))}
key={r['case_id']:r for r in csv.DictReader(open(base+'dataset/answer_key_DO_NOT_PASTE.csv',encoding='utf-8'))}
rare=sorted(c for c in mast if mast[c]['stratum']=='rare');com=sorted(c for c in mast if mast[c]['stratum']=='common')
cases=sorted(R.sample(rare,23)+R.sample(com,17))
resp={}
for m in('Claude','Gemini'):
    for s in('S2_stepwise','S3_structured'):
        for f in glob.glob(base+f'raw_outputs/{m}_A/A_redacted/*/*{s}*.txt'):
            for blk in re.split(r'(?m)^CASE:\s*(?=M\d+)',open(f,encoding='utf-8').read())[1:]:
                cid=blk.split()[0];resp[(m,s,cid)]=blk[len(cid):].strip()
LAB=r'(?im)^\s*(REASONING|KEY FINDINGS|DIFFERENTIAL|EVIDENCE FOR AND AGAINST|EXCLUSIONS AND COMMITMENT)\s*:\s*'
def norm(t):
    t=re.sub(LAB,'',t)
    t=re.sub(r'(?im)^\s*FINAL DIAGNOSIS\s*:\s*','Final diagnosis: ',t)
    t=re.sub(r'\n{2,}','\n',t).strip()
    return t
ids=list(range(1,161));R.shuffle(ids)
items=[];k=0
for c in cases:
    four=[(m,s) for m in('Claude','Gemini') for s in('S2_stepwise','S3_structured')];R.shuffle(four)
    for m,s in four:
        items.append(dict(item=f"R{ids[k]:03d}",case=c,model=m,style=s,text=norm(resp[(m,s,c)])));k+=1
json.dump(items,open('items_KEY.json','w'),indent=1)
with open('soundness_KEY.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['item','case','model','style'])
    for it in items: w.writerow([it['item'],it['case'],it['model'],it['style']])
RUB="""You are an expert clinician rating the SOUNDNESS OF DIAGNOSTIC REASONING written by AI systems. For each case you get the case as the AI saw it, the reference diagnosis, the clinician-written reference reasoning, and several AI responses (labelled with item IDs such as R017). Rate EACH response independently on its own merits, not by comparing it with the other responses.

Score each response 0, 1 or 2:
2 = SOUND: identifies the findings that actually drive the diagnosis, links them to the diagnosis with valid clinical logic consistent with the reference reasoning, and rules out the main competing alternatives with appropriate evidence (or the case leaves no serious alternative). No material factual or logical error.
1 = PARTIAL: right direction, but a key step is missing (e.g. pattern-matching without excluding an obvious alternative, or ignoring a decisive finding), or it contains an error that does not drive the conclusion.
0 = UNSOUND: reasoning is wrong, irrelevant or absent; contains a material factual error; or the conclusion does not follow from the stated evidence.

Rules:
- Do NOT reward length, formatting, the number of differentials listed, or confident tone. A short response that names the decisive findings and excludes the main alternative can score 2. A long response with a material error scores 0 or 1.
- A response whose final diagnosis is wrong cannot score 2.
- Some case details were removed and shown as [REDACTED]. Do not penalise a response for not using information that was redacted.
- Judge only the reasoning shown; do not assume reasoning that is not written.

OUTPUT FORMAT: reply with ONLY one line per item, exactly `item_id: score` (e.g. `R017: 2`). No explanations.
"""
def caseblock(c,its):
    ref=' '.join(key[c]['reference_differential_reasoning'].split('\n'))
    s=f"===== CASE =====\n{mast[c]['case_redacted'].strip()}\n\nREFERENCE DIAGNOSIS: {key[c]['ground_truth_diagnosis']}\nREFERENCE REASONING (clinician): {key[c]['reference_differential_reasoning'].strip()}\n\n"
    for it in its: s+=f"--- RESPONSE {it['item']} ---\n{it['text']}\n\n"
    return s
bycase=[(c,[it for it in items if it['case']==c]) for c in cases]
R.shuffle(bycase)
packs=[bycase[i:i+4] for i in range(0,40,4)]
for n,p in enumerate(packs,1):
    head=RUB+"\nCASES (part 1 of 10):\n\n" if n==1 else f"Continue with the SAME rubric and SAME output format (`item_id: score`, one line per item, no explanations). Rate each response independently. Do not reward length or formatting. CASES (part {n} of 10):\n\n"
    txt=head+''.join(caseblock(c,its) for c,its in p)
    open(f'soundness_pack_{n:02d}.txt','w',encoding='utf-8').write(txt)
    print(n,len(txt.split()),'words',sum(len(its) for c,its in p),'items')
# anchor: 30 items
anc=R.sample(items,30);ac={}
for it in anc: ac.setdefault(it['case'],[]).append(it)
txt="ANCHOR RATING (Akshay). Same rubric as the judges, pasted below. Rate each response 0/1/2 and write lines like `R017: 2`.\n\n"+RUB.split('OUTPUT FORMAT')[0]+"\n"+''.join(caseblock(c,its) for c,its in ac.items())
open('anchor_30_for_Akshay.txt','w',encoding='utf-8').write(txt);print('anchor',len(txt.split()),'words',len(ac),'cases')
