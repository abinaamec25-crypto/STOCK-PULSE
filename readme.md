# StockPulse AI — Enterprise Inventory Tracking & Anomaly Detection System

**Project ID**: DIT-P04 | **Team ID**: Team T04 | **Domain**: Operations & Inventory Monitoring

**Internship**: DefineInfoTech Pvt. Ltd. (DIT) Internship 2026

**Institution**: Anjalai Ammal Mahalingam Engineering College (AAMEC), Kovilvenni, Thiruvarur

**Live Production URL**: <https://stock-pulse-7ze5.onrender.com/>

**GitHub Repository**: [https://github.com/abin-s/stockpulse-ai](https://www.google.com/search?q=https://github.com/abin-s/stockpulse-ai)

## 1. Executive Summary & Overview

**StockPulse AI** is an enterprise-grade automated inventory tracking, stock balance calculation, and anomaly detection platform designed and engineered by Team T04 during the DefineInfoTech Pvt. Ltd. (DIT) Internship 2026. The platform provides complete deterministic visibility across multi-warehouse supply chain operations by processing product master registers alongside real-time timestamped stock movement transaction feeds (receipts and issues).

The platform automates dynamic balance calculations, enforces reorder safety buffers, identifies low/negative stock hazards, intercepts unauthorized SKU activity, generates audit logs, and exports formatted executive workbooks.

## 2. Team T04 Allocation & Contribution Roster

| S.No | Team Member | DIT Internship ID | Project Role | Primary Engineering Contribution | 
| ----- | ----- | ----- | ----- | ----- | 
| 1 | **Abin S (Team Lead)** | `DIT2026S1019` | Full-Stack & Integration Lead | System architecture, FastAPI backend (`app.py`), in-memory caching pipeline, automated ETL ingestion, and Render cloud deployment. | 
| 2 | **V Gopiha Sri** | `DIT2026S1016` | Data Engineering & Rules | Synthetic industrial catalog curation, dynamic balance formulation, safety buffer thresholds, and deficit calculations (`src/business_rules.py`). | 
| 3 | **P. Dharshini** | `DIT2026S1017` | Validation & Anomaly Engine | Canonical header normalization, schema sanitization (`src/validation.py`), quarantine of invalid records, and unknown SKU interception (`PRD-9999`). | 
| 4 | **A. Flora Emmaculate** | `DIT2026S1018` | Reporting Engine & Excel Workbooks | OpenPyXL report generation (`src/report_generator.py`), dynamic column auto-fitting, automated cell merge, and generating all 5 output workbooks. | 
| 5 | **Heamkumar R** | `DIT2026S1020` | Analytics & QA Verification | Executive dashboard analytics, Chart.js visual data bindings, KPI summary cards, and automated unit test suite (`tests/test_inventory.py`). | 

## 3. Mathematical Foundations & Business Rules

The calculation engine in `src/business_rules.py` executes strict deterministic mathematical logic:

* **Dynamic Stock Balance Equation**:
  

  $$
  \text{Current Balance} = \text{Opening Stock} + \sum \text{Stock IN (Receipts)} - \sum \text{Stock OUT (Issues)}
  $$

* **Reorder Condition**:
  

  $$
  \text{Reorder Required} = \begin{cases} \text{"YES"}, & \text{if } \text{Current Balance} < \text{Minimum Stock} \\ \text{"NO"}, & \text{otherwise} \end{cases}
  $$

* **Stock Deficit (Units)**:
  

  $$
  \text{Stock Deficit} = \max(0, \text{Minimum Stock} - \text{Current Balance})
  $$

* **Estimated Purchase Order Cost (INR)**:
  

  $$
  \text{PO Value} = \text{Recommended Reorder Qty} \times \text{Unit Price}
  $$

* **Current Stock Valuation (INR)**:
  

  $$
  \text{Stock Valuation} = \max(0, \text{Current Balance}) \times \text{Unit Price}
  $$

### Six-Tier Inventory Health Classification

1. **NEGATIVE STOCK (CRITICAL)**: $\text{Current Balance} < 0$. Overdrawn stockout; physical parts issued without system receipts. Immediate physical audit required.

2. **OUT OF STOCK**: $\text{Current Balance} == 0$. Complete exhaustion; assembly line halted. Emergency PO dispatch.

3. **CRITICAL BUFFER**: $0 < \text{Current Balance} \le 0.25 \times \text{Minimum Stock}$. Severely depleted safety buffer ($\le 25\%$). High stockout risk within 24–48 operating hours.

4. **LOW STOCK**: $0.25 \times \text{Minimum} < \text{Balance} < \text{Minimum Stock}$. Sub-buffer level. Routine purchase requisition triggered to replenish buffer.

5. **HEALTHY**: $\text{Minimum Stock} \le \text{Balance} \le 3.0 \times \text{Minimum Stock}$. Optimal operational equilibrium. Stable buffer with no procurement capital commitment needed.

6. **OVERSTOCKED**: $\text{Current Balance} > 3.0 \times \text{Minimum Stock}$. Excessive holding. Working capital tied up; potential shelf-life or obsolescence risk.

## 4. Repository Structure

```
stockpulse-ai/
├── app.py                      # FastAPI web server, API routing, in-memory cache
├── requirements.txt            # Production dependencies
├── Dockerfile                  # Container definition for reproducible deployment
├── render.yaml                 # Render cloud infrastructure specification
├── README.md                   # System documentation & execution guide
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

## 5. Installation & Execution Guide

### Prerequisites

* Python 3.10+ installed

* Git version control

* Google Chrome or modern web browser

### Step 1: Clone Repository & Create Virtual Environment

```
git clone https://github.com/abin-s/stockpulse-ai.git
cd stockpulse-ai

# Create isolated virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

```

### Step 2: Install Production Dependencies

```
pip install -r requirements.txt

```

### Step 3: Run the Application

```
# Start FastAPI web server with Uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

```

Open your browser and navigate to `http://localhost:8000` to access the interactive executive dashboard.

## 6. Running Automated Unit Tests

In compliance with Task 6 testing standards, execute the automated test suite:

```
python -m unittest discover tests

```

### Verified Test Suite Results (0.000s execution)

* `test_stock_balance_calculation`: Verifies dynamic formula $50 + 20 - 25 == 45.0$ units. **\[PASS\]**

* `test_reorder_condition`: Verifies reorder flag: $15 < 25 \rightarrow \text{YES}$ and $30 \ge 25 \rightarrow \text{NO}$. **\[PASS\]**

* `test_negative_stock_health`: Verifies health classifier assigns `NEGATIVE STOCK (CRITICAL)` for balance $< 0$. **\[PASS\]**

* `test_unknown_product_code_rejection`: Verifies validator rejects unregistered part IDs (`PRD-9999`). **\[PASS\]**

* `test_valid_transaction`: Verifies valid movements are correctly sanitized and parsed as float quantities. **\[PASS\]**

## 7. API Endpoint Specification

| HTTP Method | Endpoint Route | Operational Purpose & Return Payload | 
| ----- | ----- | ----- | 
| `GET` | `/` | Renders the responsive HTML5 dark-theme dashboard with Chart.js charts and official DIT corporate branding. | 
| `GET` | `/api/data` | Returns cached JSON payload with summary KPIs, calculated inventory records, valid transactions, and anomalies. | 
| `POST` | `/api/run-pipeline` | Forces an explicit ETL pipeline recalculation across the active input dataset, regenerating all 5 Excel workbooks. | 
| `POST` | `/api/upload-excel` | Accepts multipart Excel upload (`.xlsx`), updates `input/Input_Data.xlsx`, and triggers automated pipeline ingestion. | 
| `GET` | `/api/download/{report}` | Directly streams generated Excel files (`Stock_Report`, `Reorder_List`, `Error_Report`, etc.) as download attachments. | 
| `GET` | `/api/quick-action/{type}` | Generates dynamic vendor purchase order emails (`po_email`) or operations risk briefing assessments. | 

## 8. Sponsoring Enterprise & Certification

* **Sponsoring Enterprise**: DefineInfoTech Pvt. Ltd. (DIT), Coimbatore, Tamil Nadu, India

* **Tagline**: *We Define Intellect | People • Technology • Impact*

* **Submission Status**: Fully Verified, Tested, and Deployed for Project Review (Task 10).