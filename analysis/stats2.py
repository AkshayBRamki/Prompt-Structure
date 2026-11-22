exec(open('stats.py').read().split('print("\\n== Pooled')[0].replace('print(','(lambda *a,**k:None)('))
import csv,collections,statistics
from scipy.stats import binomtest,spearmanr,mannwhitneyu
base='/home/claude/leakfree_experiment/dataset/'
mast={r['case_id']:r for r in csv.DictReader(open(base+'master_dataset.csv',encoding='utf-8'))}
flags={r['case_id'] for r in csv.DictReader(open(base+'post_dx_cue_flags.csv',encoding='utf-8'))}
print("flags",len(flags))
S=['S1_bare','S2_stepwise','S3_structured']
print("== Pooled style test (both models, case-level paired, strict)")
for s in S[1:]:
    b=c=0
    for m in('Claude','Gemini'):
        for cs in cases:
            x=D[(m,'A_redacted','S1_bare',cs)]['strict'];y=D[(m,'A_redacted',s,cs)]['strict']
            b+=(x==1 and y==0);c+=(x==0 and y==1)
    print(s,"S1-only",b,"style-only",c,f"p={binomtest(b,b+c,.5).pvalue:.4f}")
print("\n== Instability: cases where correctness (strict) differs across the 3 styles, Arm A")
for m in('Claude','Gemini'):
    unst=[cs for cs in cases if len({D[(m,'A_redacted',s,cs)]['strict'] for s in S})>1]
    allc=[cs for cs in cases if all(D[(m,'A_redacted',s,cs)]['strict']==1 for s in S)]
    allw=[cs for cs in cases if all(D[(m,'A_redacted',s,cs)]['strict']==0 for s in S)]
    print(m,"unstable",len(unst),"always-correct",len(allc),"always-wrong",len(allw))
both=[cs for cs in cases if all(D[(m,'A_redacted',s,cs)]['strict']==0 for m in('Claude','Gemini') for s in S)]
print("wrong for both models in all 3 styles:",len(both),both)
print("\n== Rare vs common (Arm A strict, per cell)")
for st in('rare','common'):
    cs_=[c for c in cases if mast[c]['stratum']==st]
    for m in('Claude','Gemini'):
        print(st,len(cs_),m,[f"{s[:2]} {sum(D[(m,'A_redacted',s,c)]['strict'] for c in cs_)/len(cs_):.3f}" for s in S],f"B {sum(D[(m,'B_original','S1_bare',c)]['strict'] for c in cs_)/len(cs_):.3f}")
print("\n== Cue-flag cases (34) vs other (86): Arm A S1 strict and A->B gain")
for name,cs_ in(('flagged',[c for c in cases if c in flags]),('other',[c for c in cases if c not in flags])):
    for m in('Claude','Gemini'):
        a=sum(D[(m,'A_redacted','S1_bare',c)]['strict'] for c in cs_)/len(cs_);b=sum(D[(m,'B_original','S1_bare',c)]['strict'] for c in cs_)/len(cs_)
        print(name,len(cs_),m,f"A {a:.3f} B {b:.3f} gain {b-a:+.3f}")
print("\n== Leak status: A->B gain (S1 strict) by redaction status")
for ls in sorted({r['leak_status'] for r in mast.values()}):
    cs_=[c for c in cases if mast[c]['leak_status']==ls]
    for m in('Claude','Gemini'):
        a=sum(D[(m,'A_redacted','S1_bare',c)]['strict'] for c in cs_)/len(cs_);b=sum(D[(m,'B_original','S1_bare',c)]['strict'] for c in cs_)/len(cs_)
        print(ls,len(cs_),m,f"A {a:.3f} B {b:.3f} gain {b-a:+.3f}")
print("\n== Word count (mean words per output) and correlation with correctness, Arm A")
for m in('Claude','Gemini'):
    for s in S+[]:
        w=[D[(m,'A_redacted',s,c)]['words'] for c in cases]
        print(m,s,f"mean {statistics.mean(w):.1f} median {statistics.median(w)}")
    w=[D[(m,'A_redacted',s,c)]['words'] for s in S for c in cases];y=[D[(m,'A_redacted',s,c)]['strict'] for s in S for c in cases]
    print(m,"spearman words~strict",spearmanr(w,y))
    # within-style
    for s in S:
        w=[D[(m,'A_redacted',s,c)]['words'] for c in cases];y=[D[(m,'A_redacted',s,c)]['strict'] for c in cases]
        r=spearmanr(w,y);print("  ",s,f"rho={r.statistic:.3f} p={r.pvalue:.3f}")
print("\n== Strict-vs-lenient gap (answers that are 'lenient only')")
for m in('Claude','Gemini'):
    for a,s in[('A_redacted',x) for x in S]+[('B_original','S1_bare')]:
        n=sum(1 for c in cases if D[(m,a,s,c)]['grade']==1);print(m,a,s,"lenient-only",n)
tot=sum(1 for r in rows if r['grade']==1);print("total lenient-only",tot,"of 960; wrong",sum(1 for r in rows if r['grade']==0))
