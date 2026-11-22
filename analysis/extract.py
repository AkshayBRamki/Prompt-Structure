import re,glob,csv,json,random,os
R='/home/claude/leakfree_experiment/raw_outputs'
files=glob.glob(R+'/**/*.txt',recursive=True)
rec=[]  # model,arm,style,batch,case,dx,words
for f in files:
    m=re.search(r'(Claude|Gemini)_(A_redacted|B_original)_(S\d_\w+?)_B0*(\d+)\.txt',f)
    mod,arm,sty,b=m.group(1),m.group(2),m.group(3),int(m.group(4))
    t=open(f,encoding='utf-8',errors='replace').read()
    parts=re.split(r'^[\W_]*CASE[\W_]*\s*:?\s*[\W_]*(?=M\d{3})',t,flags=re.M|re.I)
    for p in parts[1:]:
        cid=p[:4]
        fd=re.search(r'^[\W_]*FINAL DIAGNOSIS[\W_]*:?[\W_]*\s*(.+)$',p,re.M|re.I)
        dx=re.sub(r'\*+','',fd.group(1)).strip()
        rec.append(dict(model=mod,arm=arm,style=sty,batch=b,case=cid,dx=dx,words=len(p.split())))
json.dump(rec,open('/tmp/claude-0/-home-claude/ee83b28a-b1e9-5ffe-8928-0cc102c4c8da/scratchpad/records.json','w'),indent=0)
print(len(rec))
from collections import Counter
print(Counter((r['model'],r['arm'],r['style']) for r in rec))
