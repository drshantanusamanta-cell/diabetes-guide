# ============================================================
# treatment.py  —  Treatment Planner + Insulin Calculator
# ADA-EASD Consensus 2022, ADA Standards 2024, RSSDI CPR 2023
# ============================================================

try:
    from data import ORAL_DRUGS, GLP1_DRUGS, INSULIN_DRUGS, COMBO_INJECTABLES
except ImportError:
    from modules.data import ORAL_DRUGS, GLP1_DRUGS, INSULIN_DRUGS, COMBO_INJECTABLES


def _brand_str(brands: list, max_show: int = 3) -> str:
    shown = brands[:max_show]
    parts = [f"**{b['name']}** ({b['company']}, {b['cost']} cost)" for b in shown]
    return " · ".join(parts)


def recommend_treatment(inputs: dict) -> dict:
    """
    Inputs:
      hba1c, egfr, has_ascvd, has_hf, has_ckd, hf_type ('HFrEF'/'HFpEF'),
      sglt2_allergy, glp1_ok, obesity (BMI>27), hypo_concern,
      cost_preference ('low'/'medium'/'any'),
      on_metformin, current_drugs (list of drug names),
      age, pregnancy, dm_type ('T2DM'/'LADA'/'FCPD'/'T1DM'),
      has_nash_ir (bool) — NASH/NAFLD, PCOS, or documented high HOMA-IR (specific indication for Pioglitazone),
      bladder_cancer (bool) — history of bladder cancer (Pioglitazone contraindication)
    Returns: dict with 'steps' list, 'notes', 'refs'
    """
    hba1c          = inputs.get("hba1c", 8.0)
    egfr           = inputs.get("egfr", 90)
    has_ascvd      = inputs.get("has_ascvd", False)
    has_hf         = inputs.get("has_hf", False)
    has_ckd        = inputs.get("has_ckd", False)
    sglt2_allergy  = inputs.get("sglt2_allergy", False)
    glp1_ok        = inputs.get("glp1_ok", True)
    obesity        = inputs.get("obesity", False)
    hypo_concern   = inputs.get("hypo_concern", False)
    cost_pref      = inputs.get("cost_preference", "any")
    on_metformin   = inputs.get("on_metformin", False)
    current_drugs  = inputs.get("current_drugs", [])
    age                = inputs.get("age", 50)
    dm_type            = inputs.get("dm_type", "T2DM")
    irregular_schedule = inputs.get("irregular_schedule", False)
    has_nash_ir        = inputs.get("has_nash_ir", False)      # NASH/NAFLD / PCOS / high HOMA-IR
    bladder_cancer     = inputs.get("bladder_cancer", False)   # Pioglitazone contraindication

    steps = []
    notes = []
    refs  = set()

    # ── T1DM / LADA (advanced) / FCPD → insulin mandatory ───
    if dm_type in ("T1DM", "FCPD"):
        return _insulin_mandatory_plan(dm_type, inputs)

    # ── Step 1: Metformin ────────────────────────────────────
    if not on_metformin and egfr >= 30:
        met = ORAL_DRUGS["Metformin"]
        steps.append({
            "step":      "1. Start / optimise Metformin",
            "rationale": "First-line T2DM agent — reduces hepatic glucose output, weight-neutral, CV-safe (UKPDS).",
            "drug":      "Metformin",
            "dose":      f"Start {met['start_dose']}, target {met['max_dose']}",
            "brands":    _brand_str(met["brands"]),
            "hba1c_reduction": met["HbA1c_reduction"],
            "hypo_risk": met["hypo_risk"],
            "confidence": "High",
            "ref":        met["ref"],
        })
        refs.add(met["ref"])
    elif on_metformin:
        steps.append({
            "step":      "1. Optimise Metformin dose",
            "rationale": "Ensure target dose 1500–2000 mg/day is achieved before adding agents.",
            "drug":      "Metformin",
            "dose":      "Target 2000 mg/day (1000 mg BD) if tolerated",
            "brands":    _brand_str(ORAL_DRUGS["Metformin"]["brands"]),
            "hba1c_reduction": "1.0–1.5%",
            "hypo_risk": "Low",
            "confidence": "High",
            "ref":        "RSSDI CPR 2023; ICMR T2DM 2018",
        })

    if egfr < 30:
        notes.append("⚠️ Metformin CONTRAINDICATED — eGFR < 30 mL/min. Use insulin-based regimen.")
    elif egfr < 45:
        notes.append("⚠️ Metformin — use with caution if eGFR 30–45. Reduce dose. Monitor 3-monthly.")

    # ── Step 2: Second agent — CardioRenal pathway first ────────
    # ADA-EASD Consensus 2022: after Metformin, consider GLP-1 RA / SGLT2i
    # based on (1) CV/renal risk, (2) weight, (3) hypoglycaemia, (4) cost.

    # 2a. GLP-1 RA — for ASCVD OR obesity (BMI>27) even without ASCVD
    if glp1_ok and (has_ascvd or obesity) and not (dm_type in ("T1DM","FCPD")):
        glp1 = GLP1_DRUGS["Semaglutide SC"]
        if has_ascvd:
            glp1_rationale = (
                "SUSTAIN-6 (Semaglutide SC) / LEADER (Liraglutide) / REWIND (Dulaglutide) — "
                "all proved MACE reduction in established CVD. Highest priority after Metformin "
                "in ASCVD [ADA-EASD Consensus 2022]."
            )
            glp1_step = "2a. Add GLP-1 RA (established ASCVD — proven MACE reduction)"
        else:
            glp1_rationale = (
                "BMI > 27 kg/m² — GLP-1 RA preferred weight-loss agent in T2DM. "
                "Semaglutide SC: mean weight loss 4–6 kg (SUSTAIN programme). "
                "ADA-EASD Consensus 2022: GLP-1 RA recommended when weight loss is a priority "
                "even in absence of established CVD."
            )
            glp1_step = "2a. Add GLP-1 RA (obesity / weight loss priority)"
        steps.append({
            "step":      glp1_step,
            "rationale": glp1_rationale,
            "drug":      "Semaglutide SC 0.5 mg/week (preferred) · Liraglutide 1.2 mg OD · Dulaglutide 0.75 mg/week",
            "dose":      glp1["titration"],
            "brands":    _brand_str(glp1["brands"]) + " · Victoza (Novo Nordisk, High) · Trulicity (Lilly, High)",
            "hba1c_reduction": "1.5–2.0%",
            "hypo_risk": "Low (glucose-dependent mechanism)",
            "confidence": "High",
            "ref":        "Marso SP et al., NEJM 2016 (SUSTAIN-6); Marso SP et al., NEJM 2016 (LEADER); Gerstein HC et al., NEJM 2019 (REWIND); ADA-EASD Consensus 2022",
        })
        notes.append("ℹ️ Stop DPP-4i (Sitagliptin/Vildagliptin) when starting GLP-1 RA — same incretin axis, no additive benefit [Pratley RE, Lancet 2010].")
        notes.append("⚠️ GLP-1 RA: Avoid in personal/family history of medullary thyroid cancer or MEN2. Caution in pancreatitis history.")

    # 2b. SGLT2i — for HF/CKD (organ protection) OR glucose lowering / weight
    if not sglt2_allergy and egfr >= 20:
        if has_hf or has_ckd:
            sglt2_rationale = (
                "DAPA-HF / EMPEROR-Reduced: 25–26% ↓ HF hospitalisation independent of DM status. "
                "CREDENCE / DAPA-CKD: 30–39% ↓ renal progression. Start even if eGFR 20–45 "
                "for organ protection [ADA Standards 2024, Sections 10–11]."
            )
            sglt2_step = "2b. Add SGLT2 inhibitor (Heart Failure / CKD — organ protection)"
        elif obesity and not any("GLP-1" in s.get("step","") for s in steps):
            sglt2_rationale = (
                "Obesity without ASCVD/HF/CKD — SGLT2i provides weight loss 2–3 kg, "
                "BP reduction 3–5 mmHg, and HbA1c reduction 0.7–1.0% [ADA-EASD Consensus 2022]. "
                "No hypoglycaemia risk. Preferred if GLP-1 RA not available or affordable."
            )
            sglt2_step = "2b. Add SGLT2 inhibitor (weight / glucose lowering)"
        elif not has_ascvd and not obesity:
            sglt2_rationale = (
                "Second-line glucose lowering — SGLT2i provides moderate HbA1c reduction, "
                "weight loss, BP reduction. EMPA-REG OUTCOME, DECLARE-TIMI 58 showed CV safety "
                "and benefit even in lower-risk populations [ADA Standards 2024, Section 9]."
            )
            sglt2_step = "2b. Add SGLT2 inhibitor (glucose lowering / cardiometabolic benefit)"
        else:
            sglt2_step = None

        if sglt2_step:
            sglt2 = ORAL_DRUGS["Empagliflozin"]
            steps.append({
                "step":      sglt2_step,
                "rationale": sglt2_rationale,
                "drug":      "Empagliflozin 10–25 mg OD / Dapagliflozin 10 mg OD / Canagliflozin 100–300 mg OD",
                "dose":      sglt2["start_dose"],
                "brands":    _brand_str(sglt2["brands"]) + " · Forxiga (AstraZeneca) · Invokana (J&J)",
                "hba1c_reduction": "0.7–1.0%",
                "hypo_risk": "Low (glycosuric mechanism — not insulin dependent)",
                "confidence": "High",
                "ref":        "Zinman B et al., NEJM 2015 (EMPA-REG); McMurray JJV et al., NEJM 2019 (DAPA-HF); ADA Standards 2024, Sections 9–11",
            })
            notes.append("⚠️ SGLT2i: Check eGFR before starting. Educate on genital hygiene (mycotic infections). Withhold 3–5 days before surgery (euglycaemic DKA risk). Avoid in recurrent UTI.")
    elif sglt2_allergy and (has_hf or has_ckd):
        notes.append("⚠️ SGLT2i allergy — cannot use for HF/CKD organ protection. Maximise RAAS blockade (ACEi/ARB + Finerenone in CKD+DM). Cardiology/Nephrology referral.")

    # ── Step 3: Glucose lowering add-on ─────────────────────────
    # Algorithm: ADA-EASD Consensus 2022 + RSSDI CPR 2023
    # SU is a valid Step 3 option for ALL patients without hypo concern.
    # Gliclazide MR is preferred SU (ADVANCE trial, lowest hypo risk).
    # Repaglinide preferred if irregular meals or CKD (hepatic clearance).
    # DPP-4i preferred if hypo concern or obesity without GLP-1 RA access.
    if hba1c > 7.5:
        glp1_already = any("GLP-1" in s.get("step","") for s in steps)
        sglt2_already = any("SGLT2" in s.get("step","") for s in steps)

        # ── 3a. Sulfonylurea / Meglitinide ──────────────────────
        if not hypo_concern:
            # Repaglinide if irregular meals or CKD (eGFR 30-60)
            if irregular_schedule or (egfr < 60 and egfr >= 30):
                su = ORAL_DRUGS["Repaglinide"]
                su_name  = "Repaglinide (meglitinide — meal-linked, CKD-safe)"
                su_rationale = (
                    "Rapid-onset, short-duration prandial secretagogue. Take WITH each meal — skip if meal skipped. "
                    "Hepatically cleared — safe in CKD eGFR 30–60 where SUs carry prolonged hypo risk. "
                    "Ideal for irregular meal patterns and shift workers [ADA Standards 2024, Section 9]."
                )
            elif age >= 65:
                su = ORAL_DRUGS["Gliclazide MR"]
                su_name  = "Gliclazide MR (preferred SU in elderly — lowest hypo risk)"
                su_rationale = (
                    "Preferred SU in elderly: no cardiac K-ATP channel binding (unlike Glibenclamide), "
                    "lowest nocturnal hypoglycaemia risk among SUs. ADVANCE trial: 21% ↓ nephropathy, "
                    "14% ↓ microvascular events, no excess CV mortality [Patel A, NEJM 2008]."
                )
            else:
                su = ORAL_DRUGS["Gliclazide MR"]
                su_name  = "Gliclazide MR (preferred SU per RSSDI CPR 2023 & ADVANCE trial)"
                su_rationale = (
                    "Preferred SU per RSSDI CPR 2023. Selective beta-cell K-ATP action — no cardiac channel binding. "
                    "Lower hypoglycaemia risk than Glimepiride or Glibenclamide. "
                    "ADVANCE trial proved microvascular benefit and CV safety [Patel A, NEJM 2008]. "
                    "Affordable, excellent HbA1c reduction 1.0–1.5%."
                )
            steps.append({
                "step":      "3a. Add Sulfonylurea / Secretagogue",
                "rationale": su_rationale,
                "drug":      su_name,
                "dose":      f"{su['start_dose']} → max {su['max_dose']}",
                "brands":    _brand_str(su["brands"]),
                "hba1c_reduction": su["HbA1c_reduction"],
                "hypo_risk": su["hypo_risk"] + " — counsel patient; skip dose if meal skipped (Repaglinide)",
                "confidence": "High",
                "ref":        su["ref"],
            })
        else:
            notes.append(
                "⚠️ Hypoglycaemia concern flagged — Sulfonylurea / Meglitinide avoided. "
                "Using DPP-4 inhibitor or GLP-1 RA as glucose-lowering add-on."
            )

        # ── 3b. DPP-4 inhibitor (if GLP-1 RA not chosen) ───────
        glp1_already = any("GLP-1" in s.get("step","") for s in steps)
        if not glp1_already and not has_ascvd:
            if cost_pref == "low":
                dpp4 = ORAL_DRUGS["Teneligliptin"]
                dpp4_name = "Teneligliptin (most affordable DPP-4i in India)"
            else:
                dpp4 = ORAL_DRUGS["Sitagliptin"]
                dpp4_name = "Sitagliptin 100 mg OD"
            steps.append({
                "step":      "3b. Add DPP-4 inhibitor (alternative / add-on to SU)",
                "rationale": (
                    "Weight-neutral, very low hypoglycaemia risk. "
                    "Can be combined with SU for dual secretagogue + incretin effect. "
                    "Preferred over SU if hypo concern, elderly, or CKD (dose-adjust Sitagliptin) [ADA Standards 2024, Section 9]."
                ),
                "drug":      dpp4_name,
                "dose":      dpp4["start_dose"],
                "brands":    _brand_str(dpp4["brands"]),
                "hba1c_reduction": "0.6–0.9%",
                "hypo_risk": "Very Low",
                "confidence": "High",
                "ref":        ORAL_DRUGS["Sitagliptin"]["ref"],
            })

        # ── 3c. Pioglitazone — ONLY when specific indication is present AND no key contraindications
        # Indications: NASH/NAFLD confirmed, PCOS with IR, documented high HOMA-IR (>2.5), obesity-driven IR
        # Contraindications: HF (any class — black box warning for III–IV; avoid I–II too), bladder cancer
        pio = ORAL_DRUGS["Pioglitazone"]
        pio_contraindicated = has_hf or bladder_cancer
        if has_nash_ir and not pio_contraindicated:
            steps.append({
                "step":      "3c. Add Pioglitazone (specific indication: NASH / PCOS / documented IR)",
                "rationale": (
                    "Thiazolidinedione — most potent insulin sensitiser available orally. "
                    "PIVENS trial: Pioglitazone 30 mg improved NASH histology (steatosis, inflammation, fibrosis score) "
                    "vs placebo (Sanyal AJ et al., NEJM 2010). "
                    "PCOS with IR: restores ovulation, improves androgen excess. "
                    "PROactive trial: significant 16% RRR in secondary MACE endpoint (HR 0.84, p=0.027) in T2DM. "
                    "CONTRAINDICATED in HF (any class — fluid retention risk; FDA black box for NYHA III–IV). "
                    "Slow onset — allow 8–12 weeks for full glycaemic effect [ADA Standards 2024, Section 9; RSSDI CPR 2023]."
                ),
                "drug":      "Pioglitazone 15 mg OD (starting dose)",
                "dose":      f"{pio['start_dose']} → max {pio['max_dose']}",
                "brands":    _brand_str(pio["brands"]),
                "hba1c_reduction": pio["HbA1c_reduction"],
                "hypo_risk": pio["hypo_risk"] + " (hypoglycaemia risk low as monotherapy; increases when combined with SU or insulin)",
                "confidence": "High",
                "ref":        pio["ref"],
            })
            notes.append("⚠️ Pioglitazone MANDATORY screening before starting: heart failure (NYHA any class), bladder cancer history, osteoporosis/fragility fracture, macular oedema, active hepatic disease. Monitor weight and leg oedema monthly for first 3 months.")
        elif has_nash_ir and pio_contraindicated:
            notes.append(
                "ℹ️ Pioglitazone indicated for NASH/IR but CONTRAINDICATED in this patient "
                f"({'heart failure' if has_hf else ''}{' + ' if has_hf and bladder_cancer else ''}{'bladder cancer history' if bladder_cancer else ''}). "
                "Consider Vitamin E 800 IU/day (PIVENS trial) for NASH; GLP-1 RA also improves hepatic steatosis."
            )

    # ── Step 4b: Combination injectable (iGlarLixi / IDegLira) ──
    # Intensification option BEFORE full MDI — when basal insulin alone insufficient
    # and GLP-1 RA + basal benefits both needed
    if hba1c >= 8.5 and not any("GLP-1" in s.get("step","") for s in steps) and glp1_ok:
        combo = COMBO_INJECTABLES["IDegLira (Xultophy)"]
        steps.append({
            "step":      "4b. Consider Fixed-ratio Combo Injectable (iGlarLixi / IDegLira)",
            "rationale": (
                "When HbA1c ≥ 8.5% and oral agents inadequate — fixed-ratio GLP-1 RA + basal insulin "
                "in a SINGLE injection is superior to basal alone with less weight gain and less hypoglycaemia. "
                "IDegLira (DUAL V trial): comparable HbA1c reduction to basal-bolus MDI with 75% fewer injections. "
                "iGlarLixi (LixiLan-O): 1.6% HbA1c reduction, weight neutral. "
                "Consider BEFORE full MDI if patient willing to inject but wants fewer injections [ADA Standards 2024, Section 9]."
            ),
            "drug":      "IDegLira (Xultophy) preferred · Alternative: iGlarLixi (Soliqua)",
            "dose":      "IDegLira: start 10 units OD → titrate 2 units/3–4 days (max 50 units) · iGlarLixi: start 15 units OD → titrate 2 units/week (max 60 units)",
            "brands":    "Xultophy 100/3.6 (Novo Nordisk, Very High) · Soliqua 100/33 (Sanofi, Very High)",
            "hba1c_reduction": "1.8–2.2% (IDegLira) / 1.5–2.0% (iGlarLixi)",
            "hypo_risk": "Low–Moderate (lower than MDI)",
            "confidence": "High",
            "ref":        combo["ref"],
        })
        notes.append("ℹ️ Combo injectables: Stop GLP-1 RA pen before starting iGlarLixi/IDegLira (GLP-1 RA component now in the combo). Stop separate basal insulin when switching to combo.")

    # ── Step 4: Basal insulin (if HbA1c ≥ 9% or symptomatic) ──
    if hba1c >= 9.0:
        insulin_choice = _select_basal_insulin(inputs)
        steps.append({
            "step":      "4. Initiate Basal Insulin (HbA1c ≥ 9% / symptomatic hyperglycaemia)",
            "rationale": insulin_choice["rationale"],
            "drug":      insulin_choice["drug"],
            "dose":      insulin_choice["dose"],
            "brands":    insulin_choice["brands"],
            "hba1c_reduction": "1.0–1.5% from FBG component",
            "hypo_risk": insulin_choice["hypo_risk"],
            "confidence": "High",
            "ref":        insulin_choice["ref"],
        })
        notes.append("ℹ️ When adding basal insulin to any SU (Gliclazide MR / Glimepiride): reduce SU dose by 50% to avoid hypoglycaemia [ADA Standards 2024, Section 9; RSSDI CPR 2023].")
        notes.append("ℹ️ Basal insulin targets FBG 80–130 mg/dL. Titrate 2U every 3 days.")

    if not steps:
        steps.append({
            "step":      "Continue current regimen — reassess in 3 months",
            "rationale": "If HbA1c near target and no complications, optimise lifestyle + monitor.",
            "drug":      "—",
            "dose":      "—",
            "brands":    "—",
            "hba1c_reduction": "N/A",
            "hypo_risk": "Low",
            "confidence": "High",
            "ref":        "ADA Standards 2024; RSSDI CPR 2023",
        })

    return {
        "steps": steps,
        "notes": notes,
        "refs":  sorted(refs),
    }


def _select_basal_insulin(inputs: dict) -> dict:
    age          = inputs.get("age", 50)
    egfr         = inputs.get("egfr", 90)
    has_ascvd    = inputs.get("has_ascvd", False)
    cost_pref    = inputs.get("cost_preference", "any")
    high_dose    = inputs.get("high_dose_need", False)  # if likely to need >60U
    irregular    = inputs.get("irregular_schedule", False)
    elderly_alone = age >= 70
    dm_type      = inputs.get("dm_type", "T2DM")

    # T1DM → Degludec always preferred
    if dm_type == "T1DM":
        ins = INSULIN_DRUGS["Degludec U-100 (Tresiba)"]
        return {
            "drug":      "Insulin Degludec U-100 (Tresiba)",
            "rationale": "T1DM: Lowest nocturnal hypoglycaemia of all basals (BEGIN trials). CV safety proven (DEVOTE).",
            "dose":      ins["start"],
            "brands":    _brand_str(ins["brands"]),
            "hypo_risk": "Lowest",
            "ref":       ins["ref"],
        }

    # Cost-constrained → NPH or Glargine U-100 biosimilar
    if cost_pref == "low":
        if egfr >= 45:
            ins = INSULIN_DRUGS["Glargine U-100"]
            return {
                "drug":      "Glargine U-100 biosimilar (Basalog / Glaritus)",
                "rationale": "Most cost-effective analogue basal. Biosimilars endorsed by RSSDI CPR 2023.",
                "dose":      ins["start"],
                "brands":    _brand_str(ins["brands"]),
                "hypo_risk": "Moderate (nocturnal)",
                "ref":       ins["ref"],
            }
        else:
            ins = INSULIN_DRUGS["NPH (Isophane)"]
            return {
                "drug":      "NPH Insulin at bedtime",
                "rationale": "Most affordable basal. Accept higher nocturnal hypoglycaemia risk. Monitor closely.",
                "dose":      ins["start"],
                "brands":    _brand_str(ins["brands"]),
                "hypo_risk": "High nocturnal — educate patient",
                "ref":       ins["ref"],
            }

    # High dose need → Glargine U-300
    if high_dose:
        ins = INSULIN_DRUGS["Glargine U-300 (Toujeo)"]
        return {
            "drug":      "Glargine U-300 (Toujeo)",
            "rationale": "High dose (>60 U/day): 3× concentrated → smaller injection volume, better absorption consistency.",
            "dose":      ins["start"],
            "brands":    _brand_str(ins["brands"]),
            "hypo_risk": "Lower than U-100 during titration (BRIGHT trial)",
            "ref":       ins["ref"],
        }

    # High CV risk / elderly / irregular schedule / CKD → Degludec
    if has_ascvd or elderly_alone or irregular or egfr < 45:
        ins = INSULIN_DRUGS["Degludec U-100 (Tresiba)"]
        reasons = []
        if has_ascvd:     reasons.append("established CVD (DEVOTE: 40% lower severe hypoglycaemia)")
        if elderly_alone: reasons.append("elderly patient (lower hypoglycaemia risk, flexible timing)")
        if irregular:     reasons.append("irregular schedule (flexible ≥8 hr dosing)")
        if egfr < 45:     reasons.append("CKD (reduced insulin clearance — lower hypoglycaemia risk critical)")
        return {
            "drug":      "Insulin Degludec U-100 (Tresiba)",
            "rationale": f"Preferred for: {', '.join(reasons)}. Lowest within-subject variability (CV ~20%).",
            "dose":      ins["start"] + " — Do NOT re-titrate before Day 4 (steady state at 3–4 days)",
            "brands":    _brand_str(ins["brands"]),
            "hypo_risk": "Lowest of all basals",
            "ref":       ins["ref"],
        }

    # Default: Glargine U-100
    ins = INSULIN_DRUGS["Glargine U-100"]
    return {
        "drug":      "Glargine U-100 (Lantus / Basalog biosimilar)",
        "rationale": "Standard first basal analogue — well-studied, widely available, biosimilars reduce cost.",
        "dose":      ins["start"],
        "brands":    _brand_str(ins["brands"]),
        "hypo_risk": "Moderate",
        "ref":       ins["ref"],
    }


def _insulin_mandatory_plan(dm_type: str, inputs: dict) -> dict:
    steps = []
    notes = []

    if dm_type == "T1DM":
        basal = INSULIN_DRUGS["Degludec U-100 (Tresiba)"]
        bolus = INSULIN_DRUGS["Aspart (NovoRapid)"]
        steps.append({
            "step":      "Basal Insulin — Degludec U-100 (Tresiba)",
            "rationale": "T1DM MDI: Lowest nocturnal hypoglycaemia. Flexible timing. BEGIN T1DM trials.",
            "drug":      "Insulin Degludec U-100",
            "dose":      "~40–50% of TDD as basal. Start 10–20U OD at any time of day.",
            "brands":    _brand_str(basal["brands"]),
            "hba1c_reduction": "Basal controls FBG; bolus controls PPG",
            "hypo_risk": "Lowest among basals",
            "confidence": "High",
            "ref":        basal["ref"],
        })
        steps.append({
            "step":      "Bolus Insulin — Aspart (NovoRapid) or Lispro (Humalog/Basuloc)",
            "rationale": "Rapid analogue with each meal. Carbohydrate counting + correction factor.",
            "drug":      "Aspart or Lispro",
            "dose":      "1 U per 10–15 g carbohydrate. Correction: 1 U per 2–3 mmol/L above target. Inject 5–15 min pre-meal.",
            "brands":    _brand_str(bolus["brands"]) + " · Basuloc (Biocon biosimilar, Medium cost)",
            "hba1c_reduction": "N/A (TDD-based)",
            "hypo_risk": "Moderate — educate hypoglycaemia management",
            "confidence": "High",
            "ref":        bolus["ref"],
        })
        notes.append("ℹ️ CGM (Freestyle Libre 2 / Dexcom G6) strongly recommended for T1DM — Time-in-Range target >70% [ATTD Consensus 2023].")
        notes.append("ℹ️ Structured carbohydrate counting education essential.")

    elif dm_type == "FCPD":
        regular = INSULIN_DRUGS["Regular Human (Soluble)"]
        steps.append({
            "step":      "Basal-Bolus Insulin (FCPD — insulin mandatory)",
            "rationale": "FCPD: complete exocrine + progressive endocrine failure. OADs ineffective. SU and SGLT2i dangerous.",
            "drug":      "Conservative Basal-Bolus MDI",
            "dose":      "Start conservatively at 0.3 U/kg/day total. Basal: Glargine U-100 (Basalog). Bolus: Regular or Aspart.",
            "brands":    "Basalog (Biocon, Medium) · Actrapid (Novo Nordisk, Low) · NovoRapid (Novo Nordisk, High)",
            "hba1c_reduction": "Target-to-FBG 80–130 mg/dL, PPG <180 mg/dL",
            "hypo_risk": "VERY HIGH — alpha-cell loss → no glucagon counter-regulation",
            "confidence": "High",
            "ref":        "Mohan V, Pancreatology 2012; ADA Standards 2024",
        })
        notes.append("⚠️ FCPD: Hypoglycaemia is life-threatening — no glucagon reserve. CGM essential. Prescribe glucagon kit.")
        notes.append("ℹ️ PERT mandatory: Creon 25,000–50,000 U lipase with every main meal.")
        notes.append("⚠️ AVOID: Sulfonylureas, SGLT2i, aggressive GLP-1 RA — all dangerous in FCPD.")

    return {"steps": steps, "notes": notes, "refs": []}


def calculate_insulin_dose(weight_kg: float, hba1c: float, dm_type: str,
                            insulin_type: str, current_basal_u: float = 0) -> dict:
    """Insulin dose calculator with titration guidance."""
    result = {}

    if insulin_type == "basal_initiation":
        start = max(10, round(weight_kg * 0.1))
        result = {
            "starting_dose": f"{start} units at bedtime",
            "titration":     "Increase by 2 units every 3 days",
            "target_fbg":    "80–130 mg/dL (4.4–7.2 mmol/L)",
            "max_safe_step": "No more than 4 units per adjustment",
            "note":          "If FBG < 80 mg/dL (4.4 mmol/L) on any morning → reduce dose by 4 units",
            "ref":           "ADA Standards 2024, Section 9; RSSDI CPR 2023 — treat-to-target approach",
        }

    elif insulin_type == "tdd_mdi":
        # Estimate TDD
        if dm_type == "T1DM":
            tdd = round(weight_kg * 0.5)
        elif hba1c > 10:
            tdd = round(weight_kg * 0.7)
        else:
            tdd = round(weight_kg * 0.5)
        basal = round(tdd * 0.5)
        bolus_per_meal = round(tdd * 0.5 / 3)
        # PPG target differs by DM type:
        # T1DM/LADA: <140 mg/dL (7.8 mmol/L) at 2 hr — tighter postprandial target (ADA 2024 Sec 7; ISPAD 2022)
        # T2DM/FCPD: <180 mg/dL (10 mmol/L) at 1–2 hr — standard (ADA 2024 Sec 9; RSSDI CPR 2023)
        if dm_type in ("T1DM", "LADA"):
            ppg_target = "< 140 mg/dL (7.8 mmol/L) at 2 hr — T1DM/LADA tighter target [ADA 2024 Sec 7; ISPAD 2022]"
            ppg_ref    = "ADA Standards 2024, Section 7; ISPAD Clinical Practice Consensus Guidelines 2022"
        else:
            ppg_target = "< 180 mg/dL (10 mmol/L) at 1–2 hr — T2DM/FCPD standard target [ADA 2024 Sec 9; RSSDI CPR 2023]"
            ppg_ref    = "ADA Standards 2024, Section 9; RSSDI CPR 2023"
        result = {
            "estimated_TDD":        f"{tdd} units/day",
            "basal_dose":           f"{basal} units/day (50% of TDD)",
            "bolus_per_meal":       f"{bolus_per_meal} units per meal (starting point)",
            "correction_factor":    f"1 unit lowers glucose by ~{round(1700 / tdd)} mg/dL (1700 rule)",
            "ICR":                  f"1 unit covers ~{round(500 / tdd)} g carbohydrate (500 rule)",
            "titration":            f"Adjust bolus based on 2-hr PPG target {ppg_target}",
            "ref":                  ppg_ref,
        }

    elif insulin_type == "basal_titration":
        result = {
            "current_dose":  f"{current_basal_u} units",
            "next_step":     f"If FBG > 130 mg/dL for 3 consecutive days → increase by 2 units (new dose: {int(current_basal_u)+2} U)",
            "reduce_if":     f"If FBG < 80 mg/dL or hypoglycaemia → reduce by 4 units (new dose: {max(0, int(current_basal_u)-4)} U)",
            "target_fbg":    "80–130 mg/dL (4.4–7.2 mmol/L)",
            "ref":           "ADA Standards 2024 treat-to-target; RSSDI CPR 2023",
        }

    elif insulin_type == "premixed_titration":
        result = {
            "current_dose":  f"{current_basal_u} units",
            "next_step_pre_breakfast": f"If FBG > 130 mg/dL for 3 days → increase pre-dinner dose by 2 U (FBG reflects overnight)",
            "next_step_pre_dinner":    f"If pre-dinner glucose > 180 mg/dL for 3 days → increase pre-breakfast dose by 2 U",
            "reduce_if":     "Any glucose < 72 mg/dL → reduce the dose preceding that time-point by 2–4 U",
            "target":        "FBG 80–130 mg/dL · Pre-dinner 80–140 mg/dL · 2-hr PPG < 180 mg/dL",
            "note":          "⚠️ Meal timing must be fixed with premixed insulin — irregular meals → consider switch to basal-bolus",
            "ref":           "RSSDI CPR 2023; ADA Standards 2024, Section 9",
        }

    return result


# ── INSULIN SWITCHING / CONVERSION CALCULATOR ────────────────
INSULIN_SWITCH_PROTOCOLS = {
    "NPH → Glargine U-100": {
        "from": "NPH (Isophane)", "to": "Glargine U-100",
        "conversion_rule": "Reduce dose by 20% (safety margin for less peak effect). Round DOWN to nearest 2 units.",
        "conversion_factor": 0.80,
        "timing_change": "NPH: usually BD (morning + bedtime) → Glargine: ONCE daily at bedtime or same time daily",
        "titration_after": "Titrate 2 U every 3 days to FBG target 80–130 mg/dL",
        "rationale": "Glargine U-100 has no peak → less nocturnal hypoglycaemia. Initial dose reduction prevents hypoglycaemia from residual NPH effect.",
        "monitoring": "Check FBG daily for first 2 weeks. Alert patient to reduce by 4 U if any FBG < 72 mg/dL.",
        "ref": "ADA Standards 2024, Section 9; RSSDI CPR 2023; LANMET trial",
    },
    "NPH → Degludec U-100": {
        "from": "NPH", "to": "Degludec U-100",
        "conversion_rule": "Reduce total daily NPH dose by 20%. Give as ONCE daily (regardless of how many NPH injections).",
        "conversion_factor": 0.80,
        "timing_change": "Any time daily — same time preferred. At least 8 hours between consecutive days if changing time.",
        "titration_after": "Wait 3–4 days between dose adjustments (Degludec takes 3 days to reach steady state). Increase 2 U every 3–4 days.",
        "rationale": "Degludec: >42 hr duration, CV ~20% — lowest hypoglycaemia risk. Initial reduction prevents overlap during transition.",
        "monitoring": "Do NOT re-titrate before Day 4. Higher nadir glucose than Glargine U-300 during first week.",
        "ref": "DEVOTE trial (Marso 2017); BEGIN trials; ADA Standards 2024",
    },
    "Glargine U-100 → Degludec U-100": {
        "from": "Glargine U-100", "to": "Degludec U-100",
        "conversion_rule": "Unit-for-unit conversion (1:1). No dose reduction required at equivalent control.",
        "conversion_factor": 1.0,
        "timing_change": "Glargine: fixed time daily → Degludec: any time daily (≥8 hr apart). Flexibility is an advantage.",
        "titration_after": "Wait 3–4 days between adjustments. Titrate 2 U every 3–4 days if FBG above target.",
        "rationale": "CONCLUDE trial: Degludec = Glargine U-300 for HbA1c. BRIGHT trial: equivalent HbA1c, lower nocturnal hypo with Degludec at maintenance. DEVOTE: 40% lower severe hypo vs Glargine U-100.",
        "monitoring": "Expect lower nocturnal hypoglycaemia within 2–4 weeks. CGM recommended to confirm.",
        "ref": "CONCLUDE trial (Mathieu 2020); BRIGHT trial (Rosenstock 2018); DEVOTE trial (Marso 2017)",
    },
    "Glargine U-100 → Glargine U-300": {
        "from": "Glargine U-100", "to": "Glargine U-300 (Toujeo)",
        "conversion_rule": "Same number of UNITS (not volume). Toujeo is 3× concentrated — same unit dose delivered in 1/3 volume.",
        "conversion_factor": 1.0,
        "timing_change": "Same timing. Once daily.",
        "titration_after": "Titrate 2 U every 3 days. Toujeo has ± 3 hr injection time flexibility.",
        "rationale": "Glargine U-300: longer duration than U-100 (up to 36 hr), lower peak, lower nocturnal hypo at titration phase (EDITION trials). Better for high-dose patients (large volume in U-100 pen may cause absorption variability).",
        "monitoring": "Same units — do NOT confuse unit dose with volume. Patients must understand pen is different.",
        "ref": "EDITION I–IV trials; ADA Standards 2024",
    },
    "Premixed → Basal-Bolus MDI": {
        "from": "Premixed 30/70 or BiAsp 30", "to": "Basal (Glargine/Degludec) + Bolus (Aspart/Lispro)",
        "conversion_rule": "Total daily premixed dose → Basal 50% + Bolus 50% split equally across 3 meals. Then titrate each component independently.",
        "conversion_factor": 1.0,
        "timing_change": "Premixed: BD (before breakfast + dinner) → MDI: Basal OD (bedtime) + Bolus TDS (before each meal)",
        "titration_after": "Basal: titrate to FBG 80–130 mg/dL. Bolus: titrate to 2-hr PPG < 180 mg/dL (10 mmol/L). Adjust one component at a time.",
        "rationale": "MDI provides physiological basal + prandial coverage. Better PPG control, more flexibility, suitable for T1DM and advanced T2DM. Required when premixed regimen fails to control post-meal excursions.",
        "monitoring": "SMBG: pre-meal + 2-hr post-meal × 3/day minimum. CGM preferred. Hypoglycaemia education mandatory.",
        "ref": "ADA Standards 2024, Section 7 and 9; RSSDI CPR 2023",
    },
    "Basal Only → Basal + 1 Bolus (Basal Plus)": {
        "from": "Basal insulin alone", "to": "Basal + 1 bolus injection (Basal Plus)",
        "conversion_rule": "Keep current basal dose unchanged. Add 4 U bolus rapid analogue before the LARGEST meal of the day.",
        "conversion_factor": 1.0,
        "timing_change": "No change to basal timing. Add bolus 5–15 min before largest meal.",
        "titration_after": "Titrate added bolus: increase 1–2 U if 2-hr PPG > 180 mg/dL for 3 consecutive days. Add second bolus before 2nd largest meal if PPG uncontrolled.",
        "rationale": "Stepwise intensification — 1 extra injection is more acceptable than full MDI. 1647 trial: Basal-Plus non-inferior to MDI for HbA1c with fewer hypoglycaemic events.",
        "monitoring": "Measure 2-hr PPG after the meal where bolus is added. Adjust dose based on that reading.",
        "ref": "1647 trial; Riddle MC et al., Diabetes Care 2012; ADA Standards 2024, Section 9",
    },
    "Basal Only → IDegLira / iGlarLixi": {
        "from": "Basal insulin alone (uncontrolled)", "to": "IDegLira (Xultophy) / iGlarLixi (Soliqua)",
        "conversion_rule": "IDegLira: start at 16 dose units (= 16 U Degludec + 0.58 mg Liraglutide) if currently on ≤20 U basal. Start at same unit dose if on 20–40 U basal. iGlarLixi: start 15 units if on basal insulin.",
        "conversion_factor": 1.0,
        "timing_change": "Stop separate basal insulin pen. Stop any separate GLP-1 RA pen. Use only the combo pen.",
        "titration_after": "IDegLira: increase 2 units every 3–4 days to FBG target (max 50 units). iGlarLixi: increase 2 units/week to FBG target (max 60 units).",
        "rationale": "DUAL V trial: IDegLira achieved same HbA1c as basal-bolus MDI with 75% fewer injections, less weight gain, less hypoglycaemia. Better than adding bolus for adherence-challenged patients.",
        "monitoring": "Watch for GLP-1 side effects initially (nausea, vomiting — usually transient week 1–2). Monitor FBG and PPG.",
        "ref": "DUAL V trial (Billings LK, Diabetes Care 2018); LixiLan-L trial; ADA Standards 2024, Section 9",
    },
}


def calculate_insulin_switch(from_insulin: str, to_insulin: str, current_dose_u: float) -> dict:
    """
    Calculate conversion dose and provide switching protocol.
    from_insulin: one of the keys in INSULIN_SWITCH_PROTOCOLS
    current_dose_u: total daily dose of current insulin in units
    Returns dict with new_dose, protocol, titration, monitoring, ref
    """
    key = f"{from_insulin} → {to_insulin}"
    proto = INSULIN_SWITCH_PROTOCOLS.get(key)
    if not proto:
        return {"error": f"No conversion protocol found for '{key}'. Check spelling or select from available pairs."}

    factor = proto["conversion_factor"]
    new_dose = round(current_dose_u * factor)
    # Round DOWN to nearest 2 for safety
    if factor < 1.0:
        new_dose = (new_dose // 2) * 2

    return {
        "from":            proto["from"],
        "to":              proto["to"],
        "current_dose":    f"{current_dose_u} units/day",
        "new_dose":        f"{new_dose} units/day",
        "conversion_rule": proto["conversion_rule"],
        "timing_change":   proto["timing_change"],
        "titration_after": proto["titration_after"],
        "rationale":       proto["rationale"],
        "monitoring":      proto["monitoring"],
        "ref":             proto["ref"],
        "safety_note":     "Always recheck glucose daily for the first 2 weeks after any insulin switch. Have patient report any glucose < 72 mg/dL immediately.",
    }
