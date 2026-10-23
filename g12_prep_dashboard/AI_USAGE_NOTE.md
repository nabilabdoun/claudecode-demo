# How I used AI tools for this test

I used Claude Code (an AI coding agent) end-to-end as a pair-programmer and analyst, not as a
one-shot "write me the answer" tool. Concretely:

- **Reading the brief.** The candidate brief was a `.docx`; I had it extract the raw text
  (including the two file-description tables) so the actual task wording drove the work,
  rather than guessing from the filenames.
- **Exploring the data before deciding anything.** Before writing any cleaning logic, I had it
  write a throwaway exploration script (`explore.py`) against the real CSVs — duplicate
  emails, out-of-range scores, whitespace/casing mismatches, unmatched emails — so every
  claim in the "data problems found" section of the report is backed by a number that was
  actually computed, not assumed.
- **Building the tool.** I had it write the cleaning/join/funnel/gain logic (`pipeline.py`) as
  small, separately testable functions, write unit tests for it (`tests/test_pipeline.py`,
  6 tests), and build the Streamlit dashboard (`app.py`) on top. It then ran the dashboard in
  a real browser, which caught two real bugs before I ever saw them (a stale-cache issue and
  an index-name bug after a refactor) — I had it fix both and re-verify by re-running the app
  and the tests, not by inspection alone.
- **Drafting the report.** I had it draft the Analyse / Protect / Plan document from the
  numbers the pipeline actually produced, then I reviewed the conclusions myself — in
  particular pushing on the learning-gain confidence caveat (survivorship bias: gain is only
  measured on the ~half of learners who sat both tests) and keeping the two product
  recommendations tied to the specific funnel stages the data shows are weakest, rather than
  generic suggestions.
- **Document formatting.** The Word document was generated with a script (`docs/build_report.js`,
  using the `docx` npm library) rather than typed by hand, then rendered to PDF and checked
  page-by-page to confirm it actually fits the brief's page budget (2 pages for Analyse +
  Protect, 1 page for Plan).

What I did **not** do: accept the first draft of the report uncritically, or let it invent data.
Every number quoted (funnel counts, gain percentages, counts of data problems) traces back to
running `pipeline.py` against the two provided CSVs — nothing was estimated.
