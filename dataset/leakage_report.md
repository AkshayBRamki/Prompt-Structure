# Leakage report (120-case sample, MedR-Bench oracle diagnosis input)

Source: MAGIC-AI4Med/MedRBench `diagnosis_957_cases_with_rare_disease_491.json`, field `generate_case.case_summary` (the text the models see).

Sample: random stratified, 70 rare + 50 common, seed 42, shuffled and relabelled M001-M120. **This is NOT the pilot sample** (the pilot case IDs and sampling code were not recoverable), so results cannot be paired with pilot results.

## Counts

- Redacted (diagnostic label / organism / gene / entity named in a conclusion or result): **56** of 120
- Full ground-truth label verbatim in the original text: 15 of 120; after redaction: 0 (this check misses partial and paraphrased labels, so it is not proof of a leak-free text)
- Kept, label is itself an imaging/exam finding (cannot be removed without deleting the evidence): 11
- Kept, pre-existing condition in history (not the answer): 5
- Kept, detector false positive: 6
- No match: 42

## Redaction rule

Replaced with `[REDACTED]`: the diagnostic label or its abbreviation when it appears in a conclusion ("confirmed X", "consistent with X", "histology: X"), an identified organism, gene, or tumour type, or a component of the final diagnosis stated as a result. Not redacted: descriptive imaging or exam findings, and conditions listed as pre-existing history when they are only part of the answer. Indirect cues remain (e.g. Hurley stage in a hidradenitis case), so the leak count is a lower bound, as in the earlier audit.

## Judgement calls to veto before you run

- Organism and gene names were redacted in result lines (e.g. M041, M060, M067, M068, M105). That removes the decisive finding in those cases, so they become harder than in the original benchmark. If you prefer, restore them from `case_original`.
- The 11 irreducible cases (M014, M023, M040, M054, M058, M062, M084, M094, M107, M109, M112) still contain imaging findings that essentially state the diagnosis. Report them as a limitation or drop them from the leak-free analysis.
- The 27.5% (33/120) leak rate in the earlier audit used a looser definition; this sample is not directly comparable.

## Round 2 (added after the first Claude output was checked)
A scan of the redacted text against the ground-truth labels found residual statements of the answer in M007, M012, M024, M029, M030, M034, M069, M096 and M106 (for example "Diagnosis: Arachnoid cyst", "histopathological findings consistent with pyoderma gangrenosum", "Blood cultures positive for Vibrio cholerae"). These were redacted and M058 and M084 were added to the irreducible-finding group. The first-round verification only checked that each curated pattern matched and that the full label string was gone, so it missed partial and paraphrased labels. M028 (final pathology names the ovarian and endometrial endometrioid adenocarcinomas) is still kept as a judgement call. Treat the redaction as a lower bound on leakage.

## Per-case redactions

| Case | Status | Removed |
|---|---|---|
| M002 | redacted | primary pulmonary carcinoma |
| M003 | redacted | omental cystic lymphangioma |
| M005 | redacted | HSV infection; HSV-1 |
| M007 | redacted | interstitial ectopic pregnancy; suspicious for an ectopic pregnancy |
| M008 | kept_history_premise | - |
| M010 | redacted | uterine AVM; the AVM |
| M012 | redacted | Splenic hamartoma; consistent with splenic rupture |
| M013 | redacted | Dewey.s modification type 2 malocclusion \(spacing\) |
| M014 | kept_irreducible_imaging_label | - |
| M016 | redacted | Diffuse cerebral lymphomatosis; primary CNS lymphoma |
| M017 | redacted | mucinous adenocarcinoma of the appendix |
| M018 | redacted | extrathyroid parathyroid adenoma |
| M020 | redacted | desmoid-type fibromatosis \(DF\) |
| M021 | redacted | infective endocarditis |
| M022 | redacted | SYNE2 |
| M023 | kept_irreducible_imaging_label | - |
| M024 | redacted | Histologically consistent with hamartoma |
| M026 | kept_false_positive | - |
| M027 | redacted | fibroepithelial polyp |
| M028 | kept_false_positive | - |
| M029 | redacted | leading to a clinical diagnosis of EBV-positive lymphoid proliferations and lymphomas arising in post-transplantation \(B cell lineage\); NK/T cell lymphoma arising in post-transplantation |
| M030 | redacted | Vibrio cholerae \(non-O1/non-O139 serogroup\); Vibrio cholerae |
| M031 | redacted | mesenteric inflammatory pseudotumor |
| M032 | redacted | Cognard type 1 DAVF |
| M034 | redacted | Lyme disease; Diagnosis: Arachnoid cyst \(AC\) in the CP angle\. |
| M037 | redacted | Paracoccidioidomycosis; Paracoccidioides spp\.? |
| M038 | redacted | IDH-mutant astrocytoma, WHO grade 3 |
| M039 | redacted | classic biphasic pulmonary blastoma \(CBPB\) |
| M040 | kept_irreducible_imaging_label | - |
| M041 | redacted | Abiotrophia defectiva |
| M043 | kept_false_positive | - |
| M050 | redacted | Double superior vena cava \(DSVC\) |
| M051 | redacted | poorly differentiated neuroendocrine carcinoma, small cell type |
| M052 | redacted | choledochal cysts? |
| M053 | redacted | isochromosome mosaic Turner syndrome \(IMTS\) |
| M054 | kept_irreducible_imaging_label | - |
| M055 | redacted | Pancreaticobiliary maljunction \(PBM\); Type 1A choledochal cyst; extrahepatic cholangiocarcinoma |
| M056 | redacted | UCU; jejunal atresia |
| M057 | redacted | Benign Sertoli cell tumor |
| M058 | kept_irreducible_imaging_label | - |
| M060 | redacted | Paraclostridium tenue |
| M062 | kept_irreducible_imaging_label | - |
| M064 | redacted | nodular-stage Kaposi sarcoma |
| M066 | redacted | Acute cholecystitis; hydatid cysts?; cholecysto-hydatid (?:cyst )?fistula |
| M067 | redacted | CLCN1 |
| M068 | redacted | SPTA1 |
| M069 | redacted | Diffuse large B-cell lymphoma \(DLBCL\) |
| M074 | redacted | recurrent metastatic atypical carcinoid tumor |
| M077 | redacted | Wernicke encephalopathy |
| M078 | redacted | Highly suspicious of malignant transformation |
| M082 | redacted | \bGPA\b |
| M083 | redacted | Human Bocavirus \(HBoV; Ct value 28\) |
| M084 | kept_irreducible_imaging_label | - |
| M085 | redacted | primary hepatic leiomyosarcoma \(PHLS\) |
| M086 | redacted | leiomyosarcoma \(LMS\); \bLMS\b |
| M087 | redacted | gastric hamartomatous inverted polyp \(GHIP\) |
| M090 | kept_history_premise | - |
| M091 | redacted | urachal adenocarcinoma |
| M092 | redacted | invasive pancreatic ductal adenocarcinoma \(PDAC\) arising from an IPMN with high-grade dysplasia |
| M094 | kept_irreducible_imaging_label | - |
| M095 | kept_history_premise | - |
| M096 | redacted | postsurgical pyoderma gangrenosum \(PSPG\); consistent with pyoderma gangrenosum |
| M097 | kept_false_positive | - |
| M098 | redacted | hidradenitis suppurativa \(HS\); \bHS\b |
| M100 | redacted | the chronic phase of Hemiconvulsion-Hemiplegia-Epilepsy \(HHE\) syndrome |
| M101 | kept_false_positive | - |
| M105 | redacted | CLN5; neuronal ceroid lipofuscinosis \(NCL\) |
| M106 | redacted | a CFV saccular aneurysm |
| M107 | kept_irreducible_imaging_label | - |
| M108 | redacted | \bCML\b |
| M109 | kept_irreducible_imaging_label | - |
| M110 | kept_history_premise | - |
| M112 | kept_irreducible_imaging_label | - |
| M113 | redacted | Bacillus megaterium |
| M116 | kept_history_premise | - |
| M118 | redacted | B-cell CLL/SLL; plasmacytoma |
| M119 | kept_false_positive | - |
| M120 | redacted | diagnosed as infarcted spleen secondary to torsion; Splenic infarction confirmed |
