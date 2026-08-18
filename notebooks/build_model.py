import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect("../data/university.db")

query = """
SELECT
    e.student_id,
    e.program,
    e.full_time,
    e.cohort_term,
    d.first_gen,
    fa.pell_eligible,
    r.retained AS retained_year1
FROM enrollments e
JOIN students s ON e.student_id = s.student_id
JOIN demographics d ON s.demographic_id = d.demographic_id
LEFT JOIN (SELECT DISTINCT student_id, MAX(pell_eligible) as pell_eligible FROM financial_aid GROUP BY student_id) fa
    ON e.student_id = fa.student_id
JOIN retention r ON e.student_id = r.student_id AND r.checkpoint_year = 1
"""
df = pd.read_sql(query, conn)

# first-semester academic performance features
perf_query = """
SELECT
    student_id,
    SUM(credits_earned) * 1.0 / SUM(credits_attempted) AS credit_completion_rate,
    AVG(CASE grade WHEN 'A' THEN 4.0 WHEN 'B' THEN 3.0 WHEN 'C' THEN 2.0
                    WHEN 'D' THEN 1.0 WHEN 'F' THEN 0.0 END) AS first_sem_gpa,
    COUNT(*) AS n_courses_attempted
FROM course_attempts
GROUP BY student_id
"""
perf = pd.read_sql(perf_query, conn)

df = df.merge(perf, on="student_id", how="left")
df["first_sem_gpa"] = df["first_sem_gpa"].fillna(0)  # all-fail/withdraw students

# TARGET: did the student NOT retain to year 1? (1 = dropped out, what we want to predict)
df["at_risk"] = 1 - df["retained_year1"]

print(df.shape)
print(df["at_risk"].value_counts(normalize=True))
print(df.head())






from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (classification_report, precision_recall_curve,
                               roc_auc_score, confusion_matrix)

# one-hot encode categorical features
model_df = pd.get_dummies(
    df[["program", "full_time", "first_gen", "pell_eligible",
        "credit_completion_rate", "first_sem_gpa", "n_courses_attempted", "at_risk"]],
    columns=["program"], drop_first=True
)

X = model_df.drop(columns=["at_risk"])
y = model_df["at_risk"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# scale numeric features (logistic regression coefficients are only comparable when scaled)
scaler = StandardScaler()
numeric_cols = ["credit_completion_rate", "first_sem_gpa", "n_courses_attempted"]
X_train_scaled = X_train.copy()
X_test_scaled = X_test.copy()
X_train_scaled[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
X_test_scaled[numeric_cols] = scaler.transform(X_test[numeric_cols])

logreg = LogisticRegression(max_iter=1000, class_weight="balanced")
logreg.fit(X_train_scaled, y_train)

# THE INTERPRETABILITY PAYOFF: coefficients, sorted by impact
coefs = pd.DataFrame({
    "feature": X.columns,
    "coefficient": logreg.coef_[0]
}).sort_values("coefficient", key=abs, ascending=False)

print("\n=== LOGISTIC REGRESSION COEFFICIENTS (sorted by impact) ===")
print(coefs.to_string(index=False))

# convert to odds ratios -- much easier to explain in plain English
coefs["odds_ratio"] = np.exp(coefs["coefficient"])
print("\n=== ODDS RATIOS ===")
print(coefs[["feature", "odds_ratio"]].to_string(index=False))


y_pred = logreg.predict(X_test_scaled)
y_proba = logreg.predict_proba(X_test_scaled)[:, 1]

print("\n=== CLASSIFICATION REPORT (Logistic Regression) ===")
print(classification_report(y_test, y_pred, target_names=["Retained", "At-risk"]))

print("=== CONFUSION MATRIX ===")
print(confusion_matrix(y_test, y_pred))

print(f"\nROC-AUC: {roc_auc_score(y_test, y_proba):.3f}")





import xgboost as xgb
import shap
import matplotlib.pyplot as plt

xgb_model = xgb.XGBClassifier(
    n_estimators=100, max_depth=3, learning_rate=0.1,
    scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),  # handles imbalance, like class_weight did
    eval_metric="logloss", random_state=42
)
xgb_model.fit(X_train, y_train)  # note: XGBoost doesn't need scaled features

y_pred_xgb = xgb_model.predict(X_test)
y_proba_xgb = xgb_model.predict_proba(X_test)[:, 1]

print("\n=== CLASSIFICATION REPORT (XGBoost) ===")
print(classification_report(y_test, y_pred_xgb, target_names=["Retained", "At-risk"]))
print(f"ROC-AUC (XGBoost): {roc_auc_score(y_test, y_proba_xgb):.3f}")

# SHAP explains WHY the model made each prediction
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(X_test)

plt.figure()
shap.summary_plot(shap_values, X_test, show=False)
plt.tight_layout()
plt.savefig("../reports/shap_summary.png", dpi=150)
print("\nSaved SHAP summary plot to reports/shap_summary.png")

from sklearn.calibration import calibration_curve

prob_true, prob_pred = calibration_curve(y_test, y_proba, n_bins=5)  # logistic regression's probabilities

plt.figure(figsize=(6, 6))
plt.plot(prob_pred, prob_true, marker="o", label="Logistic Regression")
plt.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Perfectly calibrated")
plt.xlabel("Mean predicted probability")
plt.ylabel("Fraction of actual positives")
plt.title("Calibration Curve — At-Risk Prediction")
plt.legend()
plt.tight_layout()
plt.savefig("../reports/calibration_curve.png", dpi=150)
print("\nSaved calibration curve to reports/calibration_curve.png")