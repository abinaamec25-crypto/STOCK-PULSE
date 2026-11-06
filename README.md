# StockPulse AI — Enterprise Inventory & Stock Monitoring Suite
### DefineInfoTech Pvt. Ltd. (DIT) Internship 2026
**Project ID**: DIT-P04 | **Team ID**: Team T04  
**College**: Anjalai Ammal Mahalingam Engineering College, Kovilvenni, Thiruvarur  
**Live Cloud Deployment**: [https://stock-pulse-rsvn.onrender.com/](https://stock-pulse-rsvn.onrender.com/)

---

## 👥 Team T04 Roster & Allocation
| S.No | Full Name | DIT Internship ID | Project Role & Contribution |
| :---: | :--- | :---: | :--- |
| 1 | **Abin S** *(Team Lead)* | **DIT2026S1019** | System Architecture, Pipeline Integration & Cloud Deployment |
| 2 | **V Gopiha Sri** | **DIT2026S1016** | Dataset Schema Design, Business Rules & Reorder Logic |
| 3 | **P. Dharshini** | **DIT2026S1017** | Data Validation Engine, Schema Mapping & Anomaly Auditing |
| 4 | **A. Flora Emmaculate** | **DIT2026S1018** | Excel Workbook Generation, Reporting Engine & Styling |
| 5 | **Heamkumar R** | **DIT2026S1020** | Executive Dashboard Analytics, Visualizations & Test Suite |

---

## 🎯 Business Problem Statement & Scope
Modern manufacturing and assembly lines suffer frequent supply chain disruptions caused by:
1. Stockouts and delayed emergency purchase requisitions.
2. Unauthorized stock movement entries referencing unregistered parts (unknown SKU codes).
3. Overdrawn inventory balances resulting from stock issues exceeding verified warehouse receipts (negative stock).

**StockPulse AI** automates multi-warehouse inventory monitoring by ingesting product master catalogs and stock transaction ledgers, dynamically computing balances, identifying low and negative stock risks, detecting unregistered SKUs, and automatically generating purchase orders with estimated budget commitments.

$$\text{Current Balance} = \text{Opening Stock} + \text{Stock IN (Receipts)} - \text{Stock OUT (Issues)}$$

---

## 📦 Project Deliverables
1. **Warehouse Stock Report (`output/Stock_Report.xlsx`)**: Real-time calculated balances, unit prices, total stock valuation, warehouse bay locations, and stock health classifications.
2. **Reorder Recommendations (`output/Reorder_List.xlsx`)**: Prioritized purchase requisitions for all SKUs falling below minimum buffer levels, with deficit units, suggested reorder lot sizes, vendor contacts, and estimated PO values.
3. **Audit Exception Register (`output/Error_Report.xlsx`)**: Comprehensive isolation log for unauthorized product codes, invalid movement quantities, and overdrawn stock balances.
4. **Executive Dashboard (`output/Dashboard_Report.xlsx`)**: Formatted workbook with high-level KPI metric cards and category-wise stock valuation breakdowns.
5. **Interactive Web Dashboard**: Live web application built with FastAPI, TailwindCSS, Chart.js, and Lucide icons featuring official DIT corporate branding.

---

## 🚀 Setup & Execution Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Automation ETL Pipeline
Ingests master data and transactions, runs business rules, and generates all 5 Excel deliverables:
```bash
python src/main.py
```

### 3. Run Automated Unit Test Suite
Executes unit tests verifying dynamic balance formulas, reorder evaluations, stock health classification, and anomaly rejections:
```bash
python -m unittest discover tests
```

### 4. Start Web Application & Dashboard
```bash
python app.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser to access the interactive dashboard.

---

## 🏛️ Project Directory Structure
```text
StockPulse_AI/
├── app.py                      # FastAPI web server, REST API & interactive dashboard
├── README.md                   # Project documentation & team allocation details
├── requirements.txt            # Python dependencies (openpyxl, fastapi, uvicorn)
├── input/
│   └── Input_Data.xlsx         # Product master catalog and stock transaction feed
├── output/
│   ├── Stock_Report.xlsx       # Calculated warehouse stock balances and valuations
│   ├── Reorder_List.xlsx       # Automated reorder requisitions with supplier contacts
│   ├── Error_Report.xlsx       # Isolated unknown codes and negative stock alerts
│   ├── Dashboard_Report.xlsx   # Executive KPI and category performance workbook
│   └── Master_and_Transactions_Archived.xlsx
├── logs/
│   └── error_log.txt           # Timestamped audit ledger of validation and stock anomalies
├── src/
│   ├── __init__.py
│   ├── main.py                 # Core orchestration pipeline
│   ├── validation.py           # Schema normalization, master and transaction validation
│   ├── business_rules.py       # Balance calculations, reorder checks & health classification
│   ├── report_generator.py     # Openpyxl styled workbook generation with dynamic headers
│   ├── dashboard.py            # KPI metric cards & category summary table generation
│   └── logger.py               # Audit error logger and pipeline stream handler
├── static/
│   └── dit_logo.png            # Official DefineInfoTech corporate logo
└── tests/
    ├── __init__.py
    └── test_inventory.py       # Automated unit test suite
```

---

## 🛡️ DIT Internship 2026 Compliance
- **AI-Assisted Engineering**: Developed following the DIT TASK 07 AI-assisted software engineering lifecycle.
- **Corporate Branding**: Integrates the official DefineInfoTech Pvt. Ltd. corporate logo in the application interface and generated assets.
- **Data Privacy**: All sample inventory items, supplier contacts, and transaction IDs utilize synthetic, privacy-safe industrial data.
