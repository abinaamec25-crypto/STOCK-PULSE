# StockPulse AI
## Enterprise Inventory Tracking, Stock Balance & Anomaly Monitoring Platform

<p align="center">
  <strong>DefineInfoTech Pvt. Ltd. (DIT) — Industrial Internship Programme 2026</strong><br>
  Project ID: <strong>DIT-P04</strong> · Team ID: <strong>Team T04</strong><br>
  Anjalai Ammal Mahalingam Engineering College (AAMEC), Kovilvenni, Thiruvarur
</p>

<p align="center">
  <a href="https://stock-pulse-7ze5.onrender.com/">Live Application</a> ·
  <a href="https://github.com/abinaamec25-crypto/STOCK-PULSE">GitHub Repository</a>
</p>

---

## 1. Project Overview

**StockPulse AI** is an inventory monitoring and stock analysis application developed by Team T04 as part of the DefineInfoTech Pvt. Ltd. (DIT) Industrial Internship Programme 2026.

The platform reads product master data and stock movement transactions from an Excel workbook, validates and normalizes the input, calculates current stock balances, identifies inventory risks, and generates structured Excel reports. A FastAPI-powered web dashboard presents inventory KPIs, stock movement charts, reorder information, and audit exceptions.

### Problems addressed

- **Negative stock:** identifies products whose recorded issues exceed available stock and receipts.
- **Unknown product codes:** rejects transactions that refer to product IDs absent from the master catalog.
- **Low-stock conditions:** identifies products below their minimum stock threshold and calculates reorder requirements.
- **Manual reporting effort:** automates stock, reorder, exception, and dashboard workbook generation.
- **Inventory visibility:** provides a web interface for reviewing balances, transactions, reorder items, and operational summaries.

### Key capabilities

- Excel-based product master and transaction ingestion.
- Flexible column-name normalization and input validation.
- Dynamic stock balance calculation.
- Six-level stock health classification.
- Reorder evaluation and purchase-cost estimation.
- Unknown-code, invalid-record, and negative-stock anomaly logging.
- Automated Excel report generation using OpenPyXL.
- FastAPI REST endpoints and an interactive browser dashboard.
- Excel upload, report download, and operational quick-action summaries.

---

## 2. Team T04

| No. | Team member | DIT Internship ID | Project responsibility |
|---:|---|---|---|
| 1 | **Abin S — Team Lead** | DIT2026S1019 | System architecture, FastAPI application, pipeline integration, caching, and cloud deployment |
| 2 | **V Gopiha Sri** | DIT2026S1016 | Product data, inventory business rules, stock balance, and reorder calculations |
| 3 | **P. Dharshini** | DIT2026S1017 | Input normalization, data validation, and anomaly handling |
| 4 | **A. Flora Emmaculate** | DIT2026S1018 | Excel report generation, workbook formatting, and reporting |
| 5 | **Heamkumar R** | DIT2026S1020 | Dashboard analytics, visualizations, and test verification |

---

## 3. Technology Stack

| Area | Technology |
|---|---|
| Programming language | Python |
| Web framework | FastAPI |
| ASGI server | Uvicorn |
| Excel processing | OpenPyXL |
| Frontend | HTML, Tailwind CSS, JavaScript |
| Charts | Chart.js |
| Icons | Lucide |
| Automated testing | Python unittest |
| Cloud deployment | Render |

---

## 4. Inventory Calculation & Business Rules

The calculation and classification functions are implemented in **src/business_rules.py**. The main processing pipeline is in **src/main.py**.

### 4.1 Stock balance

For each product:

\[
\text{Current Balance}
=
\text{Opening Stock}
+
\text{Total Stock IN}
-
\text{Total Stock OUT}
\]

- **Opening Stock:** starting quantity.
- **Stock IN:** total quantity received.
- **Stock OUT:** total quantity issued.
- **Current Balance:** calculated quantity remaining.

### 4.2 Reorder condition

A reorder is required when the current balance is below the minimum stock level.

\[
\text{Reorder Required} =
\begin{cases}
\text{YES}, & \text{Current Balance} < \text{Minimum Stock}\\
\text{NO}, & \text{otherwise}
\end{cases}
\]

### 4.3 Stock deficit

\[
\text{Stock Deficit}
=
\max(0,\text{Minimum Stock}-\text{Current Balance})
\]

### 4.4 Recommended order quantity

When a reorder is required, the system uses the product's configured reorder quantity. Otherwise, the recommended order quantity is zero.

### 4.5 Estimated purchase order value

\[
\text{Estimated PO Cost}
=
\text{Recommended Order Quantity}
\times
\text{Unit Price}
\]

### 4.6 Current stock valuation

\[
\text{Stock Valuation}
=
\max(0,\text{Current Balance})
\times
\text{Unit Price}
\]

Negative balances therefore do not create negative inventory asset valuations.

### 4.7 Six-level stock health classification

The classification order and conditions below follow the implementation in **classify_stock_health()** in **src/business_rules.py**.

| Status | Condition | Meaning |
|---|---|---|
| **NEGATIVE STOCK (CRITICAL)** | Balance < 0 | Stock issues have exceeded available stock |
| **OUT OF STOCK** | Balance = 0 | No stock remains |
| **CRITICAL BUFFER** | 0 < Balance ≤ 25% of Minimum Stock | Severely depleted stock buffer |
| **LOW STOCK** | 25% of Minimum Stock < Balance < Minimum Stock | Below the required minimum |
| **HEALTHY** | Minimum Stock ≤ Balance ≤ 3 × Minimum Stock | Within the defined healthy range |
| **OVERSTOCKED** | Balance > 3 × Minimum Stock | Stock exceeds three times the minimum level |

---

## 5. System Workflow

1. **Read the workbook:** load the product master and, when available, the stock transaction worksheet.
2. **Identify worksheets:** select master and transaction sheets using their names, with a fallback to the available worksheets.
3. **Detect headers:** scan the first 15 rows for recognizable column headers.
4. **Normalize fields:** map supported column-name variations to standard internal field names.
5. **Validate records:** sanitize master records and transactions; reject duplicate master IDs, invalid quantities, and unknown product IDs.
6. **Calculate stock:** aggregate stock receipts and issues for each product and calculate the balance.
7. **Evaluate inventory health:** classify stock status, determine reorder requirements, and calculate deficit and valuation figures.
8. **Record anomalies:** log invalid records, unknown codes, and negative stock alerts.
9. **Generate reports:** create the Excel output workbooks.
10. **Display results:** serve the dashboard and JSON data through FastAPI.

### Core stock calculation example

For an item with:

- Opening Stock = 100 units
- Stock IN = 40 units
- Stock OUT = 55 units

\[
100 + 40 - 55 = 85\text{ units}
\]

The calculated current balance is **85 units**.

---

## 6. Input Data

The default input workbook is:

    input/Input_Data.xlsx

The pipeline supports a product master worksheet and an optional stock transaction worksheet. It identifies worksheets and headers using names and normalized column values rather than relying exclusively on fixed worksheet positions.

### Product master fields

The validation and processing code uses the following canonical fields:

- Product_ID
- Product_Name
- Category
- Opening_Stock
- Current_Stock
- Minimum_Stock
- Reorder_Quantity
- Unit_Price
- Supplier
- Supplier_Contact
- Warehouse_Location

### Transaction fields

- Transaction_ID
- Product_ID
- Transaction_Date
- Transaction_Type
- Quantity
- Reference_No
- Department_Remarks

The column normalizer supports common aliases for product IDs, descriptions, quantities, transaction types, stock levels, supplier details, and other fields.

**Validation rules include:**

- Duplicate product IDs are rejected.
- Negative opening stock is rejected.
- Transactions for product IDs missing from the master catalog are rejected.
- Transaction quantities must be greater than zero.
- Transaction types are interpreted as stock IN or stock OUT.
- Missing or invalid optional values may be replaced with defaults by the sanitization functions.

---

## 7. Generated Reports

The pipeline creates the following files in the **output/** directory.

| Report | File | Purpose |
|---|---|---|
| Warehouse stock report | Stock_Report.xlsx | Product details, opening stock, receipts, issues, current balance, status, valuation, and warehouse location |
| Reorder recommendations | Reorder_List.xlsx | Products below minimum stock, deficit, recommended quantity, estimated purchase cost, and supplier details |
| Exception report | Error_Report.xlsx | Validation exceptions, unknown product codes, and negative stock alerts |
| Executive dashboard report | Dashboard_Report.xlsx | Inventory KPI and category summary workbook |
| Archived input workbook | Master_and_Transactions_Archived.xlsx | Snapshot of the workbook processed by the pipeline |

The report workbooks are formatted with titles, styled headers, borders, and automatically adjusted column widths.

---

## 8. Web Dashboard

The FastAPI application is defined in **app.py**.

The dashboard includes:

- Product master and inventory KPI cards.
- Current stock valuation and reorder indicators.
- Unknown product code and negative stock indicators.
- Stock movement charts for opening stock, stock IN, and stock OUT.
- Stock health distribution chart.
- Stock balance, transaction, and reorder views.
- Search and filtering for displayed records.
- Excel upload and report download actions.
- Pipeline refresh action.
- Executive briefing, vendor purchase-order draft, and risk forecast quick actions.

The application uses an in-memory data cache to avoid rerunning the pipeline for every dashboard data request. The pipeline is refreshed when the run action is invoked or a workbook is uploaded.

---

## 9. REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Serves the interactive dashboard |
| GET | /api/data | Returns inventory KPIs, records, transactions, and anomalies |
| POST | /api/run-pipeline | Re-runs the inventory processing pipeline |
| POST | /api/upload-excel | Accepts an uploaded Excel workbook and processes it |
| GET | /api/download/{report_name} | Downloads a generated workbook by report name |
| GET | /api/quick-action/{action_type} | Generates an executive summary, vendor PO draft, or risk forecast |

### Quick-action types

| Action type | Output |
|---|---|
| executive_summary | Inventory overview and KPI briefing |
| po_email | Draft purchase-order communication for a selected inventory item |
| risk_forecast | Unknown-code, negative-stock, and reorder risk summary |

### Example API URLs

    http://127.0.0.1:8000/
    http://127.0.0.1:8000/api/data
    http://127.0.0.1:8000/api/download/Stock_Report
    http://127.0.0.1:8000/api/download/Reorder_List

---

## 10. Repository Structure

The structure below reflects the files currently present in the repository.

    STOCK-PULSE/
    ├── app.py
    ├── requirements.txt
    ├── .gitignore
    ├── README.md
    ├── README_Doc_Format.docx
    ├── requirements_Doc_Format.docx
    ├── DIT orginal logo png.png
    ├── input/
    │   └── Input_Data.xlsx
    ├── output/
    │   ├── Stock_Report.xlsx
    │   ├── Reorder_List.xlsx
    │   ├── Error_Report.xlsx
    │   ├── Dashboard_Report.xlsx
    │   └── Master_and_Transactions_Archived.xlsx
    ├── logs/
    │   ├── error_log.txt
    │   └── error_log_legacy_backup.txt
    ├── src/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── validation.py
    │   ├── business_rules.py
    │   ├── report_generator.py
    │   ├── dashboard.py
    │   ├── logger.py
    │   └── legacy backup modules
    ├── static/
    │   └── dit_logo.png
    └── tests/
        ├── __init__.py
        └── test_inventory.py

---

## 11. Installation & Local Execution

### Prerequisites

- Python 3.10 or later
- Git
- A modern web browser

### Step 1 — Clone the repository

    git clone https://github.com/abinaamec25-crypto/STOCK-PULSE.git
    cd STOCK-PULSE

### Step 2 — Create a virtual environment

**Windows:**

    python -m venv venv
    venv\Scripts\activate

**macOS / Linux:**

    python3 -m venv venv
    source venv/bin/activate

### Step 3 — Install dependencies

    python -m pip install --upgrade pip
    pip install -r requirements.txt

### Step 4 — Run the inventory pipeline

    python src/main.py

This processes the default input workbook and generates the Excel reports in output/.

### Step 5 — Run the unit tests

    python -m unittest discover -s tests -v

### Step 6 — Start the web application

    uvicorn app:app --host 127.0.0.1 --port 8000 --reload

Open the following address in your browser:

    http://127.0.0.1:8000

---

## 12. Automated Test Coverage

The repository's **tests/test_inventory.py** currently defines five unit tests.

| Test | What it checks |
|---|---|
| Stock balance calculation | Opening + Stock IN − Stock OUT |
| Reorder condition | Balance below minimum returns YES; otherwise NO |
| Negative stock classification | Negative balance is classified as negative stock |
| Unknown product rejection | A transaction referencing an unknown product ID is rejected |
| Valid transaction | A valid stock transaction is accepted and its quantity is sanitized |

Run the tests using:

    python -m unittest discover -s tests -v

Test results should be taken from the actual execution output; this documentation does not assume an unverified test result.

---

## 13. Deployment & Project Links

- **Live application:** https://stock-pulse-7ze5.onrender.com/
- **Source repository:** https://github.com/abinaamec25-crypto/STOCK-PULSE
- **Hosting platform:** Render

The live application may take time to respond when its hosting service is starting or waking from inactivity.

---

## 14. Sponsoring Organization & Academic Partner

| Particular | Details |
|---|---|
| Internship organization | DefineInfoTech Pvt. Ltd. (DIT) |
| Location | Coimbatore, Tamil Nadu, India |
| Project | StockPulse AI — DIT-P04 |
| Team | Team T04 |
| Academic institution | Anjalai Ammal Mahalingam Engineering College (AAMEC) |
| Institution location | Kovilvenni, Thiruvarur |

---

## 15. Project Summary

StockPulse AI brings inventory data ingestion, validation, stock balance computation, reorder evaluation, anomaly tracking, Excel reporting, and dashboard visualization into one workflow.

Its central business rule is:

\[
\boxed{\text{Closing Stock}=\text{Opening Stock}+\text{Stock IN}-\text{Stock OUT}}
\]

By turning stock movement records into calculated balances and actionable reports, the project helps make inventory monitoring more consistent, traceable, and accessible.

---

<p align="center">
  <strong>StockPulse AI · Team T04 · DIT Internship 2026</strong><br>
  Built at Anjalai Ammal Mahalingam Engineering College
</p>
