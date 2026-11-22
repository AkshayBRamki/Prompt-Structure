import csv,re,glob,random,statistics,math,json
from scipy.stats import wilcoxon
random.seed(11)
STOP=set("a an the of and or with without to in on at by for from as is are was were be been this that these those it its their there which who whom his her patient patients case further then also after before during while including such may can could would should showed shows revealed reveals led lead leading based consistent suggesting suggested noted note found finding findings demonstrated demonstrating confirmed confirm indicated indicating raised concern prompting prompted initial initially diagnosis diagnostic diagnosed likely most more less not no".split())
def stem(w):
    for s in("ations","ation","itis","ies","ing","ed","es","s","al","ic"):
        if len(w)>5 and w.endswith(s): return w[:-len(s)]
    return w
def toks(t): return {stem(w) for w in re.findall(r"[a-z0-9]+",t.lower()) if w not in STOP and len(w)>2}
key={r['case_id']:r['reference_differential_reasoning'] for r in csv.DictReader(open('/home/claude/leakfree_experiment/dataset/answer_key_DO_NOT_PASTE.csv',encoding='utf-8'))}
steps={c:[toks(b) for b in re.split(r'\n\s*[-*•]\s*|\n\s*\d+[.)]\s*',"\n"+t) if len(toks(b))>=3] for c,t in key.items()}
for c in steps: assert steps[c],c
def cover(resp_toks,c,thr=0.5):
    st=steps[c];return sum(len(s&resp_toks)/len(s)>=thr for s in st)/len(st)
resp={}
for model in('Claude','Gemini'):
    for style in('S2_stepwise','S3_structured'):
        for f in glob.glob(f'/home/claude/leakfree_experiment/raw_outputs/{model}_A/A_redacted/*/*{style}*.txt'):
            txt=open(f,encoding='utf-8').read()
            for blk in re.split(r'(?m)^CASE:\s*(?=M\d+)',txt)[1:]:
                cid=blk.split()[0].strip();resp[(model,style,cid)]=blk
print(len(resp))
cases=sorted(key)
rows=[]
for (model,style,cid),blk in resp.items():
    # drop the final-diagnosis line so the answer itself is not counted as reasoning
    body=re.sub(r'(?is)FINAL DIAGNOSIS:.*$','',blk)
    rt=toks(body);raw=cover(rt,cid)
    others=random.sample([c for c in cases if c!=cid],20)
    null=statistics.mean(cover(rt,o) for o in others)
    rows.append(dict(model=model,style=style,case=cid,words=len(body.split()),raw=raw,null=null,adj=raw-null))
json.dump(rows,open('reason_rows.json','w'))
print("n rows",len(rows))
for m in('Claude','Gemini'):
    for s in('S2_stepwise','S3_structured'):
        r=[x for x in rows if x['model']==m and x['style']==s]
        print(m,s,len(r),"raw %.3f null %.3f adj %.3f words %.0f"%(statistics.mean(x['raw'] for x in r),statistics.mean(x['null'] for x in r),statistics.mean(x['adj'] for x in r),statistics.mean(x['words'] for x in r)))
    a={x['case']:x['adj'] for x in rows if x['model']==m and x['style']=='S2_stepwise'};b={x['case']:x['adj'] for x in rows if x['model']==m and x['style']=='S3_structured'}
    d=[b[c]-a[c] for c in cases];w=wilcoxon(d)
    print(m,"S3-S2 adj coverage mean diff %.3f median %.3f p=%.2g"%(statistics.mean(d),statistics.median(d),w.pvalue),"| S3 higher in",sum(x>0 for x in d),"lower in",sum(x<0 for x in d))
