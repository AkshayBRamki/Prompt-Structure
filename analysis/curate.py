import json,re,sys
sys.path.insert(0,'.')
import build
rows={r['case_id']:r for r in json.load(open('rows_auto.json'))}
T='[REDACTED]'
# case -> list of regex (or (regex, replacement)); only diagnostic-label statements / pathogen & gene identification
RED={
'M002':[r'primary pulmonary carcinoma'],
'M003':[r'omental cystic lymphangioma'],
'M005':[r'HSV infection',r'HSV-1'],
'M007':[r'interstitial ectopic pregnancy'],
'M010':[r'uterine AVM',r'the AVM'],
'M012':[r'Splenic hamartoma'],
'M013':[r'Dewey.s modification type 2 malocclusion \(spacing\)'],
'M016':[r'Diffuse cerebral lymphomatosis',r'primary CNS lymphoma'],
'M017':[r'mucinous adenocarcinoma of the appendix'],
'M018':[r'extrathyroid parathyroid adenoma'],
'M020':[r'desmoid-type fibromatosis \(DF\)'],
'M021':[r'infective endocarditis'],
'M022':[r'SYNE2'],
'M027':[r'fibroepithelial polyp'],
'M029':[r'leading to a clinical diagnosis of EBV-positive lymphoid proliferations and lymphomas arising in post-transplantation \(B cell lineage\)'],
'M031':[r'mesenteric inflammatory pseudotumor'],
'M032':[r'Cognard type 1 DAVF'],
'M034':[r'Lyme disease'],
'M037':[r'Paracoccidioidomycosis',r'Paracoccidioides spp\.?'],
'M038':[r'IDH-mutant astrocytoma, WHO grade 3'],
'M039':[r'classic biphasic pulmonary blastoma \(CBPB\)'],
'M041':[r'Abiotrophia defectiva'],
'M050':[r'Double superior vena cava \(DSVC\)'],
'M051':[r'poorly differentiated neuroendocrine carcinoma, small cell type'],
'M052':[r'choledochal cysts?'],
'M053':[r'isochromosome mosaic Turner syndrome \(IMTS\)'],
'M055':[r'Pancreaticobiliary maljunction \(PBM\)',r'Type 1A choledochal cyst',r'extrahepatic cholangiocarcinoma'],
'M056':[r'UCU',r'jejunal atresia'],
'M057':[r'Benign Sertoli cell tumor'],
'M060':[r'Paraclostridium tenue'],
'M064':[r'nodular-stage Kaposi sarcoma'],
'M066':[r'Acute cholecystitis',r'hydatid cysts?',r'cholecysto-hydatid (?:cyst )?fistula'],
'M067':[r'CLCN1'],
'M068':[r'SPTA1'],
'M074':[r'recurrent metastatic atypical carcinoid tumor'],
'M077':[r'Wernicke encephalopathy'],
'M078':[r'Highly suspicious of malignant transformation'],
'M082':[r'\bGPA\b'],
'M083':[(r'Human Bocavirus \(HBoV; Ct value 28\)','[REDACTED] (Ct value 28)')],
'M085':[r'primary hepatic leiomyosarcoma \(PHLS\)'],
'M086':[r'leiomyosarcoma \(LMS\)',r'\bLMS\b'],
'M087':[r'gastric hamartomatous inverted polyp \(GHIP\)'],
'M091':[r'urachal adenocarcinoma'],
'M092':[r'invasive pancreatic ductal adenocarcinoma \(PDAC\) arising from an IPMN with high-grade dysplasia'],
'M096':[r'postsurgical pyoderma gangrenosum \(PSPG\)'],
'M098':[r'hidradenitis suppurativa \(HS\)',r'\bHS\b'],
'M100':[r'the chronic phase of Hemiconvulsion-Hemiplegia-Epilepsy \(HHE\) syndrome'],
'M105':[r'CLN5',r'neuronal ceroid lipofuscinosis \(NCL\)'],
'M108':[r'\bCML\b'],
'M113':[r'Bacillus megaterium'],
'M118':[r'B-cell CLL/SLL',r'plasmacytoma'],
'M120':[r'diagnosed as infarcted spleen secondary to torsion',r'Splenic infarction confirmed'],
}
# --- round-2 additions (found by scanning redacted text against the ground-truth labels) ---
RED['M007']=RED.get('M007',[])+[(r'suspicious for an ectopic pregnancy','suspicious for an [REDACTED]')]
RED['M012']=RED.get('M012',[])+[(r'consistent with splenic rupture','consistent with [REDACTED]')]
RED['M024']=RED.get('M024',[])+[(r'Histologically consistent with hamartoma','Histologically consistent with [REDACTED]')]
RED['M029']=RED.get('M029',[])+[r'NK/T cell lymphoma arising in post-transplantation']
RED['M030']=RED.get('M030',[])+[(r'Vibrio cholerae \(non-O1/non-O139 serogroup\)','[REDACTED]'),(r'Vibrio cholerae','[REDACTED]')]
RED['M034']=RED.get('M034',[])+[(r'Diagnosis: Arachnoid cyst \(AC\) in the CP angle\.','Diagnosis: [REDACTED].')]
RED['M069']=RED.get('M069',[])+[(r'Diffuse large B-cell lymphoma \(DLBCL\)','[REDACTED]')]
RED['M096']=RED.get('M096',[])+[(r'consistent with pyoderma gangrenosum','consistent with [REDACTED]')]
RED['M106']=RED.get('M106',[])+[(r'a CFV saccular aneurysm','a [REDACTED]')]
# flagged but deliberately NOT redacted
KEEP={
 'history premise (pre-existing condition, not the answer)':['M008','M038','M090','M095','M110','M116'],
 'label is itself an imaging/exam finding (cannot redact without deleting the evidence)':['M014','M023','M040','M062','M094','M107','M112','M109'],
 'false positive (anatomy/feature word overlap)':['M026','M028','M043','M054','M101','M097','M119','M013x'],
}
out=[];problems=[]
for cid,r in rows.items():
    txt=r['case_original']; applied=[]
    for p in RED.get(cid,[]):
        rep=T
        if isinstance(p,tuple): p,rep=p
        new,n=re.subn(p,rep,txt,flags=re.I)
        if n==0: problems.append((cid,p))
        else: applied.append((p,n)); txt=new
    r['case_redacted']=txt; r['applied']=applied
json.dump(list(rows.values()),open('rows_cur.json','w'),ensure_ascii=False,indent=1)
print('patterns that did not match:',problems)
print('cases redacted:',sum(1 for r in rows.values() if r['applied']))
# residual scan: re-run the detector on redacted text, only in non-history sections, report remaining hits for cases we redacted
rem=[]
for cid,r in rows.items():
    abbr,comps=build.cores(r['dx']); sec=None
    for ln in r['case_redacted'].split('\n'):
        s=build.secname(ln); 
        if s: sec=s
        if build.line_match(ln,abbr,comps) and sec not in build.HIST and '[REDACTED]' not in ln:
            rem.append((cid,sec,ln.strip()[:200]))
print('residual non-history hits on un-redacted lines:',len(rem))
for x in rem: print(x)
