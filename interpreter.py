# ============================================================
# interpreter.py  —  Lab Result Interpreter
# ADA 2024, RSSDI CPR 2023, Matthews 1985 (HOMA), Lindkvist 2013
# ============================================================

try:
    from data import DIAGNOSTIC_CRITERIA, HBA1C_TARGETS
except ImportError:
    from modules.data import DIAGNOSTIC_CRITERIA, HBA1C_TARGETS


def interpret_hba1c(hba1c: float, age: int, dm_type: str,
                    has_ckd: bool = False, pregnancy: bool = False,
                    frail: bool = False) -> dict:
    target_key = "General adult T2DM"
    if pregnancy:    target_key = "GDM (fasting)"
    elif frail or age >= 70: target_key = "Elderly / frail (>70 yrs)"
    elif has_ckd:    target_key = "CKD (eGFR 20-60)"
    elif dm_type == "T1DM": target_key = "T1DM adult"

    target = HBA1C_TARGETS.get(target_key, HBA1C_TARGETS["General adult T2DM"])
    target_val = float(target["target"].replace("<","").replace("%","").split("–")[0].strip())

    if hba1c <= target_val:
        status = "✅ At target"
        urgency = "Continue current regimen. Review in 3 months."
        colour = "green"
    elif hba1c <= target_val + 1.5:
        status = "⚠️ Above target — optimise"
        urgency = "Optimise current regimen or add one agent. Review in 3 months."
        colour = "orange"
    elif hba1c <= target_val + 3.0:
        status = "🔴 Significantly above target"
        urgency = "Escalate therapy — add GLP-1 RA or basal insulin. Consider C-peptide / LADA workup."
        colour = "red"
    else:
        status = "🚨 Severely uncontrolled"
        urgency = "Immediate escalation — basal insulin initiation. Rule out LADA, FCPD, MODY. Consider DKA risk."
        colour = "red"

    return {
        "value":          f"{hba1c}%",
        "status":         status,
        "target":         target["target"],
        "target_context": target_key,
        "urgency":        urgency,
        "colour":         colour,
        "estimated_avg_glucose": f"{round(28.7 * hba1c - 46.7)} mg/dL ({round((28.7 * hba1c - 46.7 - 18) / 18 * 10) / 10:.1f} mmol/L)",
        "note":           "Note: HbA1c may underestimate true glycaemia in haemolytic anaemia, haemoglobinopathies, and severe malnutrition (common in FCPD). Use fasting glucose for monitoring in these cases.",
        "ref":            target["ref"] + "; Nathan DM et al., Diabetes Care 2008 (eAG formula)"
    }


def interpret_c_peptide(c_pep_nmol: float, dm_type: str = "T2DM", duration_yrs: float = 0) -> dict:
    thresholds = DIAGNOSTIC_CRITERIA["C_peptide"]
    if c_pep_nmol < 0.1:
        interp = "Virtually absent — complete beta-cell failure"
        implication = "Insulin mandatory and permanent. Consistent with T1DM, advanced LADA, or advanced FCPD."
        colour = "red"
        confidence = "High"
    elif c_pep_nmol < thresholds["low_nmol"]:
        interp = f"Low ({c_pep_nmol:.2f} nmol/L < {thresholds['low_nmol']} nmol/L threshold)"
        implication = "Significant secretory reserve loss. Insulin likely mandatory. Rule out LADA (GAD65) and FCPD."
        colour = "red"
        confidence = "High"
    elif c_pep_nmol < 1.0:
        interp = f"Reduced ({c_pep_nmol:.2f} nmol/L — moderate secretory capacity)"
        implication = "GLP-1 RA or early insulin may be needed. Consider incretin therapy to preserve remaining beta-cell function."
        colour = "orange"
        confidence = "Moderate"
    elif c_pep_nmol < 2.0:
        interp = f"Adequate ({c_pep_nmol:.2f} nmol/L — reasonable secretory reserve)"
        implication = "Oral agents and/or GLP-1 RA can be effective. Insulin may not be immediately required."
        colour = "green"
        confidence = "High"
    else:
        interp = f"High ({c_pep_nmol:.2f} nmol/L — insulin resistance pattern)"
        implication = "Insulin resistance likely dominant. Prioritise insulin sensitisers (Metformin, Pioglitazone) and GLP-1 RA. Consider weight management."
        colour = "blue"
        confidence = "High"

    homa_note = ""
    if c_pep_nmol > 1.5 and duration_yrs < 5:
        homa_note = "ℹ️ High C-peptide at < 5 years duration — calculate HOMA-IR to quantify insulin resistance component."

    return {
        "value":         f"{c_pep_nmol:.2f} nmol/L ({c_pep_nmol * 3.0:.1f} ng/mL approx.)",
        "interpretation": interp,
        "clinical_implication": implication,
        "colour":        colour,
        "confidence":    confidence,
        "note":          homa_note or "C-peptide is more reliable than fasting insulin — not cleared by liver, not affected by exogenous insulin.",
        "ref":           thresholds["ref"]
    }


def interpret_homa(fasting_glucose_mmol: float, fasting_insulin_uiuML: float) -> dict:
    if fasting_glucose_mmol <= 3.5:
        return {"error": "Fasting glucose must be > 3.5 mmol/L for HOMA calculation."}

    homa_ir = round((fasting_insulin_uiuML * fasting_glucose_mmol) / 22.5, 2)
    homa_b  = round((20 * fasting_insulin_uiuML) / (fasting_glucose_mmol - 3.5), 1)

    if homa_ir < 1.5:
        ir_interp = "Normal insulin sensitivity"
        ir_colour = "green"
    elif homa_ir < 2.5:
        ir_interp = "Borderline insulin resistance"
        ir_colour = "orange"
    elif homa_ir < 5.0:
        ir_interp = "Insulin resistance"
        ir_colour = "red"
    else:
        ir_interp = "Severe insulin resistance"
        ir_colour = "red"

    if homa_b > 100:
        b_interp = "Normal beta-cell function"
        b_colour = "green"
    elif homa_b > 50:
        b_interp = "Mildly reduced beta-cell function"
        b_colour = "orange"
    else:
        b_interp = "Significantly impaired beta-cell function"
        b_colour = "red"

    return {
        "HOMA_IR":     homa_ir,
        "IR_interp":   ir_interp,
        "IR_colour":   ir_colour,
        "HOMA_beta":   homa_b,
        "Beta_interp": b_interp,
        "Beta_colour": b_colour,
        "formula_IR":  f"({fasting_insulin_uiuML} × {fasting_glucose_mmol}) ÷ 22.5 = {homa_ir}",
        "formula_B":   f"(20 × {fasting_insulin_uiuML}) ÷ ({fasting_glucose_mmol} − 3.5) = {homa_b}%",
        "clinical_note": (
            "HOMA indices are population-level tools — interpret with clinical context. "
            "Asian Indians tend to have higher HOMA-IR at lower BMI than European populations. "
            "Inter-lab insulin assay variability is significant in India — use same lab for serial measurements."
        ),
        "ref": "Matthews DR et al., Diabetologia 1985; Mohan V et al., J Diabetes Sci Technol 2019"
    }


def interpret_egfr(egfr: float, uacr: float = None) -> dict:
    if egfr >= 90:
        stage = "G1 (Normal or high)"
        mgmt  = "Annual UACR screening. No drug dose adjustment needed. Metformin: full dose."
        colour = "green"
    elif egfr >= 60:
        stage = "G2 (Mildly reduced)"
        mgmt  = "Annual UACR + eGFR. Metformin: full dose. SGLT2i: full dose for glucose lowering and CV/renal benefit (glycosuric effect intact ≥45)."
        colour = "green"
    elif egfr >= 45:
        stage = "G3a (Mildly–moderately reduced)"
        mgmt  = "Metformin: reduce dose (max 1000 mg BD, use with caution). SGLT2i: continue for CV/renal benefit; glucose-lowering effect diminishes — consider not initiating below 45 purely for glucose. Sitagliptin: reduce to 50 mg OD (full dose threshold is eGFR ≥45)."
        colour = "orange"
    elif egfr >= 30:
        stage = "G3b (Moderately–severely reduced)"
        mgmt  = "METFORMIN CONTRAINDICATED (eGFR <30). SGLT2i: do NOT initiate for glucose lowering; Empagliflozin/Dapagliflozin may continue for CV/renal benefit if already on treatment (down to eGFR 20/25 respectively). Sitagliptin 25 mg OD. Refer nephrology."
        colour = "orange"
    elif egfr >= 15:
        stage = "G4 (Severely reduced)"
        mgmt  = "Insulin-based management. Most oral agents unsafe. DPP-4i with dose adjustment only. Urgent nephrology referral. Plan for renal replacement therapy."
        colour = "red"
    else:
        stage = "G5 (Kidney failure)"
        mgmt  = "Dialysis / transplant planning. Insulin only — doses are REDUCED (reduced renal clearance). Strict glucose target 7.8–10 mmol/L inpatient."
        colour = "red"

    uacr_interp = None
    if uacr is not None:
        if uacr < 30:
            uacr_interp = "A1 (Normal) — < 30 mg/g: No albuminuria. Screen annually."
        elif uacr < 300:
            uacr_interp = f"A2 (Microalbuminuria) — {uacr} mg/g: ACE inhibitor or ARB indicated. SGLT2i adds renoprotection."
        else:
            uacr_interp = f"A3 (Macroalbuminuria) — {uacr} mg/g: Maximise RAS blockade. Add SGLT2i (if eGFR allows). Nephrology referral."

    return {
        "eGFR":        f"{egfr} mL/min/1.73m²",
        "CKD_stage":   stage,
        "colour":      colour,
        "management":  mgmt,
        "UACR":        uacr_interp,
        "drug_doses": {
            "Metformin":       "Full dose" if egfr >= 45 else ("Halve dose, use with caution (max 1000 mg BD)" if egfr >= 30 else "CONTRAINDICATED"),
            "Sitagliptin":     "100 mg OD" if egfr >= 45 else ("50 mg OD" if egfr >= 30 else "25 mg OD (including dialysis)"),
            "Empagliflozin":   ("10–25 mg OD — full glucose + CV/renal benefit" if egfr >= 45
                                else ("10 mg OD — CV/renal benefit only; do not initiate for glucose lowering" if egfr >= 20
                                      else "STOP (eGFR < 20 — benefit unproven below this threshold)")),
            "Dapagliflozin":   ("10 mg OD — full glucose + CV/renal benefit" if egfr >= 45
                                else ("10 mg OD — CKD/HF benefit only (DAPA-CKD ≥25); do not initiate for glucose lowering" if egfr >= 25
                                      else "STOP (eGFR < 25)")),
            "Canagliflozin":   ("100–300 mg OD — full glucose + CV benefit" if egfr >= 45
                                else ("100 mg OD — renal benefit only (CREDENCE: eGFR 30–90)" if egfr >= 30
                                      else "STOP (eGFR < 30)")),
            "Glimepiride":     "Use with caution — risk of prolonged hypoglycaemia" if egfr >= 30 else "AVOID (eGFR < 30 — severe prolonged hypoglycaemia risk)",
            "Gliclazide MR":   "Standard dose — can use cautiously to eGFR 30" if egfr >= 30 else "AVOID (eGFR < 30)",
            "Repaglinide":     "Safe at all eGFR (hepatic clearance) — preferred secretagogue in CKD" if egfr >= 15 else "Use with extreme caution",
            "GLP-1 RA":        "Full dose — no renal dose adjustment required" if egfr >= 15 else "Not studied in dialysis — use with caution",
            "Degludec":        "Preferred basal in CKD (lowest hypoglycaemia risk — reduced insulin clearance increases duration)",
        },
        "ref": "ADA Standards 2024, Section 11; RSSDI CPR 2023; Kidney Disease: Improving Global Outcomes (KDIGO) 2022"
    }


def interpret_gad(gad_result: str, lada_score: int = 0, c_pep: float = None) -> dict:
    if gad_result == "positive":
        severity = "confirmed" if (c_pep and c_pep < 0.6) else "early/partial"
        return {
            "result":      "GAD65 Antibody: POSITIVE",
            "interpretation": f"Autoimmune beta-cell destruction confirmed — {severity} beta-cell reserve loss.",
            "diagnosis":   "LADA (if age 30–60 with initial OAD response) OR T1DM (if younger, acute onset, DKA)",
            "immediate_action": [
                "STOP Sulfonylurea immediately — accelerates beta-cell exhaustion",
                "STOP SGLT2i if in use — DKA risk as beta-cell function declines",
                "Start Metformin (if eGFR allows) + Basal Insulin",
                "If C-peptide < 0.6 nmol/L: full basal-bolus MDI (manage as T1DM)",
                "Screen: Anti-TPO + TSH (concurrent autoimmune thyroid in ~30%)",
                "CGM strongly recommended",
            ],
            "colour":      "red",
            "confidence":  "High",
            "ref":         "ADA Standards 2024, Section 2; Fourlanos S et al., Diabetes Care 2006"
        }
    elif gad_result == "negative":
        note = ""
        if lada_score >= 3:
            note = "⚠️ LADA Clinical Score ≥ 3 despite negative GAD65 — order IA-2 antibody and ZnT8 antibody (GAD65 sensitivity ~70–80%; combined panel increases to >90%)."
        return {
            "result":      "GAD65 Antibody: NEGATIVE",
            "interpretation": "Does not fully exclude autoimmune DM. GAD65 alone misses ~20–30% of LADA cases.",
            "next_step":   note or "If clinical suspicion low: consider T2DM / MODY / FCPD as alternatives.",
            "colour":      "green",
            "confidence":  "Moderate",
            "ref":         "ADA Standards 2024, Section 2"
        }
    else:
        return {
            "result":      "GAD65 Antibody: Not done",
            "interpretation": "Order GAD65 antibody — essential to exclude LADA in all atypical or refractory diabetes presentations.",
            "colour":      "blue",
            "confidence":  "High",
            "ref":         "ADA Standards 2024, Section 2; RSSDI CPR 2023"
        }


def interpret_faecal_elastase(fe1_ug_g: float) -> dict:
    if fe1_ug_g >= 200:
        return {
            "value":  f"{fe1_ug_g} µg/g stool",
            "result": "✅ Normal exocrine function (≥ 200 µg/g)",
            "implication": "FCPD unlikely based on exocrine function. Does not exclude early FCPD (imaging still needed if clinical suspicion).",
            "colour": "green",
            "ref":    "Lindkvist B, World J Gastroenterol 2013"
        }
    elif fe1_ug_g >= 100:
        return {
            "value":  f"{fe1_ug_g} µg/g stool",
            "result": "⚠️ Moderate exocrine insufficiency (100–200 µg/g)",
            "implication": "Significant pancreatic exocrine impairment. Consistent with chronic pancreatitis / FCPD. Start PERT (Creon 25,000 U/meal). CECT abdomen for structural assessment.",
            "colour": "orange",
            "ref":    "Lindkvist B, World J Gastroenterol 2013"
        }
    else:
        return {
            "value":  f"{fe1_ug_g} µg/g stool",
            "result": "🔴 Severe exocrine insufficiency (< 100 µg/g)",
            "implication": "Severe pancreatic exocrine failure — strongly supports FCPD / chronic calcific pancreatitis. PERT mandatory: Creon 50,000 U with main meals, 25,000 U with snacks. Check fat-soluble vitamins (A, D, E, K) + B12 + Zinc.",
            "colour": "red",
            "ref":    "Lindkvist B, World J Gastroenterol 2013; Mohan V, Pancreatology 2012"
        }
