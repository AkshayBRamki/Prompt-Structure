"""Independent scripted grader. Thresholds fixed a priori (not tuned on LLM grades).
G1: gold-concept recall: share of gold content-word stems present in answer. strict>=0.70, lenient>=0.40
G2: char n-gram (3-5) TF-IDF cosine between gold and answer, fit on all gold+answer text. strict>=0.50, lenient>=0.30
"""
import csv,re,sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
STOP=set("a an the of and or with without to in on at by for from as is are was were be been due secondary associated presenting presentation likely probable possible suspected consistent related type case patient disease syndrome disorder multiple left right bilateral involving including features feature evidence no non vs versus".split())
def stem(w):
    for s in("ations","ation","itis","ies","ing","ed","es","s","al","ic"):
        if len(w)>5 and w.endswith(s): return w[:-len(s)]
    return w
def toks(t):
    t=re.sub(r'\(.*?\)',lambda m:' '+m.group(0)[1:-1]+' ',t.lower())
    return [stem(w) for w in re.findall(r"[a-z0-9]+",t) if w not in STOP and len(w)>1]
rows=list(csv.DictReader(open('graded_long.csv',encoding='utf-8')))
gold={r['case_id']:r['ground_truth_diagnosis'] for r in csv.DictReader(open('/home/claude/leakfree_experiment/dataset/answer_key_DO_NOT_PASTE.csv',encoding='utf-8'))}
vec=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),sublinear_tf=True).fit(list(gold.values())+[r['dx'] for r in rows])
G=vec.transform([gold[r['case']] for r in rows]);A=vec.transform([r['dx'] for r in rows])
out=[]
for i,r in enumerate(rows):
    g=set(toks(gold[r['case']]));a=set(toks(r['dx']))
    rec=len(g&a)/len(g) if g else 0
    cos=float(cosine_similarity(G[i],A[i])[0,0])
    g1=2 if rec>=.70 else 1 if rec>=.40 else 0
    g2=2 if cos>=.50 else 1 if cos>=.30 else 0
    out.append(dict(r,recall=round(rec,3),cosine=round(cos,3),g1=g1,g2=g2))
w=csv.DictWriter(open('graded_auto.csv','w',newline='',encoding='utf-8'),fieldnames=out[0].keys());w.writeheader();w.writerows(out)
print(len(out))
