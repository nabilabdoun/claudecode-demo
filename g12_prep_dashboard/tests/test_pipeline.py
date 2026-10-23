import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import (
    build_funnel,
    build_learning_gain,
    drop_unmatched_scores,
    load_app_export,
    load_scores,
)


def _write_csv(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text.strip() + "\n")
    return str(path)


def test_load_app_export_normalizes_email_case_and_whitespace(tmp_path):
    csv = _write_csv(
        tmp_path,
        "app.csv",
        """
learner_email,full_name,phone,date_of_birth,ngo,device,registered_date,password_set,orientation_done,topics_completed,subjects_started,subjects_completed,last_active_date
 Ana.Noor@mail.example ,Ana Noor,+1,2008-01-01,NGO-A,phone,2026-11-01,1,1,5,1,0,2026-12-01
""",
    )
    df = load_app_export(csv)
    assert df["learner_email"].tolist() == ["ana.noor@mail.example"]


def test_load_app_export_collapses_duplicate_learner_keeping_max_progress(tmp_path):
    csv = _write_csv(
        tmp_path,
        "app.csv",
        """
learner_email,full_name,phone,date_of_birth,ngo,device,registered_date,password_set,orientation_done,topics_completed,subjects_started,subjects_completed,last_active_date
dup@mail.example,Dup One,+1,2008-01-01,NGO-A,phone,2026-11-20,1,1,17,2,1,2027-02-13
dup@mail.example,Dup One,+1,2008-01-01,NGO-A,phone,2026-11-23,1,1,0,0,0,2027-02-13
""",
    )
    df = load_app_export(csv)
    assert len(df) == 1
    row = df.iloc[0]
    assert row["registered_date"] == "2026-11-20"
    assert row["topics_completed"] == 17
    assert row["subjects_completed"] == 1


def test_load_scores_drops_out_of_range_scores(tmp_path):
    csv = _write_csv(
        tmp_path,
        "scores.csv",
        """
email,assessment,subject,score_pct,date_taken
a@mail.example,Mock,Mathematics,112,2027-02-02
b@mail.example,Mock,Mathematics,80,2027-02-02
""",
    )
    df = load_scores(csv)
    assert df["score_pct"].tolist() == [80]


def test_drop_unmatched_scores_removes_emails_not_in_app_export():
    app = pd.DataFrame({"learner_email": ["known@mail.example"]})
    scores = pd.DataFrame(
        {
            "email": ["known@mail.example", "test.user@mail.example"],
            "assessment": ["Baseline", "Baseline"],
            "subject": ["English", "English"],
            "score_pct": [40, 0],
        }
    )
    cleaned = drop_unmatched_scores(scores, app)
    assert cleaned["email"].tolist() == ["known@mail.example"]


def test_build_funnel_counts_each_step_per_ngo():
    app = pd.DataFrame(
        {
            "learner_email": ["a@x.example", "b@x.example", "c@x.example"],
            "ngo": ["NGO-A", "NGO-A", "NGO-B"],
            "password_set": [1, 0, 1],
            "orientation_done": [1, 0, 1],
            "topics_completed": [5, 0, 0],
            "subjects_started": [1, 0, 0],
            "subjects_completed": [0, 0, 0],
        }
    )
    scores = pd.DataFrame(
        {
            "email": ["a@x.example", "c@x.example"],
            "assessment": ["Baseline", "Baseline"],
            "subject": ["English", "English"],
            "score_pct": [40, 50],
        }
    )
    funnel = build_funnel(app, scores)
    assert funnel.loc["NGO-A", "registered"] == 2
    assert funnel.loc["NGO-A", "password_set"] == 1
    assert funnel.loc["NGO-A", "took_baseline"] == 1
    assert funnel.loc["NGO-B", "took_baseline"] == 1
    assert funnel.loc["All NGOs", "registered"] == 3


def test_build_learning_gain_only_pairs_matching_subject_and_learner():
    app = pd.DataFrame({"learner_email": ["a@x.example"], "ngo": ["NGO-A"]})
    scores = pd.DataFrame(
        {
            "email": ["a@x.example", "a@x.example", "a@x.example"],
            "assessment": ["Baseline", "Mock", "Mock"],
            "subject": ["English", "English", "Mathematics"],
            "score_pct": [40, 60, 70],
        }
    )
    summary, detail = build_learning_gain(app, scores)
    assert len(detail) == 1
    assert detail.iloc[0]["gain"] == 20
    row = summary[summary["subject"] == "English"].iloc[0]
    assert row["avg_gain"] == 20.0
    assert "Mathematics" not in summary["subject"].values
