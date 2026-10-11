# Model Architecture and Evaluation

This document describes the classification model, training pipeline, evaluation metrics, calibration, and readiness decision rules for SkillGraph.

## 1. Feature Representation

The model accepts candidate skill profiles as binary multi-hot vectors.

- Vocabulary size: 800 canonical skills from `artifacts/skill_vocab.json`.
- Vector width: 800 features (`n_features_in_ = 800`).
- Vector encoding: Binary indicator where index `i` equals 1 if the corresponding canonical skill is present, and 0 otherwise (`ml/features.py`).
- Dense conversion during inference: Multi-hot arrays are evaluated directly via matrix multiplication against exported weights in `artifacts/model.json`.

## 2. Data Augmentation

Job postings frequently omit skills that applicants possess, and applicants enter short skill profiles with 2 to 4 items. Training purely on full job descriptions biased earlier models against short inputs.

- Augmentation logic: `ml/augment.py` creates `n_copies = 2` additional training rows per posting.
- Subsampling: For each copy, a random subset of skills with size between 2 and `len(skills) - 1` is retained.
- Raw training rows: 8,941 postings from `artifacts/metrics.json`.
- Augmented training rows: 26,039 rows (`artifacts/metrics.json`).
- Validation and test splits were not augmented to preserve unbiased evaluation.

## 3. Dataset Splitting

The raw dataset contains no usable posting dates; relative date strings such as "6 Days Ago" prevented temporal splitting (`data/raw.parquet`).

- Split method: Stratified random split with seed 42 (`ml/train.py`).
- Split ratios: 70% train (8,941 postings), 15% validation (1,916 postings), 15% test (1,917 postings).
- Classes: 10 role families from `taxonomy/role_families.csv` (DevOps / Cloud, QA / Test, ERP / Enterprise, Data / BI Analyst, Full Stack, Backend, Data Science / ML, Support / IT Ops, Frontend, Mobile).

## 4. Model Selection and the 3-Point Rule

Two model architectures were evaluated on identical train and validation splits: Multi-class Logistic Regression with L2 regularization (`C=1.0`, `solver='lbfgs'`) and LightGBM (`n_estimators=100`, `learning_rate=0.05`).

From `artifacts/metrics.json`:

| Model | Val Macro F1 | Test Macro F1 | Test Accuracy | Top-3 Accuracy |
|---|---|---|---|---|
| Logistic Regression | 0.7435 | 0.7499 | 0.7527 | 0.9254 |
| LightGBM | 0.7532 | 0.7648 | 0.7632 | 0.9306 |

The engineering rule in `ml/train.py` required tree ensembles to exceed linear model test macro F1 by at least 3.0 percentage points (+0.0300) to justify added runtime complexity.

- Observed test macro F1 delta: 0.7648 - 0.7499 = 0.0149 (+1.49 percentage points).
- Decision: Because 0.0149 is below the 0.0300 threshold, Logistic Regression was selected for production.
- Production rationale: Logistic Regression exported to a 77 KB JSON payload (`artifacts/model.json`), required only NumPy for inference, eliminated C++ compilation on Vercel Serverless, and kept cold start latency at 2,521.1 ms.

## 5. Evaluation Metrics

Metrics were computed on the held-out test split of 1,917 postings (`artifacts/metrics.json`):

- Overall Accuracy: 0.7527 (75.27%)
- Macro F1: 0.7499 (74.99%)
- Top-3 Accuracy: 0.9254 (92.54%)
- Majority Baseline Accuracy: 0.1774 (17.74%, DevOps / Cloud)
- Short-Input Test Macro F1: 0.6116 (measured on synthetic 2 to 3 skill test inputs)

### Per-Class Test Performance

| Role Family | Precision | Recall | F1 Score | Support |
|---|---|---|---|---|
| Backend | 0.7292 | 0.7330 | 0.7311 | 191 |
| Data / BI Analyst | 0.7107 | 0.8390 | 0.7696 | 205 |
| Data Science / ML | 0.7802 | 0.7889 | 0.7845 | 180 |
| DevOps / Cloud | 0.7579 | 0.5618 | 0.6453 | 340 |
| ERP / Enterprise | 0.8622 | 0.8700 | 0.8661 | 223 |
| Frontend | 0.6129 | 0.6496 | 0.6307 | 117 |
| Full Stack | 0.6742 | 0.7680 | 0.7181 | 194 |
| Mobile | 0.7333 | 0.8462 | 0.7857 | 65 |
| QA / Test | 0.8843 | 0.8807 | 0.8825 | 243 |
| Support / IT Ops | 0.6790 | 0.6918 | 0.6854 | 159 |

## 6. Calibration

Model probability outputs feed user readiness percentages directly, requiring calibration against observed true frequencies.

From `artifacts/metrics.json`:
- Pooled One-vs-Rest Expected Calibration Error (ECE): 0.0120
- Top-Label Expected Calibration Error: 0.0614
- Calibration curve behavior: Observed probabilities track predicted probabilities closely between 0.10 and 0.85. The top bin (predicted probability > 0.90) exhibits slight overconfidence (0.976 predicted vs 0.911 true).

## 7. Readiness Decision Rules

Readiness is evaluated by combining predicted role probability with skill coverage against the target role top 20 skills (`ml/predict.py`).

```python
def band_for(p: float, coverage: float = 1.0) -> str:
    if p >= 0.60:
        p_band = 2  # Ready
    elif p >= 0.30:
        p_band = 1  # Close
    else:
        p_band = 0  # Not yet

    if coverage >= 0.20:
        c_band = 2
    elif coverage >= 0.10:
        c_band = 1
    else:
        c_band = 0

    final_band = min(p_band, c_band)
    if final_band == 2: return "Ready"
    elif final_band == 1: return "Close"
    return "Not yet"
```

The final readiness band is the minimum of the probability band and the coverage band. Even if predicted probability reaches 0.99, an applicant with coverage below 0.20 receives Close rather than Ready.

## 8. Persona 1 Instability Note

In data-v4, Persona 1 (`python, sql, pandas` targeting `Data / BI Analyst`) shifted top role match from Data / BI Analyst (0.4313 Close in v3) to Backend (0.4906, with Data / BI Analyst at 0.1080 Not yet).

- Cause: `pandas` appeared in only 36 of 8,941 training postings (0.40%).
- Weight shift: In `artifacts/model.json`, the coefficient for `pandas` on Data / BI Analyst shifted from +0.8412 to -0.7813, while Backend retained +2.0626.
- Decision: Documented as a known limitation of low-frequency skill tokens under L2 regularized retraining.
