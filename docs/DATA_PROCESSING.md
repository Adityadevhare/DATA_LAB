# Data Processing Specification
## ML Model Comparison Lab — V1

**Status:** Active  
**Version:** V1  
**Last Updated:** 2025

---

## 1. Overview

This document specifies **exactly how data is processed, analyzed, cleaned, and validated** throughout the ML Model Comparison Lab application.

It defines:
- File ingestion and parsing
- Type inference and detection
- Missing-value handling
- Duplicate detection
- Type incompatibility detection
- Suspicious-value detection
- Data cleaning operations
- Audit trail recording
- Export formatting

This document is the source of truth for implementation. When PRD.md says "the system detects missing values," this document explains **how**.

---

## 2. File Ingestion and Parsing

### 2.1 Supported Input Formats

#### CSV (.csv)

**Parsing:**
- Use Polars `read_csv()` or Pandas `read_csv()` as fallback
- Infer delimiter automatically (comma, semicolon, tab)
- Infer header row (assume first row is header unless otherwise specified)

**Configuration:**
- Encoding: UTF-8 (default), Latin-1 (fallback if UTF-8 fails)
- Quote character: `"` (double-quote, standard)
- Escape character: `\` (backslash, standard)

**Behavior:**
- If delimiter detection fails, raise clear error: "Could not parse CSV. Try different delimiter."
- If header is missing, user is prompted: "No header detected. Use first row as header or treat as data?"

**Polars-first principle:**
- Primary ingestion: `pl.read_csv(file_path, infer_schema_length=10000, ...)`
- Fallback to Pandas only if Polars fails or compatibility is needed

#### Excel (.xlsx, .xls)

**Parsing:**
- Use Polars `read_excel()` or openpyxl (Python library) for reading
- Support `.xlsx` (modern Excel) and `.xls` (legacy Excel) via openpyxl
- Infer header row (assume first row is header)

**Configuration:**
- Sheet selection: Use first sheet by default; allow user to select sheet
- Range: Read entire sheet by default; skip hidden rows and columns

**Behavior:**
- Detect and preserve data types where Excel metadata is available
- For cells with formulas, read calculated values, not formulas
- If multiple sheets exist, show user a sheet picker

#### Tabular JSON (.json)

**Accepted format:**
Array of objects (one object per row):

```json
[
  { "Name": "Alice", "Age": 30, "City": "NYC" },
  { "Name": "Bob", "Age": 25, "City": "LA" },
  { "Name": "Charlie", "Age": null, "City": "Chicago" }
]
```

**Parsing:**
- Use `json.loads()` or Polars `read_json()`
- Require array at root level
- Each object is one row; keys become column names

**Behavior:**
- Missing keys within an object are treated as null/missing values
- All rows must be objects (not arrays or primitives)
- Nested objects or arrays within rows are not supported (flatten first)

**Invalid formats (rejected):**
```json
// WRONG: Object at root level (not array)
{ "rows": [...] }

// WRONG: Nested structure
[{ "person": { "name": "Alice" } }]

// WRONG: Array of arrays
[["Alice", 30], ["Bob", 25]]
```

### 2.2 File Validation

**Before processing, validate:**

| Check | Condition | Action |
|---|---|---|
| File exists | File not found | Raise "File not found" error |
| File readable | Cannot open file | Raise "Permission denied" or "File corrupted" error |
| File size | Exceeds tested limit (see PRD Section 10) | Warn user: "File is very large. Processing may be slow." |
| Format match | File claims to be CSV but is not | Raise "File format mismatch" error |
| Non-empty | File is empty or zero rows | Raise "Dataset is empty" error |
| Header row | No headers detected | Prompt user for header handling |

**Error messages** must be actionable:
- ❌ Bad: "Error 500"
- ✅ Good: "Could not read file. Is this a valid CSV? Check encoding (try UTF-8 or Latin-1)."

### 2.3 Ingestion Workflow

```
1. User uploads file
2. Validate file format and existence
3. Parse file into DataFrame (Polars preferred)
4. Infer column names from header or generate (Column_1, Column_2, ...)
5. Infer data types (see Section 3)
6. Store original DataFrame (read-only)
7. Create working DataFrame (copy of original)
8. Return dataset summary to frontend
```

---

## 3. Column Type Inference

### 3.1 Type Categories

The system recognizes these conceptual column types:

| Type | Characteristics | Examples |
|---|---|---|
| **Numerical** | Numeric values (int or float) | `42`, `3.14`, `-10` |
| **Categorical** | Discrete categories, typically strings | `"Red"`, `"Small"`, `"Active"` |
| **Date/Time** | Recognized date/time formats | `2025-01-15`, `01/15/2025`, `2025-01-15 10:30:00` |
| **Boolean** | Binary/logical values | `True`, `False`, `Yes`, `No`, `1`, `0` |
| **Identifier** | High-cardinality numeric or string IDs | `Employee_ID`, `Order_123`, `UUID` |
| **Text** | Free-form text, typically longer strings | Comments, descriptions, paragraphs |

### 3.2 Type Inference Algorithm

**Input:** Column data (all values in a column)  
**Output:** Inferred type, confidence score

**Process:**

```
1. Sample first 1,000 rows (or entire column if < 1,000 rows)

2. Count non-null values
   - If >= 90% null: Flag as sparse, revisit later

3. Try to parse as each type (in order):
   a. Boolean
   b. Numerical
   c. Date/Time
   d. Identifier (numeric, high cardinality)
   e. Categorical (low cardinality string)
   f. Text (default fallback)

4. For each successful parse, calculate:
   - Percentage of values matching the type
   - Threshold: >= 95% of non-null values must match

5. Select type with highest confidence
   - If tie or low confidence (< 80%), flag for user review
```

### 3.3 Type-Specific Inference Rules

#### Boolean

**Recognized patterns:**
- `True`, `False` (case-insensitive)
- `Yes`, `No` (case-insensitive)
- `Y`, `N` (case-insensitive)
- `1`, `0` (numeric)
- `T`, `F` (case-insensitive)

**Acceptance:** >= 95% of non-null values match one of the above patterns

**Conflict handling:** If column contains `[True, False, 0, 1, "Yes"]`, it's ambiguous. Flag for user review.

#### Numerical

**Accepted formats:**
- Integers: `42`, `-10`, `0`
- Floats: `3.14`, `-2.71`, `1e-5` (scientific notation)
- Thousands separator: `1,000` or `1.000` (locale-aware, optional)

**Rejection criteria:**
- Contains alphabetic characters (except `.`, `-`, `e`, `,`)
- Percentage signs or currency symbols require special handling

**Thousands separator handling:**
- Detect if column uses `,` for thousands: `1,000` or `.` for thousands: `1.000`
- Detect if column uses `.` or `,` for decimal: `3.14` vs `3,14`
- Infer locale and parse accordingly
- If ambiguous, prompt user

#### Date/Time

**Recognized patterns:**
- ISO format: `YYYY-MM-DD`, `YYYY-MM-DDTHH:MM:SS`
- US format: `MM/DD/YYYY`, `MM-DD-YYYY`
- European format: `DD/MM/YYYY`, `DD-MM-YYYY`
- Other: `YYYY/MM/DD`, `DD.MM.YYYY`, `MMMM DD, YYYY`

**Parsing:**
- Use `dateutil.parser.parse()` (Python) or Polars date inference
- Try multiple formats; accept first match
- Handle timezone information if present

**Acceptance:** >= 95% of non-null values parse successfully as dates

**Ambiguity:** If dates like `01-02-2025` could be Jan 2 or Feb 1, prompt user: "Is this MM/DD/YYYY or DD/MM/YYYY?"

#### Identifier

**Characteristics:**
- High cardinality (unique value count close to row count)
- Numeric or alphanumeric strings
- Semantic meaning is "uniqueness," not numerical quantity

**Inference rule:**
```
If (column contains mostly unique numeric or string values)
   AND (cardinality >= 95% of row count)
   AND (column name contains ID-like patterns: "ID", "id", "_id", "identifier", "code", "number")
Then: Infer as Identifier
```

**Examples:**
- `Employee_ID: [1001, 1002, 1003, ...]` → Identifier (even though numeric)
- `Order_Number: [ORD-001, ORD-002, ...]` → Identifier
- `Age: [25, 30, 35, ...]` → Numerical (not an identifier, despite numbers)

**User override:** User can explicitly change to/from Identifier type.

#### Categorical

**Characteristics:**
- String values
- Low cardinality (distinct values << row count)
- Represent discrete categories

**Inference rule:**
```
If (column is string)
   AND (unique value count < sqrt(row count))
   AND (does not match Date/Boolean/Identifier patterns)
Then: Infer as Categorical
```

**Examples:**
- `Color: ["Red", "Blue", "Green"]` (unique count: 3, rows: 1000) → Categorical
- `Status: ["Active", "Inactive"]` → Categorical

#### Text

**Default fallback:**
- String data that doesn't fit other categories
- Long, free-form content
- High cardinality or varied values

**Examples:**
- `Comment: ["Great product!", "Not satisfied.", "Good value for money."]` → Text
- `Description: [Long paragraphs of text...]` → Text

### 3.4 User Type Override

**Critical capability:**  
Users must be able to manually change the inferred type for any column.

**Workflow:**
1. System shows inferred type with confidence
2. User clicks "Change type" or similar control
3. Dropdown/selector shows available types
4. User selects new type
5. System updates:
   - The column's type metadata
   - Subsequent data-quality detection logic
   - Visualization recommendations
   - Statistics display

**Validation on override:**
- If user selects Numerical but column contains `["Red", "Blue"]`, warn: "Column contains non-numeric values. Type mismatch will be detected as an error."
- Allow override anyway (user may want to see type incompatibilities)

---

## 4. Missing-Value Detection

### 4.1 Definition

A value is considered **missing** if:

| Representation | Platform/Format | Treated as Missing |
|---|---|---|
| `None` / `null` | Python, JSON, SQL | ✅ Yes |
| `NaN` | NumPy, Pandas, floating-point | ✅ Yes |
| `""` (empty string) | CSV, Excel, text | ✅ Yes (configurable) |
| `NA`, `N/A`, `#N/A` | Excel, text | ⚠️ Configurable (off by default) |
| Blank cell | Excel, CSV | ✅ Yes |
| Space-only string | `" "`, `"  "` | ⚠️ Configurable (treat as missing or keep) |

**Default behavior (V1):**
- Treat `None`, `null`, `NaN`, empty string (`""`) as missing
- Optionally detect `"NA"` or similar if user configures custom missing markers

### 4.2 Detection Algorithm

```
For each column:
  For each row:
    If value is null OR value is NaN OR value == "":
      Record issue:
        {
          row: row_index,
          column: column_name,
          issue_type: "Missing Value",
          current_value: null,
          severity: "High" or "Medium",
          suggested_action: "Replace or Remove"
        }
```

### 4.3 Severity Classification

**Missing value severity:**
- **High:** Column is numeric or required-looking (e.g., ID, Date, Primary Key)
- **Medium:** Column is categorical or optional-looking

(Severity is informational; user can ignore severity and act on any issue.)

### 4.4 Detection Performance

**Polars-based detection (preferred):**
```python
null_mask = df.select(pl.col("column_name").is_null())
null_indices = null_mask.to_numpy().flatten().nonzero()[0]
```

**Pandas fallback:**
```python
null_indices = df[column_name].isna().nonzero()[0]
```

---

## 5. Duplicate Record Detection

### 5.1 Definition

**Exact duplicate:** Two or more rows where every column value is identical.

**In scope for V1:**
```
Row 15: [Alice, 30, NYC, Engineer]
Row 42: [Alice, 30, NYC, Engineer]
→ Exact duplicate detected
```

**Out of scope for V1:**
- Fuzzy/approximate matching (e.g., "Alise" vs "Alice")
- Partial duplicates (all columns except one are identical)
- Case-insensitive or whitespace-normalized matching

### 5.2 Detection Algorithm

```
1. Create hash of each row (all column values concatenated)
2. Identify rows with identical hashes
3. Group by hash value
4. For each group with > 1 row:
     Record issue for each row in group:
       {
         row: row_index,
         column: null (entire row),
         issue_type: "Duplicate Record",
         current_value: [all column values],
         duplicate_of: [list of other row indices with same hash],
         severity: "High",
         suggested_action: "Remove one or more duplicates"
       }
```

### 5.3 Detection Performance

**Polars-based detection (preferred):**
```python
# Create concatenated string hash
df_with_hash = df.with_columns(
    row_hash=pl.concat_str(pl.all()).hash().alias("row_hash")
)

# Find duplicates
duplicate_hashes = (
    df_with_hash
    .group_by("row_hash")
    .agg(pl.count().alias("count"))
    .filter(pl.col("count") > 1)
)
```

**Pandas fallback:**
```python
df['row_hash'] = df.apply(lambda x: hash(tuple(x)), axis=1)
duplicate_rows = df[df.duplicated(subset=['row_hash'], keep=False)]
```

### 5.4 User Resolution: Remove

**When user selects "Remove" for a duplicate:**

Option A: Remove all but first occurrence
```
Rows 15, 42 are duplicates
→ Keep row 15, remove row 42
```

Option B: Remove all duplicates
```
Rows 15, 42 are duplicates
→ Remove both rows
```

Option C: User selects specific duplicates to remove
```
Rows 15, 42, 99 are all identical
→ Keep row 15, remove rows 42 and 99 (user choice)
```

**Recommended UX:**
- Show all rows in the duplicate group
- Highlight which row would be kept (default: first occurrence)
- Allow user to select alternative row to keep
- Confirm before removal

---

## 6. Type Incompatibility Detection

### 6.1 Definition

**Type incompatibility:** A value that cannot be parsed or interpreted as the column's inferred or user-selected type.

**Examples:**

| Column Type | Value | Is Incompatible? |
|---|---|---|
| Numerical | `42` | ❌ No (valid numeric) |
| Numerical | `"42"` | ❌ No (can be parsed as numeric) |
| Numerical | `"Rahul"` | ✅ Yes (cannot parse as number) |
| Date | `2025-01-15` | ❌ No (valid date) |
| Date | `"Not a date"` | ✅ Yes (cannot parse as date) |
| Boolean | `True` | ❌ No (valid boolean) |
| Boolean | `"Maybe"` | ✅ Yes (not a recognized boolean value) |
| Categorical | `"Red"` | ❌ No (is string/category) |
| Categorical | `42` | ⚠️ Maybe (can be coerced to string; typically accepted) |

### 6.2 Detection Algorithm

```
For each column (with inferred or user-selected type):
  For each value in that column:
    Try to parse/convert to column type
    If parse fails:
      Record issue:
        {
          row: row_index,
          column: column_name,
          issue_type: "Type Incompatibility",
          current_value: original_value,
          expected_type: column_type,
          actual_type: detected_type,
          severity: "High",
          suggested_action: "Replace with valid value or Remove row"
        }
```

### 6.3 Type-Specific Incompatibility Rules

#### Numerical Columns

**Accepted values:**
- Integers: `42`, `-10`, `0`
- Floats: `3.14`, `-2.71`
- Scientific notation: `1e-5`
- Strings that parse as numbers: `"42"` → `42`

**Rejected values:**
- Non-numeric strings: `"Rahul"`, `"N/A"`, `"Unknown"`
- Mixed: `"42 apples"` (contains non-numeric text)

**Parsing logic:**
```python
try:
    float(value)  # Try to convert to float
except ValueError:
    # Incompatible
```

#### Date Columns

**Accepted values:**
- ISO format: `2025-01-15`, `2025-01-15T10:30:00`
- Recognized date formats (per Section 3.3)
- Strings that parse successfully

**Rejected values:**
- Unrecognizable formats: `"Not a date"`, `"2025-13-01"` (invalid month)
- Numbers without date context: `12345` (epoch timestamp parsing is optional)

**Parsing logic:**
```python
try:
    dateutil.parser.parse(value)
except:
    # Incompatible
```

#### Boolean Columns

**Accepted values:**
- `True`, `False` (boolean)
- `Yes`, `No`, `Y`, `N` (case-insensitive)
- `1`, `0` (numeric)

**Rejected values:**
- `"Maybe"`, `"Unknown"`, other strings
- `2`, `-1` (numeric but not in {0, 1})

#### Categorical Columns

**Accepted values:**
- Any string value
- Numeric values are coerced to strings: `42` → `"42"`

**Rejected values:**
- None (almost everything can be categorical as a string)

#### Identifier Columns

**Accepted values:**
- Any value (identifier type is semantic, not syntactic)
- Identifiers can be numeric, string, alphanumeric

**Rejected values:**
- None (almost everything can be an identifier)

### 6.4 Detection Performance

**Polars-based detection (preferred):**
```python
def is_numeric(value):
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False

# For each column, filter by incompatibility
incompatible = df.filter(~df[column_name].apply(is_numeric))
```

**Pandas fallback:**
```python
pd.to_numeric(df[column_name], errors='coerce')
# Resulting NaN values indicate incompatibility
```

---

## 7. Suspicious-Value Detection

### 7.1 Definition

**Suspicious value:** A value that is technically valid for its type but appears unusual, rare, or potentially erroneous based on statistical or domain-specific heuristics.

**Key distinction:** Suspicious ≠ Invalid. Users may have legitimate reasons for these values.

### 7.2 Detection Rules

#### Rule 1: Numerical Outliers

**Condition:** Value is > 3 standard deviations from the mean.

**Algorithm:**
```
mean = column.mean()
std = column.std()

for value in column:
  if value is not null:
    z_score = (value - mean) / std
    if abs(z_score) > 3:
      flag as suspicious
```

**Example:**
- Column: `Age`
- Data: `[25, 28, 30, 32, 150]`
- Mean: ~53, Std: ~55
- Z-score for 150: ~1.76 (not flagged, within 3σ)
- Z-score for 150 in a more normal dataset would exceed 3σ

**Trigger:** Record as suspicious if flagged.

#### Rule 2: Range Violations (Domain-Specific)

**Condition:** Value violates domain-specific constraints.

**Hard-coded domain rules (expandable):**

| Column Name Pattern | Constraint | Example |
|---|---|---|
| `*age*` | Value > 120 or < 0 | `Age = 150` → Suspicious |
| `*temperature*` | Value < -100 or > 60 (°C) | `Temperature = -500` → Suspicious |
| `*salary*` | Value < 0 | `Salary = -50000` → Suspicious |
| `*percentage*` | Value < 0 or > 100 | `Completion = 150%` → Suspicious |
| `*price*`, `*cost*` | Value < 0 | `Price = -99.99` → Suspicious |
| `*count*`, `*quantity*` | Value < 0 or non-integer | `Quantity = -5` → Suspicious |

**Implementation:**
```python
def check_domain_rules(column_name, value, column_type):
    rules = {
        "age": lambda v: v < 0 or v > 120,
        "temperature": lambda v: v < -100 or v > 60,
        # ... more rules
    }
    
    for pattern, rule in rules.items():
        if pattern.lower() in column_name.lower():
            if rule(value):
                return "suspicious"
    return "ok"
```

#### Rule 3: Empty or All-Zeros Columns

**Condition:** Column contains only zeros, empty values, or constant values.

**Algorithm:**
```
if column.nunique() == 1:  # All values identical
  flag column as suspicious
  (might indicate missing data or data entry error)
```

**User action:** "Consider removing this column; it contains no variance."

### 7.3 Severity Classification

**Suspicious values severity:**
- **Medium:** Value exceeds statistical bounds (3σ outlier)
- **Low:** Value is rare or unusual but not extreme
- **Info:** Column has no variance (informational, not actionable)

### 7.4 Suspicious Value Presentation

**Display in issue table:**
```
Row | Column | Issue Type | Current Value | Severity | Suggested Action
12  | Age    | Suspicious Value | 150    | Medium   | Review / Replace / Ignore
```

**User actions available:**
- **Replace:** User provides a new value
- **Ignore:** Keep the value; mark issue as intentionally ignored

(Remove is less common for suspicious values; replace or ignore are typical.)

### 7.5 Detection Performance

**Polars-based detection (preferred):**
```python
mean = df[column_name].mean()
std = df[column_name].std()
z_scores = ((df[column_name] - mean) / std).abs()
suspicious = z_scores > 3
```

---

## 8. Data Cleaning Operations

### 8.1 Replace Operation

**Trigger:** User selects "Replace" for an issue and provides a replacement value.

**Processing:**

```
1. Validate replacement value
   - Must be compatible with column type
   - Example: If column is Numerical, replacement must be numeric

2. Apply replacement
   - df.loc[row_index, column_name] = replacement_value

3. Update audit trail
   - Record: row, column, original_value, new_value, action="Replace"

4. Recompute statistics
   - Recalculate column-level statistics
   - Flag any newly introduced issues (optional)
```

### 8.2 Remove Operation

**Trigger:** User selects "Remove" for an issue.

**Two cases:**

#### Case A: Remove a Single Cell Value

For missing-value issues in a single cell:
```
1. Set df.loc[row_index, column_name] = None (leave cell empty)
2. Record in audit trail: row, column, action="Remove Value"
```

#### Case B: Remove an Entire Row

For duplicate records or type incompatibilities affecting entire row:
```
1. Delete row: df.drop(row_index, inplace=True)
2. Record in audit trail: row, action="Remove Row"
3. Reindex remaining rows (optional; maintain original row numbers for audit)
```

**Important:** After removal, row indices may shift. Maintain a mapping of original row numbers to current positions for audit clarity.

### 8.3 Ignore Operation

**Trigger:** User selects "Ignore" for an issue.

**Processing:**

```
1. Do NOT modify the value
2. Record in audit trail: row, column, action="Ignore", note="User chose to keep value"
3. Mark issue as "resolved" in the UI (even though data unchanged)
```

**Effect:** Issue no longer appears in the unresolved issue list, but remains in the audit trail.

---

## 9. Replacement Strategy: Mean, Median, Mode

### 9.1 Mean Replacement (Numerical Columns)

**Calculation:**
```
mean_value = column.mean(skipna=True)  # Exclude existing NaN values
```

**Application:**
```
df.loc[row_index, column_name] = mean_value
```

**When to use:**
- Column is numerical
- Missing value flagged
- User selects "Replace with Mean"

**Behavior:**
- Uses all non-missing values in the column
- Does not include the missing value itself in calculation
- If entire column is missing, mean is NaN; user must provide custom value

### 9.2 Median Replacement (Numerical Columns)

**Calculation:**
```
median_value = column.median(skipna=True)  # Exclude existing NaN values
```

**Application:**
```
df.loc[row_index, column_name] = median_value
```

**When to use:**
- Column is numerical
- Missing value flagged
- User selects "Replace with Median"
- Preferred over mean if column has outliers

**Behavior:**
- Uses all non-missing values
- Robust to extreme values
- If entire column is missing, median is NaN; user must provide custom value

### 9.3 Mode Replacement (Categorical Columns)

**Calculation:**
```
mode_value = column.mode(dropna=True)[0]  # Most frequent non-missing value
```

**Application:**
```
df.loc[row_index, column_name] = mode_value
```

**When to use:**
- Column is categorical or text
- Missing value flagged
- User selects "Replace with Mode"

**Behavior:**
- Uses most frequent category
- If multiple categories tie for most frequent, select first in sorted order (or configurable)
- If entire column is missing, mode is undefined; user must provide custom value

### 9.4 Custom Value Replacement

**Process:**
```
1. User enters custom value in UI
2. System validates value against column type
   - If Numerical column: value must be numeric
   - If Categorical column: value can be any string
   - If Date column: value must parse as valid date
3. If valid: apply replacement
   If invalid: show error, ask user to retry
4. Record in audit: action="Replace", new_value=custom_value
```

**Examples:**
- Replace missing Age with custom value: `25`
- Replace missing Category with custom value: `"Unknown"`
- Replace missing Date with custom value: `2025-01-01`

---

## 10. Audit Trail

### 10.1 Audit Record Schema

Each action (Replace, Remove, Ignore) is recorded with:

| Field | Type | Example | Notes |
|---|---|---|---|
| `step` | int | `1`, `2`, `3`, ... | Sequential action number |
| `timestamp` | datetime | `2025-01-15T10:30:45.123Z` | ISO 8601 format |
| `row_index` | int | `15` | Original row number (preserved even after removals) |
| `column_name` | str | `"Age"` | Column name |
| `original_value` | any | `null`, `"Rahul"`, `150` | Value before action (null if missing) |
| `action_type` | str | `"Replace"`, `"Remove"`, `"Ignore"` | User's chosen action |
| `new_value` | any | `25`, `"Unknown"`, `null` | Value after action (null if removed) |
| `issue_type` | str | `"Missing Value"`, `"Type Incompatibility"`, `"Duplicate Record"`, `"Suspicious Value"` | Classification of issue |
| `status` | str | `"Applied"`, `"Pending"`, `"Reverted"` | Execution status |
| `notes` | str | `"User provided custom value"` | Optional additional context |

### 10.2 Audit Storage

**During session:**
- Store audit records in memory (list of dictionaries or DataFrame)
- Provide API endpoint to retrieve audit trail

**Export:**
- Option to download audit trail as JSON or CSV alongside cleaned dataset
- Or append audit trail metadata to the exported file

**Format for audit export (JSON):**
```json
[
  {
    "step": 1,
    "timestamp": "2025-01-15T10:30:45.123Z",
    "row_index": 15,
    "column_name": "Age",
    "original_value": "Rahul",
    "action_type": "Replace",
    "new_value": 25,
    "issue_type": "Type Incompatibility"
  },
  {
    "step": 2,
    "timestamp": "2025-01-15T10:31:00.456Z",
    "row_index": 42,
    "column_name": null,
    "original_value": null,
    "action_type": "Remove",
    "new_value": null,
    "issue_type": "Duplicate Record"
  }
]
```

### 10.3 Audit Display in UI

**User-facing audit view:**
- Table showing all actions
- Columns: Step, Timestamp, Row, Column, Original Value, Action, New Value, Issue Type
- Sortable by any column
- Filterable by action type, column, or issue type
- Searchable by row number or value

---

## 11. Data Export

### 11.1 Export Workflow

```
1. User selects format (CSV, XLSX, JSON)
2. System prepares cleaned dataset
3. Apply user-selected columns (all by default)
4. Format data according to target format
5. Generate file
6. Return download link to frontend
```

### 11.2 CSV Export

**Format:**
- Header row with column names
- Subsequent rows with data
- Standard CSV format (RFC 4180)

**Configuration:**
- Delimiter: `,` (comma, standard)
- Quote character: `"` (double-quote)
- Escape character: `\` (backslash)
- Encoding: UTF-8

**Implementation (Polars preferred):**
```python
df.write_csv("output.csv")
```

**Implementation (Pandas fallback):**
```python
df.to_csv("output.csv", index=False, encoding="utf-8")
```

**Special handling:**
- Missing values: Rendered as empty cells (or `None` if user prefers)
- Boolean values: Export as `True`/`False` or `1`/`0` (configurable)
- Date values: Export in ISO format (`YYYY-MM-DD`) by default

### 11.3 Excel Export

**Format:**
- `.xlsx` (modern Excel, recommended)
- `.xls` (legacy, optional)

**Structure:**
- Single sheet named "Data" or "Cleaned_Data"
- Header row with column names
- Subsequent rows with data

**Implementation (Polars preferred):**
```python
df.write_excel("output.xlsx", worksheet="Data")
```

**Implementation (openpyxl):**
```python
from openpyxl import Workbook
wb = Workbook()
ws = wb.active
# Write data...
wb.save("output.xlsx")
```

**Special handling:**
- Column formatting:
  - Numerical columns: Number format (2 decimal places for floats)
  - Date columns: Date format (MM/DD/YYYY or locale-specific)
  - Boolean columns: Yes/No or True/False
  - Text columns: Text format, word-wrap enabled
- Missing values: Leave cells empty
- Autofit column widths (optional, improves UX)

### 11.4 Tabular JSON Export

**Format:**
Array of objects (one per row):

```json
[
  { "Name": "Alice", "Age": 30, "City": "NYC" },
  { "Name": "Bob", "Age": 25, "City": "LA" }
]
```

**Implementation (Polars preferred):**
```python
df.write_json("output.json", format="json")  # Or write_ndjson
```

**Implementation (Pandas):**
```python
df.to_json("output.json", orient="records", indent=2)
```

**Special handling:**
- Missing values: `null` in JSON
- Date values: ISO format string (`"2025-01-15"`)
- Boolean values: JSON boolean (`true`, `false`)
- Numeric values: JSON number (no quotes)

### 11.5 Export Quality Checks

**Before export, validate:**

| Check | Condition | Action |
|---|---|---|
| Dataset empty | No rows remain | Warn: "Dataset is empty. Continue?" |
| All null column | Column has no non-null values | Warn: "Column [X] is all null. Include in export?" |
| Large file | Export would be > 500 MB | Warn: "Export is large. This may take time." |
| Invalid values | Any remaining invalid/suspicious values | Inform: "[X] issues remain unresolved. Include them in export?" |

---

## 12. Reset to Original

### 12.1 Reset Workflow

**Trigger:** User clicks "Reset to Original" or similar control.

**Process:**
```
1. Confirm action: "Discard all changes and revert to original dataset?"
2. If confirmed:
   a. Discard working DataFrame
   b. Copy original DataFrame to working DataFrame
   c. Clear all audit records
   d. Reset issue list
   e. Recalculate statistics
   f. Return to "Dataset Analysis" view
```

**After reset:**
- User can start cleaning again from scratch
- All previous changes are discarded (no undo from UI; user can re-upload if needed)
- Original dataset remains untouched (always available)

---

## 13. Statistics Calculation

### 13.1 Numerical Column Statistics

**Calculate for every numerical column:**

| Statistic | Formula | Notes |
|---|---|---|
| Mean | `sum(values) / count(non-null)` | Arithmetic mean |
| Median | Middle value when sorted | Percentile 50 |
| Min | Minimum value | Excluding null |
| Max | Maximum value | Excluding null |
| Std Dev | Standard deviation | Sample std dev (N-1 denominator) |
| Count (total) | Number of rows | Including null |
| Count (non-null) | Number of non-null values | Excluding null |
| Count (null) | Number of null/missing values | Null count |
| Variance | Std dev squared | Optional |

**Implementation (Polars preferred):**
```python
stats = df[column_name].describe()  # Returns dict with all stats
```

**Implementation (Pandas fallback):**
```python
{
    'mean': df[column_name].mean(),
    'median': df[column_name].median(),
    'min': df[column_name].min(),
    'max': df[column_name].max(),
    'std': df[column_name].std(),
    'count': df[column_name].count(),
}
```

### 13.2 Categorical Column Statistics

**Calculate for every categorical column:**

| Statistic | Notes |
|---|---|
| Count (total) | Total number of rows |
| Count (non-null) | Number of non-null values |
| Count (null) | Number of missing values |
| Unique count | Number of distinct values |
| Mode | Most frequent value |
| Mode frequency | How many times mode appears |
| Frequency distribution | Top 10 most frequent values and counts |

**Implementation (Polars):**
```python
unique_count = df[column_name].n_unique()
mode = df[column_name].mode()[0]  # Most frequent
freq = df[column_name].value_counts().head(10)
```

### 13.3 Date Column Statistics

**Calculate for date/time columns:**

| Statistic | Notes |
|---|---|
| Count (total) | Total rows |
| Count (non-null) | Non-null values |
| Count (null) | Missing values |
| Earliest date | Minimum date |
| Latest date | Maximum date |
| Date range | Latest - Earliest (in days) |

### 13.4 Statistics Update Frequency

- **Initial load:** Calculate after dataset ingestion
- **After cleaning:** Recalculate after each Replace/Remove action (or batch after user confirms all changes)
- **Performance:** For large datasets, calculate on-demand (lazy evaluation)

---

## 14. Polars vs Pandas Principle

### 14.1 Primary: Polars

**Use Polars for:**
- Initial ingestion (read_csv, read_excel, read_json)
- Data storage (preferred in-memory representation)
- Type inference
- Missing-value detection
- Duplicate detection
- Filtering and transformations
- Aggregations and statistics
- Export operations

**Advantages:**
- Faster for large datasets
- Lazy evaluation (deferred computation)
- Strong type system
- Memory efficient

### 14.2 Secondary: Pandas

**Use Pandas for:**
- Compatibility with libraries that require DataFrame input
- Complex groupby/pivot operations if Polars is insufficient
- Visualization library inputs (if needed)
- Fallback for edge cases

**Conversion strategy:**
```python
# Convert Polars to Pandas only when necessary
if library_requires_pandas:
    pandas_df = polars_df.to_pandas()
else:
    use_polars_df_directly()
```

### 14.3 Avoid Unnecessary Conversions

**Anti-pattern:**
```python
# BAD: Polars → Pandas → Polars
df_pl = pl.read_csv(file)
df_pd = df_pl.to_pandas()
df_pl_again = pl.from_pandas(df_pd)
```

**Good pattern:**
```python
# GOOD: Stay in Polars
df_pl = pl.read_csv(file)
# Perform all operations in Polars
df_pl.filter(...)
df_pl.select(...)
```

---

## 15. Error Handling and Edge Cases

### 15.1 Empty or Null Columns

**Scenario:** Column contains only null values.

**Handling:**
```
1. Type inference → defaults to "Unknown" or prompts user
2. Statistics → show null count = row count, others = N/A
3. Data quality → flag as high-priority issue
4. Suggestion → user can remove column or replace all values
```

### 15.2 All-Identical Columns

**Scenario:** Column contains only one unique value (e.g., all "Active").

**Handling:**
```
1. Flag as suspicious (no variance)
2. Suggest removal: "Column contains no variance. Consider removing."
3. Allow user to keep or remove
```

### 15.3 Very High Cardinality Columns

**Scenario:** Column has as many unique values as rows (or close to it).

**Type inference:**
```
If unique_count >= 0.95 * row_count:
  Infer as Identifier (if numeric)
  Or Text (if string)
```

**Statistics:**
- Don't compute frequency distribution (too many categories)
- Show unique count instead
- Suggest this is an identifier or free-form text

### 15.4 Mixed Type Columns

**Scenario:** Column contains both numbers and strings.

**Detection:**
```
Numerical parsing succeeds for 60% of values, fails for 40%
→ Ambiguous type; ask user
```

**Behavior:**
- Show detected values by type breakdown
- Offer to coerce to target type (replace incompatible values)
- Or keep as Text/Categorical

### 15.5 Very Long Strings

**Scenario:** Text cell contains 10,000+ characters.

**Handling:**
```
1. Still parse normally
2. In UI, truncate display: "Lorem ipsum dolor sit amet... [TRUNCATED]"
3. Full text available on hover or detail view
4. Export includes full text
```

---

## 16. Polars Implementation Details

### 16.1 Ingestion Examples

**CSV:**
```python
import polars as pl

df = pl.read_csv(
    file_path,
    infer_schema_length=10000,
    ignore_errors=False,  # Raise on parsing error
    encoding="utf-8"
)
```

**Excel:**
```python
df = pl.read_excel(
    file_path,
    sheet_name=0,  # First sheet
    has_header=True
)
```

**JSON:**
```python
df = pl.read_json(file_path)
```

### 16.2 Type Inference with Polars

**Built-in inference:**
```python
df.schema  # Returns: {column_name: inferred_type, ...}
```

**Manual type specification:**
```python
df = pl.read_csv(
    file_path,
    dtypes={
        "Age": pl.Int32,
        "Name": pl.Utf8,
        "Date": pl.Date
    }
)
```

### 16.3 Operations Examples

**Missing values:**
```python
null_count = df[column_name].null_count()
df_without_nulls = df.filter(pl.col(column_name).is_not_null())
```

**Duplicates:**
```python
duplicates = df.filter(df.is_duplicated())
```

**Statistics:**
```python
df[column_name].describe()
```

**Export:**
```python
df.write_csv("output.csv")
df.write_excel("output.xlsx")
df.write_json("output.json")
```

---

## 17. Validation and Testing Checkpoints

**Data processing functions should be tested:**

| Function | Test Cases |
|---|---|
| **Type inference** | CSV with mixed types, Excel with dates, JSON with nulls |
| **Missing detection** | Columns with varying null representations |
| **Duplicate detection** | Exact duplicates, near-duplicates (should NOT flag), all unique |
| **Type incompatibility** | Numeric column with text, date column with invalid format |
| **Suspicious detection** | Outliers, domain rule violations, low-variance columns |
| **Replace operation** | Replace with mean, median, mode, custom value |
| **Remove operation** | Remove value, remove entire row |
| **Audit trail** | Correct recording of all operations |
| **Statistics** | Accuracy of mean, median, std dev, unique count |
| **Export** | CSV/XLSX/JSON contain correct data, preserves data types |
| **Reset** | Original dataset untouched after cleanup and reset |
| **Edge cases** | Empty column, all-null column, high cardinality, mixed types |

---

## 18. Performance Targets

**For tested dataset sizes (to be benchmarked):**

| Operation | Target Time (100 MB) | Notes |
|---|---|---|
| Ingestion | < 5 seconds | File reading and parsing |
| Type inference | < 2 seconds | Inferring column types |
| Missing detection | < 1 second | Scanning for nulls |
| Duplicate detection | < 2 seconds | Hashing and grouping |
| Incompatibility detection | < 2 seconds | Type validation |
| Statistics calculation | < 1 second | Aggregations |
| Export (CSV) | < 3 seconds | Writing file |
| Visualization generation | < 5 seconds | Matplotlib/Seaborn chart |

*These are targets; actual performance should be benchmarked and documented in README.*

---

## 19. Future Extensions (Out of Scope for V1)

**Possible enhancements post-V1:**

- Fuzzy duplicate detection (approximate matching)
- Outlier detection using isolation forest or LOF
- Automatic imputation using machine learning
- Column type standardization (e.g., parse dates, standardize categories)
- Correlation analysis between columns
- Distribution fitting (normal, exponential, etc.)
- Data profiling and recommendations
- Version control for dataset transformations
- Collaboration and commenting on issues

---

## 20. Document History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2025 | Initial data processing specification for V1 |