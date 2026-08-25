# GuidelineForge

GuidelineForge is a complete, production-grade annotation quality assurance and inter-annotator agreement (IAA) program. It instruments the entire lifecycle of dataset quality: designing guidelines, measuring multi-rater disagreement, diagnosing root-cause instruction ambiguities, shipping targeted guideline revisions, and executing tiered QA with independent audit verification.

The program evaluates a customer-support ticket corpus across two classification tasks: an 8-class macro-intent taxonomy and an ordinal 3-level sentiment scale. The dataset consists of 600 tickets evaluated across two full rounds by three annotators, using custom-implemented statistical metrics calibrated against standard references.

---

## Key Features

- **From-Scratch Metric Implementation**: Ground-up implementations of Cohen's Kappa, Fleiss' Kappa, Krippendorff's Alpha (nominal and ordinal distances), and paired percentile bootstrap confidence intervals without external library dependencies for core calculations.
- **Strict Metric Calibration**: Every metric calculation is verified in self-tests against scikit-learn, NLTK, and the canonical Fleiss (1971) 0.210 reference value.
- **Evidence-Driven Guideline Revision**: A controlled two-round study demonstrating how targeted instruction adjustments (precedence hierarchies, sarcasm overrides, polite-failure detection) resolve systematic label errors where annotator retraining fails.
- **Three-Tier Quality Architecture**: Industry-standard QA workflow combining blind multi-annotator overlap (Tier 1), 100% senior review of production labels with rule-based rework (Tier 2), and stratified spot-check auditing against embedded gold standards (Tier 3).
- **Sub-Slice Disagreement Diagnostics**: Granular evaluation isolating planted ambiguity families (sarcasm, mixed intents, polite complaints, tone traps, short fragments) that aggregate statistics obscure.
- **Dual Pipeline Operation**: Deterministic, seeded persona simulation engines for instant reproducibility, paired with full support for importing live human annotations via Label Studio or CSV sheets.
- **Multiple Reporting Interfaces**: An offline, self-contained single-file HTML dashboard, an interactive Streamlit dashboard, an automated Matplotlib PDF report generator, and an executable Jupyter analysis notebook.

---

## Results Summary

| Metric | Round 1 (Guidelines v1.0) | Round 2 (Guidelines v2.0) | Target Threshold |
|---|:---:|:---:|:---:|
| Fleiss' Kappa (Intent, 180-ticket overlap) | 0.835 [CI 0.780, 0.884] | **0.955** [CI 0.929, 0.978] | >= 0.800 |
| Fleiss' Kappa (Sentiment, nominal) | 0.668 [CI 0.589, 0.742] | **0.878** [CI 0.825, 0.926] | >= 0.800 |
| Krippendorff's Alpha (Sentiment, ordinal) | 0.610 | **0.885** | >= 0.800 |
| Paired Delta Kappa (Intent, identical items) | Baseline | **+0.120** [95% CI: 0.076, 0.168] | > 0.000 |
| Mixed-Intent Slice Kappa | 0.030 (chance level) | **0.870** | >= 0.800 |
| Sarcasm Slice Unanimity (Sentiment) | 30.0% | **80.0%** | >= 75.0% |
| Best Single-Annotator Gold Intent Accuracy | 88.9% | **98.6%** | >= 90.0% |
| Final Post-QA Gold Accuracy (Intent / Sentiment) | N/A | **100.0% / 95.8%** | >= 90.0% |
| Tier-2 Production Rework Rate | N/A | **4.7%** (28 / 600) | < 15.0% |
| Tier-3 Audit Pass Rate (n=117 stratified sample) | N/A | **100.0%** | >= 95.0% |

### Core Findings

1. **Aggregates Hide Systematic Failure Modes**: Round 1 overall intent agreement (0.835) met conventional thresholds, yet mixed-intent tickets exhibited chance-level agreement (0.030) and cancellation had a per-class Kappa of 0.580. Sliced agreement metrics are required to pinpoint instruction deficiencies.
2. **Consensus Does Not Equal Correctness**: On anger-framed requests (for example, "Your refund policy is terrible, refund my card now"), annotators achieved 75% unanimous agreement in Round 1 while achieving only 25% accuracy against design gold. All raters consistently applied a flawed "tone-first" rule. Only embedded gold standards detect unanimous error.
3. **Instruction Quality Outranks Rater Diligence**: The most literal annotator achieved the lowest Round 1 gold accuracy because diligence executes flawed instructions without deviation. Updating the guidelines to v2.0 (introducing precedence order and removing tone traps) resolved the discrepancy without changing personnel.

---

## Tech Stack

- **Language**: Python 3.10+
- **Data & Numerical Computation**: NumPy, pandas
- **Visualization & Reporting**: Matplotlib, ReportLab (optional), Streamlit
- **Notebook & Validation**: Jupyter, nbformat, nbclient, scikit-learn, NLTK
- **Frontend / Dashboard**: Modern semantic HTML5, CSS custom properties, vanilla JavaScript (zero external CDN or runtime dependencies)

---

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git (optional, for version control)

---

## Getting Started

### 1. Environment Setup

Create and activate an isolated virtual environment:

```bash
python -m venv .venv

# On Linux / macOS:
source .venv/bin/activate

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
.venv\Scripts\activate.bat
```

### 2. Install Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Run the Complete Pipeline

Execute the end-to-end data preparation, simulation, validation, and figure generation workflow:

```bash
# Set PYTHONPATH to include src/
# On Linux / macOS:
export PYTHONPATH=src

# On Windows (PowerShell):
$env:PYTHONPATH="src"

# On Windows (Command Prompt):
set PYTHONPATH=src

# Step A: Build the 600-ticket corpus and gold dataset
python src/make_dataset.py

# Step B: Run mathematical self-tests on the agreement library
python src/agreement.py

# Step C: Simulate multi-round annotation, tiered QA, and metric export
python src/simulate_pipeline.py

# Step D: Render visual analytics figures
python src/make_figures.py

# Step E: Generate the self-contained offline dashboard
python src/make_static_dashboard.py

# Step F: Generate the comprehensive publication PDF report
python src/make_report.py
```

### 4. Interactive Exploration

Launch the dashboards or notebook interfaces:

```bash
# Launch interactive Streamlit application
streamlit run qa-dashboard/streamlit_app.py

# Build and execute the Jupyter analysis notebook
python src/build_notebook.py
jupyter notebook notebooks/agreement_analysis.ipynb

# Alternatively, view the standalone static dashboard in any browser:
# Open file: qa-dashboard/static_dashboard.html
```

---

## Repository Structure

```
guidelineforge/
├── .gitignore                           # Comprehensive ignore rules
├── LICENSE                              # MIT License with third-party dataset attribution
├── README.md                            # Comprehensive program documentation
├── CASE_STUDY.md                        # High-level narrative and business findings
├── QA_PROCESS.md                        # Detailed tiered review and audit workflow documentation
├── requirements.txt                     # Pinned project dependencies
├── report.pdf                           # Generated multi-page analytical report
│
├── guidelines/
│   ├── annotation_guidelines_v1.0.md    # Initial guidelines containing deliberate edge-case flaws
│   ├── annotation_guidelines_v2.0.md    # Revised guidelines resolving ambiguity patterns
│   ├── CHANGELOG.md                     # Audit log connecting metric failures to specific rule changes
│   └── calibration_notes.md             # Calibration meeting transcripts and recertification records
│
├── data/
│   ├── raw/
│   │   ├── bitext_raw.csv               # Public source support-ticket corpus (26.8k records)
│   │   └── support_tickets.csv          # Formatted 600-ticket dataset with strata & ambiguity tags
│   ├── gold_set.csv                     # 72 adjudicated gold-standard reference items
│   ├── adjudicated_labels.csv           # Full corpus final ground-truth labels
│   ├── qa_audit_results.csv             # Tier-3 audit verification outcomes
│   ├── label_studio_import.json         # Ready-to-import tasks for Label Studio setups
│   ├── annotations/
│   │   ├── annotations_round1.csv       # Multi-rater labels under v1.0 guidelines
│   │   └── annotations_round2.csv       # Multi-rater labels under v2.0 guidelines
│   └── for_peer_annotation/
│       ├── README.md                    # Instructions for running live human annotation studies
│       └── annotator_sheet_{1,2,3}.csv  # Blank sheets for human rater data collection
│
├── src/
│   ├── agreement.py                     # Metric calculation engine with built-in validation
│   ├── annotators.py                    # Behavioral persona simulation engines
│   ├── build_notebook.py                # Automated Jupyter notebook constructor and runner
│   ├── chart_style.py                   # Unified typography and palette definitions
│   ├── import_peer_labels.py            # Ingestion adapter for real human annotation sheets
│   ├── label_studio_adapter.py          # Export and import transformations for Label Studio
│   ├── make_dataset.py                  # Stratified sampling and ambiguity injection script
│   ├── make_figures.py                  # Matplotlib rendering script for analytical figures
│   ├── make_report.py                   # PDF generation engine
│   ├── make_static_dashboard.py         # Static HTML dashboard generator
│   ├── simulate_pipeline.py             # Complete annotation lifecycle and QA orchestrator
│   └── text_features.py                 # Deterministic lexical and syntactic cue extractor
│
├── notebooks/
│   └── agreement_analysis.ipynb         # Executed Jupyter analysis notebook
│
├── qa-dashboard/
│   ├── static_dashboard.html            # Standalone editorial report and evidence explorer
│   └── streamlit_app.py                 # Live exploratory QA dashboard
│
└── results/
    ├── metrics.json                     # Complete serialized metric dictionary
    ├── metrics_summary.csv              # Tabular comparison across rounds
    ├── timeline.csv                     # Daily production and throughput tracking
    └── figures/                         # Rendered chart PNG outputs
```

---

## Architecture & Data Flow

```
[Bitext Public Corpus] + [Planted Ambiguities (80)]
                   │
                   ▼
       [support_tickets.csv (600)]
                   │
       ┌───────────┴───────────┐
       ▼                       ▼
[Round 1: v1.0 Rules]   [Kickoff Calibration (48)]
  - 180 Triple Overlap    - Gate check (>= 85%)
  - 420 Single Production - Retrain failing raters
       │
       ▼
[Disagreement Analysis & Slicing]
  - Identify tone traps (R4 failure)
  - Identify mixed-intent collapse (kappa = 0.03)
  - Formulate v2.0 Precedence & Sarcasm Rules
       │
       ▼
[Round 2: v2.0 Rules] + [Recertification Gate (>= 85%)]
  - 180 Triple Overlap (kappa: 0.835 -> 0.955)
  - 420 Single Production
       │
       ▼
[Tiered Quality Assurance]
  - Tier 1: Multi-rater overlap consensus
  - Tier 2: Senior review (100% prod + non-unanimous overlap) -> 4.7% rework
  - Tier 3: Stratified spot audit (n=117) -> 100% pass rate
       │
       ▼
[Final Label Delivery] -> 100.0% Intent Gold Acc / 95.8% Sentiment Gold Acc
```

---

## Classification Taxonomy & Slices

### Intent Classes (8 Categories)

1. `refund_request`: Demands or inquiries regarding monetary refunds or charge reversals.
2. `cancellation`: Requests to cancel subscriptions, bookings, or active recurring orders.
3. `billing_payments`: Inquiries regarding invoices, payment methods, receipts, or charges.
4. `shipping_delivery`: Delivery tracking, delays, courier updates, or address modifications.
5. `order_changes`: Requests to edit existing order items, quantities, or configurations.
6. `account_access`: Login problems, password resets, account locking, or MFA issues.
7. `feedback_complaints`: General feedback, praise, or grievances without direct transactional remedy requests.
8. `other_contact`: General policy inquiries, operational questions, or unclassified contact.

### Sentiment Scale (Ordinal 3-Level)

- `negative` (Rank 0): Frustration, distress, unmet expectations, or reported service failure.
- `neutral` (Rank 1): Informational requests, standard updates, or matter-of-fact queries.
- `positive` (Rank 2): Expressed gratitude, praise, or satisfaction with resolution.

### Ambiguity Slices (Deliberate Stress Tests)

- **Tone Traps (16 items)**: Severe frustration phrasing wrapped around clear transactional requests (for example, "This service is garbage, give me my money back").
- **Mixed Intents (16 items)**: Co-occurrence of multiple action requests (for example, cancellation accompanied by refund demands).
- **Polite Complaints (16 items)**: Courteously worded messages describing functional failures.
- **Sarcasm & Contrast (16 items)**: Positive surface lexicons expressing negative outcomes (for example, "Great job delivering my shattered package").
- **Short Fragments (16 items)**: Concise, context-sparse queries consisting of six or fewer words.

---

## Statistical Methodology

All mathematical formulations are coded in `src/agreement.py` from first principles.

### 1. Cohen's Kappa (Two Raters, Nominal)

Measures chance-corrected agreement between two raters:

$$\kappa = \frac{P_o - P_e}{1 - P_e}$$

Where $P_o$ is the observed proportion of agreement, and $P_e$ is the expected agreement by chance based on marginal rating frequencies:

$$P_e = \sum_{k} p_{1,k} \cdot p_{2,k}$$

### 2. Fleiss' Kappa (M Raters, Fixed Setup)

Measures overall inter-rater reliability across $N$ subjects and $M$ raters per subject:

$$P_i = \frac{1}{M(M-1)} \left( \sum_{j=1}^{K} n_{ij}^2 - M \right)$$

$$\bar{P} = \frac{1}{N} \sum_{i=1}^{N} P_i, \quad p_j = \frac{1}{NM} \sum_{i=1}^{N} n_{ij}, \quad P_e = \sum_{j=1}^{K} p_j^2$$

$$\kappa_{\text{Fleiss}} = \frac{\bar{P} - P_e}{1 - P_e}$$

### 3. Krippendorff's Alpha (Nominal and Ordinal Distance)

Calculated via coincidence matrices $O_{ck}$:

$$\alpha = 1 - \frac{D_o}{D_e}$$

- **Nominal Metric**: Binary delta $\delta(c, k) = 0$ if $c=k$, else $1$.
- **Ordinal Metric**: Rank-based squared metric:

$$\delta(c, k) = \left( \frac{\text{rank}(c) - \text{rank}(k)}{K - 1} \right)^2$$

This penalizes opposing polar assignments (`negative` vs. `positive`) more heavily than adjacent assignments (`negative` vs. `neutral`).

### 4. Paired Percentile Bootstrap Confidence Intervals

Rather than assuming normal approximations, uncertainty bounds are established by drawing 500 bootstrap column samples with replacement from the identical 180 overlap items across both rounds. A paired difference $\Delta\kappa = \kappa_{R2} - \kappa_{R1}$ whose 95% confidence interval strictly excludes zero confirms that observed gains are statistically significant.

---

## Detailed Script Reference

| Script | Purpose | Primary Output |
|---|---|---|
| `src/make_dataset.py` | Samples from raw Bitext data, injects ambiguity families, and builds stratified splits. | `data/raw/support_tickets.csv`, `data/gold_set.csv` |
| `src/agreement.py` | Calculates IAA metrics and executes built-in verification tests. | Metric calculation functions & CLI test logs |
| `src/annotators.py` | Defines behavioral profiles and decision logic for simulated personas. | Persona decision models |
| `src/simulate_pipeline.py` | Executes multi-round labeling, computes metrics, and runs QA tiers. | `data/annotations/*.csv`, `results/metrics.json` |
| `src/make_figures.py` | Generates publication-ready Matplotlib visualizations. | `results/figures/*.png` |
| `src/make_static_dashboard.py` | Assembles the self-contained HTML dashboard with embedded base64 assets. | `qa-dashboard/static_dashboard.html` |
| `src/make_report.py` | Compiles a multi-page analytical PDF report. | `report.pdf` |
| `src/build_notebook.py` | Generates and executes the end-to-end Jupyter analysis notebook. | `notebooks/agreement_analysis.ipynb` |
| `src/import_peer_labels.py` | Ingests real human rater CSV sheets for live benchmarking. | Overwritten `data/annotations/*.csv` |
| `src/label_studio_adapter.py` | Converts project data to and from Label Studio format. | `data/label_studio_import.json` |
| `src/text_features.py` | Extracts linguistic markers, regex patterns, and syntactic cues. | Feature extraction dictionary |
| `src/chart_style.py` | Provides unified palettes, styling parameters, and fonts. | Visual styling constants |

---

## Quality Assurance Workflow

The project implements a three-tier quality architecture modeled after enterprise data operations:

```
Pass 1: Tier 1 (Annotators)
  └─ 600 tickets labeled per round
  └─ 180 blind triple overlap + 420 rotated single production

Pass 2: Tier 2 (Senior Review & Rework)
  └─ 100% review of production single-pass labels
  └─ Review of all non-unanimous overlap cases (29 items in Round 2)
  └─ Every edit cites an explicit rule (e.g. R1 Precedence, R8 Sarcasm)
  └─ Observed rework rate: 4.7% (28 items) vs. 15-20% allowable ceiling

Pass 3: Tier 3 (Auditor Verification)
  └─ Stratified sample of 117 final labels (20% of dataset)
  └─ 21 verified against design gold; 96 re-derived independently from v2.0 rules
  └─ Observed pass rate: 100.0%
```

---

## Data Provenance & Honest Simulation Disclosure

- **Base Corpus**: 520 of the 600 tickets originate from the public [Bitext Customer Support LLM Dataset](https://github.com/bitext/customer-support-llm-chatbot-training-dataset) (CC0 license). Bitext source intent labels are mapped to the 8-class taxonomy to serve as design ground truth; annotators never see these labels.
- **Planted Stress Tests**: 80 tickets were manually authored across five defined ambiguity families to provide measurable edge cases that clean academic corpora obscure.
- **Simulated Raters**: The three annotators (Priya: careful literalist; Marcus: empathetic reader; Tom: fast skimmer) are deterministic, seeded simulation engines operating strictly on observable textual features. This simulation structure allows end-to-end reproducibility of every figure and statistic in the repository.
- **Live Human Rater Support**: The entire pipeline can be run with live human annotators by using the template sheets in `data/for_peer_annotation/` and executing `src/import_peer_labels.py`.

---

## Known Limitations & Next Steps

1. **Statement-Form Policy Inquiries**: Declarative questions regarding guarantees or terms lacking question marks (for example, ticket `GF-0249`: "i cannot check ur money back guarantee") may bypass the policy gate and misroute to `refund_request`. This is slated for resolution in guidelines v2.1.
2. **Lexical Typos**: OOV spelling variations (such as "acvount" or "resititution") currently route to `other_contact`. Incorporating character-level Levenshtein distance matching would recover these cases.
3. **Short Fragment Tone**: Sentiment agreement on sub-6-word fragments improved from Kappa -0.05 to 0.60, but remains below the 0.80 threshold. This requires expanding the worked examples section in the guidelines.
4. **Single-Pass Gold Annotation**: Gold sentiment labels for organic tickets currently rely on a single expert annotation pass; adding a secondary independent expert review would further harden the evaluation baseline.

---

## License & Attribution

- **Project Code and Documentation**: Licensed under the [MIT License](file:///c:/Users/INDIA%20TECHNOLOGY/Documents/guidelineforge/LICENSE).
- **Bitext Dataset**: Copyright (c) Bitext Innovations. Used under its published research license.
