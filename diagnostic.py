# ============================================================
# diagnostic.py  —  Diagnosis Classification Engine
# Rule-based algorithms from ADA 2024, RSSDI CPR 2023,
# Fourlanos 2006 (LADA), Shields 2012 (MODY), Mohan 2012 (FCPD)
# ============================================================

try:
    from data import LADA_SCORE_CRITERIA, LADA_SCORE_CUTOFF
except ImportError:
    from modules.data import LADA_SCORE_CRITERIA, LADA_SCORE_CUTOFF


def compute_lada_score(age_at_dx, acute_onset, bmi, personal_ai, family_ai):
    """Fourlanos LADA Clinical Score (0–5). Score ≥3 → investigate."""
    score = 0
    details = []
    if age_at_dx is not None and age_at_dx < 50:
        score += 1
        details.append("✅ Age < 50 at diagnosis (+1)")
    else:
        details.append("❌ Age ≥ 50 at diagnosis (0)")
    if acute_onset:
        score += 1
        details.append("✅ Acute onset symptoms (+1)")
    else:
        details.append("❌ No acute onset symptoms (0)")
    if bmi is not None and bmi < 25:
        score += 1
        details.append(f"✅ BMI {bmi:.1f} < 25 kg/m² (+1)")
    else:
        details.append(f"❌ BMI ≥ 25 kg/m² (0)")
    if personal_ai:
        score += 1
        details.append("✅ Personal autoimmune history (+1)")
    else:
        details.append("❌ No personal autoimmune history (0)")
    if family_ai:
        score += 1
        details.append("✅ Family autoimmune history (+1)")
    else:
        details.append("❌ No family autoimmune history (0)")
    return score, details


def classify_diabetes(inputs: dict) -> list:
    """
    Master diagnosis classifier. Returns a list of dicts, each with:
    {
      'diagnosis': str,
      'probability': str,   # 'High' / 'Moderate' / 'Low' / 'Unlikely'
      'confidence': str,    # 'High' / 'Moderate' / 'Low'
      'key_features': list,
      'next_steps': list,
      'ref': str,
      'warning': str or None
    }
    """
    results = []

    age          = inputs.get("age")
    bmi          = inputs.get("bmi")
    age_at_dx    = inputs.get("age_at_dx")
    duration_yrs = inputs.get("duration_yrs", 0)
    hba1c        = inputs.get("hba1c")
    fpg_mgdl     = inputs.get("fpg_mgdl")
    c_peptide    = inputs.get("c_peptide")       # nmol/L
    gad_status   = inputs.get("gad_status")       # 'positive'/'negative'/'not done'
    homa_ir      = inputs.get("homa_ir")
    acute_onset  = inputs.get("acute_onset", False)
    ketosis      = inputs.get("ketosis", False)
    family_dm    = inputs.get("family_dm", False)
    family_ai    = inputs.get("family_ai", False)
    personal_ai  = inputs.get("personal_ai", False)
    abdo_pain    = inputs.get("abdo_pain", False)
    pancreatic_calculi = inputs.get("pancreatic_calculi", False)
    steatorrhoea = inputs.get("steatorrhoea", False)
    oad_failure  = inputs.get("oad_failure", False)
    pregnancy    = inputs.get("pregnancy", False)
    family_3gen  = inputs.get("family_3gen", False)
    steroid_use  = inputs.get("steroid_use", False)
    other_drug   = inputs.get("other_drug", False)
    pancreatitis_hx = inputs.get("pancreatitis_hx", False)
    metabolic_synd  = inputs.get("metabolic_synd", False)
    tropical_india  = inputs.get("tropical_india", False)

    # ── GDM ─────────────────────────────────────────────────
    if pregnancy:
        results.append({
            "diagnosis":    "Gestational Diabetes Mellitus (GDM)",
            "probability":  "High" if fpg_mgdl and fpg_mgdl >= 92 else "Possible",
            "confidence":   "High",
            "key_features": ["Pregnancy", "Hyperglycaemia detected in pregnancy"],
            "next_steps": [
                "75g OGTT — DIPSI criteria: 2-hr plasma glucose ≥ 140 mg/dL (7.8 mmol/L) = GDM",
                "FPG ≥ 126 mg/dL or 2-hr ≥ 200 mg/dL in 1st trimester = pre-existing DM, not GDM",
                "Medical Nutrition Therapy (MNT) for 2 weeks first",
                "If targets not met → Insulin (Aspart + Detemir or Aspart + NPH)",
                "Metformin as 2nd-line oral option per DIPSI 2020",
            ],
            "ref": "DIPSI 2020; ADA Standards 2024, Section 15",
            "warning": "⚠️ Metformin and most OADs are not first-line in pregnancy. Insulin preferred."
        })
        return results

    # ── SECONDARY DM ─────────────────────────────────────────
    secondary_features = []
    if steroid_use:
        secondary_features.append("Glucocorticoid-induced diabetes")
    if other_drug:
        secondary_features.append("Drug-induced diabetes (antipsychotics, tacrolimus, thiazides)")
    if pancreatitis_hx and not pancreatic_calculi:
        secondary_features.append("Post-pancreatitis diabetes (non-calcific)")
    if secondary_features:
        results.append({
            "diagnosis":    "Secondary / Drug-induced Diabetes",
            "probability":  "High",
            "confidence":   "High",
            "key_features": secondary_features,
            "next_steps": [
                "Identify and address underlying cause",
                "Steroid-induced: often postprandial predominance → prandial insulin or premixed",
                "Taper steroid dose if clinically feasible",
                "Screen for other endocrinopathies: Cushing's (UFC/LDDST), Acromegaly (IGF-1), Haemochromatosis (serum ferritin)",
            ],
            "ref": "ADA Standards 2024, Section 2; Williams Endocrinology 14th ed.",
            "warning": None
        })

    # ── FCPD ─────────────────────────────────────────────────
    fcpd_flags = sum([abdo_pain, pancreatic_calculi, steatorrhoea,
                      (bmi is not None and bmi < 19),
                      tropical_india])
    if pancreatic_calculi or (abdo_pain and (tropical_india or (bmi is not None and bmi < 19))):
        fcpd_prob = "High" if pancreatic_calculi else "Moderate"
        results.append({
            "diagnosis":   "Fibrocalculous Pancreatic Diabetes (FCPD)",
            "probability": fcpd_prob,
            "confidence":  "High" if pancreatic_calculi else "Moderate",
            "key_features": [
                f"Pancreatic calculi: {'Yes' if pancreatic_calculi else 'Not confirmed — imaging needed'}",
                f"Abdominal pain history: {'Yes' if abdo_pain else 'No'}",
                f"BMI: {bmi:.1f} kg/m²" if bmi else "BMI not entered",
                f"Tropical India origin: {'Yes' if tropical_india else 'No'}",
                f"Steatorrhoea: {'Yes' if steatorrhoea else 'No'}",
            ],
            "next_steps": [
                "X-ray abdomen (plain) — pancreatic calculi?",
                "CECT abdomen if X-ray inconclusive — calculi, ductal dilatation, atrophy, exclude malignancy",
                "Faecal Elastase-1 — exocrine sufficiency",
                "Fasting C-peptide — beta-cell reserve",
                "CA 19-9 — baseline malignancy screen",
                "SPINK1 mutation (tertiary centre — found in ~50% Indian FCPD)",
                "Fat-soluble vitamins (A, D, E, K) + B12 + Zinc",
                "MANAGEMENT: Insulin mandatory (Regular IV only for DKA); PERT (Creon 25,000–50,000 U with meals)",
                "⚠️ AVOID Sulfonylureas, SGLT2i, GLP-1 RA in FCPD — high hypoglycaemia risk (alpha-cell loss → no glucagon counter-regulation)",
            ],
            "ref": "Mohan V, Pancreatology 2012; Bhatia E et al., Gut 2002; Williams Endocrinology 14th ed., Ch. 31",
            "warning": "⚠️ FCPD: BOTH insulin AND glucagon are deficient — severe brittle hypoglycaemia risk. Start insulin at low dose (0.3 U/kg/day), titrate carefully."
        })

    # ── LADA ─────────────────────────────────────────────────
    lada_score, lada_details = compute_lada_score(age_at_dx, acute_onset, bmi, personal_ai, family_ai)
    if lada_score >= 2 or oad_failure or (gad_status == "positive"):
        lada_prob = "High" if (gad_status == "positive" or lada_score >= 3) else "Moderate" if lada_score == 2 else "Low"
        results.append({
            "diagnosis":   "LADA (Latent Autoimmune Diabetes in Adults)",
            "probability": lada_prob,
            "confidence":  "High" if gad_status == "positive" else "Moderate",
            "key_features": [
                f"LADA Clinical Score: {lada_score}/5 (cut-off ≥3 — sensitivity 90%, specificity 71%)",
                f"GAD65 status: {gad_status or 'Not done'}",
                f"OAD failure: {'Yes' if oad_failure else 'No'}",
                f"BMI: {bmi:.1f} kg/m²" if bmi else "",
            ],
            "next_steps": [
                "GAD65 antibody (order first — most sensitive single test, ~70–80%)",
                "If GAD65 negative but suspicion remains: IA-2 antibody + ZnT8 antibody",
                "Fasting C-peptide (assess beta-cell reserve)",
                "Anti-TPO antibody + TSH (concurrent autoimmune thyroid disease in ~30%)",
                "MANAGEMENT: STOP sulfonylurea immediately if GAD+",
                "If C-peptide preserved (>0.6 nmol/L): basal insulin early + Metformin ± GLP-1 RA",
                "If C-peptide low (<0.6 nmol/L): full MDI (basal-bolus) — manage as T1DM",
                "CGM strongly recommended (ATTD Consensus 2023)",
            ],
            "ref": "Fourlanos S et al., Diabetes Care 2006; ADA Standards 2024, Section 2; RSSDI CPR 2023",
            "warning": "⚠️ LADA: Sulfonylureas accelerate beta-cell exhaustion — discontinue immediately on confirmation. Do not delay insulin."
        })

    # ── MODY ─────────────────────────────────────────────────
    mody_flags = 0
    mody_flag_list = []
    if age_at_dx is not None and age_at_dx < 35:
        mody_flags += 1; mody_flag_list.append("Age at diagnosis < 35 years")
    if bmi is not None and bmi < 25:
        mody_flags += 1; mody_flag_list.append("Non-obese at diagnosis")
    if family_3gen:
        mody_flags += 2; mody_flag_list.append("3-generation family history (autosomal dominant pattern)")
    if gad_status == "negative":
        mody_flags += 1; mody_flag_list.append("GAD antibody negative")
    if c_peptide and c_peptide > 0.6 and duration_yrs > 3:
        mody_flags += 1; mody_flag_list.append("C-peptide detectable at >3 years duration")
    if not metabolic_synd:
        mody_flags += 1; mody_flag_list.append("No features of metabolic syndrome")

    if mody_flags >= 3:
        mody_prob = "High" if (family_3gen and mody_flags >= 5) else "Moderate" if mody_flags >= 3 else "Low"
        results.append({
            "diagnosis":   "MODY (Maturity-Onset Diabetes of the Young)",
            "probability": mody_prob,
            "confidence":  "Moderate",
            "key_features": mody_flag_list,
            "next_steps": [
                "Calculate MODY Probability Score at exeter.ac.uk/mody-calculator",
                "If score >25%: refer for MODY genetic panel",
                "Key genes: GCK/MODY2 (mild stable hyperglycaemia, diet-managed), HNF1A/MODY3 (sulphonylurea-sensitive), HNF4A/MODY1, HNF1B/MODY5",
                "MODY2/GCK: FPG typically 5.5–8.0 mmol/L, stable, usually no pharmacotherapy needed",
                "MODY3/HNF1A: Responds dramatically to low-dose sulphonylurea — diagnostic and therapeutic",
                "Genetic counselling for family members",
            ],
            "ref": "Shields BM et al., Diabet Med 2012; ADA Standards 2024, Section 2; RSSDI CPR 2023",
            "warning": None
        })

    # ── LEAN T2DM ────────────────────────────────────────────
    lean_flags = []
    if bmi is not None and bmi < 22:
        lean_flags.append(f"BMI {bmi:.1f} < 22 kg/m² (low for Asian T2DM threshold)")
    if not metabolic_synd:
        lean_flags.append("No features of metabolic syndrome")
    if homa_ir is not None and homa_ir < 2.5:
        lean_flags.append(f"HOMA-IR {homa_ir:.1f} — low insulin resistance")
    if c_peptide and c_peptide < 0.8:
        lean_flags.append(f"C-peptide {c_peptide:.1f} nmol/L — reduced secretory capacity")

    if bmi is not None and bmi < 22 and gad_status != "positive" and not pancreatic_calculi and len(lean_flags) >= 2:
        results.append({
            "diagnosis":   "Lean T2DM",
            "probability": "Moderate",
            "confidence":  "Moderate",
            "key_features": lean_flags,
            "next_steps": [
                "Exclude LADA (GAD65, IA-2 antibodies — if not done)",
                "Exclude FCPD (X-ray abdomen, CECT if abdominal pain history)",
                "Exclude MODY (family history 3-generation? → MODY probability calculator)",
                "Fasting C-peptide + HOMA-IR (secretory defect vs resistance)",
                "Body composition (waist circumference — metabolically obese normal weight?)",
                "MANAGEMENT: Secretagogue (low-dose SU) may be more effective than Metformin alone",
                "Early insulin if C-peptide low",
                "Nutritional rehabilitation — ensure caloric adequacy (not caloric restriction)",
                "GLP-1 RA if some secretory reserve remains",
            ],
            "ref": "Mohan V et al., J Diabetes Sci Technol 2019; RSSDI CPR 2023; Williams Endocrinology 14th ed.",
            "warning": "⚠️ Do NOT aggressively restrict calories in lean T2DM — further weight loss is harmful."
        })

    # ── T1DM ─────────────────────────────────────────────────
    t1_flags = []
    if acute_onset: t1_flags.append("Acute / abrupt onset")
    if ketosis:     t1_flags.append("Ketosis / DKA")
    if age_at_dx is not None and age_at_dx < 30: t1_flags.append(f"Age at diagnosis < 30 years ({age_at_dx} yrs)")
    if bmi is not None and bmi < 23: t1_flags.append(f"BMI {bmi:.1f} (normal/low)")
    if c_peptide is not None and c_peptide < 0.3: t1_flags.append(f"Very low C-peptide {c_peptide:.2f} nmol/L")
    if gad_status == "positive": t1_flags.append("GAD65 antibody positive")

    if (ketosis and acute_onset) or (gad_status == "positive" and c_peptide and c_peptide < 0.3) or len(t1_flags) >= 3:
        t1_prob = "High" if (ketosis or (gad_status == "positive" and c_peptide and c_peptide < 0.3)) else "Moderate"
        results.append({
            "diagnosis":   "Type 1 Diabetes Mellitus (T1DM)",
            "probability": t1_prob,
            "confidence":  "High" if (gad_status == "positive" and ketosis) else "Moderate",
            "key_features": t1_flags,
            "next_steps": [
                "If DKA / ketosis → ACUTE PROTOCOL (see DKA tab)",
                "GAD65 + IA-2 + ZnT8 antibodies",
                "Fasting C-peptide",
                "Anti-TPO + TSH (concurrent autoimmune thyroid — screen at diagnosis)",
                "Coeliac screen (anti-tTG IgA + total IgA)",
                "MANAGEMENT: Basal-bolus MDI mandatory from diagnosis",
                "Preferred basal: Degludec U-100 (Tresiba) — lowest nocturnal hypoglycaemia (BEGIN trials)",
                "Preferred bolus: Aspart (NovoRapid) or Lispro (Humalog/Basuloc)",
                "CGM (Freestyle Libre / Dexcom G6) — strongly recommended (ATTD 2023)",
                "Structured diabetes education (carbohydrate counting)",
            ],
            "ref": "ADA Standards 2024, Sections 2, 7; RSSDI CPR 2023; ATTD Consensus 2023",
            "warning": "⚠️ T1DM requires insulin from day 1 — never delay for OAD trial."
        })

    # ── T2DM ─────────────────────────────────────────────────
    t2_flags = []
    if age_at_dx is not None and age_at_dx >= 30: t2_flags.append(f"Age at diagnosis ≥ 30 years ({age_at_dx} yrs)")
    if bmi is not None and bmi >= 23: t2_flags.append(f"BMI {bmi:.1f} ≥ 23 kg/m² (Asian threshold)")
    if family_dm: t2_flags.append("Family history of T2DM")
    if metabolic_synd: t2_flags.append("Metabolic syndrome features (dyslipidaemia, hypertension, central obesity)")
    if homa_ir is not None and homa_ir > 2.5: t2_flags.append(f"HOMA-IR {homa_ir:.1f} — insulin resistance")
    if not acute_onset and not ketosis: t2_flags.append("Gradual / insidious onset")
    if gad_status == "negative": t2_flags.append("GAD antibody negative")

    # T2DM is a diagnosis of exclusion among the major types
    if len(t2_flags) >= 2 and gad_status != "positive" and not pancreatic_calculi:
        t2_prob = "High" if len(t2_flags) >= 4 else "Moderate"
        results.append({
            "diagnosis":   "Type 2 Diabetes Mellitus (T2DM)",
            "probability": t2_prob,
            "confidence":  "High" if len(t2_flags) >= 4 else "Moderate",
            "key_features": t2_flags,
            "next_steps": [
                "Confirm: rule out LADA (GAD65), MODY (family history), FCPD (imaging if abdominal pain)",
                "Baseline investigations: HbA1c, FPG, 2-hr PPG, eGFR, UACR, lipids, LFT, ECG",
                "10-year ASCVD risk assessment",
                "Fundus examination, foot examination at diagnosis",
                "MANAGEMENT: See Treatment Planner tab",
                "Metformin first-line if eGFR ≥ 30 and no contraindications",
                "Add second agent based on CV risk, CKD, weight, cost — see treatment algorithm",
            ],
            "ref": "ADA Standards 2024, Section 9; RSSDI CPR 2023; ICMR T2DM 2018",
            "warning": None
        })

    # ── No clear classification ───────────────────────────────
    if not results:
        results.append({
            "diagnosis":   "Insufficient information for classification",
            "probability": "N/A",
            "confidence":  "Low",
            "key_features": ["Please complete more clinical details"],
            "next_steps": [
                "Enter age, BMI, age at diagnosis, HbA1c, C-peptide, GAD status",
                "Minimum required: age at diagnosis, BMI, symptom onset pattern",
            ],
            "ref": "ADA Standards 2024, Section 2",
            "warning": None
        })

    # Sort by probability
    prob_order = {"High": 0, "Moderate": 1, "Possible": 2, "Low": 3, "Unlikely": 4, "N/A": 5}
    results.sort(key=lambda x: prob_order.get(x["probability"], 5))
    return results


def get_investigation_list(diagnosis_name: str) -> list:
    """Returns the recommended investigation list for a given diagnosis."""
    inv_map = {
        "T2DM": [
            "HbA1c", "FPG", "2-hr PPG (OGTT)", "eGFR (CKD-EPI)", "UACR",
            "Fasting lipid profile", "LFT", "ECG", "Fundus examination",
            "Foot exam (monofilament + ABI)", "GAD65 (to exclude LADA)",
        ],
        "T1DM": [
            "GAD65 antibody", "IA-2 antibody", "ZnT8 antibody",
            "Fasting C-peptide", "HbA1c", "eGFR", "UACR",
            "Anti-TPO antibody + TSH", "Anti-tTG IgA (coeliac screen)",
            "Fundus", "Foot exam",
        ],
        "LADA": [
            "GAD65 antibody (FIRST)", "IA-2 antibody", "ZnT8 antibody",
            "Fasting C-peptide", "Anti-TPO + TSH",
            "HbA1c", "eGFR", "UACR",
        ],
        "FCPD": [
            "X-ray abdomen (plain)", "CECT abdomen (pancreatic protocol)",
            "Faecal Elastase-1", "Fasting C-peptide",
            "CA 19-9", "SPINK1 mutation (tertiary)",
            "Vitamins A, D, E, K levels", "B12", "Zinc",
            "HbA1c", "eGFR",
        ],
        "MODY": [
            "GAD65 antibody", "Fasting C-peptide",
            "MODY Probability Score (exeter.ac.uk/mody-calculator)",
            "MODY genetic panel (if score >25%): GCK, HNF1A, HNF4A, HNF1B",
            "Family screening (first-degree relatives)",
        ],
        "GDM": [
            "75g OGTT (DIPSI: 2-hr plasma glucose ≥140 mg/dL = GDM)",
            "FPG, 2-hr PG", "HbA1c (if available)",
            "Fasting lipids", "Renal function",
            "Fundus examination",
        ],
    }
    for key, val in inv_map.items():
        if key.lower() in diagnosis_name.lower():
            return val
    return inv_map.get("T2DM", [])
