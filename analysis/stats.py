import csv,collections,math
from scipy.stats import binomtest, spearmanr, mannwhitneyu
rows=list(csv.DictReader(open('graded_long.csv',encoding='utf-8')))
for r in rows:
    for k in('strict','lenient','grade','words'): r[k]=int(r[k])
D={}
for r in rows: D[(r['model'],r['arm'],r['style'],r['case'])]=r
cases=sorted({r['case'] for r in rows})
def wilson(k,n,z=1.96):
    p=k/n;d=1+z*z/n;c=p+z*z/(2*n);a=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))
    return (c-a)/d,(c+a)/d
def mcn(m,a1,s1,a2,s2,met):
    b=c=0
    for cs in cases:
        x=D[(m,a1,s1,cs)][met];y=D[(m,a2,s2,cs)][met]
        if x==1 and y==0:b+=1
        if x==0 and y==1:c+=1
    p=1.0 if b+c==0 else binomtest(b,b+c,0.5).pvalue
    return b,c,p
def holm(ps):
    o=sorted(range(len(ps)),key=lambda i:ps[i]);adj=[0]*len(ps);mx=0
    for r,i in enumerate(o):
        v=min(1,(len(ps)-r)*ps[i]);mx=max(mx,v);adj[i]=mx
    return adj
print("== Accuracy + Wilson")
for m in('Claude','Gemini'):
    for a,s in[('A_redacted','S1_bare'),('A_redacted','S2_stepwise'),('A_redacted','S3_structured'),('B_original','S1_bare')]:
        out=[]
        for met in('strict','lenient'):
            k=sum(D[(m,a,s,c)][met] for c in cases);lo,hi=wilson(k,120)
            out.append(f"{met} {k}/120={k/120:.3f} [{lo:.3f},{hi:.3f}]")
        print(m,a,s,' | '.join(out))
print("\n== McNemar style vs S1 (Arm A), Holm over 4 tests per metric (2 models x 2 styles)")
for met in('strict','lenient'):
    res=[]
    for m in('Claude','Gemini'):
        for s in('S2_stepwise','S3_structured'):
            b,c,p=mcn(m,'A_redacted','S1_bare','A_redacted',s,met);res.append((m,s,b,c,p))
    adj=holm([r[4] for r in res])
    for r,ap in zip(res,adj): print(met,r[0],r[1],f"S1-only-right={r[2]} style-only-right={r[3]} p={r[4]:.4f} holm={ap:.4f}")
print("\n== S3 vs S2")
for met in('strict','lenient'):
    for m in('Claude','Gemini'):
        b,c,p=mcn(m,'A_redacted','S2_stepwise','A_redacted','S3_structured',met);print(met,m,b,c,f"p={p:.4f}")
print("\n== Leakage: Arm B vs Arm A (S1)")
res=[]
for met in('strict','lenient'):
    for m in('Claude','Gemini'):
        b,c,p=mcn(m,'A_redacted','S1_bare','B_original','S1_bare',met);res.append((met,m,b,c,p))
adj=holm([r[4] for r in res])
for r,ap in zip(res,adj): print(r[0],r[1],f"A-only-right={r[2]} B-only-right={r[3]} p={r[4]:.4g} holm={ap:.4g}")
print("\n== Model contrast (Claude vs Gemini) Arm A, per style, strict")
for s in('S1_bare','S2_stepwise','S3_structured'):
    b=c=0
    for cs in cases:
        x=D[('Claude','A_redacted',s,cs)]['strict'];y=D[('Gemini','A_redacted',s,cs)]['strict']
        b+=(x==1 and y==0);c+=(x==0 and y==1)
    print(s,b,c,f"p={binomtest(b,b+c,.5).pvalue:.3f}")
print("\n== Pooled over styles, per-case (strict): rare vs common & leak status")
import os
mast={r['case_id'] if 'case_id' in r else list(r.values())[0]:r for r in csv.DictReader(open('/home/claude/leakfree_experiment/dataset/master_dataset.csv',encoding='utf-8'))}
print(list(next(iter(mast.values())).keys()))
