# ML Model Comparison Lab — Testing Strategy & Verification Plan

**Document Version:** 1.0
**Project Version:** V1
**Status:** Testing Specification
**Last Updated:** September 2026

---

# 1. Purpose

This document defines the testing and verification strategy for **ML Model Comparison Lab V1**.

The purpose of testing is to verify that the implemented system behaves according to:

* `PRD.md`
* `ARCHITECTURE.md`
* `API.md`
* `DATA_PROCESSING.md`

Testing must verify both:

1. **Correctness** — the system produces the expected result.
2. **Safety of transformation** — user data is not unintentionally modified, lost, or corrupted.

The V1 system is considered complete only when its core workflow has been tested end-to-end.

---

# 2. V1 Testing Boundary

Testing covers:

```text
Dataset Upload
      ↓
Dataset Analysis
      ↓
Data Quality Detection
      ↓
Issue Review
      ↓
Cleaning
      ↓
Re-analysis
      ↓
Visualization
      ↓
Export
      ↓
Session Cleanup
```

Testing does **not** cover:

* ML model training
* Logistic Regression
* Linear Regression
* Decision Trees
* Random Forest
* Model comparison
* Accuracy/F1/R² evaluation
* Hyperparameter tuning
* Cross-validation
* AutoML
* Neural networks
* Experiment tracking
* Authentication
* Database persistence

These belong to future versions.

---

# 3. Testing Philosophy

The project should use a layered testing strategy.

```text
                    ┌──────────────────┐
                    │   E2E Testing    │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │ Integration/API  │
                    └────────┬─────────┘
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
        Data Quality     Cleaning         Analysis
             │               │               │
             └───────────────┼───────────────┘
                             ▼
                    Unit-Level Testing
```

Testing should begin with deterministic backend logic and progress toward full frontend-to-backend workflows.

---

# 4. Testing Levels

## 4.1 Unit Tests

Test individual processing functions independently.

Examples:

* Type inference
* Missing-value detection
* Duplicate detection
* Replacement calculation
* Row removal
* Audit-record creation
* Statistical calculations
* Visualization recommendation rules
* Export formatting

Unit tests should use small deterministic datasets.

---

## 4.2 Integration Tests

Verify that multiple backend components work together.

Examples:

```text
Upload
  ↓
Session Creation
  ↓
Analysis
```

or:

```text
Quality Detection
  ↓
Cleaning
  ↓
Audit
  ↓
Re-analysis
```

Integration tests should verify state consistency.

---

## 4.3 API Tests

Verify the FastAPI contract defined in `API.md`.

Tests should cover:

* HTTP methods
* URLs
* Request schemas
* Response schemas
* Status codes
* Error codes
* Session handling
* File upload
* File export

---

## 4.4 Frontend Tests

Verify that the React frontend correctly:

* Uploads datasets
* Displays analysis
* Displays quality issues
* Shows row/column locations
* Sends cleaning actions
* Updates after mutations
* Displays visualization results
* Downloads exports
* Handles loading states
* Handles errors

The frontend should not independently reproduce backend data-processing logic.

---

## 4.5 End-to-End Tests

E2E tests should verify the complete user workflow.

Example:

```text
Upload CSV
   ↓
Inspect dataset
   ↓
Find missing value
   ↓
Replace with median
   ↓
Verify issue resolved
   ↓
Generate histogram
   ↓
Export CSV
   ↓
Verify exported dataset
```

---

# 5. Test Environment

Testing should be performed in at least:

### Development

```text
Frontend: local Vite development server
Backend: local FastAPI server
```

### Production-like

A deployment environment should be tested before final demonstration.

The production-like test should verify:

* Frontend ↔ backend communication
* CORS
* File uploads
* Export downloads
* Temporary session handling
* Visualization generation
* Error handling

---

# 6. Test Dataset Fixtures

Testing requires controlled datasets.

The project should maintain a small collection of test fixtures.

Recommended structure:

```text
tests/
├── fixtures/
│   ├── clean_small.csv
│   ├── missing_values.csv
│   ├── duplicates.csv
│   ├── type_mismatch.csv
│   ├── mixed_types.csv
│   ├── categorical.csv
│   ├── numerical.csv
│   ├── datetime.csv
│   ├── boolean.csv
│   ├── identifiers.csv
│   ├── visualization.csv
│   └── tabular.json
```

Excel fixtures should also be included for XLSX testing.

---

# 7. Baseline Clean Dataset

A baseline dataset should contain:

* Numerical columns
* Categorical columns
* Boolean values
* Date/time values where applicable
* No intentional quality problems

Expected result:

```text
Missing values = 0
Duplicate rows = 0
Known type mismatches = 0
```

This dataset verifies that the system does not report false issues on clean data.

---

# 8. Missing-Value Tests

## Test MV-001 — Detect Missing Numerical Value

Input:

```text
Age
21
24
NULL
28
```

Expected:

```text
Issue type: missing_value
Column: Age
Correct row location
```

The issue must identify the exact affected cell.

---

## Test MV-002 — Detect Missing Categorical Value

Input:

```text
Department
Engineering
Design
NULL
Marketing
```

Expected:

```text
Issue type: missing_value
Column: Department
Correct row location
```

---

## Test MV-003 — Multiple Missing Values

Dataset contains multiple missing cells.

Expected:

* Every relevant missing cell is detected.
* Missing count matches the dataset.
* Row/column locations are correct.

---

# 9. Missing-Value Cleaning Tests

## Test MVC-001 — Numerical Mean

Given:

```text
10
20
30
NULL
40
```

Select:

```text
Replace → Mean
```

Expected replacement:

```text
25
```

The original dataset must remain unchanged.

---

## Test MVC-002 — Numerical Median

Given:

```text
10
20
30
40
NULL
```

Select:

```text
Replace → Median
```

Expected replacement:

```text
25
```

---

## Test MVC-003 — Numerical Custom Value

Select:

```text
Replace → Custom
```

Value:

```text
50
```

Expected:

```text
NULL → 50
```

---

## Test MVC-004 — Categorical Mode

Given:

```text
Engineering
Design
Engineering
Marketing
NULL
```

Select:

```text
Replace → Mode
```

Expected replacement:

```text
Engineering
```

---

## Test MVC-005 — Categorical Custom Value

Expected:

```text
NULL → "Unknown"
```

---

## Test MVC-006 — Invalid Replacement

Attempt to insert an incompatible value into a typed column.

Expected:

* Request rejected.
* Dataset remains unchanged.
* Appropriate validation error returned.

---

# 10. Duplicate Detection Tests

## Test DUP-001 — Exact Duplicate Rows

Input:

```text
ID | Name | Age
1  | A    | 20
2  | B    | 21
2  | B    | 21
```

Expected:

```text
Duplicate record detected.
```

The API should identify the duplicate occurrence correctly.

---

## Test DUP-002 — Similar but Non-identical Rows

Example:

```text
1 | A | 20
1 | A | 21
```

Expected:

```text
Not classified as an exact duplicate.
```

V1 does not perform fuzzy duplicate detection.

---

## Test DUP-003 — Remove Duplicate

After user selects Remove:

Expected:

```text
Duplicate row removed from working dataset.
Original dataset unchanged.
```

---

# 11. Type Detection Tests

## Test TYPE-001 — Numerical Column

Input:

```text
Age
21
22
23
```

Expected:

```text
Type = numerical
```

---

## Test TYPE-002 — Categorical Column

Input:

```text
Department
Engineering
Design
Marketing
```

Expected:

```text
Type = categorical
```

---

## Test TYPE-003 — Boolean Column

Expected:

```text
Type = boolean
```

where the dataset clearly represents boolean values.

---

## Test TYPE-004 — Date/Time Column

Expected:

```text
Type = date_time
```

when values are consistently recognizable as dates/timestamps.

---

## Test TYPE-005 — Identifier Override

Example:

```text
Employee_ID
10001
10002
10003
```

If inferred as numerical but the user chooses:

```text
identifier
```

Expected:

* Effective type becomes `identifier`.
* Subsequent analysis respects the override where applicable.

---

# 12. Type-Incompatibility Tests

## Test TYPE-M-001 — Text in Numerical Column

Example:

```text
Age
21
22
Mumbai
24
```

Expected:

```text
Issue type = type_mismatch
Column = Age
Row = row containing Mumbai
```

The exact user-facing row number must be correct.

---

## Test TYPE-M-002 — Correct Numeric Value

A normal numerical value must not be reported as a type mismatch.

---

## Test TYPE-M-003 — Suspicious Numeric Value

Example:

```text
Age = 150
```

Expected behavior:

The system must not automatically classify this as a type mismatch solely because the value is unusual.

If the V1 processing rules classify domain-range anomalies separately, the behavior must follow `DATA_PROCESSING.md`.

---

# 13. Issue Location Tests

This is a critical V1 requirement.

Every cell-level quality issue must expose:

```text
Row
Column
Current Value
Issue Type
Severity
```

Example:

```text
Row: 17
Column: Age
Current Value: Mumbai
Issue: Type mismatch
```

Testing must verify the location against the source dataset.

---

# 14. Row Number Verification

The API uses user-facing **1-indexed row numbers**.

Example:

If the backend internally uses:

```text
index = 16
```

the API/UI must report:

```text
Row 17
```

Tests must explicitly verify this conversion.

Off-by-one errors are considered a V1 defect.

---

# 15. Replace / Remove / Ignore Tests

Every quality issue supporting user actions must be tested with:

```text
Replace
Remove
Ignore
```

---

## Replace

Expected:

* Correct cell changes.
* Audit record created.
* Original unchanged.
* Working dataset updated.

---

## Remove

Expected:

* Correct affected record/value is removed according to issue semantics.
* Row count changes correctly.
* Original unchanged.
* Audit record created.

---

## Ignore

Expected:

* Dataset value remains unchanged.
* Issue is not accidentally deleted from the underlying dataset.
* Decision may be represented in audit/state.

---

# 16. Original Dataset Preservation

This is a mandatory test category.

## Test ORG-001

Upload:

```text
original.csv
```

Perform:

```text
Replace
Remove
```

Expected:

```text
Original dataset = unchanged
Working dataset = modified
```

---

## Test ORG-002 — Reset

After multiple changes:

```text
Reset to Original
```

Expected:

```text
Working dataset = original dataset
has_changes = false
```

---

# 17. Audit Trail Tests

Every applied modification should produce an audit record containing, where applicable:

```text
Step
Timestamp
Row
Column
Original Value
Action
New Value
Issue Type
Status
```

Example:

```text
Row: 14
Column: Age
Original: NULL
Action: Replace
New Value: 25
Status: Applied
```

Tests should verify that audit information matches the actual transformation.

---

# 18. Audit Consistency Test

Perform:

```text
Replace
Remove
Ignore
```

Then request:

```http
GET /api/v1/sessions/{session_id}/audit
```

Expected:

* Correct number of records.
* Correct actions.
* Correct row/column.
* Correct original values.
* Correct resulting values.
* No fabricated modifications.

---

# 19. Analysis Tests

## Dataset-Level

Verify:

* Row count
* Column count
* Column names
* Missing counts
* Duplicate counts
* Unique counts

---

## Numerical Statistics

For a controlled dataset, independently calculate:

```text
Mean
Median
Minimum
Maximum
Standard deviation
```

Compare backend results against known expected values within an appropriate numerical tolerance.

---

## Categorical Statistics

Verify:

* Unique count
* Most frequent value
* Frequency count

---

# 20. Post-Clean Analysis

After cleaning:

```text
Before:
Missing Age = 4

Clean:
Replace 4 missing values

After:
Missing Age = 0
```

Tests must verify that analysis reflects the **current working dataset**.

The backend must not continue reporting stale values.

---

# 21. Visualization Recommendation Tests

Recommendations are deterministic.

Test representative dataset structures.

### One numerical column

Expected recommendation:

```text
Histogram
```

### Two numerical columns

Expected:

```text
Scatter
```

### Categorical column

Expected:

```text
Bar/Count
```

### Date + numerical

Expected:

```text
Line
```

### Multiple numerical columns

Expected:

```text
Correlation Heatmap
```

The recommendation engine should not require an LLM.

---

# 22. Visualization Generation Tests

Each implemented chart type must be tested using compatible data.

At minimum verify:

* Correct chart type requested
* Correct columns used
* Valid image generated
* Image can be rendered by frontend
* No unexpected server exception
* Invalid configuration returns a useful error

---

# 23. Visualization Input Validation

Test invalid combinations.

Example:

```text
Scatter plot
X = Department
Y = Age
```

If the chart requires numerical X/Y columns:

Expected:

```text
Request rejected
```

No invalid chart artifact should be generated.

---

# 24. Large Dataset Visualization Tests

When visualization is generated from a large dataset:

Verify:

* Full raw dataset is not unnecessarily plotted.
* Sampling/aggregation/binning can be applied where required.
* Response explicitly indicates whether sampling was used.
* User-facing explanation is available.

Example:

```text
sampling_applied = true
```

must not be omitted if sampling actually occurred.

---

# 25. File Upload Tests

Test all supported input formats:

```text
CSV
XLSX
Tabular JSON
```

Each format should:

* Create a valid session.
* Produce equivalent logical columns.
* Produce correct row/column counts.
* Produce correct analysis.

---

# 26. File Upload Error Tests

Test:

* Unsupported extension
* Corrupt CSV
* Corrupt XLSX
* Invalid JSON
* Non-tabular JSON
* Empty file
* Empty dataset
* Missing required file field
* Excessively large file

Expected behavior:

* Request rejected appropriately.
* Clear error returned.
* No partially initialized invalid session remains.

---

# 27. Export Tests

Test:

```text
CSV
XLSX
JSON
```

For each exported dataset:

1. Export the working dataset.
2. Re-open the exported file independently.
3. Compare:

   * Row count
   * Column count
   * Column names
   * Values
   * Relevant data types

The exported dataset must represent the current working state.

---

# 28. Export After Cleaning

Example:

```text
Original:
100 rows

Remove:
2 rows

Working:
98 rows
```

Export.

Expected:

```text
Exported dataset:
98 rows
```

The original dataset must still contain:

```text
100 rows
```

---

# 29. Round-Trip Tests

A useful integrity test is:

```text
Upload
  ↓
Analyze
  ↓
Export
  ↓
Re-import exported dataset
  ↓
Analyze again
```

Expected:

Core tabular structure should remain equivalent.

This test should be performed for:

```text
CSV → CSV
XLSX → XLSX
JSON → JSON
```

and useful cross-format combinations where practical.

---

# 30. API Contract Tests

Each documented endpoint must have tests for:

### Success

* Correct HTTP status
* Correct response structure
* Correct data

### Failure

* Correct HTTP status
* Correct error structure
* Correct error code

---

# 31. API Endpoint Test Matrix

| Endpoint                              | Success | Validation | Not Found | State Change |
| ------------------------------------- | ------: | ---------: | --------: | -----------: |
| `POST /sessions`                      |       ✓ |          ✓ |         — |            ✓ |
| `GET /sessions/{id}`                  |       ✓ |          — |         ✓ |            — |
| `GET /analysis`                       |       ✓ |          — |         ✓ |            — |
| `GET /quality`                        |       ✓ |          — |         ✓ |            — |
| `PATCH /columns/{name}/type`          |       ✓ |          ✓ |         ✓ |            ✓ |
| `POST /clean`                         |       ✓ |          ✓ |         ✓ |            ✓ |
| `POST /reset`                         |       ✓ |          — |         ✓ |            ✓ |
| `GET /audit`                          |       ✓ |          — |         ✓ |            — |
| `GET /visualizations/recommendations` |       ✓ |          — |         ✓ |            — |
| `POST /visualizations`                |       ✓ |          ✓ |         ✓ |            — |
| `GET /export`                         |       ✓ |          ✓ |         ✓ |            — |
| `DELETE /sessions/{id}`               |       ✓ |          — |         ✓ |            ✓ |

---

# 32. Error Handling Tests

The frontend must correctly handle:

```text
400
404
409
413
415
422
500
```

Tests should verify that users receive understandable messages rather than raw backend exceptions.

Example:

Bad:

```text
KeyError: 'Age'
```

Preferred:

```text
The requested column does not exist in the current dataset.
```

---

# 33. Session Isolation Tests

Although V1 does not have multi-user accounts, sessions must still be isolated.

Create:

```text
Session A
Session B
```

Upload different datasets.

Expected:

```text
Session A cannot read or modify Session B's dataset.
```

This test is especially important for deployed environments.

---

# 34. Session Cleanup Tests

Create a session.

Verify temporary resources exist as expected.

Then:

```http
DELETE /api/v1/sessions/{session_id}
```

Expected:

* Session becomes unavailable.
* Temporary resources are cleaned.
* Subsequent session requests return `404`.

---

# 35. Frontend State Tests

The frontend should correctly represent:

### Initial

```text
No dataset
```

### Uploading

```text
Loading
```

### Loaded

```text
Dataset available
```

### Quality issues found

```text
Issues displayed
```

### Cleaning

```text
Action in progress
```

### Cleaned

```text
Updated analysis
```

### Error

```text
Clear error state
```

### Session cleared

```text
Return to initial state
```

---

# 36. Loading-State Tests

Slow API operations must not make the interface appear frozen.

Verify loading indicators for:

* Upload
* Analysis
* Quality detection
* Cleaning
* Visualization
* Export where appropriate
* Reset
* Session clearing

Buttons that would cause duplicate operations should be appropriately disabled while the operation is running.

---

# 37. Empty-State Tests

Test:

* No dataset uploaded
* Dataset with zero rows where supported
* Dataset with no quality issues
* Dataset with no numerical columns
* Dataset with no categorical columns
* Dataset unsuitable for requested visualization

The UI should explain the state rather than displaying broken charts or empty panels without context.

---

# 38. Security Tests

V1 does not implement authentication, but basic application security must still be tested.

Test:

* Path traversal attempts
* Malformed upload requests
* Unsupported file types
* Oversized uploads
* Invalid session IDs
* Invalid column names
* Invalid visualization parameters
* Malformed JSON
* Unexpected request fields where relevant

Verify that internal filesystem paths, stack traces, and sensitive backend information are not exposed.

---

# 39. Dataset Privacy Tests

The application should avoid unnecessary retention of uploaded datasets.

Test that:

* Session data exists only for the intended session lifecycle.
* Clear Session removes temporary resources.
* Raw dataset contents are not unnecessarily written to application logs.
* Backend errors do not expose dataset contents.

---

# 40. CORS Tests

In production-like deployment verify:

* Authorized frontend origin can communicate with backend.
* Unexpected origins are not unnecessarily permitted.
* Upload requests work through configured CORS.
* Export requests work through configured CORS.

Development configuration may be more permissive than production configuration.

---

# 41. Performance Testing

Performance testing is particularly important because V1 is intended to handle datasets larger than ordinary demo files.

The project should benchmark progressively larger datasets.

Recommended benchmark sizes:

```text
100 MB
500 MB
1 GB
2 GB
5 GB
```

The benchmark does **not** imply that all sizes are guaranteed to work.

The purpose is to determine the tested operating boundary.

---

# 42. Performance Metrics

Record at minimum:

```text
File size
Row count
Column count
Upload/ingestion time
Peak RAM
Analysis time
Quality detection time
Cleaning time
Export time
Visualization time
Process stability
```

Where possible also record:

```text
CPU utilization
Disk usage
Output file size
```

---

# 43. Performance Test Matrix

| Dataset | Ingestion | Analysis | Quality | Cleaning |  Export | Visualization | Peak RAM |
| ------- | --------: | -------: | ------: | -------: | ------: | ------------: | -------: |
| 100 MB  |   Measure |  Measure | Measure |  Measure | Measure |       Measure |  Measure |
| 500 MB  |   Measure |  Measure | Measure |  Measure | Measure |       Measure |  Measure |
| 1 GB    |   Measure |  Measure | Measure |  Measure | Measure |       Measure |  Measure |
| 2 GB    |   Measure |  Measure | Measure |  Measure | Measure |       Measure |  Measure |
| 5 GB    |   Measure |  Measure | Measure |  Measure | Measure |       Measure |  Measure |

Actual results should be recorded after implementation.

---

# 44. Memory Testing

Special attention should be given to operations that can create large temporary structures.

Test:

* Dataset loading
* Duplicate detection
* Missing-value detection
* Statistical analysis
* Export
* Visualization

The test should identify whether an operation causes unacceptable memory growth.

The system should avoid unnecessary full-dataset copies.

---

# 45. Visualization Performance

Visualization should be tested separately from general dataset processing.

A large dataset may be processable but unsuitable for direct plotting.

Test:

```text
Small dataset → full visualization
Large dataset → sampling/aggregation
```

Verify that large visualizations do not unnecessarily consume extreme memory or produce unusably large artifacts.

---

# 46. Regression Testing

Whenever a backend or frontend feature is modified, previously passing core tests should be rerun.

At minimum, the regression suite should cover:

```text
Upload
Analysis
Quality
Cleaning
Original preservation
Reset
Audit
Visualization
Export
Session cleanup
```

A feature is not considered complete if it fixes one area while breaking an existing V1 workflow.

---

# 47. Critical Regression Scenarios

These scenarios should be preserved as permanent regression tests.

### Scenario A

```text
Upload
→ Missing value
→ Median replacement
→ Export
```

### Scenario B

```text
Upload
→ Type mismatch
→ Custom replacement
→ Re-analysis
```

### Scenario C

```text
Upload
→ Duplicate detection
→ Remove duplicate
→ Export
```

### Scenario D

```text
Upload
→ Multiple changes
→ Reset
→ Verify original
```

### Scenario E

```text
Upload
→ Visualization recommendation
→ Generate chart
```

---

# 48. End-to-End Acceptance Test

The primary V1 acceptance test should simulate a realistic user workflow.

## Dataset

Use a dataset containing:

* Numerical columns
* Categorical columns
* Missing values
* At least one exact duplicate
* At least one type-incompatible value
* Data suitable for visualization

## Workflow

```text
1. Upload dataset
2. Verify dataset summary
3. Open quality results
4. Verify exact row/column locations
5. Replace a numerical missing value using median
6. Replace a categorical missing value using mode
7. Replace a type mismatch using a custom value
8. Remove an exact duplicate
9. Verify audit records
10. Re-run analysis
11. Verify updated statistics
12. Generate recommended visualization
13. Generate custom visualization
14. Export cleaned CSV
15. Re-open exported CSV
16. Verify cleaned values
17. Verify original dataset remains unchanged
18. Clear session
19. Verify session no longer exists
```

The entire workflow must complete without data corruption or unexplained state changes.

---

# 49. Definition of Test Pass

A test passes when:

1. The actual result matches the expected result.
2. No unintended dataset mutation occurs.
3. The API returns the documented status/structure.
4. The frontend correctly represents the backend state where applicable.
5. No unexplained errors occur.

A test should not be marked as passed merely because the UI appears visually correct.

---

# 50. Defect Classification

Use the following categories.

### Critical

Prevents the core V1 workflow.

Examples:

* Dataset cannot be uploaded.
* Original data is overwritten.
* Cleaning corrupts the working dataset.
* Export produces incorrect data.
* Session data leaks between sessions.

### High

Major feature does not work correctly.

Examples:

* Missing values incorrectly detected.
* Row/column location incorrect.
* Cleaning action modifies the wrong cell.
* Analysis returns incorrect statistics.

### Medium

Feature works but has a significant usability or reliability problem.

Examples:

* Incorrect loading state.
* Visualization recommendation is wrong.
* Audit information incomplete.

### Low

Minor UI/documentation issue that does not affect core correctness.

---

# 51. Test Evidence

For important acceptance tests, preserve evidence such as:

* Test output
* Screenshots
* API response examples
* Exported test files
* Benchmark measurements
* Error logs where relevant

Evidence is especially useful for:

* Large-dataset benchmarks
* Export integrity
* Original-data preservation
* End-to-end testing

---

# 52. Automated vs Manual Testing

Automate deterministic behavior wherever practical.

### Prefer automated tests for:

* Data-quality detection
* Type inference
* Cleaning calculations
* Duplicate detection
* Statistics
* API contracts
* Export integrity
* Session behavior

### Manual testing is appropriate for:

* Visual layout
* Interaction quality
* Accessibility checks
* Chart readability
* End-to-end demonstration flow
* User-facing error clarity

---

# 53. Accessibility Verification

The UI should be checked against the V1 accessibility target.

Verify:

* Keyboard navigation
* Visible focus states
* Form labels
* Button labels
* Table readability
* Sufficient text contrast
* Error messages
* Loading-state communication
* Non-color-only indication of quality severity

The application should not rely solely on color to communicate:

```text
Error
Warning
Success
```

---

# 54. Browser Testing

At minimum, test the production-like frontend in a current:

* Chrome/Chromium-based browser
* Firefox
* Edge

The primary development browser may be used for initial testing, but final validation should not depend on a single browser.

---

# 55. API and Frontend Contract Verification

A frontend feature should not be marked complete until:

```text
Frontend request
      ↓
API validation
      ↓
Backend processing
      ↓
API response
      ↓
Frontend rendering
```

has been verified.

If the frontend expects a field that the backend does not provide, the integration is incomplete.

---

# 56. Testing Against Documentation

Implementation must be checked against:

```text
PRD.md
ARCHITECTURE.md
API.md
DATA_PROCESSING.md
```

Any intentional deviation should be documented and resolved before V1 is considered final.

The implementation should not silently introduce:

* ML functionality
* Database requirements
* Authentication
* Unspecified visualization features
* Unsupported file formats
* Unspecified processing behavior

---

# 57. V1 Acceptance Boundary

V1 is accepted when the following are verified:

### Dataset

* [ ] CSV upload works
* [ ] XLSX upload works
* [ ] Tabular JSON upload works
* [ ] Invalid files are rejected correctly

### Analysis

* [ ] Dataset-level metrics are correct
* [ ] Numerical statistics are correct
* [ ] Categorical statistics are correct
* [ ] Type inference works
* [ ] Type override works

### Quality

* [ ] Missing values detected
* [ ] Exact duplicates detected
* [ ] Type mismatches detected
* [ ] Suspicious values are not blindly classified as errors
* [ ] Exact row locations are correct
* [ ] Exact column locations are correct

### Cleaning

* [ ] Replace works
* [ ] Remove works
* [ ] Ignore works
* [ ] Mean replacement works
* [ ] Median replacement works
* [ ] Mode replacement works
* [ ] Custom replacement works
* [ ] Original dataset is preserved
* [ ] Reset works
* [ ] Audit records are correct

### Visualization

* [ ] Deterministic recommendations work
* [ ] Implemented chart types generate correctly
* [ ] Invalid configurations are rejected
* [ ] Large-data visualization communicates sampling/aggregation

### Export

* [ ] CSV export works
* [ ] XLSX export works
* [ ] JSON export works
* [ ] Exported data matches working dataset

### Sessions

* [ ] Sessions are isolated
* [ ] Session state is consistent
* [ ] Clear Session works
* [ ] Temporary resources are removed

### Quality and reliability

* [ ] API errors are handled
* [ ] Frontend loading/error states work
* [ ] Core E2E workflow passes
* [ ] Regression tests pass
* [ ] Performance benchmarks are recorded

---

# 58. V1 Performance Acceptance

The project must not claim support for a specific large-dataset size solely because the architecture was designed for it.

Instead:

```text
Test
 ↓
Measure
 ↓
Record
 ↓
Determine practical limit
```

The README should state the **tested** dataset size and relevant limitations after benchmarking.

For example:

```text
Tested successfully up to X GB under environment Y.
```

Only publish such a claim after actual testing.

---

# 59. Final V1 Verification Flow

The final verification process is:

```text
                 IMPLEMENTATION
                       │
                       ▼
                Unit Tests
                       │
                       ▼
              Integration Tests
                       │
                       ▼
                  API Tests
                       │
                       ▼
                Frontend Tests
                       │
                       ▼
                  E2E Tests
                       │
                       ▼
            Performance Benchmarks
                       │
                       ▼
             Production-like Test
                       │
                       ▼
              Documentation Check
                       │
                       ▼
              V1 Acceptance Review
```

Only after this process should V1 be considered ready for demonstration/release.

---

# 60. Final Principle

Testing for ML Model Comparison Lab V1 is not only about checking whether buttons work.

The central question is:

> **Can the system safely take a real tabular dataset, identify genuine quality problems at exact locations, allow the user to make controlled corrections, preserve the original data, produce correct analysis and visualizations, export the resulting dataset without corruption, and cleanly terminate the temporary session?**

If the answer is demonstrably yes through the tests defined here, the V1 foundation is ready for the future ML layers.

The future ML model-training and model-comparison functionality must introduce its own testing strategy when V2/V3 development begins.
