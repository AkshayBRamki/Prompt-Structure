import json,csv,random,sys
rec=json.load(open('records.json'))
key={r['case_id']:r for r in csv.DictReader(open('/home/claude/leakfree_experiment/dataset/answer_key_DO_NOT_PASTE.csv'))}
by={}
for r in rec: by.setdefault(r['case'],[]).append(r)
mapping=json.load(open("mapping.json")) if False else {}
for cid in sorted(by):
    rs=by[cid]; random.Random(int(cid[1:])*7919+7).shuffle(rs)
    mapping[cid]={chr(97+i):dict(model=r['model'],arm=r['arm'],style=r['style'],dx=r['dx']) for i,r in enumerate(rs)}
def show(a,b):
    for i in range(a,b+1):
        cid=f'M{i:03d}'
        print(f"## {cid} | GOLD: {key[cid]['ground_truth_diagnosis'].strip()[:260]}".replace('\n',' / '))
        for k,v in mapping[cid].items(): print(f"  {k}: {v['dx'][:230]}")
if __name__=='__main__': show(int(sys.argv[1]),int(sys.argv[2]))
