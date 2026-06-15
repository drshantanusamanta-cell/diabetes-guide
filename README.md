# Shantanu's Diabetes Treatment Assistant

A bedside clinical decision support web app for comprehensive management of Diabetes Mellitus and allied syndromes in the Indian clinical context.

**Zero ongoing cost · No API key required · 100% rule-based · Guideline-grounded**

---

## What it covers

- **Diagnosis classification** — T1DM, T2DM, LADA, MODY, FCPD, Lean T2DM, GDM, Secondary DM
  with probability ranking and LADA Clinical Score (Fourlanos 2006)
- **Investigation advisor** — condition-specific investigation lists with interpretation guidance
- **Lab interpreter** — HbA1c, C-peptide, HOMA-IR/β, eGFR+UACR, GAD65, Faecal Elastase
- **Treatment planner** — ADA-EASD Consensus 2022 + RSSDI CPR 2023 algorithm with Indian brand names
- **Insulin calculator** — basal initiation, MDI TDD, titration, insulin comparison table
- **Acute protocols** — DKA (JBDS 2023), HHS, Hypoglycaemia — with bedside checklists
- **Treatment targets** — personalised by DM type, age, CKD, CVD, pregnancy, frailty
- **Drug reference** — all OADs, GLP-1 RAs, insulins with Indian brands and evidence grades

---

## Guideline sources

| Guideline | Coverage |
|---|---|
| ADA Standards of Medical Care in Diabetes 2024 | Primary global guideline |
| RSSDI Clinical Practice Recommendations 2023 | Primary Indian guideline |
| ICMR T2DM Guidelines 2018 | Indian pharmacotherapy |
| DIPSI 2020 | Gestational Diabetes (Indian) |
| JBDS DKA/HHS Guidelines 2023 | Acute protocols |
| ADA-EASD Consensus Report 2022 | Hyperglycaemia algorithm |
| ATTD Consensus 2023 | CGM / Time-in-Range |
| Matthews DR et al., Diabetologia 1985 | HOMA model |
| Fourlanos S et al., Diabetes Care 2006 | LADA Clinical Score |
| Mohan V, Pancreatology 2012 | FCPD (Indian data) |

---

## Project structure

All files go in the **root of your GitHub repository** (no subfolders needed):

```
your-repo/
├── app.py            ← Main Streamlit UI (8 pages)
├── data.py           ← Master knowledge base (drugs, insulins, investigations)
├── diagnostic.py     ← Diagnosis classification engine
├── treatment.py      ← Treatment planner + insulin calculator
├── interpreter.py    ← Lab result interpreter
├── acute.py          ← DKA / HHS / Hypoglycaemia protocols
├── __init__.py       ← Package marker
├── requirements.txt
└── README.md
```

> ⚠️ Do **not** put the .py files inside a subfolder — upload them all flat to the repo root.

---

## Deploy to Streamlit Community Cloud (free, ~5 minutes)

### What you need
- A free GitHub account — [github.com](https://github.com)
- A free Streamlit Community Cloud account — [share.streamlit.io](https://share.streamlit.io)

### Step 1 — Put the code on GitHub

1. Go to [github.com](https://github.com) → Click the green **New** button
2. Name your repository (e.g., `diabetes-dss`), set it to **Public**, click **Create repository**
3. On the next screen, click **"uploading an existing file"**
4. Drag the entire `diabetes_dss` folder contents into the upload window
   - Make sure to include the `modules/` subfolder and `.streamlit/` subfolder
5. Click **Commit changes**

### Step 2 — Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) → Sign in with GitHub
2. Click **New app**
3. Under "Repository", select your `diabetes-dss` repo
4. Set **Branch** to `main`
5. Set **Main file path** to: `app.py`
6. Click **Deploy!** — your app will be live in about 2 minutes

### Step 3 — Share

Copy the URL Streamlit gives you (e.g., `https://yourname-diabetes-dss.streamlit.app`).
Open it on any device — desktop, tablet, or mobile — no installation needed.

---

## Run locally (optional)

```bash
# 1. Install Python 3.9+ if needed: python.org/downloads

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`

---

## No API key needed

This app uses **pure rule-based logic** — all clinical recommendations are hard-coded from
guideline evidence. There is no OpenAI, Anthropic, or any other API call. The app runs
completely offline after loading, and costs nothing to run permanently on Streamlit Community Cloud.

---

## Clinical disclaimer

This tool is designed for **clinical decision support** — it assists but does not replace clinical
judgement. All recommendations must be interpreted in the context of the individual patient.
The tool is not a substitute for specialist assessment and does not constitute medical advice.

Built for: **Dr Shantanu Samanta**  
Version: 1.0 · June 2026
