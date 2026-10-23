"""One-off exploration script used to find the data problems described in
docs/Analysis_Protect_Plan.docx before writing the cleaning logic in
pipeline.py. Not part of the app; kept for transparency."""

import pandas as pd

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 20)

app = pd.read_csv("data/prep_app_export.csv")
scores = pd.read_csv("data/questionmark_scores.csv")

print("=== prep_app_export.csv ===")
print("rows:", len(app))
print("\nduplicate emails (raw):")
print(app["learner_email"].value_counts().loc[lambda s: s > 1])

print("\n=== questionmark_scores.csv ===")
print("rows:", len(scores))
print("\nemail samples with whitespace/case issues:")
odd = scores[scores["email"] != scores["email"].str.strip().str.lower()]
print(odd[["email"]])

print("\nscore_pct out of range (<0 or >100):")
print(scores[(scores["score_pct"] < 0) | (scores["score_pct"] > 100)])

print("\nemails in scores not matching any (normalized) app learner:")
app_emails_norm = set(app["learner_email"].str.strip().str.lower())
scores_emails_norm = scores["email"].str.strip().str.lower()
unmatched = scores[~scores_emails_norm.isin(app_emails_norm)]
print(unmatched)

print("\nngo value counts:")
print(app["ngo"].value_counts())
