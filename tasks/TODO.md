# ML Model Comparison Lab — V1 Task Board

**Project Version:** V1
**Status:** Implementation Planning
**Last Updated:** September 2026

---

# 1. Purpose

This document is the implementation task board for **ML Model Comparison Lab V1**.

It converts the requirements defined in:

```text
docs/PRD.md
docs/ARCHITECTURE.md
docs/API.md
docs/DATA_PROCESSING.md
docs/TESTING.md
```

into actionable development tasks.

The project should be implemented incrementally.

No task should introduce functionality outside the approved V1 scope without an explicit architectural/product decision.

---

# 2. V1 Goal

Build a working web-based data preparation platform that allows a user to:

```text
Upload Dataset
      ↓
Analyze Dataset
      ↓
Detect Data Quality Issues
      ↓
Review Exact Problem Locations
      ↓
Replace / Remove / Ignore
      ↓
Maintain Audit Trail
      ↓
Re-analyze Cleaned Dataset
      ↓
Create Visualization
      ↓
Export Dataset
      ↓
Clear Session
```

---

# 3. Ownership

| Owner           | Responsibility                                                                      |
| --------------- | ----------------------------------------------------------------------------------- |
| **HUMAN**       | Architecture decisions, integration, review, testing, Git/GitHub, final acceptance  |
| **ANTIGRAVITY** | React frontend, UI, state handling, frontend API integration                        |
| **OPENCODE**    | FastAPI backend, data processing, cleaning engine, visualization generation, export |

Agents must work within the documented architecture.

They must not independently:

* Expand V1 scope
* Introduce ML training
* Introduce a database
* Introduce authentication
* Replace the approved backend architecture
* Add unnecessary infrastructure
* Add libraries without justification

---

# 4. Implementation Order

The recommended implementation sequence is:

```text
Phase 0  → Documentation Freeze
Phase 1  → Backend Foundation
Phase 2  → Frontend Foundation
Phase 3  → Dataset Ingestion & Sessions
Phase 4  → Dataset Analysis & Type Inference
Phase 5  → Data Quality Engine
Phase 6  → Cleaning, Audit & Reset
Phase 7  → Visualization
Phase 8  → Export
Phase 9  → Frontend ↔ Backend Integration
Phase 10 → Testing & Benchmarking
Phase 11 → Deployment
Phase 12 → V1 Freeze
```

Do not skip directly to advanced features before the underlying data state and processing behavior are stable.

---

# 5. Phase 0 — Documentation Freeze

## Goal

Ensure all agents are working from the same specification.

### Tasks

* [ ] **HUMAN** — Review `PRD.md`
* [ ] **HUMAN** — Review `ARCHITECTURE.md`
* [ ] **HUMAN** — Review `API.md`
* [ ] **HUMAN** — Review `DATA_PROCESSING.md`
* [ ] **HUMAN** — Review `TESTING.md`
* [ ] **HUMAN** — Confirm V1 scope
* [ ] **HUMAN** — Resolve any remaining contradictions
* [ ] **HUMAN** — Commit documentation to Git

### Acceptance

* [ ] All six documents are present
* [ ] V1 scope is consistent across documents
* [ ] No unresolved architectural decision blocks implementation
* [ ] Git commit created

---

# 6. Phase 1 — Backend Foundation

**Owner:** OPENCODE

## Goal

Create the FastAPI backend structure.

### Tasks

* [ ] Create backend Python environment
* [ ] Create FastAPI application
* [ ] Create application entry point
* [ ] Configure development server
* [ ] Configure environment variables
* [ ] Create `/api/v1` route structure
* [ ] Configure CORS
* [ ] Create API error-handling structure
* [ ] Create service/module structure
* [ ] Create session management foundation
* [ ] Add basic health endpoint if useful for deployment
* [ ] Configure logging without logging dataset contents

### Suggested backend structure

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   ├── services/
│   ├── processing/
│   ├── visualization/
│   ├── schemas/
│   └── core/
│
├── tests/
├── requirements.txt
└── README.md
```

The exact structure may change if implementation requires it, but architectural responsibilities must remain clear.

### Acceptance

* [ ] FastAPI starts successfully
* [ ] `/api/v1` routes are reachable
* [ ] CORS works in development
* [ ] Basic error handling works
* [ ] Backend tests can run

---

# 7. Phase 2 — Frontend Foundation

**Owner:** ANTIGRAVITY

## Goal

Create the V1 frontend shell.

### Tasks

* [ ] Initialize React + TypeScript + Vite application
* [ ] Configure Tailwind CSS
* [ ] Configure shadcn/ui
* [ ] Establish application layout
* [ ] Create navigation structure
* [ ] Create dataset upload interface
* [ ] Create loading states
* [ ] Create error states
* [ ] Create empty states
* [ ] Create reusable table components
* [ ] Create reusable status/message components

### Acceptance

* [ ] Frontend starts successfully
* [ ] Main layout renders
* [ ] Upload screen exists
* [ ] Loading/error/empty states exist
* [ ] UI follows the project design philosophy
* [ ] No ML-model UI is introduced

---

# 8. Phase 3 — Dataset Ingestion & Sessions

**Owners:** OPENCODE + ANTIGRAVITY

## Goal

Establish the core dataset lifecycle.

### Backend

* [ ] Implement `POST /sessions`
* [ ] Validate uploaded files
* [ ] Detect supported formats
* [ ] Create temporary session
* [ ] Preserve original dataset
* [ ] Create working dataset state
* [ ] Implement `GET /sessions/{session_id}`
* [ ] Implement `DELETE /sessions/{session_id}`
* [ ] Implement session cleanup

### Frontend

* [ ] Upload file
* [ ] Send multipart request
* [ ] Store `session_id`
* [ ] Display upload progress/loading state
* [ ] Handle upload errors
* [ ] Display dataset-ready state
* [ ] Implement Clear Session

### Formats

* [ ] CSV
* [ ] XLSX
* [ ] Tabular JSON

### Acceptance

* [ ] Supported files upload successfully
* [ ] Unsupported files are rejected
* [ ] Session is created
* [ ] Original dataset is preserved
* [ ] Working dataset is initialized
* [ ] Session can be cleared

---

# 9. Phase 4 — Dataset Analysis & Type Inference

**Owner:** OPENCODE

## Goal

Produce reliable dataset-level and column-level information.

### Tasks

* [ ] Implement row count
* [ ] Implement column count
* [ ] Implement file size
* [ ] Return column names
* [ ] Detect data types
* [ ] Implement missing-value counts
* [ ] Implement duplicate counts
* [ ] Implement unique-value information
* [ ] Implement numerical statistics
* [ ] Implement categorical statistics
* [ ] Implement date/time detection
* [ ] Implement boolean detection
* [ ] Implement identifier-like detection
* [ ] Implement user type override

### API

* [ ] `GET /sessions/{session_id}/analysis`
* [ ] `PATCH /sessions/{session_id}/columns/{column_name}/type`

### Frontend

* [ ] Dataset summary
* [ ] Column table
* [ ] Data type display
* [ ] Missing-value display
* [ ] Duplicate information
* [ ] Statistics display
* [ ] Type override interface

### Acceptance

* [ ] Analysis values are independently verifiable
* [ ] Type inference works on representative fixtures
* [ ] Type override updates effective type
* [ ] Analysis reflects the current working dataset

---

# 10. Phase 5 — Data Quality Engine

**Owner:** OPENCODE

## Goal

Detect and report data-quality problems at exact locations.

### Missing Values

* [ ] Detect missing numerical values
* [ ] Detect missing categorical values
* [ ] Detect multiple missing values
* [ ] Return exact row number
* [ ] Return exact column

### Duplicates

* [ ] Detect exact duplicate records
* [ ] Return affected rows
* [ ] Do not classify merely similar rows as exact duplicates
* [ ] Do not implement fuzzy matching

### Type Incompatibilities

* [ ] Detect incompatible values
* [ ] Identify exact row
* [ ] Identify exact column
* [ ] Return current value

### Suspicious Values

* [ ] Implement only agreed V1 suspicious-value rules
* [ ] Avoid blindly deleting unusual values
* [ ] Clearly distinguish suspicious values from definite incompatibilities

### API

* [ ] Implement `GET /sessions/{session_id}/quality`

### Frontend

* [ ] Quality summary
* [ ] Issue table
* [ ] Row number
* [ ] Column
* [ ] Current value
* [ ] Issue type
* [ ] Severity
* [ ] Suggested action

### Acceptance

* [ ] Every detected cell-level issue has an exact location
* [ ] Row numbering is correctly 1-indexed for users
* [ ] Clean datasets do not produce false quality issues beyond defined rules
* [ ] Quality results match test fixtures

---

# 11. Phase 6 — Cleaning, Audit & Reset

**Owner:** OPENCODE
**Frontend support:** ANTIGRAVITY

## Goal

Allow controlled modification of the working dataset while preserving the original.

---

## 11.1 Replace

* [ ] Implement Replace action
* [ ] Validate replacement value
* [ ] Implement numerical Mean
* [ ] Implement numerical Median
* [ ] Implement numerical Custom
* [ ] Implement categorical Mode
* [ ] Implement categorical Custom
* [ ] Implement type-mismatch Custom replacement

---

## 11.2 Remove

* [ ] Implement row removal
* [ ] Implement duplicate removal
* [ ] Validate removal target
* [ ] Update working dataset correctly

---

## 11.3 Ignore

* [ ] Implement Ignore action/state
* [ ] Preserve original value
* [ ] Preserve issue information where required

---

## 11.4 Audit

* [ ] Create audit record for Replace
* [ ] Create audit record for Remove
* [ ] Create audit record for Ignore where applicable
* [ ] Store original value
* [ ] Store new value where applicable
* [ ] Store row
* [ ] Store column
* [ ] Store action
* [ ] Store issue type
* [ ] Store timestamp/status

### API

* [ ] `POST /sessions/{session_id}/clean`
* [ ] `GET /sessions/{session_id}/audit`
* [ ] `POST /sessions/{session_id}/reset`

### Frontend

* [ ] Replace interface
* [ ] Replacement method selector
* [ ] Custom value input
* [ ] Remove confirmation
* [ ] Ignore action
* [ ] Audit display
* [ ] Reset button

### Acceptance

* [ ] Correct cell/row is modified
* [ ] Original dataset remains unchanged
* [ ] Working dataset changes correctly
* [ ] Audit trail matches actual modifications
* [ ] Reset restores original working state
* [ ] Invalid modifications are rejected

---

# 12. Phase 7 — Visualization

**Owner:** OPENCODE
**Frontend:** ANTIGRAVITY

## Goal

Provide deterministic recommendations and practical visualizations.

### Recommendation Engine

* [ ] Implement one numerical → histogram
* [ ] Implement two numerical → scatter
* [ ] Implement categorical → bar/count
* [ ] Implement date + numerical → line
* [ ] Implement multiple numerical → correlation heatmap

### Chart Generation

Implement the agreed V1 chart set:

* [ ] Scatter plot
* [ ] Bar chart
* [ ] Pie chart
* [ ] Line chart
* [ ] Histogram
* [ ] Box plot
* [ ] Area chart
* [ ] Correlation heatmap
* [ ] Pair plot
* [ ] Distribution plot
* [ ] Violin plot
* [ ] Count plot
* [ ] KDE-based plot

The exact final subset may be reduced if implementation/testing shows that a chart does not provide sufficient V1 value.

### Backend

* [ ] Generate charts using Matplotlib
* [ ] Use Seaborn where appropriate
* [ ] Validate chart configuration
* [ ] Generate primarily PNG output
* [ ] Support SVG where implemented
* [ ] Handle incompatible column types
* [ ] Handle empty/insufficient data

### Large Data

* [ ] Implement sampling where necessary
* [ ] Implement aggregation/binning where necessary
* [ ] Report when sampling/aggregation is applied

### Frontend

* [ ] Visualization recommendation UI
* [ ] Custom visualization UI
* [ ] Chart type selection
* [ ] Column selection
* [ ] Basic configuration
* [ ] Display generated visualization
* [ ] Display sampling/aggregation notice where applicable

### Acceptance

* [ ] Recommendations are deterministic
* [ ] Valid configurations generate charts
* [ ] Invalid configurations produce clear errors
* [ ] Large datasets do not blindly attempt to plot every row
* [ ] Visualization results are usable in the frontend

---

# 13. Phase 8 — Export

**Owner:** OPENCODE
**Frontend:** ANTIGRAVITY

## Goal

Allow the user to download the current working dataset.

### Backend

* [ ] Implement CSV export
* [ ] Implement XLSX export
* [ ] Implement tabular JSON export
* [ ] Validate export format
* [ ] Preserve column names
* [ ] Preserve values
* [ ] Verify cleaned state is exported

### Frontend

* [ ] Export controls
* [ ] Format selector
* [ ] Download handling
* [ ] Export error state

### Acceptance

* [ ] CSV export works
* [ ] XLSX export works
* [ ] JSON export works
* [ ] Exported data matches working dataset
* [ ] Original dataset remains unchanged

---

# 14. Phase 9 — Frontend ↔ Backend Integration

**Owners:** ANTIGRAVITY + OPENCODE
**Final review:** HUMAN

## Goal

Connect all completed backend functionality to the frontend.

### Tasks

* [ ] Connect upload API
* [ ] Connect session API
* [ ] Connect analysis API
* [ ] Connect type override API
* [ ] Connect quality API
* [ ] Connect cleaning API
* [ ] Connect audit API
* [ ] Connect reset API
* [ ] Connect visualization recommendation API
* [ ] Connect visualization generation API
* [ ] Connect export API
* [ ] Connect session deletion API

### State Management

Verify that frontend state correctly reflects:

```text
No Dataset
      ↓
Uploading
      ↓
Dataset Loaded
      ↓
Analysis Available
      ↓
Quality Issues Available
      ↓
Cleaning
      ↓
Cleaned Dataset
      ↓
Visualization
      ↓
Export
```

### Acceptance

* [ ] No hardcoded fake backend results remain
* [ ] Frontend uses documented API contract
* [ ] Loading states work
* [ ] Error states work
* [ ] Backend changes appear correctly in frontend
* [ ] Reset correctly updates frontend state
* [ ] Clear Session returns UI to initial state

---

# 15. Phase 10 — Testing & Benchmarking

**Owner:** HUMAN
**Implementation support:** OPENCODE + ANTIGRAVITY

## Goal

Verify that V1 is reliable enough for release.

### Backend Tests

* [ ] Upload tests
* [ ] Format tests
* [ ] Type inference tests
* [ ] Missing-value tests
* [ ] Duplicate tests
* [ ] Type-mismatch tests
* [ ] Suspicious-value tests
* [ ] Cleaning tests
* [ ] Audit tests
* [ ] Reset tests
* [ ] Analysis tests
* [ ] Visualization tests
* [ ] Export tests
* [ ] Session tests

### API Tests

* [ ] Success responses
* [ ] Validation errors
* [ ] Missing session
* [ ] Invalid column
* [ ] Invalid cleaning action
* [ ] Invalid visualization configuration
* [ ] Unsupported format
* [ ] Oversized input

### Frontend Tests

* [ ] Upload UI
* [ ] Analysis UI
* [ ] Quality UI
* [ ] Cleaning UI
* [ ] Audit UI
* [ ] Visualization UI
* [ ] Export UI
* [ ] Error states
* [ ] Loading states
* [ ] Empty states

### E2E

* [ ] Complete happy-path workflow
* [ ] Cleaning workflow
* [ ] Reset workflow
* [ ] Visualization workflow
* [ ] Export workflow
* [ ] Session cleanup workflow

---

# 16. Large Dataset Benchmark

**Owner:** HUMAN
**Support:** OPENCODE

## Goal

Determine the real operating boundary of V1.

### Benchmark Sizes

* [ ] 100 MB
* [ ] 500 MB
* [ ] 1 GB
* [ ] 2 GB
* [ ] 5 GB

### Measure

* [ ] Ingestion time
* [ ] Peak RAM
* [ ] Analysis time
* [ ] Quality detection time
* [ ] Cleaning time
* [ ] Export time
* [ ] Visualization time
* [ ] Stability
* [ ] Failure behavior

### Important

Do not claim that V1 supports 5 GB simply because the architecture is designed with large datasets in mind.

Record the actual tested limit.

### Acceptance

* [ ] Benchmark results documented
* [ ] Practical operating boundary identified
* [ ] README updated with tested limitation
* [ ] Known performance bottlenecks documented

---

# 17. Phase 11 — Deployment

**Owner:** HUMAN
**Support:** ANTIGRAVITY + OPENCODE

## Goal

Deploy a production-like version for demonstration.

### Frontend

* [ ] Create production build
* [ ] Configure backend API URL
* [ ] Verify environment variables
* [ ] Deploy frontend

### Backend

* [ ] Configure production server
* [ ] Configure environment variables
* [ ] Configure CORS
* [ ] Configure temporary storage
* [ ] Configure session cleanup
* [ ] Deploy backend

### Verification

* [ ] Upload works in deployment
* [ ] Analysis works
* [ ] Quality detection works
* [ ] Cleaning works
* [ ] Audit works
* [ ] Visualization works
* [ ] Export works
* [ ] Session cleanup works
* [ ] No localhost dependency remains

---

# 18. Phase 12 — V1 Freeze

**Owner:** HUMAN

## Goal

Freeze the tested V1 and prevent uncontrolled scope expansion.

### Final Checks

* [ ] All critical V1 functionality works
* [ ] Core E2E workflow passes
* [ ] API contract matches implementation
* [ ] Documentation matches implementation
* [ ] Original dataset preservation verified
* [ ] Export integrity verified
* [ ] Session isolation verified
* [ ] Session cleanup verified
* [ ] Large-dataset benchmark completed
* [ ] Deployment verified
* [ ] No critical/high defects remain

### Release

* [ ] Create final Git commit
* [ ] Create Git tag/version
* [ ] Update README
* [ ] Record known limitations
* [ ] Record tested dataset size
* [ ] Prepare demonstration dataset
* [ ] Perform final demo rehearsal

---

# 19. Git Checkpoints

Git should be used throughout development rather than only at the end.

Recommended checkpoints:

```text
checkpoint-01-documentation
checkpoint-02-backend-foundation
checkpoint-03-frontend-foundation
checkpoint-04-ingestion
checkpoint-05-analysis
checkpoint-06-quality
checkpoint-07-cleaning
checkpoint-08-visualization
checkpoint-09-export
checkpoint-10-integration
checkpoint-11-testing
checkpoint-12-v1-release
```

Use normal commits during each phase.

Do not create a release tag until V1 acceptance is complete.

---

# 20. Integration Gates

Each major phase should have a gate before the next phase begins.

## Gate 1 — Backend Foundation

```text
FastAPI runs
+
tests run
+
API structure exists
```

## Gate 2 — Data Lifecycle

```text
Upload
+
Session
+
Original/Working dataset
```

## Gate 3 — Data Quality

```text
Analysis
+
Quality Detection
+
Exact Locations
```

## Gate 4 — Cleaning

```text
Replace
+
Remove
+
Ignore
+
Audit
+
Reset
```

## Gate 5 — Visualization

```text
Recommendation
+
Chart Generation
```

## Gate 6 — Export

```text
CSV
+
XLSX
+
JSON
```

## Gate 7 — Full Integration

```text
Frontend
↕
FastAPI
↕
Processing Engine
```

## Gate 8 — Release

```text
Testing
+
Benchmark
+
Deployment
+
Documentation
```

---

# 21. Bugs / Known Issues

Use this section as the active V1 defect list.

| ID      | Issue                  | Severity | Owner | Status |
| ------- | ---------------------- | -------- | ----- | ------ |
| BUG-001 | *Add discovered issue* | —        | —     | Open   |
| BUG-002 | *Add discovered issue* | —        | —     | Open   |

Do not remove resolved bugs from project history. Mark them as resolved or move them into the project's issue tracker.

---

# 22. Deferred Work

The following items are intentionally deferred.

## V1.x Candidates

Only implement after explicit review:

* [ ] Additional visualization customization
* [ ] Additional file-format support
* [ ] Improved large-dataset processing
* [ ] Additional quality rules
* [ ] Additional export options

---

# 23. V2 — ML Problem Setup & Training

Deferred until V1 is stable.

Potential V2 work:

* [ ] Target-column selection
* [ ] Feature selection
* [ ] Train/test split
* [ ] Classification workflow
* [ ] Regression workflow
* [ ] Logistic Regression
* [ ] Linear Regression
* [ ] Decision Tree
* [ ] Random Forest
* [ ] Model evaluation
* [ ] Accuracy
* [ ] Precision
* [ ] Recall
* [ ] F1
* [ ] R²
* [ ] Confusion matrix
* [ ] Basic model configuration

V2 should begin from the cleaned dataset produced by V1.

---

# 24. V3 — Controlled Model Comparison

Deferred until V2 is validated.

Potential V3 work:

* [ ] Multiple-model training
* [ ] Consistent preprocessing
* [ ] Consistent train/test conditions
* [ ] Cross-validation
* [ ] Model comparison
* [ ] Performance comparison
* [ ] Experiment tracking
* [ ] Model recommendations
* [ ] Research-oriented analysis

---

# 25. Explicitly Out of Scope

The following must not be added to V1 without a new scope decision:

```text
ML Training
AutoML
Neural Networks
Model Comparison
Model Ranking
Hyperparameter Optimization
Cross-validation
Database
Authentication
JWT
User Accounts
Multi-user Collaboration
Redis
Celery
Kubernetes
Complex Background Job Infrastructure
Power BI-style Dashboarding
Tableau-style Analytics
LLM-based Data Analysis
Chatbot
Fuzzy Duplicate Detection
Arbitrary Nested JSON Processing
```

Infrastructure may be introduced later if actual benchmark/deployment requirements justify it.

---

# 26. Scope-Control Rule

When a new feature is proposed, ask:

```text
1. Is it required by the V1 PRD?
2. Is it required by the V1 workflow?
3. Is it required for correctness?
4. Is it required for deployment?
5. Is it already documented?
```

If the answer is no to all of these, the feature should normally be deferred.

No AI agent should independently expand project scope.

---

# 27. Definition of Done

A task is considered complete only when:

```text
Implementation
      ↓
Test
      ↓
Review
      ↓
Integration
      ↓
Documentation
```

has been completed as applicable.

For major features:

* [ ] Implementation exists
* [ ] Relevant unit tests exist
* [ ] Integration/API tests exist where applicable
* [ ] Frontend integration exists where applicable
* [ ] Error handling exists
* [ ] Documentation is consistent
* [ ] Human review completed

---

# 28. Final V1 Checklist

## Documentation

* [ ] README complete
* [ ] PRD complete
* [ ] Architecture complete
* [ ] API complete
* [ ] Data Processing complete
* [ ] Testing complete
* [ ] TODO complete

## Backend

* [ ] FastAPI operational
* [ ] Session lifecycle operational
* [ ] CSV supported
* [ ] XLSX supported
* [ ] JSON supported
* [ ] Analysis operational
* [ ] Type inference operational
* [ ] Quality engine operational
* [ ] Cleaning operational
* [ ] Audit operational
* [ ] Reset operational
* [ ] Visualization operational
* [ ] Export operational

## Frontend

* [ ] Upload interface
* [ ] Dataset analysis
* [ ] Quality dashboard
* [ ] Issue resolution
* [ ] Audit display
* [ ] Visualization interface
* [ ] Export interface
* [ ] Loading states
* [ ] Error states
* [ ] Empty states

## Reliability

* [ ] Original data preserved
* [ ] Working dataset correct
* [ ] Row/column locations correct
* [ ] Audit trail correct
* [ ] Export integrity verified
* [ ] Session isolation verified
* [ ] Session cleanup verified
* [ ] Core E2E workflow passes

## Performance

* [ ] 100 MB benchmark
* [ ] 500 MB benchmark
* [ ] 1 GB benchmark
* [ ] 2 GB benchmark
* [ ] 5 GB benchmark attempted where practical
* [ ] Actual tested limit documented

## Deployment

* [ ] Frontend deployed
* [ ] Backend deployed
* [ ] Production API configured
* [ ] CORS verified
* [ ] File upload verified
* [ ] Export verified
* [ ] Session cleanup verified

## Release

* [ ] No critical defects
* [ ] No unresolved high-severity defects
* [ ] README updated
* [ ] Known limitations documented
* [ ] Final Git commit created
* [ ] V1 release/tag created
* [ ] Demo workflow rehearsed

---

# 29. Current Execution Rule

Development should proceed from the top of this document downward.

The next unfinished phase becomes the active implementation target.

Do not begin V2 work while V1 has unfinished core functionality unless the change is explicitly approved.

The priority is:

```text
Correctness
    ↓
Data Safety
    ↓
Integration
    ↓
Testing
    ↓
Performance
    ↓
UI Polish
    ↓
Future Features
```

---

# 30. V1 Completion Definition

ML Model Comparison Lab V1 is complete when a user can reliably:

```text
Upload
   ↓
Understand
   ↓
Detect
   ↓
Correct
   ↓
Verify
   ↓
Visualize
   ↓
Export
   ↓
Clear
```

using the documented interfaces and processing rules, with the original dataset preserved throughout the workflow.

At that point, the project has a stable foundation on which V2 ML functionality can be built.
