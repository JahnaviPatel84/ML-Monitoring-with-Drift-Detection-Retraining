# -*- coding: utf-8 -*-
"""drift_detection.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1us81mG_fjENu7bnWpidc2fvHQZISSVDP
"""

# 1. IMPORTS + DRIFT FUNCTIONS

import pandas as pd
import numpy as np
from scipy.stats import ks_2samp

# Population Stability Index (PSI)
def population_stability_index(expected, actual, bins=10):
    def scale(series): return pd.cut(series, bins=bins, labels=False)

    expected_binned = scale(expected)
    actual_binned = scale(actual)

    expected_dist = pd.Series(expected_binned).value_counts(normalize=True, sort=False)
    actual_dist = pd.Series(actual_binned).value_counts(normalize=True, sort=False)

    psi = np.sum((expected_dist - actual_dist) * np.log((expected_dist + 1e-6) / (actual_dist + 1e-6)))
    return psi

# Drift check using PSI and KS test
def check_drift(ref_df, new_df, threshold=0.2):
    report = {}
    for col in ref_df.columns:
        if col == "Churn":
            continue
        psi = population_stability_index(ref_df[col], new_df[col])
        ks_pval = ks_2samp(ref_df[col], new_df[col]).pvalue
        report[col] = {
            "PSI": round(psi, 3),
            "KS_p": round(ks_pval, 3),
            "Drift": psi > threshold
        }
    return pd.DataFrame(report).T

# 2. LOAD REFERENCE DATA
ref_df = pd.read_csv("processed_telco.csv")
print(f"Reference dataset shape: {ref_df.shape}")

# SIMULATE DRIFT BY FLIPPING 'SeniorCitizen'
new_df = ref_df.copy()
if 'SeniorCitizen' in new_df.columns:
    new_df['SeniorCitizen'] = 1 - new_df['SeniorCitizen']
    print("Simulated drift by flipping 'SeniorCitizen' values.")
else:
    print("'SeniorCitizen' column not found!")

# 4. RUN DRIFT DETECTION
drift_report = check_drift(ref_df, new_df)
drift_report_sorted = drift_report.sort_values("PSI", ascending=False)

print("Drift Detection Report:")
display(drift_report_sorted)

# 5. CHECK FOR SIGNIFICANT DRIFT
if any(drift_report_sorted['Drift']):
    print("\nDrift detected in one or more features!")
else:
    print("\nNo significant drift detected.")