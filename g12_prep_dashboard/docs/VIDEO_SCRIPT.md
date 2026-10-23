# 5-minute walkthrough script (for the Loom recording)

**0:00–0:30 — What this is**
"This is my submission for the G12++ Prep Programme data challenge. I combined the app
export and the Questionmark scores export into a small Streamlit dashboard that shows the
learner funnel and learning gain per NGO, plus a written doc covering the analysis, privacy
and growth plan."

**0:30–1:30 — The tool, funnel view**
- Open the dashboard, show the "All NGOs" funnel: 60 registered → 17 took the mock (28%).
- Switch the NGO filter to NGO-C: "Here's the single biggest finding — 9 of 15 NGO-C
  learners never engaged past registration, and literally zero reached the mock exam."
- Switch to NGO-B: "NGO-B is different — they get learners to the baseline fine, 75%, but
  lose most of them before the mock. That's a different problem needing a different fix."

**1:30–2:15 — Learning gain**
- Scroll to the learning gain section, "All NGOs" view.
- "For the learners who did sit both tests, the gain is clearly positive — 14 to 18 points
  on average. But I want to flag the caveat right away: this is only the ~half of learners
  who stuck with it. NGO-C has zero data points here because nobody reached the mock."

**2:15–3:00 — Data problems**
- Point at the sidebar "data cleaning applied" list.
- "The data wasn't clean — a duplicate learner row, inconsistent email casing between the
  two files, one impossible 112% score, and a test account with no real learner behind it.
  All handled in pipeline.py, with unit tests."

**3:00–4:15 — The document (tasks 2-4)**
- Open Analysis_Protect_Plan.docx / pdf, scroll through briefly.
- "Two product recommendations: close the registration-to-first-topic gap, and add a
  baseline-to-mock checkpoint for coordinators, aimed at NGO-B specifically."
- "On privacy — treat this as children's data by default: pseudonymous IDs for analytics,
  NGO-scoped access, no PII in routine exports, defined retention."
- "On the 12-month plan to 5x — fix the funnel before scaling it, instrument it in near
  real time, and test willingness to pay by shipping this dashboard for free first and
  watching whether coordinators actually use it unprompted."

**4:15–5:00 — AI use + close**
- "I used Claude Code throughout — not just to generate a report, but to explore the raw
  data first so every number in the write-up is grounded in what's actually in the CSVs,
  to build and test the pipeline, and to catch and fix two real bugs by running the app in
  a browser rather than just reading the code. Full notes in AI_USAGE_NOTE.md."
- "That's the submission — happy to walk through any part of the code live."
