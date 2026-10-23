# G12++ Prep Programme — learner data dashboard

Technical test submission: combines `prep_app_export.csv` (app activity) and
`questionmark_scores.csv` (Questionmark baseline/mock exam scores) and shows, per NGO,
the learner funnel (registration → mock exam) and learning gain (mock − baseline).

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at http://localhost:8501. Use the NGO dropdown in the sidebar to filter to a single NGO.

## Run the tests

```bash
pip install -r requirements.txt
pytest tests -q
```

## Project layout

```
data/              the two provided CSVs (unmodified)
pipeline.py        cleaning, joining, funnel and learning-gain logic (pure functions)
app.py             Streamlit dashboard built on pipeline.py
tests/             unit tests for pipeline.py
docs/              the Analyse / Protect / Plan document (tasks 2-4), as .docx and .pdf
                   docs/build_report.js regenerates it (needs `npm install docx` in docs/)
explore.py         throwaway script used to find the data problems listed in the report
AI_USAGE_NOTE.md   how AI tools were used for this submission
```

## Data problems found and how they were handled

See `docs/Analysis_Protect_Plan.docx` (or `.pdf`) for the full writeup. Summary:

- One learner (`dana.saleh@mail.example`) appears twice in the app export with different
  progress — collapsed into one row (earliest registration date, max of each progress field).
- Several emails in the Questionmark export have leading/trailing whitespace and inconsistent
  casing — normalised (trim + lowercase) before joining the two files.
- One score is impossible (112%) — dropped.
- One score row (`test.user@mail.example`) has no matching learner — dropped as a test account.

## Privacy note

The dashboard only ever loads the two CSVs locally; it does not transmit learner data
anywhere. See the "Protect" section of the report for how this should be handled at
production scale (pseudonymous IDs for analytics, NGO-scoped access, no routine PII in
flat-file exports, retention limits).
