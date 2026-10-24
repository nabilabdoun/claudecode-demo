"""G12++ Prep Programme dashboard.

Combines the app export and the Questionmark scores export and shows,
per NGO: the learner funnel (registration -> mock exam) and the
learning gain (mock score minus baseline score).

Run with:  streamlit run app.py
"""

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from pipeline import FUNNEL_STEPS, load_and_clean

st.set_page_config(page_title="G12++ Prep Programme", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_PATH = os.path.join(BASE_DIR, "data", "prep_app_export.csv")
SCORES_PATH = os.path.join(BASE_DIR, "data", "questionmark_scores.csv")

STEP_LABELS = {
    "registered": "Registered applicants",
    "password_set": "Password set",
    "orientation_done": "Orientation done",
    "started_learning": "Started a topic",
    "completed_a_subject": "Completed a subject",
    "took_baseline": "Took baseline test",
    "took_mock": "Took mock exam",
}


@st.cache_data
def get_data():
    return load_and_clean(APP_PATH, SCORES_PATH)


app, scores, funnel, gain_summary, gain_detail = get_data()

st.title("G12++ Prep Programme — Cohort 1 dashboard")
st.caption(
    "Combines prep_app_export.csv (app activity) and questionmark_scores.csv "
    "(baseline/mock exam scores) across the three partner NGOs."
)

ngo_options = ["All NGOs"] + sorted(app["ngo"].unique().tolist())
selected_ngo = st.sidebar.selectbox("NGO", ngo_options)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Data cleaning applied**\n\n"
    "- Emails trimmed and lower-cased before matching across files\n"
    "- 1 duplicate learner row collapsed (kept max progress + earliest registration)\n"
    "- 1 impossible score (112%) dropped\n"
    "- 1 non-learner test account dropped\n"
)

# ---------------------------------------------------------------- funnel --
st.header("1. Learner funnel: registration → mock exam")

if selected_ngo == "All NGOs":
    funnel_row = funnel.loc["All NGOs"]
else:
    funnel_row = funnel.loc[selected_ngo]

funnel_df = pd.DataFrame(
    {"step": [STEP_LABELS[s] for s in FUNNEL_STEPS], "learners": funnel_row[FUNNEL_STEPS].values}
)
registered = funnel_df["learners"].iloc[0]
funnel_df["pct_of_registered"] = (funnel_df["learners"] / registered * 100).round(0)

fig_funnel = go.Figure(
    go.Funnel(
        y=funnel_df["step"],
        x=funnel_df["learners"],
        textinfo="value+percent initial",
    )
)
fig_funnel.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=420)
col1, col2 = st.columns([2, 1])
with col1:
    st.plotly_chart(fig_funnel, use_container_width=True)
with col2:
    st.dataframe(
        funnel_df.rename(columns={"step": "Step", "learners": "Learners", "pct_of_registered": "% of registered"}),
        hide_index=True,
        use_container_width=True,
    )

st.subheader("Funnel by NGO")
funnel_display = funnel.rename(columns=STEP_LABELS)
st.dataframe(funnel_display, use_container_width=True)

fig_compare = px.bar(
    funnel.drop(index="All NGOs").reset_index().melt(id_vars="ngo", var_name="step", value_name="learners"),
    x="step",
    y="learners",
    color="ngo",
    barmode="group",
    category_orders={"step": FUNNEL_STEPS},
    labels={"step": "Funnel step", "learners": "Learners", "ngo": "NGO"},
)
fig_compare.update_xaxes(ticktext=[STEP_LABELS[s] for s in FUNNEL_STEPS], tickvals=FUNNEL_STEPS)
st.plotly_chart(fig_compare, use_container_width=True)

# --------------------------------------------------------- learning gain --
st.header("2. Learning gain: mock score minus baseline score")
st.caption(
    "Only counts learners who sat BOTH the baseline and the mock for a given "
    "subject — this is a subset of all registered learners (see caveat below)."
)

gain_display = gain_summary if selected_ngo == "All NGOs" else gain_summary[gain_summary["ngo"] == selected_ngo]

col1, col2 = st.columns([1, 1])
with col1:
    st.dataframe(
        gain_display.rename(
            columns={
                "ngo": "NGO",
                "subject": "Subject",
                "learners_with_both_tests": "Learners (both tests)",
                "avg_baseline": "Avg baseline %",
                "avg_mock": "Avg mock %",
                "avg_gain": "Avg gain (pts)",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )
with col2:
    fig_gain = px.bar(
        gain_display,
        x="subject",
        y="avg_gain",
        color="ngo",
        barmode="group",
        labels={"avg_gain": "Average learning gain (points)", "subject": "Subject", "ngo": "NGO"},
    )
    st.plotly_chart(fig_gain, use_container_width=True)

if selected_ngo != "All NGOs" and gain_display.empty:
    st.warning(f"No learner in {selected_ngo} has sat both the baseline and the mock exam yet — no gain can be measured.")

with st.expander("Baseline vs mock, learner by learner"):
    detail_cols = ["email", "ngo", "subject", "score_pct_baseline", "score_pct_mock", "gain"]
    detail = gain_detail[detail_cols] if selected_ngo == "All NGOs" else gain_detail[gain_detail["ngo"] == selected_ngo][detail_cols]
    st.dataframe(detail.sort_values("gain", ascending=False), hide_index=True, use_container_width=True)

st.markdown("---")
st.caption(
    "Build for the G12++ Prep Programme technical test. "
    "All learner data is synthetic."
)
