# ============================================================
# Shantanu's Diabetes Treatment Assistant
# A bedside clinical decision support tool for Indian practice
# Sources: ADA 2024, RSSDI CPR 2023, ICMR T2DM 2018,
#          DIPSI 2020, JBDS 2023, API Guidelines
# ============================================================

import streamlit as st
try:
    # If running from repo root (flat file layout — Streamlit Cloud default)
    from diagnostic import classify_diabetes, compute_lada_score
    from treatment import recommend_treatment, calculate_insulin_dose, calculate_insulin_switch, INSULIN_SWITCH_PROTOCOLS
    from interpreter import (
        interpret_hba1c, interpret_c_peptide, interpret_homa,
        interpret_egfr, interpret_gad, interpret_faecal_elastase,
    )
    from acute import DKA_PROTOCOL, HHS_PROTOCOL, HYPOGLYCAEMIA_PROTOCOL, get_dka_checklist
    from data import ORAL_DRUGS, GLP1_DRUGS, INSULIN_DRUGS, COMBO_INJECTABLES, INVESTIGATIONS, HBA1C_TARGETS, CONFIDENCE
except ImportError:
    # If running with modules/ subfolder
    from modules.diagnostic import classify_diabetes, compute_lada_score
    from modules.treatment import recommend_treatment, calculate_insulin_dose, calculate_insulin_switch, INSULIN_SWITCH_PROTOCOLS
    from modules.interpreter import (
        interpret_hba1c, interpret_c_peptide, interpret_homa,
        interpret_egfr, interpret_gad, interpret_faecal_elastase,
    )
    from modules.acute import DKA_PROTOCOL, HHS_PROTOCOL, HYPOGLYCAEMIA_PROTOCOL, get_dka_checklist
    from modules.data import ORAL_DRUGS, GLP1_DRUGS, INSULIN_DRUGS, COMBO_INJECTABLES, INVESTIGATIONS, HBA1C_TARGETS, CONFIDENCE

st.set_page_config(
    page_title="Shantanu's Diabetes Treatment Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ──────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {font-size: 1.5rem; font-weight: 700; color: #1D6FA4; margin-bottom: 0;}
    .subtitle   {font-size: 0.85rem; color: #666; margin-bottom: 1rem;}
    .conf-high  {background:#d4edda; color:#155724; padding:4px 10px; border-radius:12px; font-size:0.78rem; font-weight:600;}
    .conf-mod   {background:#fff3cd; color:#856404; padding:4px 10px; border-radius:12px; font-size:0.78rem; font-weight:600;}
    .conf-low   {background:#f8d7da; color:#721c24; padding:4px 10px; border-radius:12px; font-size:0.78rem; font-weight:600;}
    .prob-high  {background:#dc3545; color:white; padding:2px 8px; border-radius:8px; font-size:0.78rem; font-weight:700;}
    .prob-mod   {background:#fd7e14; color:white; padding:2px 8px; border-radius:8px; font-size:0.78rem; font-weight:700;}
    .prob-low   {background:#6c757d; color:white; padding:2px 8px; border-radius:8px; font-size:0.78rem;}
    .warn-box   {background:#fff3cd; border-left:4px solid #ffc107; padding:10px 14px; border-radius:4px; margin:8px 0;}
    .ref-box    {background:#e8f4fd; border-left:3px solid #1D6FA4; padding:8px 12px; border-radius:4px; font-size:0.8rem; color:#0c5460; margin:6px 0;}
    .step-card  {background:#f8f9fa; border:1px solid #dee2e6; border-radius:8px; padding:14px; margin:8px 0;}
    .drug-name  {font-size:1.05rem; font-weight:700; color:#1D6FA4;}
    .brand-list {font-size:0.82rem; color:#444; margin-top:4px;}
    .section-hdr{font-size:1.1rem; font-weight:700; color:#1D6FA4; border-bottom:2px solid #1D6FA4; padding-bottom:4px; margin:12px 0 8px 0;}
    div[data-testid="stSidebar"] {background:#f0f4f8;}
    .checklist-item {padding:6px 0; border-bottom:1px solid #eee;}
</style>
""", unsafe_allow_html=True)


def glucose_input(label: str, key: str, default_mgdl: float, min_mgdl: float = 40, max_mgdl: float = 1200) -> float:
    """Dual-unit glucose input. Returns value always in mg/dL."""
    unit = st.radio("Unit", ["mg/dL", "mmol/L"], horizontal=True, key=f"{key}_unit")
    if unit == "mmol/L":
        default_mmol = round(default_mgdl / 18.0, 1)
        min_mmol     = round(min_mgdl / 18.0, 1)
        max_mmol     = round(max_mgdl / 18.0, 1)
        val_mmol = st.number_input(
            f"{label} (mmol/L)",
            min_value=min_mmol, max_value=max_mmol,
            value=default_mmol, step=0.1, key=key,
        )
        val_mgdl = round(val_mmol * 18.0, 1)
        st.caption(f"≈ **{val_mgdl} mg/dL**")
        return val_mgdl
    else:
        val_mgdl = st.number_input(
            f"{label} (mg/dL)",
            min_value=int(min_mgdl), max_value=int(max_mgdl),
            value=int(default_mgdl), step=1, key=key,
        )
        val_mmol = round(val_mgdl / 18.0, 1)
        st.caption(f"≈ **{val_mmol} mmol/L**")
        return float(val_mgdl)


def conf_badge(level: str) -> str:
    css = {"High": "conf-high", "Moderate": "conf-mod", "Low": "conf-low"}
    cls = css.get(level, "conf-low")
    return f'<span class="{cls}">Confidence: {level}</span>'


def prob_badge(level: str) -> str:
    css = {"High": "prob-high", "Moderate": "prob-mod"}
    cls = css.get(level, "prob-low")
    return f'<span class="{cls}">{level} probability</span>'


def ref_box(ref: str):
    st.markdown(f'<div class="ref-box">📚 <b>Reference:</b> {ref}</div>', unsafe_allow_html=True)


def warn_box(msg: str):
    st.markdown(f'<div class="warn-box">{msg}</div>', unsafe_allow_html=True)


# ── Sidebar navigation ────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="main-title">🩺 Shantanu\'s Diabetes<br>Treatment Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">India-contextualised · Guideline-grounded<br>ADA 2024 · RSSDI 2023 · ICMR 2018</div>', unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigate to:",
        options=[
            "🏠 Home",
            "🔬 Diagnose",
            "🧪 Investigate",
            "📊 Interpret Labs",
            "💊 Treatment Planner",
            "🩸 Insulin Calculator",
            "🚨 Acute Protocols",
            "🎯 Treatment Targets",
            "💉 Drug Reference",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("⚠️ For clinical decision support only. Always apply individual clinical judgement. This tool does not replace specialist assessment.")


# ═══════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.markdown('<div class="main-title">🩺 Shantanu\'s Diabetes Treatment Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">India-contextualised clinical decision support · Bedside-ready · Zero ongoing cost</div>', unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**🔬 Diagnose**\nClassify T1DM, T2DM, LADA, MODY, FCPD, Lean T2DM, GDM, Secondary DM with probability scoring")
    with col2:
        st.info("**🧪 Investigate**\nGet condition-specific investigation lists with interpretation guidance")
    with col3:
        st.info("**📊 Interpret Labs**\nHbA1c, C-peptide, HOMA-IR, GAD, eGFR, Faecal Elastase — instant clinical interpretation")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.success("**💊 Treatment Planner**\nGuideline-based drug selection with Indian brand names and cost tiers")
    with col5:
        st.success("**🩸 Insulin Calculator**\nStarting doses, titration schedules, brand recommendations")
    with col6:
        st.success("**🚨 Acute Protocols**\nDKA · HHS · Severe Hypoglycaemia — bedside checklists")

    st.divider()
    st.markdown("### Guideline sources")
    sources = [
        ("ADA Standards of Medical Care in Diabetes 2024", "Sections 2, 6, 7, 9, 10, 11, 13, 15, 16"),
        ("RSSDI Clinical Practice Recommendations 2023", "Primary Indian guideline"),
        ("ICMR T2DM Guidelines 2018", "Indian-specific pharmacotherapy"),
        ("DIPSI Consensus 2020", "Gestational Diabetes — Indian context"),
        ("JBDS DKA Guidelines 2023", "DKA / HHS acute management"),
        ("ADA-EASD Consensus Report 2022", "Hyperglycaemia management framework"),
        ("ATTD Consensus 2023", "CGM and Time-in-Range targets"),
        ("DEVOTE, SUSTAIN-6, LEADER, REWIND, EMPA-REG OUTCOME, DECLARE, DAPA-HF, EMPEROR, CREDENCE, DAPA-CKD, BRIGHT, CONCLUDE, BEGIN trials", "Key landmark RCTs embedded"),
        ("Fourlanos S et al., Diabetes Care 2006", "LADA Clinical Score"),
        ("Mohan V, Pancreatology 2012; Bhatia E et al., Gut 2002", "FCPD — Indian data"),
        ("Matthews DR et al., Diabetologia 1985", "HOMA model"),
        ("Lindkvist B, World J Gastroenterol 2013", "Faecal Elastase interpretation"),
    ]
    for src, detail in sources:
        st.markdown(f"- **{src}** — {detail}")

    st.divider()
    st.caption("Version 1.0 · Built for Indian clinical practice · No AI API required · All logic rule-based from authoritative guidelines")


# ═══════════════════════════════════════════════════════════
# PAGE: DIAGNOSE
# ═══════════════════════════════════════════════════════════
elif page == "🔬 Diagnose":
    st.markdown('<div class="section-hdr">🔬 Diabetes Diagnosis Classifier</div>', unsafe_allow_html=True)
    st.caption("Enter patient details below. The engine applies validated clinical algorithms from ADA 2024, RSSDI CPR 2023, Fourlanos 2006 (LADA), Shields 2012 (MODY), and Mohan 2012 (FCPD).")

    with st.form("diagnose_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            age         = st.number_input("Current age (years)", 1, 100, 49)
            age_at_dx   = st.number_input("Age at diabetes diagnosis (years)", 1, 100, 45)
            duration    = st.number_input("Duration of diabetes (years)", 0.0, 60.0, 4.0, step=0.5)
        with col2:
            bmi         = st.number_input("BMI (kg/m²)", 10.0, 60.0, 28.0, step=0.1)
            hba1c       = st.number_input("HbA1c (%)", 4.0, 20.0, 9.5, step=0.1)
            fpg         = glucose_input("Fasting plasma glucose", "fpg_input", default_mgdl=200, min_mgdl=40, max_mgdl=1200)
        with col3:
            c_pep       = st.number_input("Fasting C-peptide (nmol/L) — 0 = not done", 0.0, 5.0, 0.0, step=0.05)
            homa_ir_val = st.number_input("HOMA-IR — 0 = not done", 0.0, 30.0, 0.0, step=0.1)
            gad         = st.selectbox("GAD65 antibody", ["not done", "positive", "negative"])

        st.markdown("**Clinical features**")
        col4, col5, col6 = st.columns(3)
        with col4:
            acute_onset    = st.checkbox("Acute / abrupt onset (polyuria, polydipsia, weight loss)")
            ketosis        = st.checkbox("Ketosis / DKA at presentation")
            oad_failure    = st.checkbox("Failure of oral agents (inadequate response)")
            pregnancy      = st.checkbox("Currently pregnant")
        with col5:
            abdo_pain      = st.checkbox("History of recurrent abdominal pain")
            pancreatic_calc= st.checkbox("Pancreatic calculi on imaging (X-ray / CT)")
            steatorrhoea   = st.checkbox("Steatorrhoea / malabsorption")
            tropical       = st.checkbox("Origin from tropical India (Kerala, TN, coastal Karnataka, WB)")
        with col6:
            family_dm      = st.checkbox("Family history of T2DM")
            family_3gen    = st.checkbox("3-generation family history (autosomal dominant)")
            family_ai      = st.checkbox("Family history of autoimmune disease")
            personal_ai    = st.checkbox("Personal history of autoimmune disease")
            metabolic_synd = st.checkbox("Metabolic syndrome (dyslipidaemia, central obesity, HTN)")
            steroid_use    = st.checkbox("On glucocorticoids / immunosuppressants")
            other_drug     = st.checkbox("Drug-induced? (antipsychotics, thiazides, tacrolimus)")
            pancreatitis_hx= st.checkbox("History of acute pancreatitis (non-calcific)")

        submitted = st.form_submit_button("🔬 Classify Diabetes", type="primary", use_container_width=True)

    if submitted:
        inputs = dict(
            age=age, age_at_dx=age_at_dx, duration_yrs=duration,
            bmi=bmi, hba1c=hba1c, fpg_mgdl=fpg,
            c_peptide=c_pep if c_pep > 0 else None,
            homa_ir=homa_ir_val if homa_ir_val > 0 else None,
            gad_status=gad,
            acute_onset=acute_onset, ketosis=ketosis,
            oad_failure=oad_failure, pregnancy=pregnancy,
            abdo_pain=abdo_pain, pancreatic_calculi=pancreatic_calc,
            steatorrhoea=steatorrhoea, tropical_india=tropical,
            family_dm=family_dm, family_3gen=family_3gen,
            family_ai=family_ai, personal_ai=personal_ai,
            metabolic_synd=metabolic_synd, steroid_use=steroid_use,
            other_drug=other_drug, pancreatitis_hx=pancreatitis_hx,
        )
        results = classify_diabetes(inputs)

        st.divider()
        st.markdown("### Differential diagnosis — ranked by probability")

        for i, r in enumerate(results):
            prob_css = {"High":"🔴","Moderate":"🟠","Possible":"🟡","Low":"⚪"}.get(r["probability"],"⚪")
            with st.expander(f"{prob_css} **{r['diagnosis']}** — {r['probability']} probability  |  Confidence: {r['confidence']}", expanded=(i==0)):
                col_a, col_b = st.columns([2,1])
                with col_a:
                    st.markdown("**Key supporting features:**")
                    for feat in r["key_features"]:
                        if feat:
                            st.markdown(f"  - {feat}")
                with col_b:
                    st.markdown(f'**Probability:** {prob_badge(r["probability"])}', unsafe_allow_html=True)
                    st.markdown(f'**Confidence:** {conf_badge(r["confidence"])}', unsafe_allow_html=True)

                if r.get("warning"):
                    warn_box(r["warning"])

                st.markdown("**Recommended next steps:**")
                for step in r["next_steps"]:
                    st.markdown(f"  {step}")

                ref_box(r["ref"])

        # LADA Score summary
        st.divider()
        lada_score, lada_details = compute_lada_score(age_at_dx, acute_onset, bmi, personal_ai, family_ai)
        with st.expander(f"📋 LADA Clinical Score: {lada_score}/5 (threshold ≥ 3)"):
            for d in lada_details:
                st.markdown(f"  - {d}")
            if lada_score >= 3:
                st.error(f"Score {lada_score}/5 ≥ 3 — Investigate for LADA (GAD65 antibody first)")
            elif lada_score == 2:
                st.warning(f"Score {lada_score}/5 — Borderline. Order GAD65 if clinical suspicion.")
            else:
                st.success(f"Score {lada_score}/5 — LADA less likely by clinical score alone.")
            ref_box("Fourlanos S et al., Diabetes Care 2006 — Sensitivity 90%, Specificity 71% at cut-off ≥3")


# ═══════════════════════════════════════════════════════════
# PAGE: INVESTIGATE
# ═══════════════════════════════════════════════════════════
elif page == "🧪 Investigate":
    st.markdown('<div class="section-hdr">🧪 Investigation Advisor</div>', unsafe_allow_html=True)
    st.caption("Select the suspected diagnosis to get a prioritised investigation list with interpretation guidance.")

    dx_choice = st.selectbox("Suspected / confirmed diagnosis:", [
        "T2DM (routine workup at diagnosis)",
        "T1DM",
        "LADA",
        "FCPD",
        "MODY",
        "GDM",
        "Lean T2DM",
    ])

    inv_map = {
        "T2DM (routine workup at diagnosis)": [
            ("HbA1c", "High", "Baseline + 3-monthly monitoring. Target < 7.0% (< 6.5% young, < 8.0% elderly/frail)."),
            ("Fasting plasma glucose (FPG)", "High", "Diagnostic if ≥ 126 mg/dL (7.0 mmol/L). Fasting ≥ 8 hrs."),
            ("2-hr PPG post 75g OGTT", "High", "Diagnostic if ≥ 200 mg/dL (11.1 mmol/L). Confirms GDM pattern if needed."),
            ("eGFR (CKD-EPI formula)", "High", "Baseline renal function. Determines Metformin dose and SGLT2i eligibility."),
            ("UACR (Urine Albumin-Creatinine Ratio)", "High", "Early nephropathy screen. Annual if normal. ACEi/ARB if ≥ 30 mg/g."),
            ("Fasting lipid profile", "High", "T2DM carries high CV risk — LDL target < 70 mg/dL if high CV risk."),
            ("LFT (liver function tests)", "High", "NAFLD/NASH common in Indian T2DM. Baseline before starting Pioglitazone."),
            ("ECG", "High", "CV risk assessment. Look for LVH, ischaemic changes."),
            ("GAD65 antibody", "Moderate", "Rule out LADA — especially if OAD failure, non-obese, or young."),
            ("Fundus examination (dilated)", "High", "Diabetic retinopathy screen at diagnosis and annually."),
            ("Foot examination (10g monofilament + ABI)", "High", "Peripheral neuropathy and PAD screen — annually."),
            ("TSH", "Moderate", "Autoimmune thyroid disease common in Indians with DM. Annual screen."),
        ],
        "T1DM": [
            ("GAD65 antibody", "High", "Primary autoimmune marker. Positive in ~80% T1DM."),
            ("IA-2 antibody", "High", "Add if GAD65 result equivocal. Positive in ~60% T1DM."),
            ("ZnT8 antibody", "Moderate", "Third-line. Increases combined panel sensitivity to >95%."),
            ("Fasting C-peptide", "High", "Quantify beta-cell reserve. < 0.6 nmol/L = severe loss → MDI mandatory."),
            ("HbA1c", "High", "Baseline and 3-monthly. Target < 7.0%."),
            ("eGFR + UACR", "High", "Annual nephropathy screening."),
            ("Anti-TPO antibody + TSH", "High", "Autoimmune thyroid in 30% T1DM. Screen at diagnosis."),
            ("Anti-tTG IgA + Total IgA (coeliac screen)", "High", "Coeliac in 5–10% T1DM. Screen at diagnosis."),
            ("Fundus + Foot exam", "High", "Retinopathy + neuropathy annual screen."),
        ],
        "LADA": [
            ("GAD65 antibody", "High", "Order FIRST — most sensitive single LADA marker. Positive = LADA confirmed."),
            ("IA-2 antibody", "High", "Order if GAD65 negative but suspicion remains. Adds ~15% sensitivity."),
            ("ZnT8 antibody", "Moderate", "Third-line. Combined GAD65+IA-2+ZnT8 sensitivity >90%."),
            ("Fasting C-peptide", "High", "< 0.6 nmol/L = advanced LADA → full MDI. > 0.6 = early LADA → basal insulin + GLP-1 RA."),
            ("Anti-TPO antibody + TSH", "High", "Concurrent autoimmune thyroid in ~30% LADA."),
            ("HbA1c + eGFR", "High", "Standard monitoring."),
        ],
        "FCPD": [
            ("X-ray abdomen (plain)", "High", "First-line — pancreatic calculi along duct axis = diagnostic of chronic calcific pancreatitis."),
            ("CECT abdomen (pancreatic protocol)", "High", "Gold standard — calculi, ductal dilatation, parenchymal atrophy, exclude malignancy."),
            ("Faecal Elastase-1", "High", "< 200 µg/g = exocrine insufficiency. < 100 µg/g = severe → PERT mandatory."),
            ("Fasting C-peptide", "High", "Typically very low in FCPD — guides insulin dose planning."),
            ("CA 19-9", "High", "Baseline malignancy surveillance. Chronic pancreatitis carries 10–20× cancer risk."),
            ("SPINK1 mutation (tertiary)", "Moderate", "Found in ~50% Indian FCPD — confirmatory genetic marker."),
            ("Vitamins A, D, E, K (fat-soluble)", "High", "Deficient due to malabsorption. Replace supplementally."),
            ("Vitamin B12 + Zinc", "High", "Commonly deficient in FCPD malnutrition."),
            ("HbA1c", "Moderate", "May underestimate glycaemia in malnutrition (low Hb). Use FBG + PPG for monitoring."),
            ("MRCP / EUS (if surgical consideration)", "Moderate", "Ductal anatomy for endoscopic or surgical decompression planning."),
        ],
        "MODY": [
            ("GAD65 antibody", "High", "Must be negative to support MODY diagnosis."),
            ("Fasting C-peptide", "High", "Must be detectable at > 3 years duration — confirms residual beta-cell function."),
            ("MODY Probability Score (online)", "High", "exeter.ac.uk/mody-calculator — if score > 25%: refer for genetic panel."),
            ("MODY genetic panel (if score > 25%)", "High", "GCK (MODY2), HNF1A (MODY3), HNF4A (MODY1), HNF1B (MODY5)."),
            ("Family screening — first-degree relatives", "High", "Autosomal dominant — 50% risk to children."),
        ],
        "GDM": [
            ("75g OGTT — DIPSI method", "High", "2-hr plasma glucose ≥ 140 mg/dL (7.8 mmol/L) = GDM. Do at 24–28 weeks."),
            ("FPG at booking", "High", "FPG ≥ 126 mg/dL or 2-hr ≥ 200 mg/dL in 1st trimester = pre-existing DM (not GDM)."),
            ("HbA1c (if available)", "Moderate", "Targets: fasting < 5.3 mmol/L, 1-hr PPG < 7.8 mmol/L, 2-hr PPG < 6.7 mmol/L."),
            ("Fasting lipids + renal function", "High", "Baseline assessment."),
            ("Fundus examination", "High", "Pre-existing retinopathy may worsen in pregnancy."),
            ("Post-delivery 75g OGTT at 6–12 weeks", "High", "35–50% GDM → T2DM within 10 years — screen postpartum."),
        ],
        "Lean T2DM": [
            ("GAD65 antibody", "High", "Exclude LADA — essential first step."),
            ("X-ray abdomen (plain)", "High", "Exclude FCPD (pancreatic calculi)."),
            ("Fasting C-peptide + HOMA-IR", "High", "Characterise: secretory defect vs resistance pattern."),
            ("MODY Probability Score", "Moderate", "If family history 3-generational — refer for MODY panel."),
            ("Body composition (waist circumference, waist-hip ratio)", "High", "Metabolically obese normal weight? Waist > 90 cm (M) or > 80 cm (F) = central obesity."),
            ("Serum albumin + prealbumin", "Moderate", "Malnutrition assessment — if significant, nutritional rehabilitation first."),
        ],
    }

    selected_inv = inv_map.get(dx_choice, [])
    st.markdown(f"### Investigations for: **{dx_choice}**")

    for inv_name, priority, interpretation in selected_inv:
        pri_colour = {"High": "🔴", "Moderate": "🟠", "Low": "⚪"}
        full_inv = INVESTIGATIONS.get(inv_name, {})
        with st.expander(f"{pri_colour.get(priority,'⚪')} **{inv_name}** — Priority: {priority}"):
            st.markdown(f"**Clinical rationale:** {interpretation}")
            if full_inv.get("interpretation"):
                st.markdown("**Result interpretation guide:**")
                for k, v in full_inv["interpretation"].items():
                    st.markdown(f"- `{k}` → {v}")
            if full_inv.get("formula"):
                st.info(f"Formula: {full_inv['formula']}")
            if full_inv.get("ref"):
                ref_box(full_inv["ref"])


# ═══════════════════════════════════════════════════════════
# PAGE: INTERPRET LABS
# ═══════════════════════════════════════════════════════════
elif page == "📊 Interpret Labs":
    st.markdown('<div class="section-hdr">📊 Lab Result Interpreter</div>', unsafe_allow_html=True)
    st.caption("Enter one or more lab values to get instant clinical interpretation with guideline references.")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["HbA1c", "C-peptide", "HOMA-IR/β", "eGFR + UACR", "GAD Antibody", "Faecal Elastase"])

    with tab1:
        st.markdown("#### HbA1c Interpretation")
        col1, col2 = st.columns(2)
        with col1:
            hba1c_v   = st.number_input("HbA1c (%)", 4.0, 20.0, 9.5, step=0.1, key="hba1c_interp")
            age_v     = st.number_input("Patient age", 18, 100, 49, key="age_interp")
            dm_type_v = st.selectbox("DM type", ["T2DM","T1DM","GDM","LADA","FCPD"], key="dm_interp")
        with col2:
            ckd_v     = st.checkbox("CKD (eGFR 20–60)", key="ckd_interp")
            preg_v    = st.checkbox("Pregnancy / GDM", key="preg_interp")
            frail_v   = st.checkbox("Elderly / frail (≥ 70 years)", key="frail_interp")
        if st.button("Interpret HbA1c", key="btn_hba1c", type="primary"):
            r = interpret_hba1c(hba1c_v, age_v, dm_type_v, ckd_v, preg_v, frail_v)
            st.metric("HbA1c", r["value"])
            st.markdown(r["status"])
            st.info(f"**Target ({r['target_context']}):** {r['target']}")
            st.warning(r["urgency"]) if "Above" in r["status"] or "Severely" in r["status"] else st.success(r["urgency"])
            st.markdown(f"**Estimated average glucose:** {r['estimated_avg_glucose']}")
            st.caption(r["note"])
            ref_box(r["ref"])

    with tab2:
        st.markdown("#### C-peptide Interpretation")
        c_pep_v    = st.number_input("Fasting C-peptide (nmol/L)", 0.0, 5.0, 0.5, step=0.05, key="cpep_v")
        dm_type_cp = st.selectbox("DM type", ["T2DM","T1DM","LADA","FCPD"], key="dm_cp")
        dur_cp     = st.number_input("Duration of DM (years)", 0.0, 50.0, 4.0, key="dur_cp")
        if st.button("Interpret C-peptide", key="btn_cpep", type="primary"):
            r = interpret_c_peptide(c_pep_v, dm_type_cp, dur_cp)
            colour_map = {"green": st.success, "orange": st.warning, "red": st.error, "blue": st.info}
            colour_map.get(r["colour"], st.info)(r["interpretation"])
            st.markdown(f"**Clinical implication:** {r['clinical_implication']}")
            if r.get("note"): st.caption(r["note"])
            ref_box(r["ref"])

    with tab3:
        st.markdown("#### HOMA-IR and HOMA-β Calculator")
        col1, col2 = st.columns(2)
        with col1:
            fg_mgdl = glucose_input("Fasting glucose", "fg_homa", default_mgdl=144, min_mgdl=65, max_mgdl=540)
            fg_mmol = round(fg_mgdl / 18.0, 2)
        with col2:
            fi_uiu  = st.number_input("Fasting insulin (µIU/mL)", 1.0, 200.0, 15.0, step=0.5, key="fi_homa")
        if st.button("Calculate HOMA", key="btn_homa", type="primary"):
            r = interpret_homa(fg_mmol, fi_uiu)
            if "error" in r:
                st.error(r["error"])
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("HOMA-IR", r["HOMA_IR"])
                    cmap = {"green": st.success, "orange": st.warning, "red": st.error}
                    cmap.get(r["IR_colour"], st.info)(r["IR_interp"])
                    st.caption(f"Formula: {r['formula_IR']}")
                with col_b:
                    st.metric("HOMA-β", f"{r['HOMA_beta']}%")
                    cmap.get(r["Beta_colour"], st.info)(r["Beta_interp"])
                    st.caption(f"Formula: {r['formula_B']}")
                st.caption(r["clinical_note"])
                ref_box(r["ref"])

    with tab4:
        st.markdown("#### eGFR + UACR Interpretation")
        egfr_v = st.number_input("eGFR (mL/min/1.73m²)", 1.0, 130.0, 75.0, step=1.0, key="egfr_v")
        uacr_v = st.number_input("UACR (mg/g) — 0 = not done", 0.0, 5000.0, 0.0, step=1.0, key="uacr_v")
        if st.button("Interpret eGFR + UACR", key="btn_egfr", type="primary"):
            r = interpret_egfr(egfr_v, uacr_v if uacr_v > 0 else None)
            cmap = {"green": st.success, "orange": st.warning, "red": st.error}
            cmap.get(r["colour"], st.info)(f"{r['eGFR']} — **{r['CKD_stage']}**")
            st.markdown(f"**Management:** {r['management']}")
            if r.get("UACR"):
                st.info(f"**UACR:** {r['UACR']}")
            st.markdown("**Drug dose adjustments at this eGFR:**")
            for drug, dose in r["drug_doses"].items():
                icon = "⚠️" if "CONTRAINDICATED" in dose or "AVOID" in dose or "STOP" in dose else "✅"
                st.markdown(f"  {icon} **{drug}:** {dose}")
            ref_box(r["ref"])

    with tab5:
        st.markdown("#### GAD65 Antibody Interpretation")
        gad_v = st.selectbox("GAD65 result", ["not done", "positive", "negative"], key="gad_v")
        lada_sc = st.number_input("LADA Clinical Score (0–5) — 0 if not calculated", 0, 5, 0, key="lada_sc_v")
        c_pep_gad = st.number_input("C-peptide (nmol/L) — 0 = not done", 0.0, 5.0, 0.0, step=0.05, key="cpg_v")
        if st.button("Interpret GAD Result", key="btn_gad", type="primary"):
            r = interpret_gad(gad_v, lada_sc, c_pep_gad if c_pep_gad > 0 else None)
            cmap = {"red": st.error, "green": st.success, "blue": st.info}
            cmap.get(r["colour"], st.info)(r["result"])
            st.markdown(f"**Interpretation:** {r['interpretation']}")
            if r.get("immediate_action"):
                st.markdown("**Immediate actions:**")
                for act in r["immediate_action"]:
                    st.markdown(f"  - {act}")
            if r.get("next_step"):
                st.markdown(f"**Next step:** {r['next_step']}")
            ref_box(r["ref"])

    with tab6:
        st.markdown("#### Faecal Elastase-1 Interpretation (FCPD / Exocrine insufficiency)")
        fe1_v = st.number_input("Faecal Elastase-1 (µg/g stool)", 10.0, 500.0, 150.0, step=5.0, key="fe1_v")
        if st.button("Interpret Faecal Elastase", key="btn_fe1", type="primary"):
            r = interpret_faecal_elastase(fe1_v)
            cmap = {"green": st.success, "orange": st.warning, "red": st.error}
            cmap.get(r["colour"], st.info)(r["result"])
            st.markdown(f"**Clinical implication:** {r['implication']}")
            ref_box(r["ref"])


# ═══════════════════════════════════════════════════════════
# PAGE: TREATMENT PLANNER
# ═══════════════════════════════════════════════════════════
elif page == "💊 Treatment Planner":
    st.markdown('<div class="section-hdr">💊 Treatment Planner</div>', unsafe_allow_html=True)
    st.caption("Guideline-based drug selection with Indian brand names. Based on ADA-EASD Consensus 2022 + ADA Standards 2024 + RSSDI CPR 2023.")

    with st.form("treatment_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            dm_t    = st.selectbox("DM type", ["T2DM","T1DM","LADA","FCPD"], key="dm_t")
            hba1c_t = st.number_input("Current HbA1c (%)", 5.0, 20.0, 9.5, step=0.1, key="hba1c_t")
            egfr_t  = st.number_input("eGFR (mL/min/1.73m²)", 5.0, 130.0, 80.0, key="egfr_t")
            age_t   = st.number_input("Age (years)", 18, 100, 49, key="age_t")
        with col2:
            has_ascvd  = st.checkbox("Established ASCVD (CAD, stroke, PAD)")
            has_hf     = st.checkbox("Heart failure (HFrEF or HFpEF)")
            has_ckd    = st.checkbox("CKD (eGFR < 60 or UACR > 30)")
            sglt2_allergy = st.checkbox("Allergy to SGLT2 inhibitors ⚠️")
            glp1_ok    = st.checkbox("GLP-1 RA acceptable (no MTC/MEN2 history)", value=True)
        with col3:
            obesity      = st.checkbox("BMI > 27 kg/m² (weight reduction priority)")
            hypo_concern = st.checkbox("High hypoglycaemia concern (elderly, drives, works at height)")
            on_metformin = st.checkbox("Already on Metformin")
            irregular    = st.checkbox("Irregular schedule / shift worker")
            high_dose    = st.checkbox("Likely to need high insulin dose (> 60 U/day, BMI > 30)")
            has_nash_ir  = st.checkbox("NASH / NAFLD / PCOS / documented high HOMA-IR (specific indication for Pioglitazone)")
            bladder_ca   = st.checkbox("History of bladder cancer ⚠️ (Pioglitazone contraindicated)")
            cost_pref    = st.selectbox("Cost preference", ["any","medium","low"])

        submitted_t = st.form_submit_button("💊 Generate Treatment Plan", type="primary", use_container_width=True)

    if submitted_t:
        if sglt2_allergy and (has_hf or has_ckd):
            warn_box("⚠️ SGLT2i allergy + Heart Failure/CKD: Cannot use cardiorenal protective agent. Optimise RAAS blockade (ACEi/ARB/Finerenone). Cardiology/Nephrology referral recommended.")

        plan = recommend_treatment(dict(
            dm_type=dm_t, hba1c=hba1c_t, egfr=egfr_t, age=age_t,
            has_ascvd=has_ascvd, has_hf=has_hf, has_ckd=has_ckd,
            sglt2_allergy=sglt2_allergy, glp1_ok=glp1_ok,
            obesity=obesity, hypo_concern=hypo_concern,
            on_metformin=on_metformin, cost_preference=cost_pref,
            irregular_schedule=irregular, high_dose_need=high_dose,
            has_nash_ir=has_nash_ir, bladder_cancer=bladder_ca,
        ))

        st.divider()
        st.markdown("### Treatment recommendations")

        for step in plan["steps"]:
            with st.expander(f"**{step['step']}**", expanded=True):
                col_a, col_b = st.columns([3,1])
                with col_a:
                    st.markdown(f'<span class="drug-name">{step["drug"]}</span>', unsafe_allow_html=True)
                    st.markdown(f"**Dose:** {step['dose']}")
                    st.markdown(f'<span class="brand-list">🏷️ Indian brands: {step["brands"]}</span>', unsafe_allow_html=True)
                    st.markdown(f"**Rationale:** {step['rationale']}")
                with col_b:
                    st.metric("HbA1c reduction", step["hba1c_reduction"])
                    st.metric("Hypo risk", step["hypo_risk"])
                    st.markdown(f'{conf_badge(step["confidence"])}', unsafe_allow_html=True)
                ref_box(step["ref"])

        if plan["notes"]:
            st.divider()
            st.markdown("### Important clinical notes")
            for note in plan["notes"]:
                if note.startswith("⚠️"):
                    st.warning(note)
                else:
                    st.info(note)


# ═══════════════════════════════════════════════════════════
# PAGE: INSULIN CALCULATOR
# ═══════════════════════════════════════════════════════════
elif page == "🩸 Insulin Calculator":
    st.markdown('<div class="section-hdr">🩸 Insulin Calculator</div>', unsafe_allow_html=True)
    st.caption("Starting doses, titration schedules, and brand recommendations. Based on ADA 2024 treat-to-target approach.")

    calc_tab1, calc_tab2, calc_tab3, calc_tab4, calc_tab5 = st.tabs([
        "Basal initiation", "MDI (Basal-Bolus)", "Basal titration", "Insulin Switch", "Insulin comparison"
    ])

    with calc_tab1:
        st.markdown("#### Basal insulin starting dose")
        col1, col2 = st.columns(2)
        with col1:
            wt_bi    = st.number_input("Weight (kg)", 30.0, 200.0, 75.0, key="wt_bi")
            hba1c_bi = st.number_input("HbA1c (%)", 5.0, 20.0, 9.5, key="hba1c_bi")
            dm_bi    = st.selectbox("DM type", ["T2DM","T1DM","FCPD"], key="dm_bi")
        with col2:
            has_ascvd_bi = st.checkbox("Established CVD", key="ascvd_bi")
            egfr_bi   = st.number_input("eGFR", 5.0, 130.0, 80.0, key="egfr_bi")
            cost_bi   = st.selectbox("Cost preference", ["any","medium","low"], key="cost_bi")
            elderly_bi = st.checkbox("Elderly (≥ 70 yrs) / lives alone", key="eld_bi")
            irregular_bi = st.checkbox("Irregular schedule / shift worker", key="irr_bi")
            highdose_bi  = st.checkbox("Likely to need > 60 U/day", key="hd_bi")

        if st.button("Calculate basal starting dose", key="btn_bi", type="primary"):
            try:
                from treatment import _select_basal_insulin
            except ImportError:
                from modules.treatment import _select_basal_insulin
            ins = _select_basal_insulin(dict(
                age=70 if elderly_bi else 50,
                egfr=egfr_bi, has_ascvd=has_ascvd_bi,
                cost_preference=cost_bi, high_dose_need=highdose_bi,
                irregular_schedule=irregular_bi, dm_type=dm_bi,
            ))
            result = calculate_insulin_dose(wt_bi, hba1c_bi, dm_bi, "basal_initiation")

            st.success(f"**Recommended insulin:** {ins['drug']}")
            st.info(f"**Rationale:** {ins['rationale']}")
            st.markdown(f"🏷️ **Brands:** {ins['brands']}")
            st.markdown(f"**Hypoglycaemia risk:** {ins['hypo_risk']}")
            st.divider()
            col_a, col_b, col_c = st.columns(3)
            with col_a: st.metric("Starting dose", result["starting_dose"])
            with col_b: st.metric("FBG target", result["target_fbg"])
            with col_c: st.metric("Titration", result["titration"])
            st.info(f"⚠️ Safety rule: {result['note']}")
            ref_box(result["ref"])

    with calc_tab2:
        st.markdown("#### Basal-bolus MDI total daily dose estimate")
        col1, col2 = st.columns(2)
        with col1:
            wt_mdi    = st.number_input("Weight (kg)", 30.0, 200.0, 70.0, key="wt_mdi")
            hba1c_mdi = st.number_input("HbA1c (%)", 5.0, 20.0, 8.5, key="hba1c_mdi")
            dm_mdi    = st.selectbox("DM type", ["T1DM","T2DM","LADA","FCPD"], key="dm_mdi")
        if st.button("Calculate MDI doses", key="btn_mdi", type="primary"):
            result = calculate_insulin_dose(wt_mdi, hba1c_mdi, dm_mdi, "tdd_mdi")
            cols = st.columns(3)
            with cols[0]: st.metric("Estimated TDD", result["estimated_TDD"])
            with cols[1]: st.metric("Basal dose", result["basal_dose"])
            with cols[2]: st.metric("Bolus per meal", result["bolus_per_meal"])
            st.info(f"**Correction factor (ISF):** {result['correction_factor']}")
            st.info(f"**Insulin-to-carb ratio (ICR):** {result['ICR']}")
            st.caption(result["titration"])
            st.warning("⚠️ These are starting point estimates only. Adjust based on SMBG or CGM data. Individual variation is significant.")
            ref_box(result["ref"])

    with calc_tab3:
        st.markdown("#### Basal insulin titration guide")
        current_dose = st.number_input("Current basal insulin dose (units)", 2.0, 200.0, 20.0, key="cur_dose")
        if st.button("Get titration guidance", key="btn_tit", type="primary"):
            result = calculate_insulin_dose(0, 0, "T2DM", "basal_titration", current_dose)
            st.success(result["next_step"])
            st.error(result["reduce_if"])
            st.metric("FBG target", result["target_fbg"])
            ref_box(result["ref"])

    with calc_tab4:
        st.markdown("#### Insulin switching / conversion calculator")
        st.caption("Evidence-based dose conversion when switching insulin regimen. Always recheck glucose daily for the first 2 weeks after any switch.")

        switch_options = list(INSULIN_SWITCH_PROTOCOLS.keys())
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            switch_key = st.selectbox(
                "Select insulin switch",
                switch_options,
                key="switch_select",
                help="Choose the 'from → to' insulin pair"
            )
        with col_s2:
            current_dose_sw = st.number_input(
                "Current total daily dose (units/day)",
                min_value=2.0, max_value=400.0, value=20.0, step=2.0,
                key="cur_dose_sw"
            )

        if st.button("Calculate switch dose", key="btn_switch", type="primary"):
            sw = calculate_insulin_switch(
                from_insulin=switch_key.split(" → ")[0],
                to_insulin=switch_key.split(" → ")[1],
                current_dose_u=current_dose_sw,
            )
            if "error" in sw:
                st.error(sw["error"])
            else:
                st.success(f"**Switch:** {sw['from']} → {sw['to']}")
                col_sw1, col_sw2, col_sw3 = st.columns(3)
                with col_sw1:
                    st.metric("Current dose", sw["current_dose"])
                with col_sw2:
                    st.metric("New starting dose", sw["new_dose"], delta="See titration below")
                with col_sw3:
                    st.metric("Conversion rule", sw["conversion_rule"])

                st.divider()
                st.markdown(f"**🕐 Timing change:** {sw['timing_change']}")
                st.markdown(f"**📈 Titration after switch:** {sw['titration_after']}")
                st.info(f"**Rationale:** {sw['rationale']}")
                st.warning(f"**⚠️ Safety:** {sw['safety_note']}")
                st.markdown(f"**🔬 Monitoring:** {sw['monitoring']}")
                ref_box(sw["ref"])

        st.divider()
        st.markdown("##### Quick reference — all supported switches")
        for k, v in INSULIN_SWITCH_PROTOCOLS.items():
            with st.expander(f"**{k}**"):
                st.markdown(f"- **Conversion:** {v['conversion_rule']}")
                st.markdown(f"- **Timing:** {v['timing_change']}")
                st.markdown(f"- **Titration post-switch:** {v['titration_after']}")
                st.markdown(f"- **Rationale:** {v['rationale']}")
                ref_box(v["ref"])

    with calc_tab5:
        st.markdown("#### Basal insulin comparison (India)")
        st.markdown("| Property | Glargine U-100 | Glargine U-300 | Degludec U-100 | NPH |")
        st.markdown("|---|---|---|---|---|")
        st.markdown("| Duration | 20–24 hr | 24–36 hr | >42 hr | 12–18 hr |")
        st.markdown("| PK variability (CV) | ~84% (highest) | ~54% | ~20% (lowest) | Very high |")
        st.markdown("| Nocturnal hypo | Reference | Lower (titration) | Lowest (maintenance) | Highest |")
        st.markdown("| Dose flexibility | ± 2 hr | ± 3 hr | ≥ 8 hr any time | Fixed time |")
        st.markdown("| High dose suitability | Standard | Excellent (3× conc.) | U-200 available | — |")
        st.markdown("| CV safety trial | ORIGIN | None | DEVOTE (HR 0.60 severe hypo) | — |")
        st.markdown("| Indian brands | Lantus / Basalog / Glaritus | Toujeo | Tresiba | Insulatard / Insugen N |")
        st.markdown("| Approx cost | Medium (biosimilars Low) | High | Very High | Low |")
        ref_box("BRIGHT trial (Rosenstock 2018); CONCLUDE trial (Mathieu 2020); DEVOTE trial (Marso 2017); BEGIN trials; EDITION trials")


# ═══════════════════════════════════════════════════════════
# PAGE: ACUTE PROTOCOLS
# ═══════════════════════════════════════════════════════════
elif page == "🚨 Acute Protocols":
    st.markdown('<div class="section-hdr">🚨 Acute Hyperglycaemic Emergency Protocols</div>', unsafe_allow_html=True)

    acute_tab1, acute_tab2, acute_tab3 = st.tabs(["DKA", "HHS", "Hypoglycaemia"])

    def show_protocol(protocol: dict, show_checklist: bool = False):
        st.markdown(f"### {protocol['title']}")
        ref_box(protocol["ref"])
        st.divider()

        if "diagnostic_criteria" in protocol:
            st.markdown("#### Diagnostic criteria")
            for k, v in protocol["diagnostic_criteria"].items():
                if "Special" in k or "important" in k.lower():
                    warn_box(v)
                else:
                    st.markdown(f"- **{k}:** {v}")

        if "severity" in protocol:
            st.markdown("#### Severity classification")
            for k, v in protocol["severity"].items():
                col_icon = "🟡" if "Mild" in k else "🟠" if "Moderate" in k else "🔴"
                st.markdown(f"{col_icon} **{k}:** {v}")

        if "immediate_actions" in protocol:
            st.markdown("#### Immediate actions")
            for action in protocol["immediate_actions"]:
                st.markdown(f"- {action}")

        if "fluid_replacement" in protocol:
            st.markdown("#### Fluid replacement")
            for k, v in protocol["fluid_replacement"].items():
                if "caution" in k.lower():
                    warn_box(v)
                else:
                    st.markdown(f"- **{k}:** {v}")

        if "insulin" in protocol:
            st.markdown("#### Insulin")
            for k, v in protocol["insulin"].items():
                if "important" in k.lower() or "warning" in k.lower():
                    warn_box(v)
                else:
                    st.markdown(f"- **{k}:** {v}")

        if "potassium" in protocol:
            st.markdown("#### Potassium management")
            for k, v in protocol["potassium"].items():
                st.markdown(f"- **{k}:** {v}")

        if "anticoagulation" in protocol:
            st.info(f"**Anticoagulation:** {protocol['anticoagulation']['recommendation']}")

        if "conscious_patient" in protocol:
            st.markdown("#### Conscious patient")
            st.info(f"**Rule of 15:** {protocol['conscious_patient']['rule_of_15']}")
            st.markdown("**15g fast-acting carbohydrate sources (India):**")
            for src in protocol["conscious_patient"]["sources_15g"]:
                st.markdown(f"  - {src}")
            st.markdown(f"**After recovery:** {protocol['conscious_patient']['after_recovery']}")

        if "unconscious_patient" in protocol:
            st.markdown("#### Unconscious patient")
            st.error(f"**First line:** {protocol['unconscious_patient']['first_line']}")
            st.warning(f"**Alternative:** {protocol['unconscious_patient']['alternative']}")
            if "FCPD_warning" in protocol["unconscious_patient"]:
                warn_box(protocol["unconscious_patient"]["FCPD_warning"])

        if "recurrent_hypoglycaemia" in protocol:
            st.markdown("#### Recurrent hypoglycaemia — address causes")
            for item in protocol["recurrent_hypoglycaemia"]:
                st.markdown(f"  - {item}")

        if "monitoring" in protocol:
            st.info(f"**Monitoring:** {protocol['monitoring']}")

        if "resolution_criteria" in protocol:
            st.markdown("#### DKA resolution criteria (ALL must be met):")
            for c in protocol["resolution_criteria"]:
                st.markdown(f"  ✅ {c}")

        if "transition_to_sc" in protocol:
            st.markdown("#### Transition to subcutaneous insulin")
            for t in protocol["transition_to_sc"]:
                st.markdown(f"  - {t}")

        if show_checklist:
            st.divider()
            st.markdown("#### 🗒️ Bedside DKA Checklist")
            checklist = get_dka_checklist()
            for item in checklist:
                st.markdown(f'<div class="checklist-item">⬜ **[{item["time"]}]** {item["action"]}</div>', unsafe_allow_html=True)

    with acute_tab1:
        show_protocol(DKA_PROTOCOL, show_checklist=True)

    with acute_tab2:
        show_protocol(HHS_PROTOCOL)
        st.divider()
        st.markdown("#### Key differences: DKA vs HHS")
        st.markdown("| Feature | DKA | HHS |")
        st.markdown("|---|---|---|")
        st.markdown("| Onset | Hours | Days–weeks |")
        st.markdown("| Glucose | > 11 mmol/L | > 30 mmol/L |")
        st.markdown("| Osmolality | Mildly elevated | > 320 mOsm/kg |")
        st.markdown("| Ketosis | Significant | None / minimal |")
        st.markdown("| pH | < 7.3 | > 7.3 |")
        st.markdown("| Typical patient | T1DM, younger | T2DM, elderly |")
        st.markdown("| Fluid replacement | Aggressive | SLOWER |")
        st.markdown("| Insulin rate | 0.1 U/kg/hr | 0.05 U/kg/hr (half) |")
        st.markdown("| DVT risk | Moderate | VERY HIGH — anticoagulate |")

    with acute_tab3:
        show_protocol(HYPOGLYCAEMIA_PROTOCOL)


# ═══════════════════════════════════════════════════════════
# PAGE: TREATMENT TARGETS
# ═══════════════════════════════════════════════════════════
elif page == "🎯 Treatment Targets":
    st.markdown('<div class="section-hdr">🎯 Personalised Treatment Targets</div>', unsafe_allow_html=True)
    st.caption("Evidence-based glycaemic and cardiometabolic targets. Based on ADA Standards 2024 + RSSDI CPR 2023.")

    col1, col2 = st.columns(2)
    with col1:
        tgt_age   = st.number_input("Age (years)", 18, 100, 49, key="tgt_age")
        tgt_dm    = st.selectbox("DM type", ["T2DM","T1DM","GDM","LADA","FCPD"], key="tgt_dm")
        tgt_cv    = st.checkbox("Established CVD", key="tgt_cv")
        tgt_ckd   = st.checkbox("CKD (eGFR < 60)", key="tgt_ckd")
    with col2:
        tgt_frail = st.checkbox("Elderly / frail (≥ 70 years)", key="tgt_frail")
        tgt_hypo  = st.checkbox("Frequent hypoglycaemia history", key="tgt_hypo")
        tgt_preg  = st.checkbox("Pregnancy / GDM", key="tgt_preg")
        tgt_short = st.checkbox("Short duration, young, no complications", key="tgt_short")

    if st.button("Get personalised targets", type="primary", use_container_width=True, key="btn_tgt"):
        st.divider()

        # HbA1c target
        if tgt_preg:
            hba1c_target = "Fasting PG < 5.3 mmol/L (95 mg/dL) · 1-hr PPG < 7.8 mmol/L (140 mg/dL) · 2-hr PPG < 6.7 mmol/L (120 mg/dL)"
            hba1c_ref = "DIPSI 2020; ADA Standards 2024, Section 15"
        elif tgt_frail or tgt_hypo:
            hba1c_target = "< 8.0–8.5%"
            hba1c_ref = "ADA Standards 2024, Section 13; RSSDI CPR 2023"
        elif tgt_short and not tgt_cv:
            hba1c_target = "< 6.5% (if achievable without significant hypoglycaemia)"
            hba1c_ref = "ADA Standards 2024, Section 6"
        elif tgt_dm == "T1DM":
            hba1c_target = "< 7.0%"
            hba1c_ref = "ADA Standards 2024, Section 7"
        else:
            hba1c_target = "< 7.0%"
            hba1c_ref = "ADA Standards 2024, Section 6; RSSDI CPR 2023"

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("HbA1c target", hba1c_target)
        with col_b:
            st.metric("FBG target", "80–130 mg/dL (4.4–7.2 mmol/L)")
        with col_c:
            st.metric("2-hr PPG target", "< 180 mg/dL (10 mmol/L)")

        ref_box(hba1c_ref)
        st.divider()

        st.markdown("### Cardiometabolic targets")
        targets = [
            ("Blood pressure", "< 130/80 mmHg (ADA 2024)\n< 140/90 mmHg if not tolerated", "ADA Standards 2024, Section 10; RSSDI CPR 2023"),
            ("LDL-Cholesterol", f"{'< 55 mg/dL (very high risk with ASCVD)' if tgt_cv else '< 70 mg/dL (high risk T2DM)'}", "ADA Standards 2024, Section 10; ESC/EAS 2019"),
            ("Non-HDL Cholesterol", f"{'< 85 mg/dL' if tgt_cv else '< 100 mg/dL'}", "ADA Standards 2024, Section 10"),
            ("Triglycerides", "< 150 mg/dL", "ADA Standards 2024"),
            ("BMI / waist", "BMI < 23 kg/m² (Asian target) · Waist < 90 cm (M), < 80 cm (F)", "WHO 2004 Asia-Pacific; RSSDI CPR 2023"),
            ("Smoking", "Cessation — No safe level in DM", "ADA Standards 2024, Section 5"),
            ("Aspirin", "75–100 mg OD if established ASCVD (secondary prevention)" if tgt_cv else "Not routinely in primary prevention", "ADA Standards 2024, Section 10"),
            ("Statin", "High-intensity (Atorvastatin 40–80 mg)" if tgt_cv else "Moderate-intensity if age > 40 with risk factors", "ADA Standards 2024, Section 10"),
            ("ACE inhibitor / ARB", "If UACR > 30 mg/g or BP > 130/80 mmHg", "ADA Standards 2024, Section 11"),
            ("Foot exam", "Annual monofilament + ABI", "ADA Standards 2024, Section 12"),
            ("Dilated fundus exam", "Annual (T2DM); within 5 years then annual (T1DM)", "ADA Standards 2024, Section 12"),
        ]
        if tgt_dm == "T1DM":
            targets.append(("CGM / Time-in-Range", "> 70% time in 3.9–10 mmol/L range · TBR < 4%", "ATTD Consensus 2023; ADA Standards 2024, Section 7"))

        for target_name, target_val, ref in targets:
            with st.expander(f"**{target_name}:** {target_val.split(chr(10))[0]}"):
                st.markdown(target_val)
                ref_box(ref)


# ═══════════════════════════════════════════════════════════
# PAGE: DRUG REFERENCE
# ═══════════════════════════════════════════════════════════
elif page == "💉 Drug Reference":
    st.markdown('<div class="section-hdr">💉 Complete Drug Reference — Indian Brands</div>', unsafe_allow_html=True)

    drug_tab1, drug_tab2, drug_tab3, drug_tab4 = st.tabs(["Oral agents", "GLP-1 receptor agonists", "Insulins", "Combo injectables"])

    with drug_tab1:
        search_oral = st.text_input("Search oral drug", "", placeholder="e.g. Metformin, Glimepiride...")
        for name, drug in ORAL_DRUGS.items():
            if search_oral.lower() in name.lower() or not search_oral:
                with st.expander(f"**{name}** — {drug['class']}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**Mechanism:** {drug['mechanism']}")
                        st.markdown(f"**Starting dose:** {drug['start_dose']}")
                        st.markdown(f"**Max dose:** {drug['max_dose']}")
                        st.markdown(f"**HbA1c reduction:** {drug['HbA1c_reduction']}")
                        st.markdown(f"**Weight effect:** {drug['weight_effect']}")
                        st.markdown(f"**Hypoglycaemia risk:** {drug['hypo_risk']}")
                    with col_b:
                        st.markdown("**Indian brands:**")
                        for b in drug["brands"]:
                            st.markdown(f"  - {b['name']} ({b['company']}) — {b['cost']} cost")
                        if drug.get("CV_benefit"):
                            st.success(f"CV benefit: {drug['CV_benefit']}")
                        st.markdown("**Contraindications:**")
                        for c in drug["contraindications"]:
                            st.markdown(f"  ⚠️ {c}")
                    ref_box(drug["ref"])

    with drug_tab2:
        for name, drug in GLP1_DRUGS.items():
            with st.expander(f"**{name}** — {drug['class']}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Route:** {drug['route']}")
                    st.markdown(f"**Titration:** {drug['titration']}")
                    st.markdown(f"**Frequency:** {drug['frequency']}")
                    st.markdown(f"**HbA1c reduction:** {drug['HbA1c_reduction']}")
                    st.markdown(f"**Weight:** {drug['weight_effect']}")
                    st.success(f"CV benefit: {drug['CV_benefit']}")
                with col_b:
                    st.markdown("**Indian brands:**")
                    for b in drug["brands"]:
                        st.markdown(f"  - {b['name']} ({b['company']}) — {b['cost']} cost")
                    st.markdown("**Contraindications:**")
                    for c in drug["contraindications"]:
                        st.markdown(f"  ⚠️ {c}")
                ref_box(drug["ref"])

    with drug_tab3:
        for name, ins in INSULIN_DRUGS.items():
            with st.expander(f"**{name}** — {ins['type']}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Onset:** {ins['onset']} · **Peak:** {ins['peak']} · **Duration:** {ins['duration']}")
                    st.markdown(f"**Starting dose:** {ins['start']}")
                    st.markdown(f"**Titration:** {ins['titration']}")
                    st.markdown(f"**Frequency:** {ins['frequency']}")
                    st.markdown(f"**Variability (CV):** {ins['variability']}")
                    st.markdown(f"**Hypoglycaemia risk:** {ins['hypo_risk']}")
                with col_b:
                    st.markdown(f"**Best for:** {ins['best_for']}")
                    st.markdown("**Indian brands:**")
                    for b in ins["brands"]:
                        st.markdown(f"  - {b['name']} ({b['company']}, {b['cost']} cost, {b['type']})")
                ref_box(ins["ref"])

    with drug_tab4:
        st.markdown("Fixed-ratio GLP-1 RA + Basal insulin co-formulations. Combine the glucose-lowering power of basal insulin with GI-friendly weight-neutral or weight-positive titration. Preferred before full MDI when HbA1c ≥ 8.5% and BMI > 27.")
        st.divider()
        for name, combo in COMBO_INJECTABLES.items():
            with st.expander(f"**{name}** — {combo['class']}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Components:** {combo['components']}")
                    st.markdown(f"**Fixed ratio:** {combo['ratio']}")
                    st.markdown(f"**Dose range:** {combo['dose_range']}")
                with col_b:
                    st.markdown("**Indian brands:**")
                    for b in combo["brands"]:
                        st.markdown(f"  - {b['name']} ({b['company']}) — {b['cost']} cost")
                st.info("**Key advantage:** Single injection covers both basal insulin and GLP-1 RA benefits — simplifies regimen and improves adherence vs. two separate injections.")
                st.warning("⚠️ **Avoid** in: eGFR < 15, personal/family history of medullary thyroid cancer or MEN-2, pancreatitis, T1DM, FCPD (alpha-cell loss renders GLP-1 RA of limited benefit).")
                ref_box(combo["ref"])


if __name__ == "__main__":
    pass
