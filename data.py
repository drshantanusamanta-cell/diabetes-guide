# ============================================================
# data.py  —  Shantanu's Diabetes Treatment Assistant
# Master knowledge base: drugs, guidelines, thresholds, refs
# Sources: ADA 2024, RSSDI CPR 2023, ICMR T2DM 2018,
#          DIPSI 2020, JBDS 2023, API Guidelines
# ============================================================

# ── DIAGNOSTIC THRESHOLDS ───────────────────────────────────
DIAGNOSTIC_CRITERIA = {
    "DM diagnosis": {
        "FPG_mmol":   7.0,   "FPG_mgdl":  126,
        "2hr_mmol":  11.1,   "2hr_mgdl":  200,
        "HbA1c_pct":  6.5,
        "random_mmol": 11.1, "random_mgdl": 200,
        "ref": "ADA Standards 2024, Section 2"
    },
    "Pre-diabetes": {
        "IFG_FPG_low_mgdl": 100, "IFG_FPG_high_mgdl": 125,
        "IGT_2hr_low_mgdl": 140, "IGT_2hr_high_mgdl": 199,
        "HbA1c_low": 5.7, "HbA1c_high": 6.4,
        "Indian_note": (
            "IFG threshold divergence: ADA uses FPG >= 100 mg/dL (5.6 mmol/L); "
            "WHO and historically RSSDI used FPG >= 110 mg/dL (6.1 mmol/L). "
            "RSSDI CPR 2023 now aligns with ADA (100 mg/dL threshold). "
            "ADA criterion identifies more at-risk individuals — appropriate for Indian practice given early-onset IR."
        ),
        "ref": "ADA Standards 2024, Section 2; RSSDI CPR 2023; WHO 2006 Definition and Classification"
    },
    "GDM_DIPSI": {
        "threshold_2hr_mgdl": 140,
        "test": "75g OGTT, 2-hour plasma glucose",
        "ref": "DIPSI 2020; ADA Standards 2024, Section 15"
    },
    "Asian BMI": {
        "overweight": 23.0, "obese": 25.0,
        "ref": "WHO 2004 Asia-Pacific cut-offs"
    },
    "Waist circumference": {
        "male_cm": 90, "female_cm": 80,
        "ref": "WHO 2004; RSSDI CPR 2023"
    },
    "C_peptide": {
        "low_nmol":    0.6,   "low_ngml":  1.8,
        "stimulated_low_nmol": 1.0,
        "ref": "ADA Standards 2024, Section 2; Holt et al., Textbook of Diabetes 5th ed."
    },
    "HOMA_IR": {
        "normal_max": 2.5,
        "insulin_resistant": 2.5,
        "ref": "Matthews DR et al., Diabetologia 1985"
    },
    "HOMA_beta": {
        "low": 50,
        "ref": "Matthews DR et al., Diabetologia 1985"
    }
}

# ── HbA1c TARGETS ────────────────────────────────────────────
HBA1C_TARGETS = {
    "General adult T2DM":        {"target": "<7.0%", "ref": "ADA Standards 2024, Section 6; RSSDI CPR 2023"},
    "Young, short duration, no CVD": {"target": "<6.5%", "ref": "ADA Standards 2024, Section 6"},
    "Elderly / frail (>70 yrs)": {"target": "<8.0–8.5%", "ref": "ADA Standards 2024, Section 13; RSSDI CPR 2023"},
    "T1DM adult":                {"target": "<7.0%", "ref": "ADA Standards 2024, Section 7"},
    "LADA (confirmed, on insulin)": {"target": "<7.0% (manage as T1DM once confirmed)", "ref": "ADA Standards 2024, Sections 2 and 7; RSSDI CPR 2023"},
    "GDM (fasting)":             {"target": "<5.3 mmol/L (95 mg/dL)", "ref": "ADA Standards 2024, Section 15; DIPSI 2020"},
    "GDM (1-hr post-meal)":      {"target": "<7.8 mmol/L (140 mg/dL)", "ref": "ADA Standards 2024, Section 15"},
    "CKD (eGFR 20-60)":          {"target": "<8.0%", "ref": "ADA Standards 2024, Section 11"},
    "Established CVD":            {"target": "<7.0%", "ref": "ADA Standards 2024, Section 10"},
    "Frequent hypoglycaemia":     {"target": "<8.0%", "ref": "ADA Standards 2024, Section 6"},
}

# ── LADA CLINICAL SCORE (Fourlanos 2006) ─────────────────────
LADA_SCORE_CRITERIA = [
    {"criterion": "Age < 50 years at diagnosis",         "score": 1},
    {"criterion": "Acute symptoms at onset (polyuria, polydipsia, weight loss)", "score": 1},
    {"criterion": "BMI < 25 kg/m²",                      "score": 1},
    {"criterion": "Personal history of autoimmune disease","score": 1},
    {"criterion": "Family history of autoimmune disease", "score": 1},
]
LADA_SCORE_CUTOFF = 3  # Sensitivity 90%, Specificity 71% — Fourlanos et al., Diabetes Care 2006

# ── MODY PROBABILITY (Exeter simplified) ─────────────────────
MODY_FLAGS = [
    "Diagnosis before age 35",
    "Non-obese at diagnosis (BMI < 25 kg/m²)",
    "Three consecutive generations with diabetes (autosomal dominant pattern)",
    "GAD antibody negative",
    "C-peptide detectable at > 3 years duration",
    "No features of metabolic syndrome",
    "Sulphonylurea-sensitive (MODY3/HNF1A)",
    "Mild stable fasting hyperglycaemia 5.5–8.0 mmol/L (MODY2/GCK)",
]

# ── FCPD DIAGNOSTIC FEATURES ──────────────────────────────────
FCPD_FLAGS = [
    "History of recurrent epigastric/abdominal pain (especially in childhood/adolescence)",
    "Pancreatic calculi on X-ray or CT abdomen",
    "Underweight / severe malnutrition (BMI < 19 kg/m²)",
    "Resident of or origin from tropical India (Kerala, Tamil Nadu, coastal Karnataka, West Bengal)",
    "Steatorrhoea / exocrine insufficiency symptoms",
    "History of cassava (tapioca) consumption",
    "No significant alcohol use",
    "Diabetes onset between age 10–40 years",
    "Non-ketotic despite severe hyperglycaemia",
]

# ── DRUG DATABASE — ORAL AGENTS ───────────────────────────────
ORAL_DRUGS = {
    "Metformin": {
        "class":        "Biguanide",
        "mechanism":    "Reduces hepatic glucose output; improves insulin sensitivity",
        "start_dose":   "500 mg OD or BD with meals",
        "max_dose":     "2000–2550 mg/day in divided doses",
        "brands": [
            {"name": "Glyciphage",  "company": "Franco-Indian", "cost": "Low"},
            {"name": "Glucophage",  "company": "Merck",         "cost": "Low"},
            {"name": "Obimet",      "company": "Glenmark",      "cost": "Low"},
            {"name": "Cetapin",     "company": "Cipla",         "cost": "Low"},
            {"name": "Gluformin",   "company": "Sun Pharma",    "cost": "Low"},
        ],
        "contraindications": ["eGFR < 30 mL/min", "Active liver disease", "Contrast media within 48 hrs", "Acute illness with dehydration"],
        "cautions":          ["Hold if eGFR 30–45 (use cautiously)", "Hold perioperatively"],
        "HbA1c_reduction":   "1.0–1.5%",
        "weight_effect":     "Neutral / slight loss",
        "hypo_risk":         "Low",
        "evidence_grade":    "A",
        "ref":               "ADA Standards 2024, Section 9; RSSDI CPR 2023; UKPDS"
    },
    "Glimepiride": {
        "class":        "Sulphonylurea (2nd gen)",
        "mechanism":    "Closes K-ATP channel on beta cells → insulin secretion",
        "start_dose":   "1–2 mg OD before breakfast",
        "max_dose":     "8 mg/day (clinical ceiling benefit at 4–6 mg)",
        "brands": [
            {"name": "Amaryl",   "company": "Sanofi",    "cost": "Medium"},
            {"name": "Glimer",   "company": "Mankind",   "cost": "Low"},
            {"name": "Zoryl",    "company": "Intas",     "cost": "Low"},
            {"name": "Glimpid",  "company": "Zydus",     "cost": "Low"},
            {"name": "Glimy",    "company": "Sun Pharma","cost": "Low"},
        ],
        "contraindications": ["T1DM", "LADA", "FCPD", "Pregnancy", "Severe hepatic/renal failure"],
        "cautions":          ["Reduce 50% when adding basal insulin", "Elderly — hypoglycaemia risk"],
        "HbA1c_reduction":   "1.0–1.5%",
        "weight_effect":     "Weight gain +1–2 kg",
        "hypo_risk":         "Moderate–High",
        "evidence_grade":    "A",
        "ref":               "ADA Standards 2024, Section 9; RSSDI CPR 2023"
    },
    "Gliclazide MR": {
        "class":        "Sulphonylurea (2nd gen) — Preferred SU",
        "mechanism":    "Selective K-ATP channel closure on beta cells → insulin secretion. Antioxidant properties. Does NOT bind to cardiac/vascular K-ATP channels (unlike Glibenclamide).",
        "start_dose":   "30 mg OD with breakfast (must be swallowed whole — MR formulation)",
        "max_dose":     "120 mg OD",
        "brands": [
            {"name": "Diamicron MR",  "company": "Servier",       "cost": "Medium"},
            {"name": "Glizid MR",     "company": "Panacea Biotec","cost": "Low"},
            {"name": "Reclide",       "company": "Glenmark",      "cost": "Low"},
            {"name": "Glyclazide MR", "company": "Sun Pharma",    "cost": "Low"},
            {"name": "Glucored MR",   "company": "Cipla",         "cost": "Low"},
        ],
        "contraindications": ["T1DM", "LADA", "FCPD", "Pregnancy", "eGFR < 30 (use with caution at eGFR 30–60)"],
        "cautions":          [
            "Reduce 50% when adding basal insulin to avoid hypoglycaemia",
            "Preferred SU in elderly — lower nocturnal hypo risk than Glimepiride/Glibenclamide",
            "Do NOT crush or halve MR tablets",
        ],
        "HbA1c_reduction":   "1.0–1.5%",
        "weight_effect":     "Weight gain +1–2 kg (less than Glibenclamide)",
        "hypo_risk":         "Low–Moderate (lowest among SUs)",
        "evidence_grade":    "A",
        "CV_benefit":        "ADVANCE trial — Intensive Gliclazide MR-based therapy: 21% RRR in combined microvascular events (HR 0.79, p<0.001), driven by 21% RRR in new or worsening nephropathy. 10% RRR in combined micro + macrovascular composite (HR 0.90, p=0.01). No excess CV mortality (Patel A et al., NEJM 2008).",
        "ref":               "ADVANCE trial (Patel A et al., NEJM 2008); RSSDI CPR 2023; ADA Standards 2024, Section 9; ICMR T2DM Guidelines 2018"
    },
    "Glipizide": {
        "class":        "Sulphonylurea (2nd gen)",
        "mechanism":    "Closes K-ATP channel on beta cells → insulin secretion",
        "start_dose":   "2.5–5 mg OD 30 min before breakfast",
        "max_dose":     "20 mg/day (>10 mg: divide BD)",
        "brands": [
            {"name": "Dibizide",  "company": "Abbott",   "cost": "Low"},
            {"name": "Glynase",   "company": "Pfizer",   "cost": "Low"},
            {"name": "Minidiab",  "company": "Pfizer",   "cost": "Low"},
        ],
        "contraindications": ["T1DM", "LADA", "FCPD", "Pregnancy", "Severe renal/hepatic failure"],
        "cautions":          ["Shorter-acting — lower prolonged hypo risk vs Glibenclamide", "Use with caution in elderly"],
        "HbA1c_reduction":   "1.0–1.5%",
        "weight_effect":     "Weight gain",
        "hypo_risk":         "Moderate",
        "evidence_grade":    "A",
        "ref":               "ADA Standards 2024, Section 9; ICMR T2DM Guidelines 2018"
    },
    "Repaglinide": {
        "class":        "Meglitinide (non-SU insulin secretagogue)",
        "mechanism":    "Rapidly closes K-ATP channels on beta cells → short-duration prandial insulin secretion. Cleared hepatically — safe in CKD.",
        "start_dose":   "0.5 mg before each main meal (3× daily)",
        "max_dose":     "4 mg per meal; 16 mg/day",
        "brands": [
            {"name": "Novonorm",  "company": "Novo Nordisk", "cost": "Medium"},
            {"name": "Regan",     "company": "Sun Pharma",   "cost": "Low"},
            {"name": "Eurepa",    "company": "Torrent",      "cost": "Low"},
            {"name": "Repace",    "company": "Cipla",        "cost": "Low"},
        ],
        "contraindications": ["T1DM", "LADA", "FCPD", "Pregnancy", "Severe hepatic failure", "Concomitant Gemfibrozil (↑levels 8×)"],
        "cautions":          [
            "Take only WITH meal — skip dose if meal skipped (key advantage over SUs)",
            "Ideal for irregular meal patterns and shift workers",
            "No dose adjustment needed in CKD (hepatic clearance) — preferred secretagogue in CKD",
        ],
        "HbA1c_reduction":   "0.5–1.5%",
        "weight_effect":     "Weight gain (less than SU)",
        "hypo_risk":         "Low–Moderate (meal-linked, brief duration)",
        "evidence_grade":    "B",
        "ref":               "ADA Standards 2024, Section 9; RSSDI CPR 2023; Novo Nordisk Prescribing Information"
    },
    "Sitagliptin": {
        "class":        "DPP-4 inhibitor",
        "mechanism":    "Inhibits DPP-4 → prolongs endogenous GLP-1/GIP → glucose-dependent insulin secretion",
        "start_dose":   "100 mg OD",
        "max_dose":     "100 mg OD (reduce to 50 mg if eGFR 30–50; 25 mg if eGFR < 30)",
        "brands": [
            {"name": "Januvia",  "company": "MSD",          "cost": "High"},
            {"name": "Istavel",  "company": "Sun Pharma",   "cost": "Medium"},
            {"name": "Sitaglo",  "company": "Glenmark",     "cost": "Medium"},
            {"name": "Zita",     "company": "Cipla",        "cost": "Medium"},
        ],
        "contraindications": ["Pancreatitis history (use with caution)", "eGFR < 45 without dose adjustment — reduce dose"],
        "cautions":          [
            "Do NOT combine with GLP-1 RA (same incretin axis, no additive benefit — PRACTISE trial)",
            "Rare: pancreatitis, nasopharyngitis, SJS (rare)",
            "eGFR dose guide: ≥45 → 100 mg OD; 30–44 → 50 mg OD; <30 → 25 mg OD (including dialysis)",
        ],
        "HbA1c_reduction":   "0.6–0.8%",
        "weight_effect":     "Neutral",
        "hypo_risk":         "Low",
        "evidence_grade":    "A",
        "ref":               "ADA Standards 2024, Section 9; SAVOR-TIMI 53"
    },
    "Vildagliptin": {
        "class":        "DPP-4 inhibitor",
        "mechanism":    "Inhibits DPP-4 → prolongs endogenous GLP-1",
        "start_dose":   "50 mg BD",
        "max_dose":     "100 mg/day",
        "brands": [
            {"name": "Galvus",   "company": "Novartis",  "cost": "High"},
            {"name": "Vildamet", "company": "Sun Pharma","cost": "Medium"},
            {"name": "Zomelis",  "company": "Cipla",     "cost": "Medium"},
        ],
        "contraindications": ["Hepatic impairment (LFT > 3× ULN)", "eGFR < 50 (50 mg OD only)"],
        "cautions":          ["Monitor LFTs every 6 months"],
        "HbA1c_reduction":   "0.6–0.9%",
        "weight_effect":     "Neutral",
        "hypo_risk":         "Low",
        "evidence_grade":    "A",
        "ref":               "ADA Standards 2024, Section 9"
    },
    "Teneligliptin": {
        "class":        "DPP-4 inhibitor",
        "mechanism":    "Inhibits DPP-4 → prolonged GLP-1 action",
        "start_dose":   "20 mg OD",
        "max_dose":     "40 mg OD",
        "brands": [
            {"name": "Tendia",   "company": "Glenmark",  "cost": "Low"},
            {"name": "Tenegla",  "company": "Mankind",   "cost": "Low"},
            {"name": "Tenofit",  "company": "Cipla",     "cost": "Low"},
        ],
        "contraindications": ["Severe hepatic impairment"],
        "cautions":          ["Most affordable DPP-4i in India — good for cost-constrained patients"],
        "HbA1c_reduction":   "0.7–0.9%",
        "weight_effect":     "Neutral",
        "hypo_risk":         "Low",
        "evidence_grade":    "B",
        "ref":               "RSSDI CPR 2023; Tenelia trial"
    },
    "Pioglitazone": {
        "class":        "Thiazolidinedione (TZD)",
        "mechanism":    "PPAR-γ agonist → improves peripheral insulin sensitivity",
        "start_dose":   "15 mg OD",
        "max_dose":     "45 mg OD",
        "brands": [
            {"name": "Pioz",    "company": "Zydus",    "cost": "Low"},
            {"name": "Pioglit", "company": "Sun Pharma","cost": "Low"},
            {"name": "Actos",   "company": "Takeda",   "cost": "Medium"},
        ],
        "contraindications": [
            "Heart failure NYHA class III–IV: CONTRAINDICATED (FDA black box warning — fluid retention, oedema)",
            "Heart failure NYHA class I–II: generally avoid (risk of HF exacerbation; individualise only with close monitoring)",
            "Bladder cancer (current or history)",
            "Osteoporosis / fragility fracture history (increased fracture risk — especially in women)",
            "Macular oedema",
            "Pregnancy",
        ],
        "cautions":          ["Weight gain +2–4 kg; fluid retention; avoid in HTN with oedema"],
        "HbA1c_reduction":   "0.8–1.4%",
        "weight_effect":     "Weight gain +2–4 kg",
        "hypo_risk":         "Low",
        "evidence_grade":    "A",
        "ref":               "ADA Standards 2024, Section 9; PROactive trial"
    },
    "Empagliflozin": {
        "class":        "SGLT-2 inhibitor",
        "mechanism":    "Inhibits SGLT-2 in proximal tubule → glycosuria → glucose and calorie excretion",
        "start_dose":   "10 mg OD (morning)",
        "max_dose":     "25 mg OD",
        "brands": [
            {"name": "Jardiance", "company": "Boehringer/Lilly", "cost": "High"},
            {"name": "Empaglu",   "company": "Cipla",            "cost": "Medium"},
            {"name": "Empa",      "company": "Sun Pharma",       "cost": "Medium"},
        ],
        "contraindications": [
            "eGFR < 30: do not initiate for glucose lowering (glycosuric effect minimal, adverse risk increases)",
            "eGFR < 20: stop even for CV/renal benefit (EMPA-KIDNEY lower limit ~20; consider clinical judgement below this)",
            "T1DM (high euglycaemic DKA risk — not approved)",
            "Recurrent UTI or genital mycotic infections",
            "CLASS ALLERGY in this patient",
        ],
        "cautions":          ["Hold during acute illness, surgery, contrast", "Euglycaemic DKA risk in T1DM", "Genital mycotic infections"],
        "HbA1c_reduction":   "0.7–1.0%",
        "weight_effect":     "Weight loss −2 to −3 kg",
        "hypo_risk":         "Low",
        "evidence_grade":    "A",
        "CV_benefit":        "EMPA-REG OUTCOME: 38% RRR CV death; EMPEROR-Reduced: HFrEF benefit",
        "ref":               "Zinman B et al., NEJM 2015 (EMPA-REG OUTCOME); ADA Standards 2024, Sections 9, 10, 11"
    },
    "Dapagliflozin": {
        "class":        "SGLT-2 inhibitor",
        "mechanism":    "Inhibits SGLT-2 → glycosuria",
        "start_dose":   "10 mg OD",
        "max_dose":     "10 mg OD",
        "brands": [
            {"name": "Forxiga",  "company": "AstraZeneca", "cost": "High"},
            {"name": "Dapaglu",  "company": "Cipla",       "cost": "Medium"},
        ],
        "contraindications": [
            "eGFR < 45: do not initiate for glucose lowering (reduced glycosuric effect below this threshold)",
            "eGFR < 25: contraindicated even for CKD/HF cardio-renal benefit (DAPA-CKD lower limit eGFR 25)",
            "T1DM (DKA risk — not approved)",
            "CLASS ALLERGY in this patient",
        ],
        "cautions":          ["Hold perioperatively; Fournier's gangrene (rare)"],
        "HbA1c_reduction":   "0.7–1.0%",
        "weight_effect":     "Weight loss −2 to −3 kg",
        "hypo_risk":         "Low",
        "evidence_grade":    "A",
        "CV_benefit":        "DECLARE-TIMI 58: HF hospitalisation reduction; DAPA-CKD: renal protection",
        "ref":               "Wiviott SD et al., NEJM 2019 (DECLARE); Heerspink HJL et al., NEJM 2020 (DAPA-CKD)"
    },
    "Canagliflozin": {
        "class":        "SGLT-2 inhibitor",
        "mechanism":    "Inhibits SGLT-2 → glycosuria",
        "start_dose":   "100 mg OD before first meal",
        "max_dose":     "300 mg OD",
        "brands": [
            {"name": "Invokana", "company": "J&J", "cost": "High"},
        ],
        "contraindications": [
            "eGFR < 45: do not initiate for glucose lowering (CANVAS/CREDENCE: glucose lowering effect lost below ~45)",
            "eGFR < 30: contraindicated even for renal protection (CREDENCE lower limit eGFR 30)",
            "T1DM (DKA risk — not approved)",
            "CLASS ALLERGY in this patient",
        ],
        "cautions":          [
            "Lower limb amputation risk (CANVAS: HR 1.97 vs placebo) — use with caution in peripheral vascular disease, prior amputation, or active foot ulcer",
            "Hold 3–5 days before major surgery (euglycaemic DKA risk)",
        ],
        "HbA1c_reduction":   "0.8–1.2%",
        "weight_effect":     "Weight loss",
        "hypo_risk":         "Low",
        "evidence_grade":    "A",
        "ref":               "Neal B et al., NEJM 2017 (CANVAS); CREDENCE trial"
    },
}

# ── GLP-1 RECEPTOR AGONISTS ──────────────────────────────────
GLP1_DRUGS = {
    "Semaglutide SC": {
        "class":     "GLP-1 receptor agonist",
        "mechanism": "Activates GLP-1R → glucose-dependent insulin secretion, glucagon suppression, gastric emptying delay, appetite reduction",
        "route":     "Subcutaneous injection",
        "titration": "0.25 mg/week × 4 weeks → 0.5 mg/week × 4 weeks → 1.0 mg/week (maintenance) → 2.0 mg/week if needed",
        "frequency": "Once weekly",
        "brands": [
            {"name": "Ozempic 0.25/0.5 mg pen", "company": "Novo Nordisk", "cost": "High"},
            {"name": "Ozempic 1 mg pen",         "company": "Novo Nordisk", "cost": "High"},
        ],
        "HbA1c_reduction":   "1.5–2.0%",
        "weight_effect":     "Weight loss −4 to −6 kg",
        "hypo_risk":         "Low",
        "CV_benefit":        "SUSTAIN-6: 26% RRR MACE in established CVD",
        "contraindications": ["Personal/family history MTC or MEN2", "Pregnancy", "Active pancreatitis"],
        "cautions":          ["GI side effects — start low, titrate slow", "Do NOT combine with DPP-4i"],
        "evidence_grade":    "A",
        "ref":               "Marso SP et al., NEJM 2016 (SUSTAIN-6); ADA Standards 2024, Section 9; RSSDI CPR 2023"
    },
    "Semaglutide oral": {
        "class":     "GLP-1 receptor agonist",
        "mechanism": "Same as SC Semaglutide; absorbed via SNAC technology",
        "route":     "Oral tablet",
        "titration": "3 mg OD × 4 weeks → 7 mg OD × 4 weeks → 14 mg OD (maintenance)",
        "frequency": "Once daily — take on empty stomach with plain water, wait 30 min before eating",
        "brands": [
            {"name": "Rybelsus 3 mg", "company": "Novo Nordisk", "cost": "High"},
            {"name": "Rybelsus 7 mg", "company": "Novo Nordisk", "cost": "High"},
            {"name": "Rybelsus 14 mg","company": "Novo Nordisk", "cost": "High"},
        ],
        "HbA1c_reduction":   "1.0–1.4%",
        "weight_effect":     "Weight loss −3 to −4 kg",
        "hypo_risk":         "Low",
        "CV_benefit":        "PIONEER-6: non-inferior CV safety",
        "contraindications": ["MTC/MEN2 history", "Pregnancy", "Dialysis (not studied)"],
        "cautions":          ["Needle-averse patients; absorption affected by other oral medications"],
        "evidence_grade":    "A",
        "ref":               "Husain M et al., NEJM 2019 (PIONEER-6); ADA Standards 2024"
    },
    "Liraglutide": {
        "class":     "GLP-1 receptor agonist",
        "mechanism": "Activates GLP-1R",
        "route":     "Subcutaneous injection",
        "titration": "0.6 mg/day × 1 week → 1.2 mg/day → 1.8 mg/day",
        "frequency": "Once daily",
        "brands": [
            {"name": "Victoza 1.2 mg pen", "company": "Novo Nordisk", "cost": "High"},
            {"name": "Victoza 1.8 mg pen", "company": "Novo Nordisk", "cost": "High"},
        ],
        "HbA1c_reduction":   "1.0–1.5%",
        "weight_effect":     "Weight loss −3 to −4 kg",
        "hypo_risk":         "Low",
        "CV_benefit":        "LEADER: 13% RRR MACE, 22% RRR CV death in established CVD",
        "contraindications": ["MTC/MEN2", "Pregnancy", "Pancreatitis"],
        "cautions":          ["Daily injection; GI side effects"],
        "evidence_grade":    "A",
        "ref":               "Marso SP et al., NEJM 2016 (LEADER); ADA Standards 2024"
    },
    "Dulaglutide": {
        "class":     "GLP-1 receptor agonist",
        "mechanism": "Activates GLP-1R (Fc-fusion, long half-life)",
        "route":     "Subcutaneous injection",
        "titration": "0.75 mg/week → 1.5 mg/week after 4 weeks if tolerated",
        "frequency": "Once weekly",
        "brands": [
            {"name": "Trulicity 0.75 mg pen", "company": "Lilly", "cost": "High"},
            {"name": "Trulicity 1.5 mg pen",  "company": "Lilly", "cost": "High"},
        ],
        "HbA1c_reduction":   "1.2–1.6%",
        "weight_effect":     "Weight loss −2 to −3 kg",
        "hypo_risk":         "Low",
        "CV_benefit":        "REWIND: 12% RRR MACE (included primary prevention population)",
        "contraindications": ["MTC/MEN2", "Pregnancy"],
        "cautions":          ["Most competitively priced weekly GLP-1 RA in India"],
        "evidence_grade":    "A",
        "ref":               "Gerstein HC et al., Lancet 2019 (REWIND); ADA Standards 2024"
    },
}

# ── INSULIN DATABASE ──────────────────────────────────────────
INSULIN_DRUGS = {
    "Glargine U-100": {
        "type":     "Long-acting basal analogue",
        "onset":    "1–2 hr", "peak": "Minimal (4–8 hr)", "duration": "20–24 hr",
        "start":    "10 U at bedtime OR 0.1–0.2 U/kg/day",
        "titration":"Increase 2U every 3 days to FBG 80–130 mg/dL (4.4–7.2 mmol/L)",
        "frequency":"Once daily (same time ± 2 hr)",
        "brands": [
            {"name": "Lantus SoloStar",  "company": "Sanofi",          "cost": "High",   "type": "Originator"},
            {"name": "Basalog",          "company": "Biocon",           "cost": "Medium", "type": "Biosimilar"},
            {"name": "Glaritus",         "company": "Wockhardt",        "cost": "Medium", "type": "Biosimilar"},
            {"name": "Basugine",         "company": "Lupin",            "cost": "Medium", "type": "Biosimilar"},
            {"name": "Semglee",          "company": "Mylan/Viatris",    "cost": "Medium", "type": "Biosimilar"},
        ],
        "variability": "CV ~84% (highest)",
        "hypo_risk": "Moderate (nocturnal)",
        "best_for":  "First basal insulin choice; cost-sensitive; stable T2DM; GDM (most studied)",
        "ref":       "ADA Standards 2024, Section 9; RSSDI CPR 2023"
    },
    "Glargine U-300 (Toujeo)": {
        "type":     "Concentrated long-acting basal analogue",
        "onset":    "2–3 hr", "peak": "Peakless", "duration": "24–36 hr",
        "start":    "10 U at same time daily; convert from U-100 at 1:1 (expect 10–17% more units needed)",
        "titration":"Increase 2U every 3 days to FBG target",
        "frequency":"Once daily (same time ± 3 hr)",
        "brands": [
            {"name": "Toujeo SoloStar",     "company": "Sanofi", "cost": "High", "type": "Originator"},
            {"name": "Toujeo Max SoloStar", "company": "Sanofi", "cost": "High", "type": "Originator"},
        ],
        "variability": "CV ~54%",
        "hypo_risk": "Lower than U-100 (especially during titration — BRIGHT trial)",
        "best_for":  "High dose T2DM (>60 U/day) — 3× concentrated, smaller volume; aggressive titration phase",
        "ref":       "Rosenstock J et al., Diabetes Care 2018 (BRIGHT); EDITION trials; ADA Standards 2024"
    },
    "Degludec U-100 (Tresiba)": {
        "type":     "Ultra-long-acting basal analogue",
        "onset":    "1–2 hr", "peak": "Peakless", "duration": ">42 hr",
        "start":    "10 U once daily; convert from Glargine U-100 at 1:1",
        "titration":"Increase 2U every 3 days — do NOT re-titrate before Day 4 (time to steady state 3–4 days)",
        "frequency":"Once daily, ANY time of day — must be ≥8 hr apart on consecutive days",
        "brands": [
            {"name": "Tresiba FlexTouch U-100", "company": "Novo Nordisk", "cost": "Very High", "type": "Originator"},
            {"name": "Tresiba FlexTouch U-200", "company": "Novo Nordisk", "cost": "Very High", "type": "Originator (concentrated)"},
        ],
        "variability": "CV ~20% (lowest of all basals)",
        "hypo_risk": "Lowest (DEVOTE: 40% lower severe hypoglycaemia vs Glargine U-100, HR 0.60)",
        "best_for":  "T1DM; high CV risk T2DM (DEVOTE); shift workers/irregular schedule; elderly alone; CKD; recurrent nocturnal hypoglycaemia on other basals",
        "ref":       "Marso SP et al., NEJM 2017 (DEVOTE); Mathieu C et al., Diabetes Care 2020 (CONCLUDE); BEGIN trials; ADA 2024"
    },
    "Detemir (Levemir)": {
        "type":     "Long-acting basal analogue",
        "onset":    "1–2 hr", "peak": "3–9 hr (dose-dependent)", "duration": "16–24 hr",
        "start":    "10 U OD or BD; dose ~10–20% higher than Glargine equivalent",
        "titration":"Titrate to FBG target; often BD in T1DM",
        "frequency":"Once or twice daily",
        "brands": [
            {"name": "Levemir FlexPen", "company": "Novo Nordisk", "cost": "High", "type": "Originator"},
        ],
        "variability": "Moderate",
        "hypo_risk": "Moderate",
        "best_for":  "Pregnancy — highest RCT evidence in T1DM pregnancy (CONCEPTT trial); less weight gain than Glargine U-100",
        "ref":       "Mathiesen ER et al., BMJ 2007 (Detemir vs NPH randomised trial in T1DM pregnancy — primary efficacy RCT); Feig DS et al., Lancet 2017 (CONCEPTT — CGM in T1DM pregnancy, Detemir used in majority); ADA Standards 2024, Section 15"
    },
    "Regular Human (Soluble)": {
        "type":     "Short-acting / soluble insulin",
        "onset":    "30–60 min", "peak": "2–4 hr", "duration": "6–8 hr",
        "start":    "SC: inject 30 min before meal. IV: 0.1 U/kg/hr infusion for DKA",
        "titration":"SC prandial: titrate to 2-hr PPG < 140 mg/dL",
        "frequency":"TDS before meals (SC); continuous infusion (IV)",
        "brands": [
            {"name": "Actrapid",      "company": "Novo Nordisk", "cost": "Low", "type": "Human"},
            {"name": "Huminsulin R",  "company": "Lilly",        "cost": "Low", "type": "Human"},
            {"name": "Insugen R",     "company": "Biocon",       "cost": "Low", "type": "Human"},
            {"name": "Wosulin R",     "company": "Wockhardt",    "cost": "Low", "type": "Human"},
        ],
        "variability": "High",
        "hypo_risk": "High (long tail of action)",
        "best_for":  "IV use in DKA/HHS/ICU (ONLY insulin safe for IV). Resource-limited SC prandial use.",
        "ref":       "JBDS DKA Guidelines 2023; ADA Standards 2024, Section 16"
    },
    "Lispro (Humalog)": {
        "type":     "Rapid-acting analogue",
        "onset":    "15–30 min", "peak": "1–2 hr", "duration": "3–5 hr",
        "start":    "4 U per meal or 1 U per 10–15 g carbohydrate (T1DM). Inject 0–15 min before meal.",
        "titration":"Titrate to 2-hr PPG < 7.8 mmol/L (140 mg/dL)",
        "frequency":"TDS with meals ± correction doses",
        "brands": [
            {"name": "Humalog",  "company": "Lilly",   "cost": "High",   "type": "Analogue"},
            {"name": "Basuloc",  "company": "Biocon",  "cost": "Medium", "type": "Biosimilar"},
            {"name": "Lupsulin", "company": "Lupin",   "cost": "Medium", "type": "Biosimilar"},
        ],
        "variability": "Moderate",
        "hypo_risk": "Moderate",
        "best_for":  "Standard bolus insulin for T1DM MDI; CSII compatible; carbohydrate counters",
        "ref":       "ADA Standards 2024, Section 7; RSSDI CPR 2023"
    },
    "Aspart (NovoRapid)": {
        "type":     "Rapid-acting analogue",
        "onset":    "10–20 min", "peak": "1–3 hr", "duration": "3–5 hr",
        "start":    "4–6 U per meal. Inject 5–15 min before meal.",
        "titration":"Titrate to PPG target",
        "frequency":"TDS with meals ± correction doses",
        "brands": [
            {"name": "NovoRapid FlexPen", "company": "Novo Nordisk", "cost": "High", "type": "Analogue"},
        ],
        "variability": "Moderate",
        "hypo_risk": "Moderate",
        "best_for":  "T1DM CSII (pump) — most studied in pumps; preferred bolus in pregnancy; DKA SC transition",
        "ref":       "ADA Standards 2024, Sections 7, 15; RSSDI CPR 2023"
    },
    "Faster Aspart (Fiasp)": {
        "type":     "Ultra-rapid-acting analogue",
        "onset":    "4–7 min", "peak": "60–90 min", "duration": "4–5 hr",
        "start":    "Same units as Aspart. Inject 0–2 min before meal or up to 20 min after.",
        "titration":"Titrate to PPG target",
        "frequency":"With meals ± correction",
        "brands": [
            {"name": "Fiasp FlexTouch", "company": "Novo Nordisk", "cost": "High", "type": "Analogue"},
        ],
        "variability": "Moderate",
        "hypo_risk": "Moderate",
        "best_for":  "Unpredictable eating (can dose after meal); CGM users; T1DM on hybrid closed-loop",
        "ref":       "ADA Standards 2024, Section 7; ONSET trial programme"
    },
    "NPH (Isophane)": {
        "type":     "Intermediate-acting",
        "onset":    "2–4 hr", "peak": "4–10 hr", "duration": "12–18 hr",
        "start":    "10 U at bedtime OR 0.1–0.2 U/kg; T1DM: twice daily",
        "titration":"Increase 2U every 3 days to FBG target",
        "frequency":"Once or twice daily",
        "brands": [
            {"name": "Insulatard",   "company": "Novo Nordisk", "cost": "Low", "type": "Human"},
            {"name": "Huminsulin N", "company": "Lilly",        "cost": "Low", "type": "Human"},
            {"name": "Insugen N",    "company": "Biocon",       "cost": "Low", "type": "Human"},
            {"name": "Wosulin N",    "company": "Wockhardt",    "cost": "Low", "type": "Human"},
        ],
        "variability": "Very High",
        "hypo_risk": "High nocturnal risk",
        "best_for":  "Cost-constrained settings where Glargine/Degludec not affordable; bedtime NPH in T2DM on Metformin is validated (UKPDS). Accept hypoglycaemia trade-off.",
        "ref":       "RSSDI CPR 2023; UKPDS; ADA Standards 2024"
    },
    "Premixed 30/70 (Human)": {
        "type":     "Premixed human insulin",
        "onset":    "30 min", "peak": "Dual: 2–4 hr + 4–10 hr", "duration": "12–18 hr",
        "start":    "0.3–0.4 U/kg/day; 2/3 before breakfast, 1/3 before dinner",
        "titration":"Adjust dinner dose for FBG; adjust breakfast dose for pre-dinner glucose",
        "frequency":"Twice daily, 30 min before breakfast and dinner",
        "brands": [
            {"name": "Mixtard 30",       "company": "Novo Nordisk", "cost": "Low", "type": "Human premix"},
            {"name": "Huminsulin 30/70", "company": "Lilly",        "cost": "Low", "type": "Human premix"},
            {"name": "Wosulin 30/70",    "company": "Wockhardt",    "cost": "Low", "type": "Human premix"},
            {"name": "Insugen 30/70",    "company": "Biocon",       "cost": "Low", "type": "Human premix"},
        ],
        "variability": "High",
        "hypo_risk": "High",
        "best_for":  "Cost-constrained T2DM on fixed diet/schedule. Not suitable for variable eaters. Most affordable premix.",
        "ref":       "RSSDI CPR 2023; ADA Standards 2024"
    },
    "Biphasic Aspart 30 (NovoMix)": {
        "type":     "Premixed analogue",
        "onset":    "10–20 min", "peak": "Dual: 1–4 hr + 4–8 hr", "duration": "10–16 hr",
        "start":    "0.3 U/kg/day BD; inject immediately before meal (no 30-min wait)",
        "titration":"Adjust as for human premix",
        "frequency":"Twice or three times daily before meals",
        "brands": [
            {"name": "NovoMix 30 FlexPen", "company": "Novo Nordisk", "cost": "High", "type": "Analogue premix"},
        ],
        "variability": "Moderate",
        "hypo_risk": "Moderate",
        "best_for":  "T2DM preferring 2-injection simplified regimen with analogue convenience (no pre-meal wait). Better PPG than human premix.",
        "ref":       "ADA Standards 2024; RSSDI CPR 2023"
    },
    "Degludec/Aspart 70/30 (Ryzodeg)": {
        "type":     "Basal+prandial co-formulation",
        "onset":    "Aspart component: 10–20 min; Degludec: 1–2 hr",
        "peak":     "Dual: Aspart 1–3 hr + Degludec peakless",
        "duration": ">42 hr (Degludec component)",
        "start":    "10 U OD before largest meal; can increase to BD (breakfast + dinner)",
        "titration":"Titrate to FBG and PPG targets",
        "frequency":"Once or twice daily before meal",
        "brands": [
            {"name": "Ryzodeg 70/30 FlexTouch", "company": "Novo Nordisk", "cost": "High", "type": "Co-formulation"},
        ],
        "variability": "Degludec component: CV ~20%",
        "hypo_risk": "Moderate",
        "best_for":  "T2DM needing basal + prandial in 1–2 injections; adherence-challenged; simplification from MDI",
        "ref":       "DUAL trial programme; ADA Standards 2024"
    },
    "Degludec U-200 (Tresiba U-200)": {
        "type":     "Ultra-long-acting basal analogue (concentrated)",
        "onset":    "1–2 hr", "peak": "Peakless", "duration": ">42 hr",
        "start":    "Convert from Degludec U-100 1:1 (same units, half the volume)",
        "titration":"Same as Degludec U-100 — increase 2U every 3–4 days",
        "frequency":"Once daily, ANY time ≥8 hr apart",
        "brands": [
            {"name": "Tresiba FlexTouch U-200", "company": "Novo Nordisk", "cost": "Very High", "type": "Concentrated analogue"},
        ],
        "variability": "CV ~20% (same as U-100)",
        "hypo_risk": "Lowest (same clinical profile as Degludec U-100)",
        "best_for":  "High insulin requirement (>60 U/day basal) — reduces injection volume 50%; obese T2DM; insulin-resistant patients needing large doses",
        "ref":       "BEGIN trials; FDA/CDSCO approval data; ADA Standards 2024, Section 9"
    },
}

# ── COMBINATION INJECTABLE THERAPY ───────────────────────────
COMBO_INJECTABLES = {
    "iGlarLixi (Soliqua)": {
        "class":        "Fixed-ratio GLP-1 RA + Basal insulin combination",
        "components":   "Insulin Glargine U-100 + Lixisenatide (GLP-1 RA)",
        "ratio":        "1 unit Glargine : 0.5 mcg Lixisenatide per dose unit",
        "dose_range":   "15–60 dose units OD before breakfast",
        "start_dose":   "15 units (if on basal insulin) or 15 units (insulin-naïve on GLP-1 RA)",
        "titration":    "Increase 2 units every week guided by FBG target",
        "brands": [
            {"name": "Soliqua 100/33", "company": "Sanofi", "cost": "Very High", "type": "Fixed-ratio combination pen"},
        ],
        "HbA1c_reduction": "1.5–2.0% (additive GLP-1 + basal effect)",
        "weight_effect":   "Neutral to slight loss (GLP-1 component offsets insulin weight gain)",
        "hypo_risk":       "Low–Moderate (GLP-1 glucose-dependent, reduces hypo vs basal alone)",
        "advantages": [
            "Single injection covering FBG (basal) + breakfast PPG (lixisenatide)",
            "Less nausea than GLP-1 RA alone (lower dose, slower titration)",
            "Weight-neutral vs basal insulin alone",
            "Simplified adherence — 1 injection, 1 pen",
        ],
        "best_for": "T2DM uncontrolled on basal insulin alone; high PPG component; obesity with insulin need; step-up from basal without adding bolus injections",
        "contraindications": ["T1DM", "LADA", "FCPD", "Personal/family history MTC or MEN2", "Pregnancy", "Pancreatitis history"],
        "ref": "LixiLan-O trial (Rosenstock J, Diabetes Care 2016); LixiLan-L trial (Aroda VR, Diabetes Care 2016); ADA Standards 2024, Section 9; RSSDI CPR 2023"
    },
    "IDegLira (Xultophy)": {
        "class":        "Fixed-ratio GLP-1 RA + Basal insulin combination",
        "components":   "Insulin Degludec U-100 + Liraglutide (GLP-1 RA)",
        "ratio":        "1 unit Degludec : 0.036 mg Liraglutide per dose unit",
        "dose_range":   "10–50 dose units OD (max Degludec 50U + Liraglutide 1.8 mg)",
        "start_dose":   "10 units OD (insulin-naïve) or 16 units (converting from basal insulin)",
        "titration":    "Increase 2 units every 3–4 days guided by FBG",
        "brands": [
            {"name": "Xultophy 100/3.6", "company": "Novo Nordisk", "cost": "Very High", "type": "Fixed-ratio combination pen"},
        ],
        "HbA1c_reduction": "1.8–2.2% (highest in DUAL programme)",
        "weight_effect":   "Weight loss 0.5–2 kg (Degludec weight gain offset by Liraglutide loss)",
        "hypo_risk":       "Low (DUAL V: lower hypo than basal-bolus MDI with similar HbA1c reduction)",
        "advantages": [
            "Single injection. Max Liraglutide dose 1.8 mg — full CV benefit (LEADER trial applies)",
            "DUAL V: comparable glycaemic control to basal-bolus with 75% fewer injections and less hypoglycaemia",
            "Degludec component: lowest basal hypoglycaemia risk (DEVOTE trial)",
            "Weight loss vs basal insulin alone",
        ],
        "best_for": "T2DM inadequately controlled on basal insulin; alternative to MDI intensification; obesity with insulin need; high CV risk (Liraglutide LEADER benefit)",
        "contraindications": ["T1DM", "LADA", "FCPD", "Personal/family history MTC or MEN2", "Pregnancy", "Pancreatitis history", "eGFR < 15"],
        "ref": "DUAL I–VIII trials; LEADER trial (Liraglutide CV safety); DEVOTE trial (Degludec); ADA Standards 2024, Section 9; RSSDI CPR 2023"
    },
}

# ── INVESTIGATION REFERENCE DATABASE ─────────────────────────
INVESTIGATIONS = {
    "GAD65 antibody": {
        "use":    "LADA diagnosis; distinguish autoimmune from non-autoimmune DM",
        "interpretation": {
            "positive": "Confirms autoimmune beta-cell destruction → LADA (if age 30–60, initial OAD response) or T1DM",
            "negative":  "Does not fully exclude LADA — add IA-2 and ZnT8 if suspicion remains",
        },
        "ref": "ADA Standards 2024, Section 2; Fourlanos S et al., Diabetes Care 2006"
    },
    "IA-2 antibody": {
        "use":    "LADA / T1DM; second-line if GAD65 negative",
        "interpretation": {
            "positive": "Supports autoimmune DM diagnosis",
            "negative":  "Add ZnT8 antibody if still high suspicion",
        },
        "ref": "ADA Standards 2024, Section 2"
    },
    "ZnT8 antibody": {
        "use":    "Third-line autoimmune marker; increases sensitivity when added to GAD65 + IA-2",
        "interpretation": {
            "positive": "Confirms autoimmune DM",
        },
        "ref": "ADA Standards 2024, Section 2"
    },
    "Fasting C-peptide": {
        "use":    "Beta-cell reserve assessment; distinguish secretory failure vs insulin resistance",
        "interpretation": {
            "<0.6 nmol/L (1.8 ng/mL)":   "Severely impaired secretory reserve — insulin mandatory",
            "0.6–1.2 nmol/L":              "Reduced secretory capacity — consider early insulin",
            ">1.2 nmol/L":                 "Adequate secretory reserve — oral agents may suffice",
        },
        "ref": "ADA Standards 2024, Section 2; Holt et al., Textbook of Diabetes 5th ed."
    },
    "Stimulated C-peptide": {
        "use":    "More sensitive than fasting — gold standard for secretory reserve",
        "interpretation": {
            "<1.0 nmol/L (3.0 ng/mL) at 90 min post-75g OGTT": "Significant secretory failure",
        },
        "ref": "ADA Standards 2024, Section 2"
    },
    "HOMA-IR": {
        "use":    "Quantify insulin resistance",
        "formula": "HOMA-IR = (Fasting Insulin µIU/mL × Fasting Glucose mmol/L) ÷ 22.5",
        "interpretation": {
            "<2.5": "Normal insulin sensitivity",
            "2.5–5.0": "Insulin resistance",
            ">5.0":    "Severe insulin resistance",
        },
        "ref": "Matthews DR et al., Diabetologia 1985"
    },
    "HOMA-β": {
        "use":    "Quantify beta-cell secretory function",
        "formula": "HOMA-β = (20 × Fasting Insulin µIU/mL) ÷ (Fasting Glucose mmol/L − 3.5)",
        "interpretation": {
            ">100%": "Normal",
            "50–100%": "Mildly reduced",
            "<50%":    "Significant beta-cell dysfunction",
        },
        "ref": "Matthews DR et al., Diabetologia 1985"
    },
    "Faecal Elastase-1": {
        "use":    "Pancreatic exocrine insufficiency — screen for FCPD",
        "interpretation": {
            ">200 µg/g":  "Normal exocrine function",
            "100–200 µg/g": "Moderate exocrine insufficiency",
            "<100 µg/g":  "Severe exocrine insufficiency — FCPD, chronic pancreatitis",
        },
        "ref": "Lindkvist B, World J Gastroenterol 2013"
    },
    "X-ray abdomen (plain)": {
        "use":    "Screen for pancreatic calculi — FCPD first-line imaging",
        "interpretation": {
            "Calcifications along pancreatic duct axis": "Pancreatic calculi — strongly supports FCPD diagnosis",
            "No calcifications": "Does not exclude FCPD — proceed to ultrasound or CT",
        },
        "ref": "Mohan V, Pancreatology 2012"
    },
    "CECT Abdomen": {
        "use":    "Gold standard imaging for FCPD; rules out pancreatic malignancy",
        "interpretation": {
            "Calculi + ductal dilatation + atrophy": "Diagnostic of chronic calcific pancreatitis / FCPD",
            "Mass lesion": "Suspect pancreatic adenocarcinoma — urgent oncology referral",
        },
        "ref": "Mohan V, Pancreatology 2012; Lindkvist B, WJG 2013"
    },
    "CA 19-9": {
        "use":    "Pancreatic malignancy surveillance in FCPD patients",
        "interpretation": {
            ">37 U/mL": "Elevated — warrants CECT to rule out malignancy; can be elevated in pancreatitis too",
            "<37 U/mL": "Normal — reassuring but does not exclude early malignancy",
        },
        "ref": "ADA Standards 2024"
    },
    "SPINK1 mutation": {
        "use":    "Genetic confirmation of FCPD predisposition (tertiary setting)",
        "interpretation": {
            "Positive": "Supports FCPD genetic basis; found in ~50% Indian FCPD patients",
        },
        "ref": "Bhatia E et al., Gut 2002"
    },
    "MODY probability score (Exeter)": {
        "use":    "Screening tool to decide who needs genetic testing for MODY",
        "interpretation": {
            ">25%": "Refer for MODY genetic panel (GCK/MODY2, HNF1A/MODY3, HNF4A/MODY1, HNF1B/MODY5)",
            "<25%": "MODY less likely — clinical monitoring sufficient",
        },
        "ref": "Shields BM et al., Diabet Med 2012; ADA Standards 2024, Section 2"
    },
    "Anti-TPO antibody + TSH": {
        "use":    "Screen for concurrent autoimmune thyroid disease in LADA / T1DM",
        "interpretation": {
            "Anti-TPO positive + TSH elevated": "Hashimoto's thyroiditis — start levothyroxine per ATA guidelines",
            "Anti-TPO positive + TSH normal":   "Monitor TSH annually",
        },
        "ref": "Holt et al., Textbook of Diabetes 5th ed."
    },
    "eGFR (CKD-EPI)": {
        "use":    "Renal function for drug dose adjustment and CKD staging",
        "interpretation": {
            "≥60":    "G1–G2: Standard doses; screen UACR annually",
            "45–59":  "G3a: Metformin caution; SGLT2i reduced efficacy below 45",
            "30–44":  "G3b: Metformin contraindicated; SGLT2i stop for glucose lowering; refer nephrology",
            "15–29":  "G4: Insulin dose reduce; DPP-4i dose adjust; urgent nephrology",
            "<15":    "G5/ESKD: Insulin-based management; dialysis planning",
        },
        "ref": "ADA Standards 2024, Section 11; RSSDI CPR 2023"
    },
    "UACR (Urine Albumin-Creatinine Ratio)": {
        "use":    "Early diabetic nephropathy screening and staging",
        "interpretation": {
            "<30 mg/g":   "Normal",
            "30–300 mg/g":"Microalbuminuria (A2) — ACE inhibitor/ARB indicated",
            ">300 mg/g":  "Macroalbuminuria (A3) — maximise RAS blockade; SGLT2i for renoprotection",
        },
        "ref": "ADA Standards 2024, Section 11; RSSDI CPR 2023"
    },
}

# ── ACUTE PROTOCOLS ───────────────────────────────────────────
ACUTE_REFS = {
    "DKA":         "JBDS DKA Guidelines 2023; ADA Standards 2024, Section 16",
    "HHS":         "JBDS HHS Guidelines 2023; ADA Standards 2024, Section 16",
    "Hypoglycaemia":"ADA Standards 2024, Section 6; RSSDI CPR 2023",
}

# ── CONFIDENCE LEVEL DEFINITIONS ──────────────────────────────
CONFIDENCE = {
    "High":     "Directly supported by ≥1 major guideline with Grade A/B evidence or landmark RCT. Recommendation is unambiguous.",
    "Moderate": "Supported by Grade C/Expert opinion, observational data, or small RCTs. Some divergence between guidelines may exist.",
    "Low":      "Limited or no direct guideline coverage. Extrapolated from adjacent evidence. Significant clinical uncertainty exists.",
}
