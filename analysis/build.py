import json,re,random,csv,math,sys,collections
SRC='/tmp/medrbench_src/MedRBench/data/MedRBench/diagnosis_957_cases_with_rare_disease_491.json'
D=json.load(open(SRC))
GENERIC=set("""syndrome disease case patient acute chronic primary secondary tumor tumour cancer carcinoma with and due the of in for from after following complicated associated related type stage left right bilateral unilateral rare suspected severe mild moderate recurrent atypical early late spectrum disorder infection lesion mass complete incomplete large small giant multiple isolated coexisting presenting mimicking""".split())
def norm(s): return re.sub(r'[^a-z0-9\s\-]',' ',s.lower())
def cores(dx):
    abbr=re.findall(r'\(([A-Za-z0-9\-]{2,12})\)',dx)
    base=re.sub(r'\([^)]*\)','',dx)
    comps=re.split(r'\bwith\b|\bsecondary to\b|\bdue to\b|\bcomplicated by\b|\bfollowing\b|\band\b|\bcaused by\b|\bassociated with\b|\bpresenting\b|\bcoexisting\b|\bmimicking\b|[,;:]',base,flags=re.I)
    out=[]
    for c in comps:
        c=re.split(r'\b(?:of|in|on|involving|at|from|within)\s+(?:the\s+)?',c,maxsplit=1,flags=re.I)[0].strip(' .')
        toks=[t for t in norm(c).split() if len(t)>=4 and t not in GENERIC]
        if toks: out.append((c,toks))
    return abbr,out
def stem(t): return t[:6]
def line_match(line,abbr,comps):
    n=norm(line); hits=[]
    for a in abbr:
        if len(a)>=3 and re.search(r'(?<![A-Za-z0-9])'+re.escape(a)+r'(?![A-Za-z0-9])',line): hits.append(('abbr',a))
    for c,toks in comps:
        got=[t for t in toks if stem(t) in n]
        longest=max(toks,key=len)
        if len(got)>=max(1,math.ceil(0.75*len(toks))) and stem(longest) in n: hits.append(('term',c))
    return hits
HIST=('Patient Information','Chief Complaint','History of Present Illness','Past Medical History','Personal History','Family History','Physical Examination')
def secname(ln):
    m=re.match(r'^\s{0,1}-\s+\**([^*:]+?)\**\s*:',ln)
    return m.group(1).strip() if m and not ln.startswith('  ') else None
def redact_line(line,abbr,comps):
    out=line; changes=[]
    for a in abbr:
        pat=r'(?<![A-Za-z0-9])'+re.escape(a)+r'(?![A-Za-z0-9])'
        if re.search(pat,out): out=re.sub(pat,'[REDACTED]',out); changes.append(a)
    for c,toks in comps:
        # ordered tokens with up to 2 intervening words
        pat=r'\b'+r'(?:\W+\w+){0,2}?\W+'.join(re.escape(t[:max(5,len(t)-2)])+r'\w*' for t in toks)
        m=re.search(pat,out,re.I)
        if m: out=out[:m.start()]+'[REDACTED]'+out[m.end():]; changes.append(m.group(0))
        else:
            lt=max(toks,key=len); m=re.search(r'\b'+re.escape(lt[:max(5,len(lt)-2)])+r'\w*',out,re.I)
            if m: out=out[:m.start()]+'[REDACTED]'+out[m.end():]; changes.append(m.group(0))
    return out,changes
def process(cs,dx):
    abbr,comps=cores(dx); sec=None; lines=cs.split('\n'); res=[];flag=[]
    for i,ln in enumerate(lines):
        s=secname(ln); 
        if s: sec=s
        h=line_match(ln,abbr,comps)
        if h:
            new,ch=redact_line(ln,abbr,comps)
            res.append(new); flag.append((sec,ln.strip(),new.strip(),ch))
        else: res.append(ln)
    return '\n'.join(res),flag
if __name__=='__main__':
    ids=list(D.keys())
    rare=[i for i in ids if D[i]['checked_rare_disease']]; common=[i for i in ids if not D[i]['checked_rare_disease']]
    R=random.Random(42).sample(rare,70); C=random.Random(42).sample(common,50)
    S=R+C; random.Random(42).shuffle(S)
    rows=[]
    for k,pid in enumerate(S,1):
        g=D[pid]['generate_case']; red,fl=process(g['case_summary'],g['diagnosis_results'])
        rows.append(dict(case_id=f'M{k:03d}',pmc_id=pid,stratum='rare' if D[pid]['checked_rare_disease'] else 'common',
            case_original=g['case_summary'].strip(),case_redacted=red.strip(),flags=fl,dx=g['diagnosis_results']))
    json.dump(rows,open('rows_auto.json','w'),ensure_ascii=False,indent=1)
    nfl=sum(1 for r in rows if r['flags'])
    print('sample',len(rows),'rare',sum(r['stratum']=='rare' for r in rows),'flagged cases',nfl)
    anc=sum(1 for r in rows if any(f[0] not in HIST for f in r['flags']))
    print('flagged outside history/exam sections:',anc)
