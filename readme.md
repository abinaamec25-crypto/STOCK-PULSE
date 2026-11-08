# StockPulse AI — Enterprise Inventory Tracking & Anomaly Detection Platform



> **Project ID:** DIT-P04 | **Team ID:** Team T04 | **Domain:** Operations & Inventory Monitoring
>
> **Internship Programme:** DefineInfoTech Pvt. Ltd. (DIT) Industrial Internship 2026
>
> **Institution:** Anjalai Ammal Mahalingam Engineering College (AAMEC), Kovilvenni, Thiruvarur
>
> **Live Production URL:** <https://stock-pulse-7ze5.onrender.com/>
>
> **GitHub Repository:** <https://github.com/abinaamec25-crypto/STOCK-PULSE>

## 1. Executive Summary & Problem Scope

**StockPulse AI** is an enterprise-grade automated inventory tracking, stock balance calculation, and anomaly detection platform designed and engineered by **Team T04** during the **DefineInfoTech Pvt. Ltd. (DIT) Internship 2026**.

In discrete manufacturing plants, assembly facilities, and logistics distribution centers, manual spreadsheet inventory management leads to severe operational downtime and financial losses:

1. **Negative Stock Emergencies:** Spare parts are issued to shop-floor technicians without verified stock receipts, driving physical balances below zero.

2. **Unauthorized SKU Movements:** Obsolete, mistyped, or unapproved product codes (e.g., `PRD-9999`) bypass master catalog validation, corrupting ledger integrity.

3. **Buffer Depletion & Assembly Line Stoppages:** Production lines halt unexpectedly when parts drop below buffer levels without proactive alerts, forcing expensive emergency rush shipments.

StockPulse AI eliminates these liabilities through automated multi-tab Excel ingestion, canonical regex normalization, deterministic balance calculations, automated safety buffer deficit tracking, and OpenPyXL workbook exports.

## 2. Team T04 Allocation & Contribution Roster

| S.No | Team Member | DIT Internship ID | Project Role | Granular Technical Ownership | 
| ----- | ----- | ----- | ----- | ----- | 
| 1 | **Abin S (Team Lead)** | `DIT2026S1019` | Full-Stack & Integration Lead | System architecture, FastAPI REST API (`app.py`), in-memory caching pipeline, automated batch ETL ingestion, and Render cloud deployment. | 
| 2 | **V Gopiha Sri** | `DIT2026S1016` | Data Engineering & Business Rules | Synthetic industrial catalog curation, dynamic balance formulation ($Opening + In - Out$), safety buffer thresholds, and deficit purchase calculations (`src/business_rules.py`). | 
| 3 | **P. Dharshini** | `DIT2026S1017` | Validation & Anomaly Engine | Canonical header normalization, schema sanitization (`src/validation.py`), quarantine of invalid records, and unknown SKU interception (`PRD-9999`). | 
| 4 | **A. Flora Emmaculate** | `DIT2026S1018` | Reporting Engine & Excel Workbooks | OpenPyXL workbook architecture (`src/report_generator.py`), dynamic column width detection, cell styling, and automated generation of all 5 output workbooks. | 
| 5 | **Heamkumar R** | `DIT2026S1020` | Analytics & QA Verification | Executive dashboard UI integration, Chart.js visual data bindings, KPI summary cards, and automated unit test suite execution (`tests/test_inventory.py`). | 

## 3. Mathematical Foundations & Business Rules Engine

The core computation engine in `src/business_rules.py` executes deterministic mathematical logic:

### 3.1 Dynamic Stock Balance Equation

For every SKU in the verified catalog, real-time balances are computed dynamically:

$$
\text{Current Balance} = \text{Opening Stock} + \sum \text{Stock IN (Receipts)} - \sum \text{Stock OUT (Issues)}
$$

### 3.2 Safety Buffer & Reorder Formulation

* **Reorder Trigger:**
  

  $$
  \text{Reorder Required} = \begin{cases} \text{"YES"}, & \text{if } \text{Current Balance} < \text{Minimum Stock} \\ \text{"NO"}, & \text{otherwise} \end{cases}
  $$

* **Stock Deficit Units:**
  

  $$
  \text{Stock Deficit} = \max(0, \text{Minimum Stock} - \text{Current Balance})
  $$

* **Estimated Purchase Order Cost (INR):**
  

  $$
  \text{PO Value} = \text{Recommended Reorder Quantity} \times \text{Unit Price}
  $$

* **Zero-Bound Stock Valuation (INR):**
  

  $$
  \text{Current Stock Valuation} = \max(0, \text{Current Balance}) \times \text{Unit Price}
  $$

  
  *(Ensures negative balances never produce distorted negative inventory assets)*

### 3.3 Six-Tier Inventory Health Classification Matrix

| Health Status Category | Boundary Condition | Operational Interpretation & Action Required | 
| ----- | ----- | ----- | 
| **NEGATIVE STOCK (CRITICAL)** | $\text{Current Balance} < 0$ | Overdrawn stockout. Physical parts issued without verified receipts. Flagged for immediate physical warehouse audit. | 
| **OUT OF STOCK** | $\text{Current Balance} == 0$ | Complete inventory exhaustion. Assembly line halted. Immediate emergency PO dispatch. | 
| **CRITICAL BUFFER** | $0 < \text{Current Balance} \le 0.25 \times \text{Minimum}$ | Severely depleted buffer ($\le 25\%$). High stockout hazard within 24–48 operating hours. | 
| **LOW STOCK** | $0.25 \times \text{Minimum} < \text{Balance} < \text{Minimum}$ | Sub-buffer level. Routine purchase requisition triggered to replenish buffer. | 
| **HEALTHY** | $\text{Minimum} \le \text{Balance} \le 3.0 \times \text{Minimum}$ | Optimal operational equilibrium. Stable buffer with no procurement capital commitment needed. | 
| **OVERSTOCKED** | $\text{Current Balance} > 3.0 \times \text{Minimum}$ | Excessive holding. Working capital tied up; potential shelf-life or obsolescence risk. | 

## 4. System Architecture & Complete Codebase Layout

```
stockpulse-ai/
├── app.py                      # FastAPI web server, API routing, in-memory cache
├── requirements.txt            # Production dependencies (fastapi, uvicorn, openpyxl, etc.)
├── Dockerfile                  # Container definition for reproducible deployment
├── render.yaml                 # Render cloud infrastructure as code specification
├── README.md                   # System documentation & execution guide
├── .gitignore                  # Git ignore rules for virtualenvs, caches, logs
├── input/
│   └── Input_Data.xlsx         # Master catalog, stock receipts, and stock issues
├── src/
│   ├── __init__.py             # Module initialization
│   ├── business_rules.py       # Stock balance arithmetic & deficit PO calculation
│   ├── validation.py           # Canonical header regex normalizer & anomaly quarantine
│   └── report_generator.py     # OpenPyXL automated workbook generation engine
├── templates/
│   └── index.html              # Responsive dark-theme dashboard with Chart.js
├── static/
│   ├── css/style.css           # DIT branded stylesheet, responsive grid layout
│   └── js/dashboard.js         # Asynchronous AJAX data bindings & chart renderers
├── output/
│   ├── Stock_Report.xlsx       # Comprehensive 11-column warehouse inventory register
│   ├── Reorder_List.xlsx       # Prioritized 11-column purchase requisition ledger
│   ├── Error_Report.xlsx       # Quarantined anomaly records & audit failure reasons
│   ├── Dashboard_Report.xlsx   # Executive KPI summary cards & category totals
│   └── Master_and_Transactions_Archived.xlsx # Immutable audit snapshot
├── logs/
│   └── error_log.txt           # Timestamped stack traces & defensive exception logs
└── tests/
    ├── __init__.py             # Test package marker
    └── test_inventory.py       # Python unittest suite (5/5 passing tests)

```

## 5. Step-by-Step Installation & Local Execution

### Prerequisites

* Python 3.10 or higher

* Git installed

* Modern web browser (Chrome, Edge, Firefox)

### Step 1: Clone Repository

```
git clone https://github.com/abinaamec25-crypto/STOCK-PULSE.git
cd STOCK-PULSE

```

### Step 2: Set Up Virtual Environment

```
# Create isolated environment
python3 -m venv venv

# Activate environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

```

### Step 3: Install Dependencies

```
pip install -r requirements.txt

```

### Step 4: Run Automated Unit Tests

```
python -m unittest discover tests

```

### Step 5: Start Production Server

```
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

```

Navigate to `http://localhost:8000` to access the interactive web application.

## 6. Testing Suite & Verification Matrix (12 Test Cases)

| Test ID | Subsystem | Input Scenario | Expected Defensive Behavior | Status | 
| ----- | ----- | ----- | ----- | ----- | 
| **TC-01** | Ingestion | Upload valid multi-tab Excel (`.xlsx`) | Extracts Product Master and Stock Movements | **PASS** | 
| **TC-02** | Ingestion | Upload corrupted or non-Excel binary | Rejects payload with HTTP 400 error | **PASS** | 
| **TC-03** | Normalizer | Fuzzy alias headers (`"SKU Code"`, `"qty"`) | Maps aliases to standard internal keys | **PASS** | 
| **TC-04** | Math Engine | Conforming movement transactions | $Opening + Receipts - Issues == Balance$ | **PASS** | 
| **TC-05** | Math Engine | Cumulative overdrawn movement feed | Health status flags `NEGATIVE STOCK (CRITICAL)` | **PASS** | 
| **TC-06** | Validation | Unknown product code (`PRD-9999`) | Intercepted & quarantined to `Error_Report.xlsx` | **PASS** | 
| **TC-07** | Validation | Negative movement quantity (`-10.0`) | Blocked from calculation pipeline | **PASS** | 
| **TC-08** | Reorder | Balance breaches safety buffer | Generates `Reorder Required == 'YES'` | **PASS** | 
| **TC-09** | Reorder | Buffer deficit calculation | Computes $\max(0, \text{Min} - \text{Balance})$ | **PASS** | 
| **TC-10** | Reporting | OpenPyXL column auto-fitting | Auto-sizes columns to $(max\_len + 3)$ | **PASS** | 
| **TC-11** | REST API | In-memory cache hit on `/api/data` | Serves cached JSON in $<5\text{ms}$ | **PASS** | 
| **TC-12** | Cloud | Managed Render web service deployment | Binds dynamically to container `$PORT` | **PASS** | 

## 7. REST API Endpoints Specification

| HTTP Method | Route | Description & Return Payload | 
| ----- | ----- | ----- | 
| `GET` | `/` | Renders HTML5 responsive executive dashboard with Chart.js bindings. | 
| `GET` | `/api/data` | Returns cached JSON containing summary KPIs, catalog records, and anomalies. | 
| `POST` | `/api/run-pipeline` | Executes end-to-end ETL calculation and regenerates all 5 Excel workbooks. | 
| `POST` | `/api/upload-excel` | Multipart upload for new Excel datasets, updating `input/Input_Data.xlsx`. | 
| `GET` | `/api/download/{report}` | Streams generated report workbooks (`Stock_Report`, `Reorder_List`, etc.). | 
| `GET` | `/api/quick-action/{type}` | Generates dynamic vendor PO emails (`po_email`) or operational risk briefs. | 

## 8. Sponsoring Enterprise & Certification

* **Sponsoring Enterprise:** DefineInfoTech Pvt. Ltd. (DIT), Coimbatore, Tamil Nadu, India

* **Executive Leadership:** Mr. Selvaraj Kishok Kumar, Chief Executive Officer (CEO)

* **Academic Partner:** Anjalai Ammal Mahalingam Engineering College (AAMEC), Kovilvenni, Thiruvarur

* **Certification Status:** Production Verified & Tested for Phase 1 Technical Review (Task 10).