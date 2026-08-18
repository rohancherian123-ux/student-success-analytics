# Student Success & Retention Analysis
### A Fictional University Institutional Research Project

## Executive Summary

This analysis examined admissions, enrollment, academic performance, financial aid, and retention data for 3,000 applicants (1,076 enrolled students) across five entering cohorts (Fall 2019–Fall 2023) at a fictional university. The central finding: **first-generation status and first-semester academic performance are the strongest predictors of first-year attrition**, even after controlling for program and financial aid status. A logistic regression model built to flag at-risk students achieved 70% recall — correctly identifying 7 in 10 students who ultimately did not return — while remaining fully interpretable, a deliberate tradeoff favoring actionability over raw accuracy.

## Data & Methodology

A relational database was built with 10 tables (demographics, students, applications, enrollments, courses, course_attempts, financial_aid, retention, graduation, survey_responses), reflecting standard institutional research data structures. The dataset covers 5 entering cohorts, 6 academic programs, and includes course-level grade records, term-by-term financial aid, and annual retention checkpoints through graduation.

*Note: this is a synthetic dataset constructed to reflect realistic institutional patterns (acceptance rates, yield, demographic distributions) based on approximate national undergraduate benchmarks. Findings demonstrate methodology and analytical approach rather than real institutional outcomes.*

## Descriptive Findings

**Admissions & Enrollment**
- Acceptance rate: 63.5%–66.0% across cohorts, trending slightly upward
- Yield rate: 50.4%–59.3%, with no clear directional trend
- Enrollment was distributed relatively evenly across the 6 programs, with Education and Nursing drawing the largest cohorts in recent years

**Retention & Graduation**
- First-year retention: 84.3%–87.4% across cohorts
- Second-year retention: 68.6%–77.8%, showing a steeper decline than year 1 — consistent with national patterns where the second year is often a critical attrition point
- Graduation rate (for cohorts old enough to measure): 34.3%–37.1%, average time to degree 4.5–4.6 years

**Equity Analysis**
- **First-generation status**: 77.8% first-year retention vs. 89.1% for continuing-generation students — an 11.3 percentage point gap
- **Financial aid (Pell eligibility)**: no meaningful raw gap (84.8% vs. 85.8%), suggesting aid receipt alone does not predict attrition risk in this dataset
- **Race/ethnicity**: retention ranged from 83.9% to 94.7% across groups, with Hispanic and Asian students showing the lowest raw retention rates — though this gap narrows substantially once program and first-gen status are controlled for (see Predictive Model)
- **Program**: graduation rates ranged from 13.2% (Computer Science) to 24.5% (Nursing)

## Predictive Model: Identifying At-Risk Students

Two models were built to predict first-year attrition: a logistic regression (interpretable baseline) and XGBoost (a more flexible ensemble model), evaluated on precision, recall, and ROC-AUC rather than raw accuracy — because the dataset is imbalanced (85% retained / 15% at-risk), where accuracy alone rewards a trivial model that never flags anyone.

| Metric | Logistic Regression | XGBoost |
|---|---|---|
| At-risk recall | **0.70** | 0.40 |
| At-risk precision | 0.23 | 0.20 |
| ROC-AUC | **0.642** | 0.576 |

**Logistic regression was selected as the recommended model**, despite XGBoost's higher overall accuracy (0.67 vs. 0.61), because recall — correctly identifying students who will actually leave — is the more actionable metric for an early-intervention use case. Missing an at-risk student (a false negative) has a higher real-world cost than flagging a student who turns out fine (a false positive, which simply results in an unnecessary but low-cost advising check-in).

**Key drivers (logistic regression odds ratios):**
- First-generation status: OR = 2.31 — first-gen students have more than double the odds of attrition, controlling for program, aid, and academic performance
- Credit completion rate: OR = 0.78 — each one-standard-deviation increase in first-semester credit completion is associated with a ~22% reduction in attrition odds
- Financial aid (Pell eligibility): OR = 0.99 — negligible independent effect once other factors are controlled

**SHAP analysis** (run on the XGBoost model as a cross-check) independently confirmed first-generation status and credit completion rate as the two dominant predictors, with a notable nuance: the effect of low credit completion was highly variable across students — some low-completion students showed sharply elevated risk, while others were offset by other factors. This suggests credit completion is a necessary but not sufficient risk signal, and supports using it alongside first-gen status rather than in isolation.

**Headline finding:** Students completing fewer than 70% of attempted credits in their first semester showed a first-year retention rate of 73.3%, compared to 85.6% for students above that threshold — a 12.3 percentage point gap that persists as a significant, independent predictor even after controlling for program and financial aid status in the multivariate model.

## Model Limitations

- **Calibration**: the logistic regression model's predicted probabilities are not well-calibrated — at higher predicted risk levels (~85%), actual attrition rates were closer to 37%. This stems from using `class_weight="balanced"` to improve recall on an imbalanced dataset, which improves the model's *ranking* of relative risk but distorts its raw probability outputs. In a production setting, this would be corrected via post-hoc calibration (e.g., Platt scaling) before showing probability estimates to advisors; the model's relative risk *ranking* remains valid and usable in the meantime.
- **Sample size**: 1,076 enrolled students (269 in the test set) is modest for machine learning; results should be treated as directional rather than precise, and would benefit from a larger sample in a real institutional setting.
- **Synthetic data**: while designed to reflect realistic patterns, this dataset does not capture the full complexity of real student circumstances (e.g., life events, mental health, employment status) that a real institution's data would include.
- **Deliberate exclusion of race/ethnicity as a model feature**: to avoid encoding demographic categories directly into an automated risk score, race/ethnicity was excluded from the predictive model and instead analyzed separately as a descriptive equity metric. This is standard practice in responsible institutional research modeling.

## Recommendations

1. **Prioritize first-generation students for proactive advising outreach**, independent of financial aid status — the data suggests aid alone does not close this gap.
2. **Monitor first-semester credit completion as an early-warning signal**, with intervention triggered below the 70% threshold identified in this analysis.
3. **Investigate the second-year retention drop** (68.6%–77.8%, a steeper decline than year 1) as a distinct intervention point, separate from first-year onboarding efforts.
4. **Recalibrate model probabilities before deploying to advisors**, and treat current output as a relative risk ranking rather than a literal probability.