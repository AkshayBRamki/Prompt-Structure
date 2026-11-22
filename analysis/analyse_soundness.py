import json,csv,statistics as st,math
from scipy.stats import wilcoxon,binomtest,spearmanr
from sklearn.metrics import cohen_kappa_score
def load(f): return {a.strip():int(b) for a,b in (l.split(':') for l in open(f) if ':' in l)}
CG,DS=load('chatgpt.txt'),load('deepseek.txt')
items=json.load(open('items_KEY.json'))
assert len(CG)==len(DS)==160 and set(CG)==set(DS)=={i['item'] for i in items}
g={(r['model'],r['style'],r['case']):int(r['grade']) for r in csv.DictReader(open('/home/claude/paper/graded_auto.csv',encoding='utf-8')) if r['arm']=='A_redacted'}
for i in items:
    i['cg']=CG[i['item']];i['ds']=DS[i['item']];i['mean']=(i['cg']+i['ds'])/2;i['acc']=int(g[(i['model'],i['style'],i['case'])]==2)
    i['words']=len(i['text'].split())
ids=[i['item'] for i in items];a=[CG[x] for x in ids];b=[DS[x] for x in ids]
print("== Judge agreement (160 items)")
print("exact %.3f  kappa %.3f  linear-weighted %.3f  sound(2)-vs-not kappa %.3f  adjacent %.3f"%(sum(x==y for x,y in zip(a,b))/160,cohen_kappa_score(a,b),cohen_kappa_score(a,b,weights='linear'),cohen_kappa_score([x==2 for x in a],[y==2 for y in b]),sum(abs(x-y)<=1 for x,y in zip(a,b))/160))
print("ChatGPT lower in",sum(x<y for x,y in zip(a,b)),"higher in",sum(x>y for x,y in zip(a,b)))
def wil(k,n,z=1.96):
    p=k/n;d=1+z*z/n;c=p+z*z/(2*n);h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n));return (c-h)/d,(c+h)/d
print("\n== Soundness by model x style (n=40 each)")
for m in('Claude','Gemini'):
    for s in('S2_stepwise','S3_structured'):
        r=[i for i in items if i['model']==m and i['style']==s]
        out=[]
        for j in('cg','ds'):
            k=sum(i[j]==2 for i in r);lo,hi=wil(k,40);out.append(f"{j} sound {k}/40={100*k/40:.0f}% [{100*lo:.0f},{100*hi:.0f}] mean {st.mean(i[j] for i in r):.2f}")
        kb=sum(i['cg']==2 and i['ds']==2 for i in r)
        print(m,s,' | '.join(out),f"| both-sound {kb}/40 | acc {sum(i['acc'] for i in r)}/40 | words {st.mean(i['words'] for i in r):.0f}")
print("\n== S3 vs S2 paired (40 cases)")
for m in('Claude','Gemini'):
    A={i['case']:i for i in items if i['model']==m and i['style']=='S2_stepwise'};B={i['case']:i for i in items if i['model']==m and i['style']=='S3_structured'}
    for j in('cg','ds','mean'):
        d=[B[c][j]-A[c][j] for c in A];nz=[x for x in d if x!=0]
        p=wilcoxon(nz).pvalue if nz else 1
        print(m,j,"mean diff %+.3f  S3 higher %d lower %d  Wilcoxon p=%.3f"%(st.mean(d),sum(x>0 for x in d),sum(x<0 for x in d),p))
    for j in('cg','ds'):
        up=sum(B[c][j]==2 and A[c][j]!=2 for c in A);dn=sum(A[c][j]==2 and B[c][j]!=2 for c in A)
        print("  ",m,j,"sound only in S3:",up,"only in S2:",dn,"McNemar p=%.3f"%(binomtest(up,up+dn,.5).pvalue if up+dn else 1))
    da=[B[c]['acc']-A[c]['acc'] for c in A];print("  ",m,"accuracy S3-S2 on these 40: %+.1f pts"%(100*st.mean(da)))
print("\n== Dissociation: correct answers (strict) that are NOT rated sound")
for m in('Claude','Gemini'):
    for s in('S2_stepwise','S3_structured'):
        r=[i for i in items if i['model']==m and i['style']==s and i['acc']]
        for j in('cg','ds'):
            k=sum(i[j]<2 for i in r)
            print(m,s,j,f"correct n={len(r)}, not sound {k} ({100*k/len(r):.0f}%)",end=' || ')
        print()
    w=[i for i in items if i['model']==m and not i['acc']]
    print("   ",m,"wrong answers rated 2 by any judge:",sum(i['cg']==2 or i['ds']==2 for i in w),"of",len(w))
print("\n== Length check: within style, soundness vs words (Spearman, mean of judges)")
for s in('S2_stepwise','S3_structured'):
    r=[i for i in items if i['style']==s];x=spearmanr([i['words'] for i in r],[i['mean'] for i in r]);print(s,"rho %.2f p=%.3f"%(x.statistic,x.pvalue))
json.dump(items,open('items_scored.json','w'),indent=1)
