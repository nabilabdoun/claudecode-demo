const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, PageBreak,
} = require("docx");

const PINK = "E6007E";
const DARK = "3C3C46";
const LIGHT = "FBE3EF";

const body = (text, opts = {}) =>
  new Paragraph({
    spacing: { after: 90, ...(opts.spacing || {}) },
    children: [new TextRun({ text, size: 20, font: "Arial", ...opts })],
  });

const bullet = (text, opts = {}) =>
  new Paragraph({
    bullet: { level: 0 },
    spacing: { after: 50 },
    children: [new TextRun({ text, size: 20, font: "Arial", ...opts })],
  });

const h1 = (text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 160, after: 80 },
    children: [new TextRun({ text, bold: true, size: 26, font: "Arial", color: PINK })],
  });

const h2 = (text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 120, after: 60 },
    children: [new TextRun({ text, bold: true, size: 21, font: "Arial", color: DARK })],
  });

function statTable(headers, rows) {
  const colWidth = Math.floor(9000 / headers.length);
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map(
      (hText) =>
        new TableCell({
          width: { size: colWidth, type: WidthType.DXA },
          shading: { type: ShadingType.CLEAR, fill: PINK },
          margins: { top: 40, bottom: 40, left: 80, right: 80 },
          children: [
            new Paragraph({
              children: [new TextRun({ text: hText, bold: true, size: 16, font: "Arial", color: "FFFFFF" })],
            }),
          ],
        })
    ),
  });
  const dataRows = rows.map(
    (r) =>
      new TableRow({
        children: r.map(
          (cell) =>
            new TableCell({
              width: { size: colWidth, type: WidthType.DXA },
              margins: { top: 40, bottom: 40, left: 80, right: 80 },
              children: [
                new Paragraph({
                  children: [new TextRun({ text: String(cell), size: 16, font: "Arial", color: DARK })],
                }),
              ],
            })
        ),
      })
  );
  return new Table({
    width: { size: 9000, type: WidthType.DXA },
    columnWidths: headers.map(() => colWidth),
    rows: [headerRow, ...dataRows],
    borders: {
      top: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
      left: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
      right: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
      insideVertical: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
    },
  });
}

const doc = new Document({
  sections: [
    {
      properties: {
        page: { size: { width: 12240, height: 15840 }, margin: { top: 900, bottom: 900, left: 1000, right: 1000 } },
      },
      children: [
        new Paragraph({
          children: [
            new TextRun({ text: "G12++ Prep Programme — Data Challenge", bold: true, size: 32, font: "Arial", color: PINK }),
          ],
        }),
        new Paragraph({
          spacing: { after: 200 },
          children: [
            new TextRun({ text: "Tasks 2–4: Analyse, Protect, Plan   ·   Cohort 1, February 2027   ·   All learner data synthetic", italics: true, size: 18, font: "Arial", color: DARK }),
          ],
        }),

        h1("2. Analyse"),

        h2("What the data tells us"),
        body(
          "60 unique learners across three NGOs after cleaning (NGO-A: 25, NGO-B: 20, NGO-C: 15). The funnel from registration to mock exam drops sharply and unevenly by NGO:"
        ),
        statTable(
          ["NGO", "Registered", "Password set", "Orientation", "Started topic", "Completed subject", "Took baseline", "Took mock"],
          [
            ["NGO-A", "25", "24", "22", "17", "13", "21", "13 (52%)"],
            ["NGO-B", "20", "20", "15", "10", "5", "15", "4 (20%)"],
            ["NGO-C", "15", "9", "7", "1", "1", "6", "0 (0%)"],
            ["All", "60", "53", "44", "28", "19", "42", "17 (28%)"],
          ]
        ),
        body("", { spacing: { after: 40 } }),
        bullet("NGO-C effectively stalled: 9 of 15 learners (60%) never engaged beyond registration — no topic, no test, nothing — and zero learners reached the mock exam. This is the single largest signal in the data."),
        bullet("NGO-B gets learners to the baseline well (15/20, 75%) but loses most of them before the mock (only 4/20, 20%) — a specific mid-funnel leak, not a registration problem."),
        bullet("NGO-A converts best overall (13/25 reach the mock, 52%) and is the closest thing to a working funnel in this cohort."),
        bullet("Device (phone vs laptop) does not explain the drop-off — 47% vs 44% of learners start a topic on each — so NGO-C's stall looks operational (onboarding, local support, connectivity), not a device/UX issue."),
        bullet("For the 31 learners who sat both tests, learning gain is clearly positive: +14 to +18 percentage points on average (NGO-A: English +14.0, Maths +14.7; NGO-B: English +15.0, Maths +17.8). Real evidence the content works for learners who engage with it."),

        h2("Data problems found, and how handled"),
        bullet("Duplicate learner row (dana.saleh@mail.example, two export snapshots with different progress) → collapsed to one row: earliest registration date, the higher value of every progress field (progress only increases), latest activity date."),
        bullet("Inconsistent emails between files (e.g. \" Lina.Youssef@mail.example \" — padded, mixed case, in the Questionmark export) → trimmed and lower-cased before joining. Left unfixed, 3 learners' scores would have silently failed to match."),
        bullet("One impossible score: huda.aziz, Mock Mathematics = 112% → dropped as a data-entry/export error; her other valid scores were kept."),
        bullet("One score row for test.user@mail.example has no matching learner in the app export → dropped as a QA/test record."),
        bullet("Checked explicitly for duplicate (learner, assessment, subject) score rows after normalising emails — found none, so no double-counted averages."),

        h2("How confident am I"),
        body(
          "Funnel counts: high confidence — plain counts after the fixes above, covered by unit tests (tests/test_pipeline.py)."
        ),
        body(
          "Learning gain: moderate confidence only. It is measured on the 31 of 60 learners who sat both tests — the most motivated, most-retained group. That is survivorship bias: we don't know the gain for the 43 who registered but never reached the mock, and NGO-C has zero data points at all, so \"the programme works\" really means \"it works for the roughly half who stick with it.\" Per-NGO gain comparisons also rest on small samples (≤15 paired learners), so differences between NGO-A and NGO-B could be noise."
        ),

        h2("Two recommended product changes"),
        bullet("Close the registration → first-topic gap (53% of all learners never start a topic, and it is NGO-C's exact failure point): trigger an automatic nudge a few days after orientation if no topic has started, and add first-session telemetry (app opened, content downloaded, connectivity) so we can tell apart \"didn't open the app\" from \"couldn't load content\" — right now the data only shows the outcome, not the cause."),
        bullet("Add a baseline → mock checkpoint for coordinators, not just learners, aimed first at NGO-B (75% reach baseline, only 20% reach mock — the sharpest single-stage drop in the data): a visible \"on track for mock\" flag per learner so an NGO can intervene in week 3, not discover the drop-off from a quarterly export in February."),

        h1("3. Protect"),
        body(
          "Every learner in this dataset is a young person, registered through an NGO across several countries, and the combined files (name, phone, DOB, NGO, device, exam scores) are enough to fully identify and locate a specific minor and know exactly how they performed. That should be treated as sensitive children's data by default, regardless of which country's specific law applies."
        ),
        bullet("Minimise: analytics and dashboards (including the one built for this test) should run on a pseudonymous learner ID, never on full_name / phone / date_of_birth directly — those fields belong only in the app's own learner-profile store, not in any export used for reporting or analysis."),
        bullet("Scope access: an NGO should only ever see its own learners (role-based access scoped by the ngo field); individual learner drill-down should be restricted to the coordinator role, with funders/leadership seeing NGO- and cohort-level aggregates only."),
        bullet("Control the pipeline: routine flat-file CSV handoffs between the app, Questionmark and NGOs (like the ones used for this test) are themselves a privacy risk — replace with an access-controlled, logged pipeline/API, and treat any CSV that leaves that pipeline as a reportable event."),
        bullet("Vendor risk: Questionmark is a data processor — confirm a data processing agreement restricting them from retaining or reusing learner data beyond returning scores, and apply the same standard to any analytics/BI tool used downstream."),
        bullet("Cross-border transfer: confirm where learner data is hosted and processed against each partner country's child-data rules, and prefer regional data residency where that's required rather than one global store by default."),
        bullet("Retention: define and enforce a retention window for raw PII (e.g. deleted a fixed period after a learner exits the programme), keeping only pseudonymised, aggregated metrics for longer-term reporting; give NGOs a deletion-request path on behalf of a learner or guardian."),

        new Paragraph({ children: [new PageBreak()] }),

        h1("4. Plan — growing from 150 to 750 participants in 12 months"),

        h2("Priorities"),
        bullet("Fix what is already broken before multiplying it: NGO-C's stall and NGO-B's baseline→mock leak are operational problems visible today at 150 learners — scaling 5× without fixing them scales the failure, not the programme."),
        bullet("Instrument the funnel in near-real-time, per NGO, so a coordinator can act in week 3, not find out from a quarterly CSV export."),
        bullet("Turn what works at NGO-A (the best-converting funnel in the data) into a repeatable onboarding playbook for new NGO partners, instead of each NGO re-inventing its own process."),
        bullet("Productise the funnel + learning-gain view built for this test into a real NGO-facing reporting feature, rather than a one-off analysis artifact."),

        h2("What I would not do"),
        bullet("Not onboard new NGOs or learners ahead of shipping the funnel fixes and real-time reporting above — adding scale to a broken funnel multiplies drop-off, not outcomes."),
        bullet("Not build a general-purpose BI/analytics platform — keep reporting scoped to the funnel and learning-gain views NGOs have actually needed so far; no speculative dashboards nobody asked for."),
        bullet("Not keep manual/periodic CSV exports as the Questionmark↔app integration at 5× scale and more countries — it will not hold up operationally or for privacy (see Task 3)."),

        h2("How I would measure success"),
        bullet("Primary: % of registered learners reaching the mock exam, per NGO, tracked monthly — today 28% overall and 0% for NGO-C."),
        bullet("Secondary: average learning gain among mock-takers, and the share of registered learners who become mock-takers with a valid paired score — directly closing the survivorship-bias gap identified in Task 2."),
        bullet("Leading indicator: time from registration to first topic started, per NGO — detects an NGO-C-style stall weeks before the mock-exam outcome would reveal it."),

        h2("Testing whether NGOs would pay for reporting"),
        bullet("Ship the funnel + learning-gain dashboard built for this test as a free, lightweight feature at the current 150-learner scale, instrumented to see whether coordinators actually open it and act on it."),
        bullet("Run a willingness-to-pay pilot with one or two NGOs: offer a paid tier for features they ask for directly (export/API access, a weekly digest, individual-learner drill-down) and see whether they adopt or stall on it."),
        bullet("Treat unprompted use — a coordinator checking the dashboard weekly and raising an NGO-C-style stall with us before we spot it — as the real signal of willingness to pay; a feature nobody opens will not convert, whatever an interview suggests."),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("Analysis_Protect_Plan.docx", buf);
  console.log("written");
});
