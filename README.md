# DATA Lab

A web-based data preparation, quality analysis, visualization, and export platform designed to help users understand and clean tabular datasets before using them for machine learning or further analysis.

> **Current Version: V1 — Data Preparation + Analysis + Visualization**

---

## 1. Overview

**ML Model Comparison Lab** is a web application for working with tabular datasets.

The V1 workflow focuses on the stages that should happen **before machine learning**:

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
Verify Cleaned Dataset
      ↓
Create Visualization
      ↓
Export Dataset
```

The system helps users identify problems such as:

* Missing values
* Duplicate records
* Incorrect or incompatible values
* Suspicious values
* Incorrectly inferred column types

Instead of simply reporting that a dataset contains errors, the system identifies **where the problem occurs**, including the relevant row and column whenever applicable.

The original uploaded dataset is preserved while corrections are applied to a separate working dataset.

---

# 2. Why This Project Exists

Machine-learning workflows often fail or produce unreliable results because the input data has not been properly inspected or prepared.

Common problems include:

```text
Missing values
Incorrect data types
Duplicate records
Invalid values
Unexpected values
Inconsistent categorical data
Incorrect column interpretation
```

A user should be able to inspect these problems before proceeding to later ML workflows.

The project therefore treats **data preparation as a first-class workflow**, rather than making it an invisible preprocessing step.

---

# 3. V1 Scope

V1 focuses on four core capabilities:

### 1. Data Preparation

Upload and inspect tabular datasets.

### 2. Data Quality

Detect and locate common data-quality problems.

### 3. Analysis & Visualization

Understand the structure and distribution of the cleaned dataset.

### 4. Export

Download the resulting dataset in a supported format.

---

# 4. Core Workflow

The complete V1 workflow is:

```text
┌─────────────────────┐
│   Upload Dataset    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Dataset Analysis    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Quality Detection   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Review Issues       │
│ Row + Column + Value│
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Replace / Remove /  │
│ Ignore              │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Cleaned Dataset     │
└───────┬───────┬─────┘
        │       │
        ↓       ↓
┌───────────┐ ┌───────────┐
│Visualize  │ │  Export   │
└───────────┘ └───────────┘
```

---

# 5. Main Features

## Dataset Upload

Supported input formats:

* CSV
* XLSX / Excel
* Tabular JSON

The application validates the uploaded file before processing it.

Only one dataset is processed within a session in V1.

---

## Dataset Analysis

After upload, the system provides an overview of the dataset.

### Dataset-level information

* Row count
* Column count
* File size
* Column names
* Detected data types
* Missing-value counts
* Duplicate information
* Unique-value information

### Numerical analysis

For numerical columns:

* Mean
* Median
* Minimum
* Maximum
* Standard deviation
* Basic distribution information

### Categorical analysis

For categorical columns:

* Unique-value count
* Most frequent value
* Frequency information

### Other detected types

The system can identify or classify columns as:

* Numerical
* Categorical / text
* Date / time
* Boolean
* Identifier-like

---

# 6. Data Type Inference

The system automatically attempts to determine the appropriate type of each column.

For example:

```text
Age          → Numerical
Name         → Text
JoiningDate  → Date
IsActive     → Boolean
Employee_ID  → Identifier
```

Automatic inference is not always correct.

Therefore, users can override the inferred type where necessary.

For example:

```text
Employee_ID
Detected: Numerical
User override: Identifier / Text
```

This allows downstream analysis and visualization to use the user's intended interpretation of the data.

---

# 7. Data Quality Detection

The system detects several categories of data-quality issues.

## Missing Values

The system identifies missing values and reports their locations.

For example:

```text
Row: 27
Column: Age
Issue: Missing Value
```

Users can choose an appropriate replacement strategy.

### Numerical columns

Available strategies include:

* Mean
* Median
* Custom value

### Categorical columns

Available strategies include:

* Mode
* Custom value

The system does not treat standard deviation as a missing-value replacement method.

Standard deviation is used as a statistical measure rather than a normal replacement value.

---

## Duplicate Records

V1 detects **exact duplicate rows**.

Example:

```text
Row 14 = Row 52
Issue: Duplicate Record
```

The system does not perform fuzzy duplicate detection in V1.

---

## Incorrect / Incompatible Values

The system identifies values that are incompatible with the expected column type.

Example:

```text
Column: Age
Expected Type: Numerical

Row 42:
Value = "Rahul"
```

The issue report should identify:

```text
Row
Column
Current Value
Issue Type
Severity
Suggested Action
```

---

## Suspicious Values

Some values may be unusual without necessarily being invalid.

For example:

```text
Age = 150
```

Such a value should not automatically be deleted merely because it is unusual.

The system distinguishes between:

```text
Clearly incompatible / invalid
        vs.
Suspicious / requires review
```

This allows the user to make the final decision.

---

# 8. Issue Resolution

Detected issues can be reviewed through the issue interface.

The primary actions are:

```text
[ Replace ]   [ Remove ]   [ Ignore ]
```

### Replace

Replace a problematic value with:

* Mean
* Median
* Mode
* Custom value

depending on the column type and issue.

### Remove

Remove:

* A problematic row
* A duplicate record
* Other explicitly removable data issues

### Ignore

Leave the original value unchanged and allow the user to continue.

---

# 9. Exact Issue Locations

One of the important design requirements of V1 is that the system should not merely say:

> "There are 17 data-quality issues."

It should tell the user **where those issues are**.

Example:

| Row | Column | Current Value | Issue            | Severity | Suggested Action |
| --: | ------ | ------------- | ---------------- | -------- | ---------------- |
|  12 | Age    | `abc`         | Type mismatch    | High     | Replace          |
|  27 | Salary | Empty         | Missing value    | Medium   | Replace          |
|  44 | Email  | `test@`       | Suspicious value | Low      | Review           |

User-facing row numbers are **1-indexed**.

---

# 10. Original vs Working Dataset

The uploaded dataset is never directly overwritten.

The application maintains two conceptual states:

```text
Original Dataset
      │
      ├── preserved
      │
      └── Working Dataset
               │
               ├── Replace
               ├── Remove
               └── Ignore
```

This provides a safe way to experiment with corrections.

Users can reset the working dataset back to the original uploaded state.

---

# 11. Audit Trail

Cleaning operations should be traceable.

A modification can be recorded as:

| Row | Column | Original  | Action  | New Value |
| --: | ------ | --------- | ------- | --------- |
|  27 | Age    | Empty     | Replace | 24        |
|  42 | Age    | `abc`     | Replace | 31        |
|  52 | —      | Duplicate | Remove  | —         |

The audit information allows users to understand what modifications were applied to the working dataset.

---

# 12. Visualization

After cleaning the dataset, users can create visualizations.

The system provides deterministic recommendations based on dataset structure.

Examples:

```text
1 numerical column
        ↓
Histogram

2 numerical columns
        ↓
Scatter Plot

Categorical column
        ↓
Bar / Count Plot

Date + numerical column
        ↓
Line Plot

Multiple numerical columns
        ↓
Correlation Heatmap
```

Recommendations are rule-based.

V1 does not require an LLM to recommend charts.

---

# 13. Supported Visualizations

The agreed V1 visualization set includes:

### Basic

* Scatter plot
* Bar chart
* Pie chart
* Line chart
* Histogram
* Box plot
* Area chart

### Statistical / Analytical

* Correlation heatmap
* Pair plot
* Distribution plot
* Violin plot
* Count plot
* KDE-based plot

Visualizations are generated using:

* Matplotlib
* Seaborn

Static image output is the primary V1 approach.

PNG is the preferred output format, with SVG support where implemented.

---

# 14. Visualization Customization

Users can create custom visualizations by selecting appropriate:

* Chart type
* X-axis
* Y-axis
* Grouping / color
* Aggregation
* Relevant chart settings

The goal is practical dataset visualization rather than reproducing the functionality of Tableau or Power BI.

---

# 15. Large Dataset Handling

The architecture is designed with larger datasets in mind, but V1 does **not** claim a guaranteed maximum dataset size before benchmarking.

Planned benchmark sizes include:

```text
100 MB
500 MB
1 GB
2 GB
5 GB
```

The benchmark will measure:

* Upload / ingestion time
* Peak memory usage
* Analysis time
* Quality detection time
* Cleaning time
* Export time
* Visualization time
* Stability

For large datasets, visualizations should not blindly attempt to render every row.

Depending on the dataset, the system may use:

* Sampling
* Aggregation
* Binning

When this occurs, the user should be informed.

The actual tested operating limit will be documented after benchmarking.

---

# 16. Supported File Formats

## Input

| Format       | V1        |
| ------------ | --------- |
| CSV          | Supported |
| XLSX / Excel | Supported |
| Tabular JSON | Supported |

## Output

| Format       | V1        |
| ------------ | --------- |
| CSV          | Supported |
| XLSX / Excel | Supported |
| Tabular JSON | Supported |

JSON support in V1 is intended for **tabular / array-of-records data**, not arbitrary deeply nested JSON structures.

Excel support focuses on tabular data and does not promise preservation of complex workbook features such as:

* Merged-cell layouts
* Charts
* Macros
* Complex formatting
* Workbook-specific automation

---

# 17. Technology Stack

## Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* shadcn/ui

## Backend

* Python
* FastAPI

## Data Processing

* Polars
* Pandas

Polars is the primary processing engine where practical.

Pandas may be used where library compatibility or functionality requires it.

The system should avoid unnecessary:

```text
Polars
   ↓
Pandas
   ↓
Polars
```

conversions.

---

## Scientific Computing

* NumPy
* SciPy where required

## Visualization

* Matplotlib
* Seaborn

## Excel

* openpyxl / appropriate Excel tooling

## Communication

* REST API

---

# 18. High-Level Architecture

```text
┌─────────────────────────────┐
│          Frontend           │
│                             │
│ React + TypeScript + Vite   │
│ Tailwind + shadcn/ui        │
└──────────────┬──────────────┘
               │
               │ REST API
               ↓
┌─────────────────────────────┐
│          FastAPI            │
│                             │
│ API / Session Management    │
└──────────────┬──────────────┘
               │
               ↓
┌─────────────────────────────┐
│      Processing Engine      │
│                             │
│ Polars / Pandas             │
│ NumPy / SciPy               │
│ Type Inference              │
│ Quality Detection           │
│ Cleaning                    │
│ Analysis                    │
└──────────────┬──────────────┘
               │
          ┌────┴─────┐
          ↓          ↓
┌────────────────┐ ┌────────────────┐
│ Visualization  │ │ File Export    │
│ Matplotlib     │ │ CSV            │
│ Seaborn        │ │ XLSX           │
└────────────────┘ │ JSON           │
                   └────────────────┘
```

V1 does not require a persistent database.

Temporary session-based storage is sufficient for the initial architecture.

---

# 19. Session Model

Each uploaded dataset is associated with a temporary session.

Conceptually:

```text
Session
│
├── Original Dataset
│
├── Working Dataset
│
├── Analysis
│
├── Quality Issues
│
├── Cleaning Operations
│
├── Audit Trail
│
└── Generated Visualizations
```

A session can be cleared when the user finishes working with the dataset.

The application should not rely on browser-exit behavior as its primary cleanup mechanism.

---

# 20. Privacy & Data Handling

V1 does not require:

* User accounts
* Authentication
* JWT
* Persistent database storage

Uploaded datasets are processed as part of the temporary session lifecycle.

The application should avoid unnecessary retention of uploaded data after the session is cleared or expires.

Dataset contents should not be unnecessarily written to application logs.

For deployment, the actual storage and retention behavior should match the deployed infrastructure configuration.

---

# 21. User Interface Philosophy

The interface is intended to feel like a serious technical data tool.

The design should prioritize:

* Clarity
* Precision
* Readability
* Data visibility
* Useful interaction
* Clear system states
* Consistent layouts
* Accessible controls

The interface should avoid unnecessary decorative patterns such as:

* Generic "AI" visual language
* Fake system-status indicators
* Excessive gradients
* Neon effects
* Glassmorphism
* Decorative AI sparkles
* Unnecessary animations
* Dashboard elements that do not communicate useful information

The product should communicate what is happening through actual data and system state.

---

# 22. Project Structure

The intended repository structure is:

```text
ML-Model-Comparison-Lab/
│
├── README.md
│
├── frontend/
│
├── backend/
│
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DATA_PROCESSING.md
│   └── TESTING.md
│
└── tasks/
    └── TODO.md
```

---

# 23. Documentation

The project documentation is divided by responsibility.

| Document                  | Purpose                        |
| ------------------------- | ------------------------------ |
| `README.md`               | What is this project?          |
| `docs/PRD.md`             | What are we building?          |
| `docs/ARCHITECTURE.md`    | How is it structured?          |
| `docs/API.md`             | How do components communicate? |
| `docs/DATA_PROCESSING.md` | How is data processed?         |
| `docs/TESTING.md`         | How is it verified?            |
| `tasks/TODO.md`           | Who builds what and when?      |

This separation prevents implementation details from being unnecessarily duplicated across documents.

---

# 24. Running the Project

The exact production/deployment configuration may evolve during implementation.

## Frontend

From the frontend directory:

```bash
npm install
npm run dev
```

The Vite development server will provide the local frontend URL.

---

## Backend

Create and activate a Python virtual environment, then install the backend dependencies.

Example:

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start FastAPI

The exact application entry point should match the backend implementation.

A typical development command is:

```bash
uvicorn app.main:app --reload
```

---

# 25. Development Workflow

Development should follow the project task board.

```text
Documentation
      ↓
Backend Foundation
      ↓
Frontend Foundation
      ↓
Dataset Ingestion
      ↓
Dataset Analysis
      ↓
Quality Detection
      ↓
Cleaning + Audit
      ↓
Visualization
      ↓
Export
      ↓
Integration
      ↓
Testing
      ↓
Benchmarking
      ↓
Deployment
      ↓
V1 Release
```

Each major phase should be tested before moving to the next.

---

# 26. Testing

The project uses multiple testing levels:

* Unit testing
* Backend/API testing
* Frontend testing
* Integration testing
* End-to-end testing
* Performance benchmarking
* Large-dataset testing
* Manual UI verification

Important verification areas include:

* Correct row/column issue locations
* Correct missing-value handling
* Exact duplicate detection
* Correct cleaning behavior
* Original dataset preservation
* Audit consistency
* Visualization correctness
* Export integrity
* Session cleanup
* Error handling

See:

```text
docs/TESTING.md
```

for the detailed testing strategy.

---

# 27. V1 Acceptance Criteria

V1 is considered complete when a user can successfully:

### Dataset

* Upload CSV, XLSX, or tabular JSON
* View dataset dimensions
* View columns and detected types
* Inspect basic statistics

### Data Quality

* Detect missing values
* Detect exact duplicate records
* Detect incompatible values
* Review suspicious values
* See exact row/column locations

### Cleaning

* Replace values
* Remove rows/duplicates
* Ignore issues
* Reset the working dataset
* Review the audit trail
* Preserve the original dataset

### Visualization

* Receive deterministic visualization recommendations
* Create supported charts
* Customize basic chart parameters
* Visualize the cleaned dataset

### Export

* Download CSV
* Download XLSX
* Download tabular JSON

### Reliability

* Handle invalid input
* Handle API errors
* Handle empty states
* Handle loading states
* Clean up sessions
* Pass the core end-to-end workflow

---

# 28. Current Limitations

V1 intentionally has several limitations.

### No Machine Learning

V1 does not train or compare ML models.

### No Authentication

There are no user accounts or JWT authentication.

### No Persistent Database

V1 uses temporary session-based storage rather than a database.

### No Fuzzy Duplicate Detection

Only exact duplicate records are handled.

### Limited JSON Support

Only tabular JSON is supported.

### Large Dataset Limit Not Yet Guaranteed

The maximum practical dataset size will be determined through benchmarking.

### Visualization Is Not a Full BI Platform

The project is not intended to replace Tableau, Power BI, or similar business-intelligence tools.

---

# 29. Out of Scope for V1

The following functionality is intentionally excluded:

```text
Machine Learning Training
Model Comparison
Model Ranking
AutoML
Neural Networks
Hyperparameter Tuning
Cross-validation
Advanced Feature Engineering
Model Explainability
Model Registry
Experiment Tracking
User Authentication
JWT
User Accounts
Multi-user Collaboration
Persistent Database
Redis
Celery
Complex Background Jobs
Enterprise Data Governance
Power BI-style Analytics
Tableau-style Analytics
Arbitrary Nested JSON Processing
Fuzzy Duplicate Detection
LLM-based Data Analysis
Chatbot
```

These are not missing features. They are deliberate scope boundaries.

---

# 30. Roadmap

## V1 — Data Preparation

```text
Upload
   ↓
Analyze
   ↓
Detect Issues
   ↓
Clean
   ↓
Visualize
   ↓
Export
```

Current focus.

---

## V2 — ML Problem Setup & Training

Potential future capabilities:

```text
Clean Dataset
      ↓
Select Target
      ↓
Select Features
      ↓
Train/Test Split
      ↓
ML Model
      ↓
Evaluation
```

Potential models include:

* Logistic Regression
* Linear Regression
* Decision Tree
* Random Forest

---

## V3 — Controlled Model Comparison

The long-term direction is:

```text
Clean Dataset
      ↓
Problem Setup
      ↓
Multiple Models
      ↓
Controlled Training
      ↓
Evaluation
      ↓
Comparison
      ↓
Research Analysis
```

V3 may introduce controlled experiments and multi-model comparison under consistent conditions.

---

# 31. Design Principle

The project follows one central principle:

> **Make the data understandable before making the model intelligent.**

A machine-learning system is only as reliable as the data and assumptions behind it.

V1 therefore focuses on making the dataset:

```text
Visible
   ↓
Understandable
   ↓
Inspectable
   ↓
Correctable
   ↓
Verifiable
```

before introducing model training and comparison.

---

# 32. Project Status

**Current phase:** Documentation / Implementation Preparation

### Documentation status

* [x] PRD
* [x] Architecture
* [x] API
* [x] Data Processing
* [x] Testing
* [x] TODO
* [x] README

### Implementation status

* [ ] Backend foundation
* [ ] Frontend foundation
* [ ] Dataset ingestion
* [ ] Dataset analysis
* [ ] Quality detection
* [ ] Cleaning
* [ ] Audit trail
* [ ] Visualization
* [ ] Export
* [ ] Frontend/backend integration
* [ ] Testing
* [ ] Benchmarking
* [ ] Deployment
* [ ] V1 release

---

# 33. Related Documentation

For detailed implementation information, see:

* [`docs/PRD.md`](docs/PRD.md)
* [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
* [`docs/API.md`](docs/API.md)
* [`docs/DATA_PROCESSING.md`](docs/DATA_PROCESSING.md)
* [`docs/TESTING.md`](docs/TESTING.md)
* [`tasks/TODO.md`](tasks/TODO.md)

---

# 34. Final V1 Definition

ML Model Comparison Lab V1 is a **data preparation and analysis foundation**.

It allows a user to:

```text
UPLOAD
  ↓
UNDERSTAND
  ↓
DETECT
  ↓
CORRECT
  ↓
VERIFY
  ↓
VISUALIZE
  ↓
EXPORT
```

The project does not attempt to solve the entire machine-learning lifecycle in V1.

Instead, it establishes a reliable foundation for future ML training and controlled model comparison.

---

**V1 Scope: Data Preparation + Analysis + Visualization + Export**
