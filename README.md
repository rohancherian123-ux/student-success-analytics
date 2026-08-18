# Student Success & Retention Analytics

An end-to-end institutional research project: a relational database of admissions, enrollment, academic, and financial aid data for a fictional university, an interpretable machine learning model for identifying at-risk students, and a live analytics dashboard.

Built to demonstrate the full pipeline an institutional research / data analyst role requires — schema design, SQL, statistical modeling, and communicating findings to non-technical stakeholders.

## Key Finding

Students completing fewer than 70% of attempted credits in their first semester showed a first-year retention rate of 73.3%, compared to 85.6% for students above that threshold — a gap that remains significant even after controlling for program and financial aid status (logistic regression odds ratio: 0.78 per SD increase in completion rate). First-generation status was the strongest overall predictor (odds ratio: 2.31).

## What's in this repo

| Folder | Contents |
|---|---|
| `sql/schema.sql` | 10-table relational schema (students, applications, enrollments, courses, course_attempts, financial_aid, retention, graduation, survey_responses, demographics) |
| `sql/metrics.sql` | Acceptance rate, yield rate, retention, graduation rate, GPA, credit completion, and equity breakdowns by program/first-gen/aid status/demographic group |
| `notebooks/generate_data.py` | Synthetic data generator (3,000 applicants, 1,076 enrolled students, 5 cohorts) |
| `notebooks/build_model.py` | Logistic regression + XGBoost comparison, SHAP analysis, calibration curve, precision/recall evaluation |
| `dashboard.py` | Live Streamlit dashboard |
| `reports/findings_report.md` | Full written findings report |
| `data/university.db` | SQLite database |

## Modeling approach: interpretability over raw accuracy

Two models were compared for identifying at-risk students: logistic regression (interpretable) and XGBoost (higher capacity, less transparent).

| Metric | Logistic Regression | XGBoost |
|---|---|---|
| At-risk recall | **0.70** | 0.40 |
| At-risk precision | 0.23 | 0.20 |
| ROC-AUC | **0.642** | 0.576 |

Logistic regression was chosen despite XGBoost's higher raw accuracy, because recall — correctly identifying students who will actually leave — is the metric that matters for an early-intervention use case. SHAP analysis on the XGBoost model independently confirmed the same top predictors (first-generation status, first-semester credit completion), cross-validating the logistic regression findings with a second method.

The model's predicted probabilities were found to be poorly calibrated (a known tradeoff of using `class_weight="balanced"` to improve recall on imbalanced data) — this is documented as a limitation in the full report, along with the recommended fix.

## Dashboard

Run locally: