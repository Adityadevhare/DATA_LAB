# Product Requirements Document (PRD)
## ML Model Comparison Lab — V1

**Status:** Active  
**Version:** V1  
**Last Updated:** 2025

---

## 1. Executive Summary

ML Model Comparison Lab is a web-based data preparation and analysis platform. V1 enables users to upload tabular datasets, detect and fix data-quality issues, analyze cleaned data, generate visualizations, and export results.

V1 is explicitly **not** an ML model comparison or training system. Model comparison functionality is planned for V3 after data preparation (V1) and ML problem setup (V2) are complete.

---

## 2. Product Vision

**What it is:**  
A technical data-preparation tool for data professionals, analysts, and ML engineers who need to clean, understand, and export datasets.

**What it is not:**
- An ML model comparison system (that's V2/V3)
- An AutoML platform
- A chatbot or conversational AI tool
- A generic "AI website"
- An enterprise data governance solution
- A replacement for Tableau or Power BI

**Design philosophy:**  
Clean, precise, professional. The interface should communicate **clarity + precision + trust + usability + technical quality**. It should feel like serious technical software, not a trendy AI demo.

---

## 3. User Personas

### Primary: Data Analyst
- Has a CSV or Excel file with potential quality issues
- Needs to understand what's in the dataset
- Wants to identify and fix problems before downstream use
- May not have programming skills; needs a visual interface

### Secondary: ML Engineer
- Preparing data for model training
- Needs fine-grained control over data cleaning
- Wants to track exactly what changed and why
- Plans to export the cleaned dataset for model development

### Tertiary: Data Scientist
- Exploring a new dataset
- Needs quick statistical summaries and visualizations
- May iterate between cleaning and analysis

---

## 4. Core User Workflow

```
1. Upload Dataset
   ├─ Supported: CSV, XLSX, Tabular JSON
   └─ System validates and ingests file

2. Review Dataset Analysis
   ├─ Row/column count, file size
   ├─ Column names and detected types
   ├─ Missing-value and duplicate summaries
   └─ Basic statistics (numerical: mean/median/min/max/std; categorical: unique/frequency)

3. Review Data Quality Detection
   ├─ Missing values (exact row/column location)
   ├─ Duplicate records (exact row numbers)
   ├─ Type incompatibilities (value incompatible with column type)
   ├─ Suspicious values (unusual but not provably invalid)
   └─ Issues shown with: Row, Column, Current Value, Issue Type, Severity, Suggested Action

4. Resolve Issues
   ├─ For each issue: Replace / Remove / Ignore
   ├─ For replacements:
   │  ├─ Numerical: Mean, Median, Custom Value
   │  └─ Categorical: Mode, Custom Value
   ├─ Each action tracked in audit log
   └─ Original dataset remains untouched

5. Analyze Cleaned Dataset
   ├─ Review updated statistics
   ├─ Examine changes made (audit trail)
   └─ Option to reset to original if needed

6. Visualize (Optional)
   ├─ Auto-recommend visualization based on column types
   └─ Manually configure custom visualization

7. Export Cleaned Dataset
   ├─ Supported: CSV, XLSX, JSON (tabular)
   └─ Download includes only the cleaned/working dataset
```

---

## 5. Functional Requirements

### 5.1 Dataset Upload

**What the user can do:**
- Upload a single dataset file
- See validation status (success or specific error)

**Supported input formats:**
- CSV (.csv)
- Excel (.xlsx, .xls)
- Tabular JSON (.json — array of objects)

**File validation:**
- System must validate that the file is readable and matches the claimed format
- File size must be within tested benchmarks (see Section 10)
- System should reject invalid files with clear error messages

**Scope note:**  
V1 does not support multiple simultaneous datasets or dataset merging.

---

### 5.2 Dataset Analysis

After successful upload, the system displays:

**Dataset-level metrics:**
- Total row count
- Total column count
- File size (bytes)
- Column names (as ordered in source file)

**Per-column information:**

| Column Type | Information Required |
|---|---|
| **All columns** | Column name, detected type, missing-value count, duplicate-value count |
| **Numerical** | Mean, Median, Min, Max, Standard Deviation |
| **Categorical/Text** | Unique-value count, most frequent value, frequency distribution |
| **Date/Time** | Detected format, earliest date, latest date, missing values |
| **Boolean** | Unique values (typically true/false), counts |
| **Identifier** | Unique-value count, cardinality note |

**Design principle:**  
Analysis is practical and focused. V1 is not a full automated exploratory data analysis (EDA) platform. Statistics are sufficient for understanding data shape and quality; they do not need to include advanced statistical measures beyond those listed.

---

### 5.3 Column Type Detection and Override

**Automatic detection:**  
The system infers column types from data inspection:
- **Numerical:** Columns containing predominantly numeric values (integers, floats)
- **Categorical/Text:** Columns containing strings, categories, or mixed text
- **Date/Time:** Columns matching common date/time formats
- **Boolean:** Columns with binary values (true/false, yes/no, 0/1)
- **Identifier:** Columns that look like IDs (high cardinality, unique values, numeric but semantic meaning differs from analytical numerical values)

**User override:**  
Users must be able to manually change the detected type of any column. This is critical because:
- A column of integers may be IDs, not analytical features (e.g., `Employee_ID`)
- A column of strings may represent ordered categories
- Date columns might be stored as strings

**Implementation note:**  
Type override affects downstream data-quality detection, statistics display, and visualization recommendations. The system must track the user's choice and apply it consistently.

---

### 5.4 Data Quality Detection

The system must detect the following classes of issues and report their exact location (row, column, current value).

#### 5.4.1 Missing Values

**What counts as missing:**
- Null / None / NaN values
- Empty cells ("")
- Supported platform-specific missing-value markers (e.g., "NA", "N/A" only if explicitly configured)

**What the system reports:**
- Row number
- Column name
- Issue type: "Missing Value"
- Suggested action: "Replace with Mean/Median/Mode" or "Remove Row/Value"

**User actions:** Replace, Remove, Ignore

---

#### 5.4.2 Duplicate Records

**What counts as a duplicate:**  
V1 detects **exact full-row duplicates only**. A duplicate record means every column value is identical to another row.

Example:
```
Row 15: [Name: "Alice", Age: 30, City: "NYC"]
Row 42: [Name: "Alice", Age: 30, City: "NYC"]
→ Exact duplicate detected
```

**What the system reports:**
- Row numbers of duplicate records
- Option to see side-by-side comparison
- Issue type: "Duplicate Record"
- Suggested action: "Remove duplicate"

**Fuzzy/approximate duplicate detection is OUT OF SCOPE for V1.**

**User actions:** Remove, Ignore (user can mark a duplicate as intentional and keep both)

---

#### 5.4.3 Type Incompatibilities

**What counts as incompatible:**  
A value that directly contradicts the inferred or user-selected column type.

Examples:
- Column type: Numerical, Actual value: "Rahul" (non-numeric string)
- Column type: Date, Actual value: "Not a date" (unrecognizable format)
- Column type: Boolean, Actual value: "Maybe" (not a recognized boolean value)

**What the system reports:**
- Row number
- Column name
- Current value
- Expected type vs. actual value
- Issue type: "Type Incompatibility"
- Suggested action: "Replace with valid value" or "Remove row"

**User actions:** Replace, Remove, Ignore

---

#### 5.4.4 Suspicious Values

**What counts as suspicious:**  
Values that are technically valid for their type but appear unusual and warrant user review.

Examples:
- Column: "Age", Value: 150 (numerically valid, but biologically suspicious)
- Column: "Temperature (°C)", Value: -500 (numerically valid but physically impossible)
- Column: "Salary", Value: 0.01 (numerically valid but economically suspicious)

**Important distinction:**  
Suspicious values are **not** errors. The user may have intentional reasons for these values. The system flags them for review but does not automatically reject them.

**What the system reports:**
- Row number
- Column name
- Current value
- Why it's suspicious (e.g., "Value 150 is beyond typical age range")
- Issue type: "Suspicious Value"
- Suggested action: "Review and decide"

**User actions:** Replace, Ignore (acknowledge but keep the value)

---

### 5.5 Exact Issue Presentation

**Critical requirement:**  
The system must clearly tell users exactly where problems occur.

**Issue table schema:**

| Field | Required | Description |
|---|---|---|
| Row | Yes | Row number (1-indexed or 0-indexed, consistently applied) |
| Column | Yes | Column name |
| Issue Type | Yes | Missing Value / Duplicate / Type Incompatibility / Suspicious Value |
| Current Value | Yes | The actual value in the cell |
| Severity | No | High / Medium / Low (severity classification) |
| Suggested Action | Yes | Replace / Remove / Ignore |

**Display behavior:**
- Issues are presented in a sortable, filterable table
- User can filter by issue type, column, or severity
- User can navigate to the affected cell in context (showing surrounding rows)
- Issue count summary (e.g., "15 Missing Values, 3 Duplicates, 2 Type Errors")

---

### 5.6 Issue Resolution

For each detected issue, the user selects an action:

#### Replace

**When available:**
- Missing values (numerical or categorical columns)
- Type incompatibilities (user provides valid replacement value)

**Options for numerical missing values:**
- Mean of column
- Median of column
- Custom numeric value

**Options for categorical missing values:**
- Mode (most frequent value) of column
- Custom value

**Options for type incompatibilities:**
- User manually enters a valid value for the column type
- System validates the replacement before applying

**Behavior:**
- Original cell value is replaced
- Change is logged in audit trail
- User can review before committing

#### Remove

**When available:**
- Duplicate records (remove one or all duplicates; user specifies)
- Records containing type incompatibilities (remove entire row)
- Values (remove a single cell value, leaving the cell empty or null)

**Behavior:**
- Row or value is deleted
- Change is logged in audit trail
- Original dataset remains untouched

#### Ignore

**When available:**  
For any issue type.

**Behavior:**
- The issue is marked as "intentionally ignored"
- The value remains unchanged
- The issue remains in the audit trail marked as "ignored"
- Ignored issues do not prevent data export

**Design note:**  
Ignore allows users to acknowledge an issue and choose not to act on it, which is important for suspicious values and legitimate outliers.

---

### 5.7 Original Dataset Preservation

**Hard requirement:**  
The uploaded original dataset must never be silently modified.

**System design:**

```
Original Dataset (read-only)
         ↓
    Working Dataset
         ├─ User applies cleaning actions
         ├─ All changes tracked
         └─ Original remains available
```

**User capabilities:**
- View original dataset at any time
- Reset working dataset to original (discarding all changes made in current session)
- Download original dataset (unmodified)

**Implementation:**  
Do not overwrite the uploaded file. Maintain separate in-memory or filesystem representations.

---

### 5.8 Modification Audit

The system maintains a detailed audit trail of all cleaning actions performed in the current session.

**Audit record schema:**

| Field | Description |
|---|---|
| Step | Sequential action number (1, 2, 3, ...) |
| Timestamp | When the action was applied |
| Row | Affected row number |
| Column | Affected column name |
| Original Value | Value before action |
| Action Type | Replace / Remove / Ignore |
| New Value | Value after action (if applicable) |
| Issue Type | The class of issue that triggered the action |
| Status | Applied / Undone (if multi-level undo is added later) |

**User access:**
- View full audit trail at any time
- Export audit trail with cleaned dataset (optional)
- Filter audit trail by column, issue type, or action

**Purpose:**  
Makes the data-cleaning process transparent and traceable. User can explain to others exactly what changed and why.

---

### 5.9 Dataset Analysis (Post-Cleaning)

After cleaning, the system displays:

**Updated metrics:**
- New row count (if rows were removed)
- New column count (if columns were removed)
- Updated missing-value counts
- Updated duplicate counts

**Statistics:**
- Recalculated statistics for numerical and categorical columns
- Updated type distribution (if user changed column types)

**Comparison option:**
- Side-by-side comparison: Original statistics vs. Cleaned statistics
- Shows impact of cleaning (e.g., "Removed 15 duplicate rows, replaced 42 missing values")

---

### 5.10 Visualization

#### 5.10.1 Automatic Visualization Recommendations

After cleaning, the system suggests one or more appropriate visualizations based on the columns present and their types.

**Recommendation rules (deterministic, rule-based):**

| Condition | Recommended Visualization |
|---|---|
| 1 numerical column | Histogram |
| 2 numerical columns | Scatter plot |
| 1 categorical column | Bar chart / Count plot |
| Categorical + Numerical | Grouped bar chart or box plot |
| Date + Numerical | Line plot (time series) |
| Multiple numerical columns (3+) | Correlation heatmap or pair plot |
| All columns categorical | Count/frequency plot |

**Behavior:**
- System recommends ONE primary visualization
- User can accept the recommendation or customize manually
- No LLM-based recommendation engine in V1 (rules-based only)

#### 5.10.2 Custom Visualization

Users can manually configure visualizations with:

**Configuration options:**
- Chart type (from available types; see Section 5.10.3)
- X-axis (select column)
- Y-axis (select column)
- Color/grouping column (optional)
- Aggregation (sum, mean, count, etc.)
- Filters (e.g., show only rows where Age > 25)

**Behavior:**
- User configures, system previews
- User can save visualization configuration
- User can generate multiple visualizations before export

#### 5.10.3 Supported Visualization Types

**Basic charts:**
- Histogram (univariate numerical distribution)
- Scatter plot (2D numerical relationship)
- Bar chart (categorical counts or aggregates)
- Pie chart (categorical proportions)
- Line chart (trends, time series)
- Area chart (stacked or cumulative trends)

**Statistical/Analytical charts:**
- Box plot (distribution by category, outlier visualization)
- Violin plot (density estimation by category)
- Correlation heatmap (numerical column relationships)
- Pair plot (matrix of scatter plots)
- Count plot (categorical frequency)
- KDE plot (kernel density estimation)
- Distribution plot (overlaid histogram + KDE)

**Implementation:**
- Backend generates visualizations using Matplotlib and Seaborn
- Visualizations are returned as images (PNG or SVG) or interactive HTML
- Frontend displays and allows user to download

**Scope note:**  
Plotly-based interactive visualizations are not required for V1. Static images are acceptable.

---

### 5.11 Dataset Export

After cleaning and (optionally) creating visualizations, users can export the cleaned dataset.

**Supported output formats:**
- CSV (.csv)
- Excel (.xlsx)
- Tabular JSON (.json — array of objects, one per row)

**What is exported:**
- The **cleaned/working dataset only** (original is not exported unless explicitly requested)
- Column types as configured by user
- All data in its final cleaned state

**JSON export detail:**  
For JSON export, the system uses tabular JSON format (array of records):

```json
[
  { "Name": "Alice", "Age": 30, "City": "NYC" },
  { "Name": "Bob", "Age": 25, "City": "LA" }
]
```

Arbitrary nested JSON structures are out of scope.

**Options:**
- Export cleaned dataset only
- Export with audit trail (optional separate file or appended metadata)
- Export selected columns only (optional)

---

## 6. Non-Functional Requirements

### 6.1 Performance and Scale

**Intended benchmark progression:**

| Dataset Size | Status | Notes |
|---|---|---|
| 100 MB | Supported | Baseline performance expectation |
| 500 MB | Target | Should load in reasonable time |
| 1 GB | Target | Stretch goal for V1 |
| 2–5 GB | Future | Benchmark after 1 GB achieved |

**Metrics to measure:**
- File ingestion time
- Memory usage during analysis
- Data-quality detection time
- Cleaning operation time
- Visualization generation time
- Export time
- Overall application stability

**Important caveat:**  
**Do not claim that V1 supports 5–6 GB datasets until benchmarking is complete.** Document the actual tested limit in README and this PRD after testing.

**Large dataset considerations:**
- Visualizations of very large datasets may require sampling, aggregation, or binning
- If a visualization does not include every row, the UI must explicitly communicate this (e.g., "Showing sample of 10,000 rows out of 500,000")

### 6.2 Usability

**The interface must be:**
- Intuitive for users unfamiliar with data science
- Clear about data states (loaded, analyzing, cleaned, etc.)
- Transparent about what has changed
- Accessible (WCAG 2.1 AA standard target)
- Responsive (works on tablet and desktop; mobile is nice-to-have, not required)

**Empty states:**
- Show helpful messaging when no dataset is loaded
- Show encouraging messages during processing

**Error states:**
- Display clear, actionable error messages
- Do not crash silently
- Suggest next steps for user recovery

**Loading states:**
- Show progress indicators for long operations
- Estimate time to completion if possible
- Allow cancellation of long operations (if practical)

### 6.3 Data Privacy and Security (V1 Baseline)

**V1 does not require:**
- User authentication or accounts
- Encrypted data transmission
- Long-term data storage or databases
- Compliance with GDPR/HIPAA

**V1 must do:**
- Allow users to work with sensitive data locally without forced cloud transmission (if possible)
- Not log or retain user data beyond the current session
- Provide a "clear all data" option on exit

**Future consideration:**  
After V1, assess whether users need data encryption, secure deletion, or compliance features.

---

## 7. User Interface Principles

### Visual Design Philosophy

**The product should feel like:**
- Professional technical software (data analysis, scientific tools, developer tooling)
- Serious, trustworthy, and precise
- Clean and minimal without being empty

**The product should NOT look like:**
- A generic AI-generated website
- A trendy SaaS landing page
- A chatbot or conversational interface
- A collection of glowing cards and gradients
- A "futuristic AI" theme

**Specific aesthetics to avoid:**
- Excessive gradients
- Purple/blue "AI" color palettes used decoratively
- Glowing or neon UI elements
- Excessive glassmorphism
- Floating gradient blobs
- AI sparkles, stars, or icon overuse
- Oversized marketing hero sections
- Fake system-status indicators
- Generic stock "AI" imagery
- Unnecessary animated elements

### Interface Hierarchy

**Information should be organized:**
1. Dataset status (loaded file, row count, column count)
2. Data-quality summary (issue counts by type)
3. Detailed issue list (sortable, filterable table)
4. Issue resolution controls
5. Audit trail / change history
6. Visualization and export options

**Each section should be scannable:**
- Clear headings
- Consistent typography
- Good whitespace
- Logical grouping
- Visual distinction between sections

### Responsive Design

**Desktop (primary target):**
- Full interface with all controls visible
- Detailed tables and charts
- Side-by-side layouts where useful

**Tablet (nice-to-have):**
- Responsive grid layout
- Touch-friendly controls
- Readable on smaller screens

**Mobile:**
- Not a primary target for V1
- If supported, a simplified, touch-optimized interface

---

## 8. Technical Constraints and Stack

### Frontend
- **Framework:** React with TypeScript
- **Build tool:** Vite
- **Styling:** Tailwind CSS
- **Component library:** shadcn/ui
- **Visualization:** Chart rendering (static or light interactivity)

### Backend
- **Language:** Python
- **Framework:** FastAPI
- **Data processing:** Polars (primary), Pandas (secondary for compatibility)
- **Scientific libraries:** NumPy, SciPy (as needed)
- **Visualization:** Matplotlib, Seaborn (for chart generation)
- **Excel handling:** openpyxl or equivalent

### Communication
- REST API (JSON over HTTP)
- No GraphQL or other query languages in V1

### Database and Persistence
- **V1 does not require:** PostgreSQL, MongoDB, Supabase, or any persistent database
- **Sufficient for V1:** Temporary filesystem storage or in-memory datasets during the session
- **Future consideration:** Add persistent storage if users need to save/resume sessions

### Authentication and Multi-User
- **V1 does not require:** User accounts, JWT, API keys, or multi-user collaboration
- **Sufficient for V1:** Single-user, single-session interface
- **Future consideration:** Add authentication if multi-user features are planned

### Background Jobs
- **V1 does not require:** Celery, Redis, or distributed job processing
- **Sufficient for V1:** Synchronous API calls for cleaning and analysis
- **Future consideration:** Add async processing if benchmarks show need

---

## 9. Out of Scope for V1

### Explicitly excluded:

**Machine Learning:**
- Model training (Logistic Regression, Linear Regression, Decision Trees, Random Forest, Neural Networks, etc.)
- Model comparison or ranking
- AutoML functionality
- Hyperparameter tuning
- Feature engineering
- Model evaluation metrics (Accuracy, Precision, Recall, F1, R², etc.)
- Cross-validation
- SHAP or model interpretability
- Model registry or experiment tracking

**Advanced Data Processing:**
- Fuzzy or approximate duplicate detection
- Arbitrary nested JSON processing
- Enterprise data governance features
- Full automated EDA platform
- Predictive imputation
- Outlier detection using statistical methods (beyond suspicious-value flagging)

**Infrastructure:**
- PostgreSQL or other relational databases
- MongoDB or document stores
- Supabase or hosted backends
- JWT authentication or OAuth
- User accounts or multi-user collaboration
- Celery or Redis
- Docker/Kubernetes orchestration (not required, though nice for deployment)
- Cloud storage integration (S3, GCS, etc.)

**Visualization:**
- Plotly interactivity (static charts sufficient)
- Real-time dashboard updates
- Custom D3.js visualizations
- 3D visualizations

---

## 10. Scalability and Benchmarking

### Tested Limits

After implementation, the project must document:

1. **Maximum dataset size tested:** (e.g., "Tested up to 1 GB")
2. **Performance on each size:**
   - Ingestion time
   - Memory peak usage
   - Analysis time
   - Cleaning time
   - Export time
3. **Visualization stability:** Can visualizations be generated for large datasets?
4. **Overall stability:** Does the application remain responsive?

### Sampling and Aggregation

For very large datasets (if supported):
- Visualizations may show samples or aggregates rather than individual rows
- UI must clearly communicate this (e.g., "Showing 1:10 sample")
- Export must still include the complete dataset

### Benchmarking Cadence

1. Implement core features
2. Benchmark at 100 MB, 500 MB, 1 GB
3. Document results in README
4. Decide on next target (2 GB, 5 GB, etc.) based on results

---

## 11. Success Criteria (V1 Completion)

The following must be true for V1 to be considered complete:

- [ ] User can upload CSV, XLSX, or tabular JSON files
- [ ] System displays dataset analysis (row count, column statistics, type inference)
- [ ] System detects missing values with exact location (row, column)
- [ ] System detects exact duplicate records with row numbers
- [ ] System detects type incompatibilities with current values
- [ ] System flags suspicious values for review
- [ ] User can replace, remove, or ignore issues
- [ ] Replacements use Mean/Median (numerical) or Mode (categorical)
- [ ] Original dataset is never silently modified
- [ ] Audit trail tracks all changes with full details
- [ ] User can reset to original dataset
- [ ] Cleaned dataset can be analyzed with updated statistics
- [ ] System recommends visualizations based on column types
- [ ] User can create custom visualizations
- [ ] At least 7 visualization types are supported (histogram, scatter, bar, pie, line, area, box plot, etc.)
- [ ] User can export cleaned dataset as CSV, XLSX, or JSON
- [ ] Application is performant up to [tested limit — to be determined]
- [ ] UI is clean, professional, and feels like serious technical software
- [ ] UI does not resemble a generic AI-generated website
- [ ] All major states (empty, loading, error, success) have clear messaging
- [ ] Documentation exists: README, PRD, ARCHITECTURE, API, DATA_PROCESSING, TESTING

---

## 12. Roadmap (Future Versions)

### V2: ML Problem Setup (Future)

- User selects target column
- System suggests feature/target split
- Feature engineering guidance
- Train/test split configuration
- Preparation for model training

### V3: Model Training and Comparison (Future)

- Train multiple models on the same dataset
- Controlled experiment framework
- Model evaluation and ranking
- Model comparison analysis
- Research and insights

---

## 13. Definition of Done

A feature is considered done when:

1. Code is written and tested
2. It matches the requirements in this PRD
3. It does not introduce scope creep
4. Documentation is updated
5. Code review is passed
6. It has been integrated into the main branch

---

## 14. Questions and Open Decisions

**None at this time.** All core requirements for V1 are defined.

If a decision point arises during implementation that is not addressed here, flag it as an OPEN DECISION with context, and resolve it through explicit team discussion rather than inference.

---

## 15. Document History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2025 | Initial PRD for V1 |