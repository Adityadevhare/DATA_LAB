# ML Model Comparison Lab — System Architecture

**Document Version:** 1.0
**Project Version:** V1
**Status:** Architecture Specification
**Last Updated:** September 2026

---

# 1. Purpose

This document defines the technical architecture of the **ML Model Comparison Lab — V1**.

V1 is a web-based data preparation and analysis platform focused on:

* Dataset ingestion
* Dataset inspection
* Data-type inference
* Data-quality detection
* Missing-value handling
* Duplicate detection
* Type/value compatibility detection
* Interactive data correction
* Dataset analysis
* Visualization
* Dataset export

V1 is intentionally **not** an ML training or model-comparison platform.

The architecture is designed so that machine-learning functionality can be added in later versions without requiring a complete rewrite of the V1 application.

---

# 2. V1 Architectural Goal

The primary architectural goal is to create a clear separation between:

1. **User interface**
2. **Application/API layer**
3. **Data-processing layer**
4. **Visualization and export operations**

The system should remain simple enough for V1 while maintaining clear boundaries between components.

The intended architecture is:

```text
                    ┌──────────────────────┐
                    │        User          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   React Frontend     │
                    │ TypeScript + Vite    │
                    │ Tailwind + shadcn/ui │
                    └──────────┬───────────┘
                               │
                         REST / JSON
                               │
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │      Python          │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌─────────────┐ ┌──────────────┐ ┌───────────────┐
       │ Data Engine │ │ Visualization│ │ Export Engine │
       │ Polars      │ │ Matplotlib   │ │ CSV/XLSX/JSON │
       │ Pandas      │ │ Seaborn      │ │               │
       └─────────────┘ └──────────────┘ └───────────────┘
```

---

# 3. Architecture Principles

The following principles govern V1 implementation.

## 3.1 Separation of Responsibilities

Each major component should have one primary responsibility.

The frontend should handle:

* User interaction
* Display
* Client-side state
* Validation that improves user experience
* Sending requests
* Rendering responses

The backend should handle:

* Dataset ingestion
* Data validation
* Data processing
* Data-quality detection
* Cleaning operations
* Analysis
* Visualization generation
* Export

The frontend should not implement core data-processing rules that need to remain consistent across the application.

---

## 3.2 Backend as the Processing Authority

The backend is the authoritative layer for dataset processing.

For example:

```text
Frontend:
"Replace missing Age values using median"

        ↓

Backend:
Validate request
        ↓
Calculate median
        ↓
Modify working dataset
        ↓
Create audit record
        ↓
Return updated result
```

The frontend should not independently calculate a replacement value and assume that it is correct.

This prevents differences between frontend and backend behavior.

---

## 3.3 Original Data Must Remain Untouched

The uploaded dataset must be treated as the original source.

Processing should operate on a separate working representation.

Conceptually:

```text
                    Uploaded Dataset
                           │
                           ▼
                    Original Dataset
                           │
                           │ copy / working representation
                           ▼
                    Working Dataset
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          Analysis      Cleaning      Visualization
                           │
                           ▼
                    Cleaned Dataset
                           │
                           ▼
                         Export
```

The original dataset must never be overwritten by a cleaning operation.

This allows the user to:

* Review detected issues
* Apply corrections
* Reset the working dataset
* Compare original and cleaned state
* Export the original dataset separately

---

# 4. High-Level System Topology

V1 uses a client-server architecture.

```text
┌─────────────────────────────────────────────────────────────┐
│                         Browser                             │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ React + TypeScript                                    │  │
│  │                                                       │  │
│  │ Upload │ Analysis │ Quality │ Cleaning │ Charts │     │  │
│  │ Export │                                             │  │
│  └──────────────────────────┬────────────────────────────┘  │
└─────────────────────────────┼───────────────────────────────┘
                              │
                         HTTP / REST
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                         │
│                                                             │
│  API Layer                                                  │
│       │                                                     │
│       ├── Session Management                                │
│       ├── Dataset Operations                                │
│       ├── Quality Operations                                │
│       ├── Analysis Operations                               │
│       ├── Visualization Operations                         │
│       └── Export Operations                                 │
│                              │                              │
│                              ▼                              │
│                     Data Processing Layer                    │
│                              │                              │
│                    ┌─────────┴─────────┐                    │
│                    │                   │                    │
│                 Polars              Pandas                  │
│                 Primary           Compatibility             │
│                                                             │
│             Matplotlib + Seaborn                            │
│                                                             │
│                     Temporary Storage                       │
└─────────────────────────────────────────────────────────────┘
```

---

# 5. Technology Stack

## 5.1 Frontend

| Technology   | Responsibility                 |
| ------------ | ------------------------------ |
| React        | UI component architecture      |
| TypeScript   | Type-safe frontend development |
| Vite         | Development/build tooling      |
| Tailwind CSS | Styling                        |
| shadcn/ui    | Reusable UI components         |

The frontend is a single-page application.

---

## 5.2 Backend

| Technology                           | Responsibility                                   |
| ------------------------------------ | ------------------------------------------------ |
| Python                               | Backend and data-processing language             |
| FastAPI                              | REST API framework                               |
| Polars                               | Primary dataframe/data-processing engine         |
| Pandas                               | Compatibility and library-boundary operations    |
| NumPy                                | Numerical operations                             |
| SciPy                                | Statistical/scientific operations where required |
| Matplotlib                           | Static visualization generation                  |
| Seaborn                              | Statistical visualization                        |
| openpyxl / appropriate Excel tooling | XLSX processing                                  |

---

# 6. Frontend Architecture

The frontend should be organized around application features rather than one large component.

A conceptual structure is:

```text
frontend/
│
├── src/
│   ├── components/
│   │   ├── upload/
│   │   ├── analysis/
│   │   ├── quality/
│   │   ├── cleaning/
│   │   ├── visualization/
│   │   └── export/
│   │
│   ├── pages/
│   │
│   ├── services/
│   │   └── api/
│   │
│   ├── types/
│   │
│   ├── hooks/
│   │
│   └── utils/
```

The exact directory structure may change during implementation, but feature boundaries should remain clear.

---

# 7. Backend Architecture

The backend should separate API routing from data-processing logic.

A conceptual structure is:

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── datasets.py
│   │   │   ├── quality.py
│   │   │   ├── analysis.py
│   │   │   ├── visualization.py
│   │   │   └── export.py
│   │
│   ├── services/
│   │   ├── ingestion/
│   │   ├── quality/
│   │   ├── cleaning/
│   │   ├── analysis/
│   │   ├── visualization/
│   │   └── export/
│   │
│   ├── models/
│   │
│   ├── schemas/
│   │
│   ├── session/
│   │
│   └── utils/
│
└── tests/
```

This is a conceptual architecture. Implementation may simplify or reorganize individual modules if there is a clear technical reason.

---

# 8. Frontend ↔ Backend Communication

Communication between frontend and backend uses:

```text
React
  │
  │ HTTP
  │ JSON / multipart form-data
  ▼
FastAPI
```

### Dataset upload

File uploads use multipart form-data.

Conceptually:

```text
POST /api/v1/datasets
Content-Type: multipart/form-data

file = dataset.csv
```

The backend processes the uploaded file and returns a dataset/session identifier plus initial metadata.

---

## 8.1 JSON API Responses

Normal API operations should return structured JSON.

Example:

```json
{
  "success": true,
  "data": {
    "dataset_id": "example-id",
    "row_count": 1000,
    "column_count": 8
  }
}
```

The exact API schema is defined in `API.md`.

---

## 8.2 Error Responses

Errors should also use a consistent structure.

Conceptually:

```json
{
  "success": false,
  "error": {
    "code": "UNSUPPORTED_FILE_TYPE",
    "message": "The uploaded file format is not supported."
  }
}
```

The frontend should use error codes for predictable UI behavior and messages for user-facing explanations.

---

# 9. Session Architecture

V1 does not require:

* User accounts
* Authentication
* JWT
* PostgreSQL
* Supabase
* MongoDB
* Persistent user profiles

Instead, V1 uses a temporary dataset/session concept.

Conceptually:

```text
Browser
   │
   │ session_id
   ▼
FastAPI
   │
   ├── Original Dataset
   ├── Working Dataset
   ├── Dataset Metadata
   └── Audit Information
```

A session identifier allows multiple requests from the same browser workflow to refer to the correct working dataset.

The exact session-storage implementation is an implementation decision governed by the API and data-processing requirements.

---

# 10. Dataset Lifecycle

The complete V1 dataset lifecycle is:

```text
Upload
  ↓
Validate
  ↓
Parse
  ↓
Create Session
  ↓
Store Original Dataset
  ↓
Create Working Dataset
  ↓
Analyze
  ↓
Detect Quality Issues
  ↓
Display Issues
  ↓
User Action
  │
  ├── Replace
  ├── Remove
  └── Ignore
  ↓
Update Working Dataset
  ↓
Record Audit Event
  ↓
Re-analyze
  ↓
Visualize
  ↓
Export
  ↓
Clear Session
```

---

# 11. Original Dataset vs Working Dataset

The distinction between original and working data is fundamental.

## Original Dataset

The original dataset represents exactly what the user uploaded after successful ingestion.

It should not be modified by normal cleaning operations.

---

## Working Dataset

The working dataset is the version on which user modifications are performed.

For example:

```text
Original:

Name       Age
Aditya     21
Rahul      22
Priya      null
```

After replacing the missing value:

```text
Working:

Name       Age
Aditya     21
Rahul      22
Priya      21
```

The original remains:

```text
Name       Age
Aditya     21
Rahul      22
Priya      null
```

---

# 12. Data-Processing Layer

The data-processing layer is the core backend subsystem.

Its responsibilities include:

```text
Input
 │
 ├── CSV
 ├── XLSX
 └── Tabular JSON
 │
 ▼
Ingestion
 │
 ▼
Type Inference
 │
 ▼
Dataset Analysis
 │
 ▼
Quality Detection
 │
 ├── Missing values
 ├── Exact duplicates
 ├── Type incompatibilities
 └── Suspicious values
 │
 ▼
Cleaning Operations
 │
 ▼
Post-clean Analysis
 │
 ▼
Visualization / Export
```

Detailed processing rules belong in `DATA_PROCESSING.md`.

---

# 13. Polars and Pandas Strategy

**Polars is the primary data-processing representation for V1.**

Pandas remains available where required for compatibility with libraries or operations that are more naturally performed using Pandas.

The preferred flow is:

```text
Input
  ↓
Polars
  ↓
Processing
  ↓
Polars
```

A conversion should occur only when a specific library boundary requires it.

For example:

```text
Polars
  ↓
Pandas conversion
  ↓
Library requiring Pandas
  ↓
Result
```

The application should avoid unnecessary repeated conversions such as:

```text
Polars → Pandas → Polars → Pandas
```

because this can increase memory usage and processing overhead, particularly for large datasets.

---

# 14. Data Quality Architecture

The quality subsystem should consist of independent detection mechanisms.

Conceptually:

```text
Working Dataset
      │
      ▼
Quality Engine
      │
      ├── Missing Detector
      │
      ├── Duplicate Detector
      │
      ├── Type Compatibility Detector
      │
      └── Suspicious Value Detector
      │
      ▼
Issue Collection
      │
      ▼
Issue Response
```

Each issue should contain enough information for the frontend to identify the affected location.

At minimum:

```text
Row
Column
Current Value
Issue Type
Severity
Suggested Action
```

User-facing row numbering should be **1-indexed**.

Internal dataframe indexing may use the indexing convention of the processing library.

---

# 15. Cleaning Architecture

Cleaning requests originate from the frontend but are executed by the backend.

Example:

```text
User selects:

Column: Age
Issue: Missing
Action: Replace
Method: Median
```

Flow:

```text
Frontend
   │
   │ cleaning request
   ▼
FastAPI
   │
   ▼
Validation
   │
   ▼
Cleaning Service
   │
   ├── Validate column
   ├── Validate method
   ├── Calculate replacement
   ├── Modify working dataset
   └── Create audit record
   │
   ▼
Updated Working Dataset
   │
   ▼
Response
```

---

# 16. Audit Architecture

Cleaning operations should generate audit information.

Conceptually:

```text
Audit Record
│
├── Step
├── Timestamp
├── Row
├── Column
├── Original Value
├── Action
├── New Value
├── Issue Type
└── Status
```

Example:

```text
Row: 14
Column: Age
Original: null
Action: Replace
New Value: 21
Issue: Missing Value
Status: Applied
```

The audit record describes changes made to the working dataset.

The audit trail should not become a replacement for version-control or database infrastructure in V1.

---

# 17. Reset Architecture

V1 requires a **Reset to Original** operation.

Conceptually:

```text
Original Dataset
       │
       ├───────────────┐
       │               │
       ▼               ▼
Working Dataset      Reset
       │               │
       ▼               │
Modifications         │
       │               │
       └───────────────┘
               │
               ▼
        Original State
```

Reset should:

1. Discard the current working modifications.
2. Recreate the working state from the original dataset.
3. Recalculate relevant analysis/quality information.
4. Update the frontend.

The original uploaded dataset remains unchanged.

---

# 18. Analysis Architecture

Analysis is performed against the current working dataset.

The analysis subsystem produces:

### Dataset-level information

* Row count
* Column count
* File size where applicable
* Column names
* Data types
* Missing-value counts
* Duplicate counts
* Unique-value information

### Numerical information

* Mean
* Median
* Minimum
* Maximum
* Standard deviation
* Basic distribution information

### Categorical information

* Unique-value count
* Most frequent value
* Frequency information

### Date/time information

Where recognized:

* Minimum date
* Maximum date
* Basic temporal distribution information

### Boolean information

Where recognized:

* True/False counts

---

# 19. Type Inference Architecture

The backend performs initial type inference.

Possible categories include:

```text
Numerical
Categorical/Text
Date/Time
Boolean
Identifier-like
```

Inference should be based on the actual data rather than only the file's storage representation.

For example:

```text
Employee_ID
1001
1002
1003
```

may technically appear numerical but can be identified as identifier-like.

The user may override the inferred type.

Conceptually:

```text
Detected Type
      │
      ▼
User Review
      │
      ├── Accept
      │
      └── Override
              │
              ▼
        Processing Type
```

---

# 20. Visualization Architecture

Visualization is generated from the current working dataset.

The architecture separates:

1. Recommendation
2. Configuration
3. Generation
4. Delivery

```text
Working Dataset
      │
      ▼
Visualization Recommendation Engine
      │
      ▼
Recommended Chart
      │
      ├───────────────┐
      │               │
      ▼               ▼
Accept             Custom
      │               │
      └───────┬───────┘
              ▼
      Visualization Config
              │
              ▼
      Chart Generation
              │
              ▼
      Matplotlib / Seaborn
              │
              ▼
          Image Output
```

V1 uses deterministic recommendation rules rather than an LLM.

Examples:

```text
1 numerical column
        ↓
Histogram

2 numerical columns
        ↓
Scatter plot

Categorical column
        ↓
Bar / Count plot

Date + numerical
        ↓
Line chart

Multiple numerical columns
        ↓
Correlation heatmap
```

These rules can evolve as the implementation gains more tested dataset patterns.

---

# 21. Visualization Output

The preferred V1 visualization output is a static image.

Primary format:

```text
PNG
```

Optional:

```text
SVG
```

Interactive HTML visualization is not required for V1.

The frontend should receive either:

* an image URL/reference, or
* an appropriate encoded/static representation,

depending on the final API implementation.

The exact response contract is defined in `API.md`.

---

# 22. Large Dataset Architecture

V1 is designed with larger datasets in mind, but the project must not claim a maximum dataset size before benchmarking.

Initial benchmarking should evaluate:

```text
100 MB
500 MB
1 GB
2 GB
5 GB
```

where the available environment permits.

Important measurements include:

* Upload/ingestion time
* Peak memory usage
* Analysis time
* Quality-detection time
* Cleaning time
* Export time
* Visualization generation time
* Overall stability

---

# 23. Large Dataset Visualization

Visualization should not automatically attempt to render every row of a very large dataset.

Potential strategies include:

```text
Large Dataset
      │
      ▼
Visualization Request
      │
      ▼
Determine Data Volume
      │
      ├── Manageable
      │       ↓
      │    Full Data
      │
      └── Very Large
              ↓
       Sampling / Aggregation
              ↓
         Visualization
```

Possible techniques include:

* Sampling
* Aggregation
* Binning

If the system uses sampling or aggregation, the UI should clearly indicate that the visualization does not represent every raw record individually.

The exact threshold should be established through testing rather than arbitrarily claimed as a fixed architectural limit.

---

# 24. Temporary Storage

V1 does not require persistent database storage.

Temporary storage may be implemented using:

* In-memory structures for smaller datasets
* Temporary server-side files
* A hybrid approach

The implementation should choose the mechanism that best balances:

* Memory usage
* Dataset size
* Performance
* Session isolation
* Cleanup reliability

The architecture must support explicit session cleanup.

---

# 25. Session Cleanup

V1 should provide a **Clear Session** operation.

Conceptually:

```text
User
 │
 ▼
Clear Session
 │
 ▼
Delete temporary working data
 │
 ├── Working Dataset
 ├── Original Dataset
 ├── Temporary Visualization Files
 └── Session Metadata
 │
 ▼
Session Ends
```

The application should not rely on browser-tab closure or browser-exit behavior as the primary cleanup mechanism.

Automatic expiration/TTL may be added if deployment conditions require it.

---

# 26. Security Architecture

V1 does not implement authentication or user accounts.

Nevertheless, the backend must treat uploaded files as untrusted input.

Important controls include:

* Validate file type
* Validate file size
* Validate request structure
* Validate column references
* Validate cleaning methods
* Avoid unsafe file-path construction
* Avoid executing uploaded content as code
* Prevent access to files belonging to other sessions
* Avoid logging raw dataset contents unnecessarily
* Clean temporary files appropriately
* Keep server-side secrets out of the frontend

---

# 27. Privacy Architecture

The application should minimize unnecessary retention of uploaded data.

V1 should not require permanent storage of user datasets.

The intended lifecycle is:

```text
Upload
  ↓
Temporary Processing
  ↓
User Analysis / Cleaning / Visualization
  ↓
Export
  ↓
Clear Session
  ↓
Temporary Data Removed
```

The system should not claim that data is processed entirely locally if the deployed architecture sends files to a remote backend.

The actual deployment model must be documented accurately.

---

# 28. Authentication and Authorization

Authentication is explicitly out of scope for V1.

Therefore:

```text
No JWT
No OAuth
No User Accounts
No Password System
No Role-Based Access Control
```

If authentication is introduced in a future version, it should be added at the API/application boundary rather than embedded into individual data-processing functions.

---

# 29. Database Architecture

V1 does not use:

* PostgreSQL
* MongoDB
* Supabase
* Persistent relational storage

The reason is scope.

V1 does not need:

* Persistent user accounts
* Saved projects
* Multi-user collaboration
* Experiment history
* Long-term dataset storage

A database can be introduced in a future version if the product requires persistent sessions or user-specific project storage.

---

# 30. Background Processing

V1 does not require a distributed task queue.

The initial architecture uses normal FastAPI request handling.

Conceptually:

```text
Frontend
   │
   ▼
FastAPI Request
   │
   ▼
Processing
   │
   ▼
Response
```

Technologies such as:

* Celery
* Redis
* Distributed workers

are not required initially.

If benchmarks demonstrate that large processing tasks make synchronous requests impractical, background processing can be introduced later.

---

# 31. Scalability Strategy

The architecture leaves room for future scaling without requiring V1 infrastructure.

Potential future architecture:

```text
                    Load Balancer
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           API-1      API-2      API-3
              │          │          │
              └──────────┼──────────┘
                         │
                    Job / Queue
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           Worker      Worker      Worker
              │          │          │
              └──────────┼──────────┘
                         │
                   Persistent Storage
```

This is future architecture only.

V1 should not introduce distributed infrastructure without a demonstrated need.

---

# 32. Failure Boundaries

The system should fail at clear boundaries.

Examples:

### Upload failure

```text
Upload
 ↓
Validation Failure
 ↓
Return structured error
 ↓
Frontend displays actionable message
```

### Processing failure

```text
Processing
 ↓
Exception
 ↓
Backend catches/logs safely
 ↓
Structured API error
 ↓
Frontend displays failure state
```

### Visualization failure

A visualization error should not destroy the dataset session.

For example:

```text
Dataset
  ↓
Cleaning
  ↓
Successful

Visualization
  ↓
Failed

Dataset remains available.
```

This separation is important because visualization is a secondary operation and should not invalidate the working dataset.

---

# 33. State Ownership

State should have a clear owner.

| State                           | Primary Owner              |
| ------------------------------- | -------------------------- |
| Current UI state                | Frontend                   |
| Selected visualization settings | Frontend                   |
| Dataset/session identifier      | Frontend + Backend         |
| Original dataset                | Backend                    |
| Working dataset                 | Backend                    |
| Quality issues                  | Backend                    |
| Audit records                   | Backend                    |
| Dataset statistics              | Backend                    |
| Generated visualization         | Backend/temp storage       |
| Exported file                   | Backend/generated artifact |

The frontend may cache backend responses for usability, but backend processing state remains authoritative.

---

# 34. API Versioning

The API should be versioned from the beginning.

Recommended structure:

```text
/api/v1/...
```

Example:

```text
/api/v1/datasets
/api/v1/analysis
/api/v1/quality
/api/v1/visualizations
/api/v1/export
```

This makes future API changes easier to manage.

---

# 35. V1 API Responsibility Boundary

The API should expose operations required by V1 only.

Conceptual responsibilities:

```text
Datasets
 ├── Upload
 ├── Metadata
 └── Session lifecycle

Quality
 ├── Detect issues
 └── Resolve issues

Analysis
 └── Generate analysis

Visualization
 ├── Recommend
 └── Generate

Export
 └── Download
```

Exact endpoint names, request schemas, response schemas, status codes, and examples belong in `API.md`.

---

# 36. Deployment Architecture

The exact production deployment provider is not fixed in V1.

The deployment must support:

```text
Browser
   │
   ▼
React Frontend
   │
   │ HTTPS
   ▼
Python/FastAPI Backend
   │
   ▼
Temporary Processing Environment
```

The frontend and backend may be deployed separately.

Example conceptual deployment:

```text
Frontend Hosting
       │
       │ HTTPS
       ▼
Backend Hosting
       │
       ▼
Python Runtime
       │
       ├── Polars
       ├── Pandas
       ├── NumPy
       ├── Matplotlib
       └── Seaborn
```

The chosen providers must be validated against:

* Python runtime availability
* File-upload limits
* Request-duration limits
* Memory limits
* Temporary storage behavior
* Deployment cost/free-tier limitations

No provider-specific limitation should be claimed until verified.

---

# 37. Local Development Architecture

For local development:

```text
┌──────────────────┐
│ Browser          │
│ localhost        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ React + Vite     │
│ Frontend         │
└────────┬─────────┘
         │ HTTP
         ▼
┌──────────────────┐
│ FastAPI          │
│ Python Backend   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Data Processing  │
│ Polars/Pandas    │
└──────────────────┘
```

The frontend and backend should be independently runnable during development.

---

# 38. CORS

During development, the FastAPI backend must permit requests from the configured frontend development origin.

Production CORS configuration should be restricted to the actual frontend origin rather than allowing arbitrary origins.

Example conceptual policy:

```text
Development:
localhost frontend → allowed

Production:
known frontend domain → allowed
unknown origins → rejected
```

---

# 39. Logging

Logging should support debugging without unnecessarily exposing user data.

Useful information includes:

* Request type
* Session identifier
* Processing duration
* Operation status
* Error code
* Exception information where appropriate

Avoid logging:

* Full uploaded datasets
* Sensitive cell contents
* Entire raw file contents
* Unnecessary personal information

---

# 40. Observability

V1 does not require a full enterprise observability stack.

Basic observability should be sufficient:

```text
Request
 ↓
Operation
 ↓
Duration
 ↓
Success / Failure
 ↓
Error information
```

Performance benchmarks should additionally record resource usage where practical.

---

# 41. V1 Architectural Constraints

The following constraints are intentional.

### No ML Training

V1 does not contain:

```text
Logistic Regression
Linear Regression
Decision Trees
Random Forest
Neural Networks
```

---

### No Model Comparison

There is no:

```text
Model ranking
Accuracy comparison
F1 comparison
RMSE comparison
R² comparison
Cross-validation
Hyperparameter tuning
```

---

### No Database

There is no persistent database in V1.

---

### No Authentication

There are no user accounts or JWT authentication mechanisms.

---

### No Distributed Job System

Celery/Redis-style infrastructure is not required.

---

### No LLM Dependency

Core data-quality detection and visualization recommendation do not depend on an LLM.

---

### No Full BI Platform

The project is not intended to reproduce:

* Power BI
* Tableau
* Enterprise data governance systems
* Full automated EDA platforms

---

# 42. Future Architecture

The architecture is intentionally extensible.

## V2 — ML Problem Setup + Training + Evaluation

Potential additions:

```text
Clean Dataset
      ↓
Problem Setup
      ↓
Feature / Target Selection
      ↓
Preprocessing
      ↓
Train/Test Split
      ↓
Model Training
      ↓
Evaluation
```

The existing V1 data-processing layer can remain the foundation.

---

# 43. V3 — Controlled Model Comparison + Research

Potential architecture:

```text
Clean Dataset
      ↓
Experiment Configuration
      ↓
Standardized Preprocessing
      ↓
Multiple Models
      ↓
Controlled Training
      ↓
Evaluation
      ↓
Comparison
      ↓
Visualization
      ↓
Experiment Record
```

Potential future components include:

* Experiment storage
* Model registry
* Persistent database
* Background workers
* Advanced visualization
* Reproducibility metadata
* Research-oriented experiment tracking

These components are intentionally excluded from V1.

---

# 44. Architectural Evolution

The intended evolution is:

```text
                    V1
       Data Preparation Platform
                    │
                    ▼
                   V2
       ML Problem Setup + Training
                    │
                    ▼
                   V3
       Controlled Model Comparison
                    │
                    ▼
              Research Platform
```

The architecture should therefore avoid V1 decisions that unnecessarily prevent these future extensions.

---

# 45. Component Responsibility Summary

| Component                | Primary Responsibility                           |
| ------------------------ | ------------------------------------------------ |
| React                    | User interface                                   |
| TypeScript               | Frontend type safety                             |
| Vite                     | Frontend build/development                       |
| Tailwind                 | Styling                                          |
| shadcn/ui                | UI components                                    |
| FastAPI                  | REST API/application layer                       |
| Polars                   | Primary data processing                          |
| Pandas                   | Compatibility operations                         |
| NumPy                    | Numerical computation                            |
| SciPy                    | Scientific/statistical operations where required |
| Matplotlib               | Static charts                                    |
| Seaborn                  | Statistical charts                               |
| openpyxl / Excel tooling | XLSX handling                                    |
| Temporary storage        | Session dataset/artifact storage                 |

---

# 46. Development Responsibility

The project currently uses separate development responsibilities.

## Antigravity

Responsible primarily for:

* React frontend
* TypeScript
* Vite
* Tailwind
* shadcn/ui
* Upload interface
* Dataset dashboard
* Quality dashboard
* Issue tables
* Cleaning controls
* Visualization interface
* Export interface
* Frontend API integration

---

## OpenCode

Responsible primarily for:

* Python backend
* FastAPI
* REST endpoints
* Polars/Pandas processing
* Dataset ingestion
* Type inference
* Data-quality detection
* Cleaning operations
* Audit records
* Analysis
* Visualization generation
* Export/conversion

---

## Human Project Owner

Responsible for:

* Architecture decisions
* Scope control
* Reviewing AI-generated implementation
* Integration
* Testing
* Validation
* Git/GitHub
* Final technical decisions

AI coding agents should not independently expand V1 scope or introduce major architectural components without review.

---

# 47. Architecture Decision Summary

The V1 architecture can be summarized as:

```text
React + TypeScript
        │
        │ REST
        ▼
FastAPI + Python
        │
        ▼
Polars-first Data Processing
        │
        ├── Data Quality
        ├── Cleaning
        ├── Analysis
        │
        ├── Matplotlib / Seaborn
        │
        └── CSV / XLSX / JSON Export
```

With:

```text
No database
No authentication
No ML training
No model comparison
No distributed workers
No LLM dependency
```

and:

```text
Original Dataset
       ≠
Working Dataset
```

The architecture prioritizes **clear responsibilities, data integrity, testability, practical performance, and future extensibility** without adding infrastructure that V1 does not require.

---

# 48. Architecture Acceptance Criteria

The architecture is considered implemented correctly when:

* [ ] Frontend and backend are separate applications.
* [ ] React communicates with FastAPI through REST.
* [ ] Dataset processing is performed on the backend.
* [ ] Polars is the primary processing representation where practical.
* [ ] Pandas is used only where required or useful for compatibility.
* [ ] Original uploaded data is preserved.
* [ ] Cleaning operates on a separate working dataset.
* [ ] Dataset state can be reset to the original.
* [ ] Quality issues contain exact user-facing row and column locations.
* [ ] Cleaning operations produce audit information.
* [ ] Analysis operates on the current working dataset.
* [ ] Visualization operates on the current working dataset.
* [ ] Large datasets do not automatically force full-row visualization.
* [ ] Temporary session data can be cleared.
* [ ] V1 does not require a persistent database.
* [ ] V1 does not require authentication.
* [ ] V1 does not require background-job infrastructure.
* [ ] API contracts are documented separately in `API.md`.
* [ ] Data-processing rules are documented separately in `DATA_PROCESSING.md`.
* [ ] Architecture decisions do not introduce V2/V3 ML functionality into V1.

---

# 49. Final V1 Architecture Statement

> **ML Model Comparison Lab V1 is a client-server data preparation platform in which a React/TypeScript frontend communicates with a Python/FastAPI backend. The backend owns dataset ingestion, quality detection, cleaning, analysis, visualization generation, and export. Polars is the primary data-processing engine, with Pandas used for compatibility where necessary. Uploaded datasets are preserved as immutable originals while user modifications are applied to a separate working dataset. V1 uses temporary session-based storage rather than a persistent database and intentionally excludes authentication, ML training, model comparison, and distributed processing.**

This architecture provides the foundation for future ML experimentation functionality while keeping V1 focused, testable, and operationally manageable.
