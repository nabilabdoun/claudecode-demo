"""Clean and join the G12++ Prep Programme data, and compute the two
metrics the brief asks for, per NGO: the registration-to-mock funnel and
the learning gain (mock score minus baseline score).

Kept deliberately small and functional so each step can be tested on its
own with a tiny in-memory DataFrame (see tests/test_pipeline.py).
"""

import pandas as pd

FUNNEL_STEPS = [
    "registered",
    "password_set",
    "orientation_done",
    "started_learning",
    "completed_a_subject",
    "took_baseline",
    "took_mock",
]


def _normalize_email(series: pd.Series) -> pd.Series:
    return series.str.strip().str.lower()


def load_app_export(path: str) -> pd.DataFrame:
    """Load prep_app_export.csv and fix the data problems found in it:

    - emails are normalised (trim + lowercase) so they join correctly
      with the Questionmark export
    - a learner that appears twice (duplicate registration/export row)
      is collapsed into one row: the registered_date is the earliest of
      the two, every progress column takes the highest value seen (a
      learner's progress can only go up), and last_active_date is the
      most recent.
    """
    df = pd.read_csv(path)
    df["learner_email"] = _normalize_email(df["learner_email"])

    progress_cols = [
        "password_set",
        "orientation_done",
        "topics_completed",
        "subjects_started",
        "subjects_completed",
    ]
    agg = {
        "full_name": "first",
        "phone": "first",
        "date_of_birth": "first",
        "ngo": "first",
        "device": "first",
        "registered_date": "min",
        "last_active_date": "max",
        **{col: "max" for col in progress_cols},
    }
    df = df.groupby("learner_email", as_index=False).agg(agg)
    return df


def load_scores(path: str) -> pd.DataFrame:
    """Load questionmark_scores.csv and fix the data problems found in it:

    - emails are normalised (trim + lowercase) to match the app export
    - rows for accounts that aren't real learners (e.g. a QA/test
      account not present in the app export) are dropped
    - a score outside the 0-100 range is impossible and is dropped
      rather than silently used in an average
    """
    df = pd.read_csv(path)
    df["email"] = _normalize_email(df["email"])
    df = df[(df["score_pct"] >= 0) & (df["score_pct"] <= 100)]
    return df


def drop_unmatched_scores(scores: pd.DataFrame, app: pd.DataFrame) -> pd.DataFrame:
    """Drop score rows whose email never appears in the app export
    (test/QA accounts, typos with no matching learner)."""
    known = set(app["learner_email"])
    return scores[scores["email"].isin(known)]


def build_funnel(app: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    """Per-NGO count of learners reaching each funnel step, registration
    through to sitting the mock exam."""
    took_baseline = set(scores.loc[scores["assessment"] == "Baseline", "email"])
    took_mock = set(scores.loc[scores["assessment"] == "Mock", "email"])

    rows = []
    for ngo, g in app.groupby("ngo"):
        rows.append(
            {
                "ngo": ngo,
                "registered": len(g),
                "password_set": int((g["password_set"] == 1).sum()),
                "orientation_done": int((g["orientation_done"] == 1).sum()),
                "started_learning": int((g["topics_completed"] > 0).sum()),
                "completed_a_subject": int((g["subjects_completed"] > 0).sum()),
                "took_baseline": g["learner_email"].isin(took_baseline).sum(),
                "took_mock": g["learner_email"].isin(took_mock).sum(),
            }
        )
    funnel = pd.DataFrame(rows).set_index("ngo").reindex(
        app["ngo"].drop_duplicates().sort_values()
    )

    totals = funnel.sum()
    totals.name = "All NGOs"
    funnel = pd.concat([funnel, totals.to_frame().T])
    funnel.index.name = "ngo"
    return funnel[FUNNEL_STEPS]


def build_learning_gain(app: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    """Per NGO and subject: mean baseline score, mean mock score, mean
    gain (mock - baseline), and how many learners sat both tests for
    that subject. Only learners with BOTH a baseline and a mock score
    for the same subject contribute to the gain."""
    baseline = scores[scores["assessment"] == "Baseline"][["email", "subject", "score_pct"]]
    mock = scores[scores["assessment"] == "Mock"][["email", "subject", "score_pct"]]

    paired = baseline.merge(
        mock, on=["email", "subject"], suffixes=("_baseline", "_mock")
    )
    paired["gain"] = paired["score_pct_mock"] - paired["score_pct_baseline"]
    paired = paired.merge(
        app[["learner_email", "ngo"]],
        left_on="email",
        right_on="learner_email",
        how="left",
    )

    summary = (
        paired.groupby(["ngo", "subject"])
        .agg(
            learners_with_both_tests=("email", "count"),
            avg_baseline=("score_pct_baseline", "mean"),
            avg_mock=("score_pct_mock", "mean"),
            avg_gain=("gain", "mean"),
        )
        .round(1)
        .reset_index()
    )
    return summary, paired


def load_and_clean(app_path: str, scores_path: str):
    """Convenience entry point: load both files, clean them, and return
    (app, scores, funnel, learning_gain_summary)."""
    app = load_app_export(app_path)
    scores = load_scores(scores_path)
    scores = drop_unmatched_scores(scores, app)
    funnel = build_funnel(app, scores)
    gain_summary, gain_detail = build_learning_gain(app, scores)
    return app, scores, funnel, gain_summary, gain_detail
