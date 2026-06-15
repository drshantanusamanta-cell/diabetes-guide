# ============================================================
# acute.py  —  Acute Hyperglycaemic Emergency Protocols
# Sources: JBDS DKA Guidelines 2023, ADA Standards 2024 Section 16
#          ADA Standards 2024 Section 6 (Hypoglycaemia)
# ============================================================


DKA_PROTOCOL = {
    "title": "Diabetic Ketoacidosis (DKA) Management Protocol",
    "ref":   "JBDS DKA Guidelines 2023; ADA Standards 2024, Section 16; RSSDI CPR 2023",
    "diagnostic_criteria": {
        "Plasma glucose":      "> 11 mmol/L (200 mg/dL) — OR known DM regardless of glucose",
        "Blood ketones":       "≥ 3.0 mmol/L (blood) OR ≥ 2+ urine ketones",
        "Venous pH":           "< 7.3",
        "Bicarbonate":         "< 15 mmol/L",
        "Special note":        "⚠️ Euglycaemic DKA: glucose may be near-normal in SGLT2i users — diagnose on pH/ketones, not glucose alone",
    },
    "severity": {
        "Mild":     "pH 7.25–7.30 · Bicarbonate 15–18 · Alert",
        "Moderate": "pH 7.00–7.24 · Bicarbonate 10–14 · Drowsy",
        "Severe":   "pH < 7.00 · Bicarbonate < 10 · Stupor/Coma",
    },
    "immediate_actions": [
        "🔴 CALL FOR HELP — Initiate DKA pathway immediately",
        "Secure IV access (2 large-bore cannulae)",
        "Bloods: ABG / VBG, RBS, U&E, serum ketones, FBC, blood culture if sepsis suspected",
        "ECG (hyperkalaemia can mimic MI; potassium abnormalities)",
        "Catheterize if unconscious or anuric",
        "Weigh patient (for fluid + insulin calculations)",
        "Identify and treat precipitant: infection (50%), omitted insulin, new T1DM",
    ],
    "fluid_replacement": {
        "protocol":       "0.9% NaCl (Normal Saline) — rates below are for average adults (60–90 kg). INDIVIDUALISE for extremes of weight, elderly, cardiac compromise, and children.",
        "first_litre":    "1 litre 0.9% NaCl over 1 hour",
        "second_litre":   "1 litre 0.9% NaCl over next 2 hours",
        "third_litre":    "1 litre 0.9% NaCl over next 2 hours",
        "thereafter":     "1 litre 0.9% NaCl every 4 hours — guided by clinical response and urine output",
        "switch_to_dextrose": "When glucose < 14 mmol/L (252 mg/dL): add 10% Dextrose at 125 mL/hr alongside continuing 0.9% NaCl (do not stop saline)",
        "caution":        "⚠️ Avoid rapid fluid shifts in children and elderly — cerebral oedema risk. Reduce rate in cardiac or renal compromise. Seek senior review if weight > 90 kg or < 60 kg, or if haemodynamically unstable.",
        "weight_note":    "JBDS 2023: Fluid replacement should be weight-based and guided by clinical response (HR, BP, urine output, JVP). These fixed rates are appropriate for uncomplicated adult DKA of average weight. Adjust for extreme body weight (use ideal body weight for obese patients).",
    },
    "insulin": {
        "type":         "ONLY Regular Human Insulin (Actrapid / Huminsulin R / Insugen R) for IV infusion",
        "important":    "⚠️ Do NOT use Analogues (Lispro, Aspart, Glargine) IV",
        "preparation":  "50 units Regular Insulin in 50 mL 0.9% NaCl = 1 unit/mL",
        "rate":         "Fixed Rate IV Insulin Infusion (FRIII): 0.1 units/kg/hr",
        "example":      "70 kg patient → 7 units/hr",
        "hold_if":      "K⁺ < 3.5 mmol/L — replace potassium FIRST, then start insulin",
        "when_to_stop": "DKA resolution criteria met AND patient eating → switch to SC",
    },
    "potassium": {
        "rationale":    "Total body K⁺ always depleted in DKA (even if serum K⁺ normal/high on admission)",
        "K < 3.5":      "Replace IV — 40 mmol/hr in 1L fluid; delay insulin until K⁺ > 3.5",
        "K 3.5–5.5":   "Add 40 mmol KCl to each litre of IV fluid",
        "K > 5.5":      "No potassium replacement. Recheck 2-hourly.",
        "monitor":      "Recheck K⁺ at 1 hour, 2 hours, 4 hours from start",
    },
    "resolution_criteria": [
        "Blood ketones < 0.6 mmol/L",
        "Venous pH > 7.3",
        "Bicarbonate > 15 mmol/L",
        "Patient able to eat and drink",
    ],
    "transition_to_sc": [
        "Give SC insulin (basal + bolus) and wait 30–60 minutes before stopping IV infusion",
        "If on insulin before admission: restart previous SC regimen",
        "If new T1DM: start basal-bolus at 0.5 U/kg/day (50% basal, 50% bolus split 3 meals)",
    ],
    "monitoring": "Hourly glucose, ketones, VBG at 0, 1, 2 hours then 2-hourly until resolution",
}


HHS_PROTOCOL = {
    "title": "Hyperglycaemic Hyperosmolar State (HHS) Management Protocol",
    "ref":   "JBDS HHS Guidelines 2012 (updated 2023); ADA Standards 2024, Section 16",
    "diagnostic_criteria": {
        "Plasma glucose":   "> 30 mmol/L (540 mg/dL)",
        "Osmolality":       "> 320 mOsm/kg",
        "No significant ketoacidosis": "Venous pH > 7.3, Bicarbonate > 15 mmol/L",
        "Volume depletion": "Severe — often 8–10 litres deficit",
    },
    "key_differences_from_DKA": [
        "HHS: Slower onset (days–weeks) vs DKA (hours)",
        "HHS: Older T2DM patients typically; DKA: younger T1DM",
        "HHS: No significant ketosis (some residual insulin present)",
        "HHS: Much higher glucose and osmolality than DKA",
        "HHS: High DVT risk — anticoagulation recommended",
        "HHS: Fluid replacement is SLOWER than DKA",
    ],
    "fluid_replacement": {
        "first_litre":    "0.9% NaCl 1 litre over 1 hour",
        "thereafter":     "0.9% NaCl 1 litre every 2–4 hours — much slower than DKA",
        "rate_goal":      "Reduce osmolality by 3–8 mOsm/kg/hour",
        "target":         "Positive fluid balance of 3–6 litres in first 12 hours",
        "caution":        "⚠️ Do NOT correct glucose/osmolality too rapidly — central pontine myelinolysis risk",
    },
    "insulin": {
        "timing":         "DO NOT start insulin until glucose fails to fall with fluids alone",
        "threshold":      "Start insulin only if glucose not falling by 5 mmol/L/hour with fluids",
        "rate":           "Fixed rate IV insulin 0.05 units/kg/hr (HALF the DKA rate)",
        "target_glucose": "10–15 mmol/L (not lower — rapid fall causes cerebral oedema)",
    },
    "anticoagulation": {
        "recommendation": "Prophylactic LMWH (Enoxaparin 40 mg SC OD) — DVT risk very high in HHS",
        "ref":            "JBDS HHS Guidelines 2023",
    },
    "monitoring":   "Hourly glucose, 2-hourly osmolality calculation, strict fluid balance, ECG monitoring",
    "resolution":   "Glucose < 15 mmol/L AND osmolality < 300 mOsm/kg AND patient alert and able to eat",
}


HYPOGLYCAEMIA_PROTOCOL = {
    "title": "Hypoglycaemia Management Protocol",
    "ref":   "ADA Standards 2024, Section 6; RSSDI CPR 2023",
    "classification": {
        "Level 1 (Alert value)": "3.0–3.9 mmol/L (54–70 mg/dL) — action required",
        "Level 2 (Clinically significant)": "< 3.0 mmol/L (< 54 mg/dL) — serious event",
        "Level 3 (Severe)":     "Any glucose with altered consciousness / requiring assistance",
    },
    "conscious_patient": {
        "rule_of_15":   "15 g fast-acting carbohydrate → recheck glucose in 15 minutes → repeat if still < 3.9 mmol/L",
        "sources_15g": [
            "3–4 glucose tablets",
            "150 mL fruit juice",
            "150 mL regular (non-diet) soft drink",
            "1 tablespoon sugar / honey",
            "Glucon-D 3 teaspoons in water",
        ],
        "after_recovery": "Follow with snack containing complex carbohydrate + protein (e.g., 2 biscuits + milk)",
        "ref":            "ADA Standards 2024, Section 6; RSSDI CPR 2023",
    },
    "unconscious_patient": {
        "first_line":    "IV Dextrose: 25 mL of 50% Dextrose IV STAT (= 12.5 g glucose) — repeat in 10 min if no response",
        "alternative":   "Glucagon 1 mg IM/SC (GlucoGen Kit / Lyumjev glucagon) — if no IV access",
        "intranasal":    "Baqsimi (Intranasal glucagon) 3 mg — if available",
        "FCPD_warning":  "⚠️ In FCPD: glucagon WILL NOT WORK — alpha-cell destruction. Only IV dextrose effective.",
        "after":         "When alert: oral glucose then meal. Monitor glucose hourly × 4 hours.",
    },
    "recurrent_hypoglycaemia": [
        "Identify and remove cause: excessive insulin dose, missed meal, alcohol, exercise",
        "Review and reduce sulphonylurea dose by 50%",
        "Reduce basal insulin by 10–20% (especially overnight doses)",
        "Relax HbA1c target to < 8.0% in vulnerable patients",
        "Consider switch to Degludec (lower severe hypo risk — DEVOTE trial)",
        "CGM with alarms strongly recommended",
    ],
    "impaired_awareness": {
        "definition": "Loss of adrenergic warning symptoms before neuroglycopenic symptoms develop",
        "action":     "Relaxed glucose targets for 3–6 months (avoid all glucose < 5 mmol/L); CGM mandatory; structured education (DAFNE-type)",
        "ref":        "ADA Standards 2024, Section 6",
    }
}


def get_dka_checklist() -> list:
    """Returns a bedside DKA management checklist (time-based)."""
    return [
        {"time": "0 min",    "action": "Establish IV access × 2, send bloods (VBG/ABG, glucose, ketones, U&E, FBC)", "done": False},
        {"time": "0 min",    "action": "ECG — check for hyperkalaemia (peaked T waves)", "done": False},
        {"time": "0 min",    "action": "Start 1L 0.9% NaCl over 60 minutes", "done": False},
        {"time": "0–30 min", "action": "Check K⁺ result — if < 3.5 mmol/L, DO NOT start insulin yet", "done": False},
        {"time": "30 min",   "action": "Start Fixed Rate IV Insulin (FRIII): 0.1 U/kg/hr Regular insulin", "done": False},
        {"time": "30 min",   "action": "Add KCl 40 mmol to each IV bag if K⁺ 3.5–5.5 mmol/L", "done": False},
        {"time": "60 min",   "action": "Recheck VBG, glucose, ketones, K⁺", "done": False},
        {"time": "2 hr",     "action": "If glucose < 14 mmol/L: add 10% Dextrose alongside saline", "done": False},
        {"time": "Ongoing",  "action": "Hourly glucose + ketones until resolution. VBG at 2 hr, 4 hr, 6 hr.", "done": False},
        {"time": "Resolution","action": "Ketones < 0.6 + pH > 7.3 + bicarbonate > 15 + eating: transition to SC insulin", "done": False},
    ]
