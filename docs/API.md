# ML Model Comparison Lab — API Contract

**Document Version:** 1.0
**Project Version:** V1
**Status:** API Specification
**Last Updated:** September 2026

---

# 1. Purpose

This document defines the REST API contract between the **React frontend** and the **FastAPI backend** for ML Model Comparison Lab V1.

The API exists to support the following workflow:

```text
Upload Dataset
      ↓
Create Session
      ↓
Dataset Analysis
      ↓
Quality Detection
      ↓
Review Issues
      ↓
Apply Cleaning Actions
      ↓
Re-analyze
      ↓
Visualize
      ↓
Export
      ↓
Clear Session
```

The API is the communication boundary between:

```text
React + TypeScript
        │
        │ REST / HTTP
        ▼
FastAPI + Python
        │
        ▼
Data Processing Layer
```

The backend is the authoritative source for dataset processing and transformation.

---

# 2. V1 API Scope

The V1 API supports:

* Dataset upload
* Dataset/session creation
* Dataset metadata
* Dataset analysis
* Column type inference
* Column type override
* Data-quality detection
* Missing-value detection
* Exact duplicate detection
* Type-incompatibility detection
* Suspicious-value handling according to V1 processing rules
* Replace operations
* Remove operations
* Ignore operations
* Reset to original
* Audit information
* Visualization recommendations
* Visualization generation
* Dataset export
* Session clearing

The V1 API does **not** support:

* User accounts
* JWT authentication
* OAuth
* Persistent projects
* Database-backed sessions
* ML model training
* Model comparison
* AutoML
* Experiment tracking
* Hyperparameter tuning
* Model evaluation
* Real-time streaming APIs

---

# 3. API Base Path

All V1 endpoints use:

```text
/api/v1
```

Local development example:

```text
http://localhost:<BACKEND_PORT>/api/v1
```

The exact backend port is determined by the development configuration.

Production deployments must use HTTPS.

---

# 4. Communication Format

The API uses:

* HTTP
* REST
* JSON for structured requests/responses
* `multipart/form-data` for file uploads
* Binary file responses for dataset exports
* Image responses or image references for generated visualizations

GraphQL is not used in V1.

---

# 5. Session Model

V1 uses a temporary single-user session model.

A successful dataset upload creates a `session_id`.

Example:

```text
POST /api/v1/sessions
        ↓
session_id
        ↓
All subsequent operations reference session_id
```

Example:

```text
/api/v1/sessions/{session_id}/analysis
/api/v1/sessions/{session_id}/quality
/api/v1/sessions/{session_id}/clean
/api/v1/sessions/{session_id}/visualizations
```

The session represents the temporary working context for one uploaded dataset.

---

# 6. Session Lifecycle

The intended lifecycle is:

```text
             CREATE
                │
                ▼
          Active Session
                │
       ┌────────┼────────┐
       │        │        │
       ▼        ▼        ▼
    Analyze   Clean   Visualize
       │        │        │
       └────────┼────────┘
                │
                ▼
             Export
                │
                ▼
          Clear Session
```

A session may contain:

```text
Original Dataset
Working Dataset
Dataset Metadata
Inferred Types
Quality Issues
Audit Records
Temporary Visualization Artifacts
```

No persistent user account is associated with the session.

---

# 7. Common Response Structure

Successful JSON responses should follow a predictable structure.

Recommended:

```json
{
  "success": true,
  "data": {}
}
```

Example:

```json
{
  "success": true,
  "data": {
    "session_id": "sess_abc123",
    "row_count": 1000,
    "column_count": 8
  }
}
```

---

# 8. Common Error Structure

Errors should use a consistent structure:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable explanation."
  }
}
```

Example:

```json
{
  "success": false,
  "error": {
    "code": "UNSUPPORTED_FILE_TYPE",
    "message": "Only CSV, XLSX, and tabular JSON files are supported."
  }
}
```

The `code` is intended for frontend logic.

The `message` is intended for display/logging.

---

# 9. HTTP Status Codes

The following status codes should be used consistently.

| Status                       | Meaning                                           |
| ---------------------------- | ------------------------------------------------- |
| `200 OK`                     | Successful operation                              |
| `201 Created`                | Resource/session successfully created             |
| `400 Bad Request`            | Invalid request                                   |
| `404 Not Found`              | Session/resource does not exist                   |
| `409 Conflict`               | Request conflicts with current session state      |
| `413 Payload Too Large`      | Uploaded file exceeds configured limit            |
| `415 Unsupported Media Type` | Unsupported file/content type                     |
| `422 Unprocessable Entity`   | Request structure is valid but values are invalid |
| `500 Internal Server Error`  | Unexpected backend failure                        |

The backend should avoid exposing internal exception details to the user.

---

# 10. Endpoint Overview

| Method   | Endpoint                                                | Purpose                           |
| -------- | ------------------------------------------------------- | --------------------------------- |
| `POST`   | `/sessions`                                             | Upload dataset and create session |
| `GET`    | `/sessions/{session_id}`                                | Get session/dataset overview      |
| `GET`    | `/sessions/{session_id}/analysis`                       | Get dataset analysis              |
| `GET`    | `/sessions/{session_id}/quality`                        | Detect/get quality issues         |
| `PATCH`  | `/sessions/{session_id}/columns/{column_name}/type`     | Override inferred column type     |
| `POST`   | `/sessions/{session_id}/clean`                          | Apply a cleaning action           |
| `POST`   | `/sessions/{session_id}/reset`                          | Reset working dataset to original |
| `GET`    | `/sessions/{session_id}/audit`                          | Get audit records                 |
| `GET`    | `/sessions/{session_id}/visualizations/recommendations` | Get chart recommendations         |
| `POST`   | `/sessions/{session_id}/visualizations`                 | Generate visualization            |
| `GET`    | `/sessions/{session_id}/export`                         | Export working dataset            |
| `DELETE` | `/sessions/{session_id}`                                | Clear session                     |

---

# 11. Create Dataset Session

## Endpoint

```http
POST /api/v1/sessions
```

## Purpose

Uploads a dataset, validates it, creates a temporary session, and initializes the original and working dataset representations.

---

## Request

Content type:

```text
multipart/form-data
```

Field:

```text
file
```

Example:

```text
file = employees.csv
```

Supported formats:

```text
.csv
.xlsx
.json
```

JSON must represent tabular data as an array of records.

Example:

```json
[
  {
    "Name": "Aditya",
    "Age": 21
  },
  {
    "Name": "Rahul",
    "Age": 22
  }
]
```

Arbitrary deeply nested JSON is outside V1 scope.

---

## Response

Status:

```text
201 Created
```

Example:

```json
{
  "success": true,
  "data": {
    "session_id": "sess_abc123",
    "dataset": {
      "filename": "employees.csv",
      "format": "csv",
      "row_count": 2,
      "column_count": 2,
      "columns": [
        {
          "name": "Name",
          "type": "categorical"
        },
        {
          "name": "Age",
          "type": "numerical"
        }
      ]
    }
  }
}
```

---

# 12. Get Session Overview

## Endpoint

```http
GET /api/v1/sessions/{session_id}
```

## Purpose

Returns the current dataset/session overview.

The response should represent the **current working dataset state** while also identifying that the original dataset remains available for reset.

---

## Response

Status:

```text
200 OK
```

Example:

```json
{
  "success": true,
  "data": {
    "session_id": "sess_abc123",
    "filename": "employees.csv",
    "format": "csv",
    "original_row_count": 1000,
    "current_row_count": 998,
    "column_count": 8,
    "has_changes": true,
    "columns": [
      {
        "name": "Name",
        "type": "categorical"
      },
      {
        "name": "Age",
        "type": "numerical"
      }
    ]
  }
}
```

---

# 13. Dataset Analysis

## Endpoint

```http
GET /api/v1/sessions/{session_id}/analysis
```

## Purpose

Returns analysis of the current working dataset.

Analysis includes:

### Dataset-level

* Row count
* Column count
* Column names
* Missing-value counts
* Duplicate counts
* Unique-value information
* File metadata where applicable

### Numerical columns

* Mean
* Median
* Minimum
* Maximum
* Standard deviation

### Categorical columns

* Unique count
* Most frequent value
* Frequency information

### Date/time columns

Basic temporal information where applicable.

### Boolean columns

True/False counts where applicable.

---

## Response

```json
{
  "success": true,
  "data": {
    "row_count": 1000,
    "column_count": 5,
    "columns": [
      {
        "name": "Age",
        "type": "numerical",
        "missing_count": 3,
        "unique_count": 71,
        "statistics": {
          "mean": 27.4,
          "median": 25.0,
          "min": 18.0,
          "max": 67.0,
          "std": 8.42
        }
      },
      {
        "name": "Department",
        "type": "categorical",
        "missing_count": 1,
        "unique_count": 6,
        "most_frequent": {
          "value": "Engineering",
          "count": 210
        }
      }
    ],
    "duplicate_row_count": 4
  }
}
```

Values that cannot be meaningfully calculated should use `null` rather than fabricated values.

---

# 14. Column Type Override

## Endpoint

```http
PATCH /api/v1/sessions/{session_id}/columns/{column_name}/type
```

## Purpose

Allows the user to override the backend's inferred column type.

Supported logical types:

```text
numerical
categorical
date_time
boolean
identifier
text
```

---

## Request

```json
{
  "type": "identifier"
}
```

---

## Response

```json
{
  "success": true,
  "data": {
    "column_name": "Employee_ID",
    "previous_type": "numerical",
    "current_type": "identifier"
  }
}
```

After a type override, quality detection and analysis should use the updated type where applicable.

---

# 15. Data Quality Detection

## Endpoint

```http
GET /api/v1/sessions/{session_id}/quality
```

## Purpose

Runs or returns quality detection for the current working dataset.

The quality engine checks for:

1. Missing values
2. Exact duplicate records
3. Type-incompatible values
4. Other explicitly supported V1 quality conditions

The backend must distinguish between:

* clearly invalid/incompatible values
* suspicious observations that are not automatically considered cleaning errors

For example, a numeric `Age = 150` should not automatically be classified as a type mismatch simply because it looks unusual.

---

# 16. Quality Response

Example:

```json
{
  "success": true,
  "data": {
    "summary": {
      "total_issues": 7,
      "missing_values": 4,
      "duplicate_records": 2,
      "type_mismatches": 1
    },
    "issues": [
      {
        "issue_id": "issue_001",
        "issue_type": "missing_value",
        "severity": "warning",
        "row_index": 14,
        "column_name": "Age",
        "raw_value": null,
        "suggested_actions": [
          "replace",
          "remove",
          "ignore"
        ]
      },
      {
        "issue_id": "issue_002",
        "issue_type": "type_mismatch",
        "severity": "error",
        "row_index": 27,
        "column_name": "Age",
        "raw_value": "Mumbai",
        "detected_type": "text",
        "expected_type": "numerical",
        "suggested_actions": [
          "replace",
          "remove",
          "ignore"
        ]
      }
    ]
  }
}
```

---

# 17. Row Number Convention

The API should use one consistent convention.

For user-facing issue locations:

```text
row_index = 1-indexed
```

Example:

```text
row_index: 14
```

means the user should see:

```text
Row 14
```

The backend may internally use zero-based dataframe indexing.

Conversion should happen at the API boundary.

This prevents implementation details from leaking into the UI.

---

# 18. Duplicate Issue Representation

V1 uses **exact full-row duplicate detection**.

Fuzzy matching is not supported.

A duplicate issue may contain:

```json
{
  "issue_id": "issue_003",
  "issue_type": "duplicate_record",
  "severity": "warning",
  "primary_row_index": 10,
  "duplicate_row_index": 24
}
```

The API should make it clear which record is the original occurrence and which record is the duplicate.

---

# 19. Cleaning Operations

## Endpoint

```http
POST /api/v1/sessions/{session_id}/clean
```

## Purpose

Applies one explicit user-approved cleaning action to the working dataset.

The backend must not mutate the original dataset.

Supported actions:

```text
replace
remove
ignore
```

---

# 20. Replace Missing Numerical Value

Example request:

```json
{
  "issue_id": "issue_001",
  "action": "replace",
  "method": "median"
}
```

Supported numerical replacement methods:

```text
mean
median
custom
```

---

# 21. Replace Missing Categorical Value

Example:

```json
{
  "issue_id": "issue_004",
  "action": "replace",
  "method": "mode"
}
```

Supported categorical replacement methods:

```text
mode
custom
```

---

# 22. Custom Replacement

Example:

```json
{
  "issue_id": "issue_005",
  "action": "replace",
  "method": "custom",
  "value": "Engineering"
}
```

The backend must validate that the replacement value is compatible with the effective column type.

---

# 23. Type-Mismatch Replacement

For an invalid value such as:

```text
Age = "Mumbai"
```

the user may provide an explicit replacement.

Example:

```json
{
  "issue_id": "issue_002",
  "action": "replace",
  "method": "custom",
  "value": 24
}
```

The backend validates the value against the column's current effective type.

---

# 24. Remove Operation

A remove operation deletes the affected record from the working dataset.

Example:

```json
{
  "issue_id": "issue_002",
  "action": "remove"
}
```

The original dataset remains unchanged.

---

# 25. Ignore Operation

Ignore means:

```text
Keep the current value unchanged.
```

Example:

```json
{
  "issue_id": "issue_002",
  "action": "ignore"
}
```

Ignoring an issue should not modify the dataset.

The system may record the decision in the audit trail.

---

# 26. Cleaning Response

Successful cleaning:

```text
200 OK
```

Example:

```json
{
  "success": true,
  "data": {
    "action": {
      "issue_id": "issue_001",
      "action": "replace",
      "status": "applied",
      "row_index": 14,
      "column_name": "Age",
      "original_value": null,
      "new_value": 25
    },
    "dataset": {
      "row_count": 1000,
      "has_changes": true
    }
  }
}
```

The frontend should refresh relevant analysis/quality information after a successful mutation.

---

# 27. Audit Endpoint

## Endpoint

```http
GET /api/v1/sessions/{session_id}/audit
```

## Purpose

Returns the recorded actions associated with the current session.

---

## Response

```json
{
  "success": true,
  "data": {
    "records": [
      {
        "step": 1,
        "timestamp": "2026-09-18T14:30:00Z",
        "row_index": 14,
        "column_name": "Age",
        "original_value": null,
        "action": "replace",
        "new_value": 25,
        "issue_type": "missing_value",
        "status": "applied"
      }
    ]
  }
}
```

The audit trail describes modifications and decisions made during the current session.

---

# 28. Reset to Original

## Endpoint

```http
POST /api/v1/sessions/{session_id}/reset
```

## Purpose

Discard all modifications to the working dataset and restore it from the original dataset.

---

## Request

No request body required.

---

## Response

```json
{
  "success": true,
  "data": {
    "reset": true,
    "row_count": 1000,
    "has_changes": false
  }
}
```

After reset:

* Working dataset = original dataset
* Previous working modifications are no longer active
* Analysis should reflect the restored state
* Quality detection should reflect the restored state

---

# 29. Visualization Recommendations

## Endpoint

```http
GET /api/v1/sessions/{session_id}/visualizations/recommendations
```

## Purpose

Returns deterministic chart recommendations based on the current dataset structure.

No LLM is required.

---

# 30. Recommendation Rules

The initial rules include:

| Dataset Pattern            | Recommendation      |
| -------------------------- | ------------------- |
| One numerical column       | Histogram           |
| Two numerical columns      | Scatter plot        |
| Categorical column         | Bar/count plot      |
| Date + numerical           | Line chart          |
| Multiple numerical columns | Correlation heatmap |

The recommendation engine may return additional context explaining why a chart was recommended.

---

## Response

```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "chart_type": "histogram",
        "reason": "Age is a numerical column and its distribution can be examined using a histogram.",
        "columns": [
          "Age"
        ]
      },
      {
        "chart_type": "scatter",
        "reason": "Height and Weight are numerical columns and can be compared using a scatter plot.",
        "columns": [
          "Height",
          "Weight"
        ]
      }
    ]
  }
}
```

---

# 31. Generate Visualization

## Endpoint

```http
POST /api/v1/sessions/{session_id}/visualizations
```

## Purpose

Generates a visualization from the current working dataset.

The backend uses:

* Matplotlib
* Seaborn

V1 primarily generates static images.

---

# 32. Visualization Request

Example:

```json
{
  "chart_type": "histogram",
  "x_column": "Age"
}
```

---

## Scatter Plot Example

```json
{
  "chart_type": "scatter",
  "x_column": "Age",
  "y_column": "Salary"
}
```

---

## Bar Chart Example

```json
{
  "chart_type": "bar",
  "x_column": "Department",
  "y_column": "Salary",
  "aggregation": "mean"
}
```

---

# 33. Supported V1 Chart Types

The V1 visualization system may support:

### Basic

```text
scatter
bar
pie
line
histogram
box
area
```

### Statistical / analytical

```text
heatmap
pair
violin
count
kde
distribution
```

The final implemented set must match the actual backend capability and testing results.

---

# 34. Visualization Configuration

The request may contain:

```json
{
  "chart_type": "scatter",
  "x_column": "Age",
  "y_column": "Salary",
  "group_by": "Department"
}
```

Only fields relevant to the selected chart type should be required.

The backend must validate:

* Chart type
* Column existence
* Column compatibility
* Aggregation compatibility
* Required/optional parameters

---

# 35. Visualization Response

Recommended response:

```json
{
  "success": true,
  "data": {
    "visualization_id": "viz_001",
    "format": "png",
    "image_base64": "iVBORw0KGgo...",
    "sampling_applied": false,
    "sampling_note": null
  }
}
```

The exact transport mechanism may instead use a temporary image URL/reference if that is more appropriate for the deployment environment.

The contract must preserve the same semantic information:

```text
Visualization
Format
Image/Artifact Reference
Sampling Status
Sampling Explanation
```

---

# 36. Large Dataset Visualization

When a dataset is too large for practical full-data visualization, the backend may apply:

* Sampling
* Aggregation
* Binning

If this happens, the response must indicate it.

Example:

```json
{
  "sampling_applied": true,
  "sampling_note": "Visualization generated from a representative sample of the dataset."
}
```

The API must not silently present a sampled visualization as if it represented every raw row.

The exact threshold for applying sampling should be determined through benchmarking.

---

# 37. Export Dataset

## Endpoint

```http
GET /api/v1/sessions/{session_id}/export?format=csv
```

Supported formats:

```text
csv
xlsx
json
```

---

# 38. Export Examples

CSV:

```http
GET /api/v1/sessions/sess_abc123/export?format=csv
```

XLSX:

```http
GET /api/v1/sessions/sess_abc123/export?format=xlsx
```

JSON:

```http
GET /api/v1/sessions/sess_abc123/export?format=json
```

The exported dataset represents the **current working dataset**.

---

# 39. Export Response

Successful export:

```text
200 OK
```

The response is a binary file attachment.

Expected header concept:

```text
Content-Disposition: attachment; filename="cleaned_dataset.csv"
```

Appropriate content types should be returned.

Examples:

```text
text/csv
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
application/json
```

---

# 40. Original Dataset Export

If the frontend provides an explicit V1 control for exporting the original dataset, the API should support a clear distinction between:

```text
original
```

and:

```text
working
```

However, the minimum V1 export contract is the current working/cleaned dataset.

If original export is implemented, it should not overwrite or alter the working dataset.

---

# 41. Clear Session

## Endpoint

```http
DELETE /api/v1/sessions/{session_id}
```

## Purpose

Ends the current session and removes temporary session resources.

Resources may include:

* Original temporary file
* Working dataset
* Temporary visualization artifacts
* Session metadata
* Audit information

---

## Response

```json
{
  "success": true,
  "data": {
    "session_id": "sess_abc123",
    "cleared": true
  }
}
```

After successful deletion:

```text
GET /api/v1/sessions/{session_id}
```

should return:

```text
404 Not Found
```

---

# 42. Session Not Found

Example:

```http
GET /api/v1/sessions/invalid_session
```

Response:

```json
{
  "success": false,
  "error": {
    "code": "SESSION_NOT_FOUND",
    "message": "The requested session does not exist or has expired."
  }
}
```

Status:

```text
404
```

---

# 43. Unsupported File

Example:

```text
dataset.exe
```

Response:

```json
{
  "success": false,
  "error": {
    "code": "UNSUPPORTED_FILE_TYPE",
    "message": "Only CSV, XLSX, and tabular JSON files are supported."
  }
}
```

Status:

```text
415
```

---

# 44. Invalid Cleaning Request

Example:

```json
{
  "issue_id": "issue_001",
  "action": "replace",
  "method": "standard_deviation"
}
```

If the method is not supported as a replacement method:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REPLACEMENT_METHOD",
    "message": "The requested replacement method is not supported for this column."
  }
}
```

Status:

```text
422
```

Standard deviation is an analytical statistic, not itself a normal missing-value replacement method.

---

# 45. Invalid Column

Example:

```json
{
  "chart_type": "histogram",
  "x_column": "UnknownColumn"
}
```

Response:

```json
{
  "success": false,
  "error": {
    "code": "COLUMN_NOT_FOUND",
    "message": "The requested column does not exist in the current dataset."
  }
}
```

Status:

```text
422
```

---

# 46. Invalid Visualization Configuration

Example:

```json
{
  "chart_type": "scatter",
  "x_column": "Department",
  "y_column": "Age"
}
```

If the chart requires numerical columns:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_COLUMN_TYPE",
    "message": "Scatter plots require compatible numerical columns."
  }
}
```

---

# 47. File Size Limit

If a configured upload limit is exceeded:

```json
{
  "success": false,
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "The uploaded file exceeds the configured dataset size limit."
  }
}
```

Status:

```text
413
```

The actual deployment-specific file-size limit must be documented separately and must not be fabricated in this API specification.

---

# 48. Request Validation

FastAPI/Pydantic schemas should validate structured requests.

Validation should cover:

* Required fields
* Data types
* Enumerated values
* Column names
* Session identifiers
* Cleaning methods
* Visualization parameters
* Export formats

Invalid requests should fail before expensive data processing begins where practical.

---

# 49. Dataset State Consistency

All operations that modify the dataset must operate on the current working state.

Example:

```text
Initial:
1000 rows

Remove row:
1000 → 999

Second operation:
must operate on 999-row working dataset
```

The original remains:

```text
1000 rows
```

---

# 50. Re-analysis After Mutation

After any successful dataset mutation:

```text
Replace
Remove
Reset
```

the frontend should request updated information as necessary.

Recommended sequence:

```text
POST /clean
       ↓
GET /analysis
       ↓
GET /quality
```

This keeps the frontend synchronized with backend state.

The backend may alternatively return enough updated information to reduce requests, but the semantic result must remain equivalent.

---

# 51. Idempotency Considerations

V1 does not require a formal distributed idempotency-key system.

However, mutation endpoints should avoid accidentally applying the same issue action multiple times when possible.

For example, once an issue has been resolved:

```text
issue_001
status = resolved
```

A subsequent attempt to apply the same action should return a clear response rather than silently applying an unintended transformation.

Possible response:

```json
{
  "success": false,
  "error": {
    "code": "ISSUE_ALREADY_RESOLVED",
    "message": "This quality issue has already been resolved."
  }
}
```

---

# 52. API and Data-Processing Boundary

The API describes **what operation is requested**.

`DATA_PROCESSING.md` defines **how that operation is performed**.

Example:

### API

```json
{
  "action": "replace",
  "method": "median"
}
```

### Data-processing layer

Determines:

* Which column is affected
* Which values are missing
* How median is calculated
* Which value is inserted
* How the working dataset is modified
* How the audit record is generated

This separation prevents processing logic from being duplicated inside API route handlers.

---

# 53. API Route Responsibility

API route handlers should remain thin.

Preferred architecture:

```text
HTTP Request
     ↓
FastAPI Route
     ↓
Validate Request
     ↓
Call Service
     ↓
Data Processing
     ↓
Build Response
     ↓
HTTP Response
```

Avoid placing large Polars/Pandas transformation logic directly inside route definitions.

---

# 54. Frontend Integration Contract

Antigravity should treat the API as the backend source of truth.

The frontend should:

* Send validated requests
* Store the current `session_id`
* Render backend results
* Display backend quality issues
* Submit explicit cleaning actions
* Refresh state after mutations
* Handle loading states
* Handle empty states
* Handle API errors
* Never assume a cleaning operation succeeded without a successful API response

---

# 55. Backend Integration Contract

OpenCode should ensure that:

* Every documented endpoint exists before frontend integration is considered complete.
* Request and response schemas remain stable.
* Errors use documented codes.
* Dataset state is session-specific.
* Original data is never mutated by cleaning operations.
* User-facing row indices follow the API convention.
* Large visualization responses communicate sampling/aggregation.
* Export responses use correct file types.
* Temporary resources can be cleared.

---

# 56. Example Complete Workflow

## Step 1 — Upload

```http
POST /api/v1/sessions
```

Response:

```text
session_id = sess_abc123
```

---

## Step 2 — Analysis

```http
GET /api/v1/sessions/sess_abc123/analysis
```

---

## Step 3 — Quality Detection

```http
GET /api/v1/sessions/sess_abc123/quality
```

Response identifies:

```text
Row 14
Column Age
Issue: Missing Value
```

---

## Step 4 — User Chooses Median Replacement

```http
POST /api/v1/sessions/sess_abc123/clean
```

```json
{
  "issue_id": "issue_001",
  "action": "replace",
  "method": "median"
}
```

---

## Step 5 — Backend Applies Change

```text
Validate
   ↓
Calculate median
   ↓
Modify working dataset
   ↓
Create audit record
   ↓
Return success
```

---

## Step 6 — Refresh Analysis

```http
GET /api/v1/sessions/sess_abc123/analysis
```

---

## Step 7 — Refresh Quality

```http
GET /api/v1/sessions/sess_abc123/quality
```

---

## Step 8 — Get Recommendations

```http
GET /api/v1/sessions/sess_abc123/visualizations/recommendations
```

---

## Step 9 — Generate Chart

```http
POST /api/v1/sessions/sess_abc123/visualizations
```

```json
{
  "chart_type": "histogram",
  "x_column": "Age"
}
```

---

## Step 10 — Export

```http
GET /api/v1/sessions/sess_abc123/export?format=csv
```

---

## Step 11 — Clear Session

```http
DELETE /api/v1/sessions/sess_abc123
```

---

# 57. API Security Requirements

V1 has no authentication, but API security still matters.

The backend should:

* Validate uploaded files
* Validate request bodies
* Restrict file paths
* Prevent path traversal
* Avoid executing uploaded content
* Restrict CORS in production
* Avoid exposing internal filesystem paths
* Avoid exposing internal stack traces
* Avoid logging raw dataset contents unnecessarily
* Isolate session resources
* Clean temporary resources

Authentication and authorization are future concerns.

---

# 58. API Performance Requirements

The API should be designed to avoid unnecessary dataset transfers.

For example, the frontend should not repeatedly download the complete dataset merely to display:

```text
Row count
Column count
Missing count
Duplicate count
```

These values should be returned as metadata/analysis responses.

For large datasets, expensive operations should be benchmarked.

The API must not claim a specific maximum dataset size until tested.

---

# 59. Large Dataset Considerations

The backend should be prepared for larger datasets through:

* Polars-first processing
* Avoiding unnecessary dataframe copies
* Avoiding unnecessary Polars/Pandas conversions
* Temporary file strategies where appropriate
* Sampling/aggregation for visualization
* Explicit benchmarking

The API itself should remain independent of the exact benchmarked maximum.

For example, the API should not hard-code a claim such as:

```text
"Supports 5 GB files"
```

unless this has been experimentally verified for the deployment environment.

---

# 60. API Documentation and OpenAPI

FastAPI automatically provides OpenAPI documentation.

The implementation should expose development documentation through FastAPI's standard tooling.

The generated OpenAPI specification should remain consistent with this document.

The code-level schemas are the executable API contract; this document describes the intended product-level contract.

If a discrepancy appears between implementation and this document, the discrepancy must be resolved rather than silently ignored.

---

# 61. V1 Endpoint Checklist

### Sessions

* [ ] `POST /sessions`
* [ ] `GET /sessions/{session_id}`
* [ ] `DELETE /sessions/{session_id}`

### Analysis

* [ ] `GET /sessions/{session_id}/analysis`

### Types

* [ ] `PATCH /sessions/{session_id}/columns/{column_name}/type`

### Quality

* [ ] `GET /sessions/{session_id}/quality`

### Cleaning

* [ ] `POST /sessions/{session_id}/clean`
* [ ] `POST /sessions/{session_id}/reset`

### Audit

* [ ] `GET /sessions/{session_id}/audit`

### Visualization

* [ ] `GET /sessions/{session_id}/visualizations/recommendations`
* [ ] `POST /sessions/{session_id}/visualizations`

### Export

* [ ] `GET /sessions/{session_id}/export`

---

# 62. V1 API Acceptance Criteria

The API contract is considered implemented when:

* [ ] Dataset upload creates a valid session.
* [ ] Unsupported files return a documented error.
* [ ] Every session has isolated dataset state.
* [ ] The original dataset remains unchanged.
* [ ] Working-dataset mutations are reflected in subsequent requests.
* [ ] Analysis returns the current working-dataset statistics.
* [ ] Quality detection identifies exact row/column locations.
* [ ] User-facing row indices are 1-indexed.
* [ ] Duplicate detection uses exact duplicate semantics.
* [ ] Cleaning supports Replace/Remove/Ignore.
* [ ] Numerical missing replacement supports Mean/Median/Custom.
* [ ] Categorical missing replacement supports Mode/Custom.
* [ ] Custom replacement values are validated.
* [ ] Cleaning operations produce audit records.
* [ ] Reset restores the working dataset to the original state.
* [ ] Visualization recommendations are deterministic.
* [ ] Visualization generation returns a usable image/artifact.
* [ ] Sampling/aggregation is explicitly reported when used.
* [ ] CSV/XLSX/JSON export works.
* [ ] Session clearing removes temporary session resources.
* [ ] Errors use documented status codes and error structures.
* [ ] API behavior does not require authentication or a database in V1.

---

# 63. V1 Scope Boundary

The API must not expand into the old ML Model Comparison Lab API during V1.

The following endpoints are explicitly deferred:

```text
/model/train
/model/evaluate
/models/compare
/experiments
/metrics
/predict
/hyperparameters
/cross-validation
```

These belong to future ML-focused versions.

---

# 64. Final API Contract

The V1 API can be summarized as:

```text
                    ┌─────────────────┐
                    │ React Frontend  │
                    └────────┬────────┘
                             │
                         REST / HTTP
                             │
                             ▼
                    ┌─────────────────┐
                    │    FastAPI      │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
       Dataset             Quality          Analysis
       Session             Cleaning         Statistics
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                             ▼
                     Working Dataset
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
              Visualization        Export
                    │                 │
                    ▼                 ▼
                PNG/SVG          CSV/XLSX/JSON
```

The fundamental contract is:

> **The frontend requests operations; the FastAPI backend validates and executes them; the data-processing layer owns dataset state and transformation logic; responses provide structured results that the frontend can render without duplicating backend processing rules.**

V1 therefore provides a clean integration boundary between **Antigravity's frontend implementation** and **OpenCode's backend implementation**, while leaving future ML functionality outside the current API surface.
