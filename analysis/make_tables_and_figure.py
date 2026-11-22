import csv,math,statistics,collections
from scipy.stats import binomtest,spearmanr
from sklearn.metrics import cohen_kappa_score
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rows=list(csv.DictReader(open('graded_auto.csv',encoding='utf-8')))
for r in rows:
    for k in('grade','strict','lenient','words','g1','g2'): r[k]=int(r[k])
base='/home/claude/leakfree_experiment/dataset/'
mast={r['case_id']:r for r in csv.DictReader(open(base+'master_dataset.csv',encoding='utf-8'))}
flags={r['case_id'] for r in csv.DictReader(open(base+'post_dx_cue_flags.csv',encoding='utf-8'))}
cases=sorted({r['case'] for r in rows}); N=len(cases)
S=['S1_bare','S2_stepwise','S3_structured']; M=['Claude','Gemini']
# ---- judge
A={int(a):int(b) for a,b in (l.split(':') for l in open('judge2.txt') if ':' in l)}
B={int(a):int(b) for a,b in (l.split(':') for l in open('judge2b.txt') if ':' in l)}
J={**A,**B}; assert len(J)==180
bl=list(csv.DictReader(open('/home/claude/out/human_review_blinded.csv',encoding='utf-8')))
KEY={int(k['item']):int(k['claude_grade']) for k in csv.DictReader(open('/home/claude/out/human_review_KEY.csv',encoding='utf-8'))}
jm={(b['case_id'],' '.join(b['model_answer'].split()).strip().lower()):J[int(b['item'])] for b in bl}
for r in rows:
    r['j']=jm.get((r['case'],' '.join(r['dx'].split()).strip().lower()))
cov=sum(r['j'] is not None for r in rows)
ks=sorted(KEY);y=[KEY[k] for k in ks];p=[J[k] for k in ks]
kap=dict(k3=cohen_kappa_score(y,p),kw=cohen_kappa_score(y,p,weights='linear'),exact=sum(a==b for a,b in zip(y,p))/180,adj=sum(abs(a-b)<=1 for a,b in zip(y,p))/180,
 kstrict=cohen_kappa_score([a==2 for a in y],[b==2 for b in p]),up=sum(1 for a,b in zip(y,p) if a==1 and b==2),down=sum(1 for a,b in zip(y,p) if a==1 and b==0),nb=sum(1 for a in y if a==1),
 s2agree=sum(1 for a,b in zip(y,p) if a==2 and b==2),s2n=sum(1 for a in y if a==2),w0agree=sum(1 for a,b in zip(y,p) if a==0 and b==0),w0n=sum(1 for a in y if a==0))
# ---- scoring variants
def build(f,thr=2):
    return {(r['model'],r['arm'],r['style'],r['case']):int(f(r)>=thr) for r in rows}
V={'mine':build(lambda r:r['grade']),
   'judge':build(lambda r:r['j'] if r['j'] is not None else r['grade']),
   'cons':build(lambda r:min(r['grade'],r['j']) if r['j'] is not None else r['grade']),
   'g1':build(lambda r:r['g1']),'g2':build(lambda r:r['g2']),
   'mine_len':build(lambda r:r['grade'],1)}
def wil(k,n,z=1.96):
    p=k/n;d=1+z*z/n;c=p+z*z/(2*n);a=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n));return (c-a)/d,(c+a)/d
def acc(D,m,a,s,cs=None):
    cs=cs or cases;return sum(D[(m,a,s,c)] for c in cs)/len(cs)
def mc(D,m,a1,s1,a2,s2):
    b=c=0
    for cs in cases:
        x=D[(m,a1,s1,cs)];yv=D[(m,a2,s2,cs)];b+=(x==1 and yv==0);c+=(x==0 and yv==1)
    return b,c,(1.0 if b+c==0 else binomtest(b,b+c,.5).pvalue)
def holm(ps):
    o=sorted(range(len(ps)),key=lambda i:ps[i]);adj=[0]*len(ps);mx=0
    for r,i in enumerate(o):
        v=min(1,(len(ps)-r)*ps[i]);mx=max(mx,v);adj[i]=mx
    return adj
def pf(p): return '<0.001' if p<0.001 else f'{p:.3f}'
def pct(x): return f'{100*x:.1f}'
def sg(x): return f'{100*x:+.1f}'
out=[]
# Table I
T1=[]
for m in M:
    for a,s,lab in[('A_redacted','S1_bare','S1 bare'),('A_redacted','S2_stepwise','S2 stepwise'),('A_redacted','S3_structured','S3 structured'),('B_original','S1_bare','S1, original text')]:
        ks_=sum(V['mine'][(m,a,s,c)] for c in cases);kl=sum(V['mine_len'][(m,a,s,c)] for c in cases)
        lo,hi=wil(ks_,N);lo2,hi2=wil(kl,N)
        T1.append(f"{m} & {lab} & {pct(ks_/N)} [{100*lo:.0f},{100*hi:.0f}] & {pct(kl/N)} [{100*lo2:.0f},{100*hi2:.0f}]\\\\")
open('t1.tex','w').write('\n'.join(T1))
# Table II contrasts
cont=[];pr_s=[];pr_l=[]
for met,D in(('strict',V['mine']),('lenient',V['mine_len'])):
    L=[]
    for m in M:
        for s in S[1:]: L.append((m,f"{s[:2]} vs S1",D,'A_redacted','S1_bare','A_redacted',s))
    pr_s.append(L)
rowsII=[]
Ds,Dl=V['mine'],V['mine_len']
def contrast_list():
    L=[]
    for m in M:
        for s in S[1:]: L.append((m,f"{s[:2]} $-$ S1",'A_redacted','S1_bare','A_redacted',s,'style'))
    return L
sty=contrast_list(); lk=[(m,'Original $-$ redacted (S1)','A_redacted','S1_bare','B_original','S1_bare','leak') for m in M]
res={}
for met,D in(('s',Ds),('l',Dl)):
    for grp,name in((sty,'style'),(lk,'leak')):
        r_=[mc(D,m,a1,s1,a2,s2) for (m,lab,a1,s1,a2,s2,g) in grp]
        h=holm([x[2] for x in r_])
        for (m,lab,a1,s1,a2,s2,g),x,hh in zip(grp,r_,h):
            res[(met,g,m,lab)]=(acc(D,m,a2,s2)-acc(D,m,a1,s1),x[0],x[1],x[2],hh)
T2=[]
for grp in(sty,lk):
    for (m,lab,a1,s1,a2,s2,g) in grp:
        d,b,c,p,h=res[('s',g,m,lab)];d2,b2,c2,p2,h2=res[('l',g,m,lab)]
        T2.append(f"{m} & {lab} & {sg(d)} & {c}/{b} & {pf(p)} & {pf(h)} & {sg(d2)} & {pf(h2)}\\\\")
    if grp is sty: T2.append('\\midrule')
open('t2.tex','w').write('\n'.join(T2))
# Table III robustness
T3=[]
names=[('mine','Primary'),('judge','Judge-adjusted'),('cons','Conservative'),('g1','Scripted G1'),('g2','Scripted G2')]
rob={}
for k,lab in names:
    D=V[k];cells=[]
    for m in M:
        lg=acc(D,m,'B_original','S1_bare')-acc(D,m,'A_redacted','S1_bare');pl=mc(D,m,'A_redacted','S1_bare','B_original','S1_bare')[2]
        st=acc(D,m,'A_redacted','S3_structured')-acc(D,m,'A_redacted','S1_bare');ps=mc(D,m,'A_redacted','S1_bare','A_redacted','S3_structured')[2]
        cells.append((lg,pl,st,ps));rob[(k,m)]=(lg,pl,st,ps)
    T3.append(f"{lab} & {sg(cells[0][0])} & {sg(cells[1][0])} & {sg(cells[0][2])} ({pf(cells[0][3])}) & {sg(cells[1][2])} ({pf(cells[1][3])})\\\\")
open('t3.tex','w').write('\n'.join(T3))
# Table IV strata
def stratum(c):
    ls=mast[c]['leak_status']
    return 'redacted' if ls=='redacted' else ('nomatch' if ls=='clean_no_match' else 'kept')
T4=[];strat={}
for key,lab in(('nomatch','No leak pattern matched'),('redacted','Redacted ($\\geq$1 span)'),('kept','Residual label kept')):
    cs=[c for c in cases if stratum(c)==key];cells=[]
    for m in M:
        a=acc(V['mine'],m,'A_redacted','S1_bare',cs);b=acc(V['mine'],m,'B_original','S1_bare',cs);cells.append(f"{pct(a)} & {pct(b)} & {sg(b-a)}");strat[(key,m)]=(a,b,len(cs))
    T4.append(f"{lab} ({len(cs)}) & "+' & '.join(cells)+"\\\\")
open('t4.tex','w').write('\n'.join(T4))
# Misc numbers
nums={}
for m in M:
    uns=[c for c in cases if len({V['mine'][(m,'A_redacted',s,c)] for s in S})>1]
    nums[f'unst_{m}']=len(uns);nums[f'allc_{m}']=sum(all(V['mine'][(m,'A_redacted',s,c)]==1 for s in S) for c in cases);nums[f'allw_{m}']=sum(all(V['mine'][(m,'A_redacted',s,c)]==0 for s in S) for c in cases)
    for s in S:
        w=[r['words'] for r in rows if r['model']==m and r['arm']=='A_redacted' and r['style']==s]; nums[f'w_{m}_{s[:2]}']=statistics.mean(w)
    for s in('S3_structured',):
        w=[D_['words'] for D_ in rows if D_['model']==m and D_['arm']=='A_redacted' and D_['style']==s];yy=[D_['strict'] for D_ in rows if D_['model']==m and D_['arm']=='A_redacted' and D_['style']==s]
        r=spearmanr(w,yy);nums[f'rho_{m}']=r.statistic;nums[f'rhop_{m}']=r.pvalue
nums['wrong_both']=sum(all(V['mine'][(m,'A_redacted',s,c)]==0 for m in M for s in S) for c in cases)
for st_ in('rare','common'):
    cs=[c for c in cases if mast[c]['stratum']==st_]
    for m in M:
        nums[f'{st_}_{m}_S1']=acc(V['mine'],m,'A_redacted','S1_bare',cs);nums[f'{st_}_{m}_S3']=acc(V['mine'],m,'A_redacted','S3_structured',cs);nums[f'{st_}_{m}_B']=acc(V['mine'],m,'B_original','S1_bare',cs)
nums['nrare']=sum(mast[c]['stratum']=='rare' for c in cases)
for nm,cs in(('flag',[c for c in cases if c in flags]),('other',[c for c in cases if c not in flags])):
    for m in M:
        a=acc(V['mine'],m,'A_redacted','S1_bare',cs);b=acc(V['mine'],m,'B_original','S1_bare',cs);nums[f'{nm}_{m}']=(a,b,len(cs))
nums['gradedist']={g:sum(r['grade']==g for r in rows) for g in(0,1,2)}
# scripted grader agreement
yy=[r['grade'] for r in rows]
for g in('g1','g2'):
    pp=[r[g] for r in rows];nums[f'{g}_k3']=cohen_kappa_score(yy,pp);nums[f'{g}_ks']=cohen_kappa_score([a==2 for a in yy],[b==2 for b in pp]);nums[f'{g}_kl']=cohen_kappa_score([a>=1 for a in yy],[b>=1 for b in pp])
import pickle;pickle.dump(dict(nums=nums,kap=kap,res=res,rob=rob,strat=strat,cov=cov),open('nums.pkl','wb'))
# ---- Figure
plt.rcParams.update({'font.family':'serif','font.size':8,'axes.linewidth':.6})
fig,ax=plt.subplots(figsize=(3.45,2.35),dpi=300)
xl=['S1\nbare','S2\nstepwise','S3\nstructured','S1\noriginal text']
cond=[('A_redacted','S1_bare'),('A_redacted','S2_stepwise'),('A_redacted','S3_structured'),('B_original','S1_bare')]
colr={'Claude':'#2a78d6','Gemini':'#eb6834'};mk={'Claude':'o','Gemini':'s'};off={'Claude':-0.09,'Gemini':0.09}
for m in M:
    xs=[];ys=[];lo=[];hi=[]
    for i,(a,s) in enumerate(cond):
        k=sum(V['mine'][(m,a,s,c)] for c in cases);l,h=wil(k,N);xs.append(i+off[m]);ys.append(100*k/N);lo.append(100*k/N-100*l);hi.append(100*h-100*k/N)
    ax.errorbar(xs[:3],ys[:3],yerr=[lo[:3],hi[:3]],fmt=mk[m]+'-',color=colr[m],ms=4.2,lw=1,capsize=2,elinewidth=.8,mfc=colr[m],label=m)
    ax.errorbar(xs[3:],ys[3:],yerr=[lo[3:],hi[3:]],fmt=mk[m],color=colr[m],ms=4.2,capsize=2,elinewidth=.8,mfc='white',mew=1.1)
ax.axvline(2.5,color='#999',lw=.6,ls=(0,(3,3)))
ax.set_xticks(range(4));ax.set_xticklabels(xl);ax.set_ylim(50,100);ax.set_ylabel('Strict accuracy (%), n=120')
ax.grid(axis='y',color='#e3e3e3',lw=.5);ax.set_axisbelow(True)
for s_ in('top','right'): ax.spines[s_].set_visible(False)
ax.legend(frameon=False,loc='upper left',fontsize=7.5,handlelength=1.6,ncol=2)
ax.text(1.0,51.5,'redacted text (Arm A)',ha='center',fontsize=7,color='#555');ax.text(3.0,51.5,'Arm B',ha='center',fontsize=7,color='#555')
fig.tight_layout(pad=.4);fig.savefig('fig1.pdf');fig.savefig('fig1.png')
# print summary for verification
print(cov,kap);print(open('t1.tex').read());print(open('t2.tex').read());print(open('t3.tex').read());print(open('t4.tex').read());print(nums)
