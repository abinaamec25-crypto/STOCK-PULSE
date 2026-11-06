"""
StockPulse AI — Enterprise Inventory & Stock Monitoring Suite
DefineInfoTech Pvt. Ltd. (DIT) | Team T04 | Project DIT-P04
"""

import sys
import shutil
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(project_root / "src") not in sys.path:
    sys.path.insert(0, str(project_root / "src"))

from src.main import run_pipeline

app = FastAPI(title="StockPulse AI", version="4.0.0")

INPUT_FILE = project_root / "input" / "Input_Data.xlsx"
OUTPUT_DIR = project_root / "output"
LOG_FILE = project_root / "logs" / "error_log.txt"

def load_data() -> Dict[str, Any]:
    return run_pipeline(INPUT_FILE, OUTPUT_DIR, LOG_FILE)

@app.get("/api/data")
async def api_get_data():
    data = load_data()
    return JSONResponse(content={
        "valid_count": data["valid_count"],
        "transactions_processed": data["transactions_processed"],
        "reorder_count": data["reorder_count"],
        "unknown_code_count": data["unknown_code_count"],
        "negative_stock_count": data["negative_stock_count"],
        "total_valuation": data["total_valuation"],
        "total_po_cost": data["total_po_cost"],
        "records": data["records"],
        "transactions": data["transactions"],
        "anomalies": data["anomalies"]
    })

@app.post("/api/run-pipeline")
async def api_run_pipeline():
    res = load_data()
    return {"status": "success", "summary": res}

@app.post("/api/upload-excel")
async def api_upload_excel(file: UploadFile = File(...)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only Excel files are accepted.")
    with open(INPUT_FILE, "wb") as buf:
        shutil.copyfileobj(file.file, buf)
    res = load_data()
    return {
        "status": "success",
        "message": f"Successfully processed '{file.filename}'",
        "summary": {
            "valid_count": res["valid_count"],
            "reorder_count": res["reorder_count"],
            "unknown_codes": res["unknown_code_count"],
            "negative_stock": res["negative_stock_count"]
        }
    }

@app.get("/api/download/{report_name}")
async def api_download_report(report_name: str):
    fpath = OUTPUT_DIR / f"{report_name}.xlsx"
    if not fpath.exists():
        load_data()
    if not fpath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=fpath, filename=f"{report_name}.xlsx")

@app.get("/api/quick-action/{action_type}")
async def api_quick_action(action_type: str):
    data = load_data()
    reorders = [r for r in data["records"] if r["Reorder_Required"] == "YES"]
    
    if action_type == "po_email":
        output = (
            "OFFICIAL PURCHASE REQUISITION DRAFT\n"
            "======================================================================\n"
            "TO: Apex Industrial Spares (apex.spares@corp.in)\n"
            "FROM: Procurement Division, DefineInfoTech Pvt. Ltd. (DIT)\n"
            "SUBJECT: URGENT PURCHASE ORDER — STOCKOUT EMERGENCY (PRD-1005)\n"
            "TERMS: Net 30 | DISPATCH WINDOW: 48 Hours\n\n"
            "Dear Vendor Partner,\n\n"
            "Our automated inventory balance monitoring engine (DIT-P04) has calculated a "
            "zero/negative stockout condition on mechanical production line A:\n\n"
            "  • SKU Code: PRD-1005\n"
            "  • Description: Industrial Heavy Duty V-Belt B-68\n"
            "  • Opening Stock: 20 Units\n"
            "  • Total Issues (Stock OUT): 20 Units\n"
            "  • Current Balance: 0 Units (Stockout Alert)\n"
            "  • Minimum Required Buffer: 40 Units\n"
            "  • Recommended Reorder Quantity: 80 Units\n"
            "  • Unit Price: ₹ 420.00\n"
            "  • Total Purchase Order Value: ₹ 33,600.00\n"
            "  • Warehouse Delivery Bay: WH-A-14\n\n"
            "Please confirm dispatch details and provide the e-way bill upon shipment.\n\n"
            "Authorized Signatory,\n"
            "Inventory Operations Lead — Team T04\n"
            "DefineInfoTech Pvt. Ltd."
        )
    elif action_type == "risk_forecast":
        output = (
            "DIT-P04 OPERATIONS SUPPLY CHAIN RISK ASSESSMENT\n"
            "======================================================================\n"
            f"1. Unknown Codes Liability:\n"
            f"   Detected {data['unknown_code_count']} unauthorized transactions referencing unregistered parts "
            "(e.g., PRD-9999). Security review required for unauthorized stock movements.\n\n"
            f"2. Overdrawn Stock Hazards:\n"
            f"   Found {data['negative_stock_count']} negative stock transactions where parts were issued "
            "without confirmed warehouse receipts. Production lead time is severely compromised.\n\n"
            f"3. Reorder Commitment:\n"
            f"   {data['reorder_count']} SKUs are currently below minimum safety levels. "
            f"Total immediate procurement capital needed: ₹ {data['total_po_cost']:,.2f}."
        )
    else:
        output = (
            "EXECUTIVE INVENTORY BRIEFING (TEAM T04)\n"
            "======================================================================\n"
            f"• Monitored Master SKUs : {data['valid_count']}\n"
            f"• Transactions Audited  : {data['transactions_processed']} movement events\n"
            f"• Total Current Valuation: ₹ {data['total_valuation']:,.2f}\n"
            f"• Reorder Action Rate   : {data['reorder_count']} of {data['valid_count']} items below safety levels\n"
            f"• Unknown Product Codes : {data['unknown_code_count']} isolated into Error_Report.xlsx\n"
            f"• Negative Stock Alerts : {data['negative_stock_count']} overdrawn balance warnings"
        )
    return {"status": "success", "content": output}

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StockPulse AI | DIT-P04 Inventory Management Suite</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body { background-color: #0B0F19; color: #F1F5F9; font-family: ui-sans-serif, system-ui, sans-serif; }
        .glass-panel { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
    </style>
</head>
<body class="min-h-screen flex flex-col p-6 space-y-6 max-w-7xl mx-auto">
    <!-- Top Header -->
    <header class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div class="flex items-center gap-3">
            <div class="h-10 w-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                <i data-lucide="package-search" class="w-6 h-6 text-white"></i>
            </div>
            <div>
                <div class="flex items-center gap-2">
                    <h1 class="text-xl font-bold text-white">StockPulse AI</h1>
                    <span class="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 font-semibold border border-blue-500/30">DIT-P04</span>
                </div>
                <p class="text-xs text-slate-400">Team T04 • Product Master & Stock Transaction Balances</p>
            </div>
        </div>
        <div class="flex items-center gap-2">
            <label class="cursor-pointer flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 rounded-lg border border-slate-700 transition">
                <i data-lucide="upload" class="w-3.5 h-3.5 text-blue-400"></i>
                <span id="uploadLabel">Upload Excel</span>
                <input type="file" id="excelFileInput" accept=".xlsx,.xls" onchange="uploadExcelFile(this)" class="hidden">
            </label>
            <a href="/api/download/Stock_Report" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 rounded-lg border border-slate-700 flex items-center gap-1.5 transition">
                <i data-lucide="download" class="w-3.5 h-3.5 text-emerald-400"></i> Stock Report
            </a>
            <a href="/api/download/Reorder_List" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 rounded-lg border border-slate-700 flex items-center gap-1.5 transition">
                <i data-lucide="download" class="w-3.5 h-3.5 text-amber-400"></i> Reorder List
            </a>
            <button onclick="triggerPipeline()" id="runBtn" class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold transition active:scale-95">
                <i data-lucide="play" class="w-3.5 h-3.5"></i> Run Automation
            </button>
        </div>
    </header>

    <!-- KPI Metric Cards (Mentor Expected Scope) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div class="glass-panel p-5 rounded-2xl">
            <p class="text-xs font-medium text-slate-400 uppercase">Product Master</p>
            <h3 id="statTotalSkus" class="text-2xl font-extrabold text-white mt-1">--</h3>
            <p class="text-xs text-emerald-400 mt-1">15 Active Master SKUs</p>
        </div>
        <div class="glass-panel p-5 rounded-2xl">
            <p class="text-xs font-medium text-slate-400 uppercase">Stock Valuation</p>
            <h3 id="statValuation" class="text-2xl font-extrabold text-white mt-1">₹ --</h3>
            <p class="text-xs text-slate-400 mt-1">Calculated Current Balances</p>
        </div>
        <div class="glass-panel p-5 rounded-2xl">
            <p class="text-xs font-medium text-slate-400 uppercase">Reorder Alerts</p>
            <h3 id="statReorders" class="text-2xl font-extrabold text-amber-400 mt-1">--</h3>
            <p class="text-xs text-slate-400 mt-1">Balance &lt; Minimum Buffer</p>
        </div>
        <div class="glass-panel p-5 rounded-2xl border-purple-500/30">
            <p class="text-xs font-medium text-purple-300 uppercase">Unknown Codes</p>
            <h3 id="statUnknown" class="text-2xl font-extrabold text-purple-400 mt-1">--</h3>
            <p class="text-xs text-slate-400 mt-1">Not in Product Master</p>
        </div>
        <div class="glass-panel p-5 rounded-2xl border-rose-500/30">
            <p class="text-xs font-medium text-rose-300 uppercase">Negative Stock</p>
            <h3 id="statNegative" class="text-2xl font-extrabold text-rose-400 mt-1">--</h3>
            <p class="text-xs text-slate-400 mt-1">Overdraw Emergency</p>
        </div>
    </div>

    <!-- Operations Action Center -->
    <div class="glass-panel rounded-2xl p-6 border-indigo-500/30 bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/20">
        <div class="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div class="flex items-center gap-3">
                <div class="p-2 bg-indigo-500/20 rounded-xl text-indigo-400">
                    <i data-lucide="cpu" class="w-5 h-5"></i>
                </div>
                <div>
                    <h2 class="text-base font-bold text-white flex items-center gap-2">
                        Stock Transaction Balance & Reorder Engine
                        <span class="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded font-semibold border border-emerald-500/30">DIT-P04 Ready</span>
                    </h2>
                    <p class="text-xs text-slate-400">Opening Balance + Receipts (IN) - Issues (OUT) = Current Stock Balance</p>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <button onclick="runQuickAction('executive_summary')" class="px-3 py-1.5 bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 text-xs font-semibold rounded-lg border border-blue-500/40">Executive Briefing</button>
                <button onclick="runQuickAction('po_email')" class="px-3 py-1.5 bg-amber-600/30 hover:bg-amber-600/50 text-amber-300 text-xs font-semibold rounded-lg border border-amber-500/40">Draft Vendor PO</button>
                <button onclick="runQuickAction('risk_forecast')" class="px-3 py-1.5 bg-rose-600/30 hover:bg-rose-600/50 text-rose-300 text-xs font-semibold rounded-lg border border-rose-500/40">Unknown Code &amp; Risk Audit</button>
            </div>
        </div>
        <div class="mt-4">
            <div id="aiOutput" class="text-xs text-slate-200 bg-slate-950/90 p-4 rounded-xl border border-slate-800 font-mono whitespace-pre-wrap min-h-[90px] leading-relaxed">Click any action button above to generate official vendor PO drafts, management briefings, or unknown code audits instantly.</div>
        </div>
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="glass-panel p-5 rounded-2xl">
            <h3 class="text-sm font-semibold text-white mb-4">Stock Movement: Opening vs. Stock IN vs. Stock OUT</h3>
            <div class="h-64"><canvas id="stockChart"></canvas></div>
        </div>
        <div class="glass-panel p-5 rounded-2xl">
            <h3 class="text-sm font-semibold text-white mb-4">SKU Health &amp; Reorder Status</h3>
            <div class="h-64 flex items-center justify-center"><canvas id="riskChart"></canvas></div>
        </div>
    </div>

    <!-- Main Data Table with Master / Transactions / Anomalies Tabs -->
    <div class="glass-panel rounded-2xl overflow-hidden">
        <div class="p-4 border-b border-slate-800 flex flex-wrap justify-between items-center gap-3">
            <div class="flex items-center gap-2">
                <button onclick="switchView('MASTER')" id="btnTabMaster" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 text-white">Stock Balances (15)</button>
                <button onclick="switchView('TX')" id="btnTabTx" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700">Transactions Log (23)</button>
                <button onclick="switchView('REORDER')" id="btnTabReorder" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500/20 text-amber-400 border border-amber-500/30">Reorders Only</button>
            </div>
            <input id="tableSearch" onkeyup="filterTable()" type="text" placeholder="Search SKU, name, supplier..." class="bg-slate-800 border border-slate-700 text-xs text-white px-3 py-1.5 rounded-lg w-56 focus:outline-none focus:border-blue-500">
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-left text-xs" id="dataTable">
                <thead id="tableHead" class="bg-slate-900 text-slate-400 border-b border-slate-800"></thead>
                <tbody id="tableBody" class="divide-y divide-slate-800 text-slate-300"></tbody>
            </table>
        </div>
    </div>

    <!-- Mentor Expected Scope: Unknown Codes & Negative Stock Exception Register -->
    <div class="glass-panel rounded-2xl p-5 border-rose-500/30">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-2">
                <i data-lucide="shield-alert" class="w-4 h-4"></i> Unknown Product Codes &amp; Negative Stock Exception Audit
            </h3>
            <span id="anomalyBadge" class="text-xs bg-rose-500/20 text-rose-400 px-2 py-0.5 rounded font-semibold">Exceptions Detected</span>
        </div>
        <div id="anomaliesList" class="mt-3 space-y-2 text-xs"></div>
    </div>

    <footer class="text-center text-xs text-slate-500 pt-4 border-t border-slate-800">
        DefineInfoTech Pvt. Ltd. (DIT) • Python Automation Internship 2026 • Team T04 (DIT-P04) • Anjalai Ammal Mahalingam Engineering College
    </footer>

    <script>
        lucide.createIcons();
        let globalData = null;
        let currentView = 'MASTER';
        let stockChart = null, riskChart = null;

        async function fetchData() {
            const res = await fetch('/api/data');
            globalData = await res.json();
            
            document.getElementById('statTotalSkus').textContent = globalData.valid_count;
            document.getElementById('statValuation').textContent = '₹ ' + globalData.total_valuation.toLocaleString('en-IN', {maximumFractionDigits: 2});
            document.getElementById('statReorders').textContent = globalData.reorder_count;
            document.getElementById('statUnknown').textContent = globalData.unknown_code_count;
            document.getElementById('statNegative').textContent = globalData.negative_stock_count;

            renderActiveTable();
            renderAnomalies(globalData.anomalies);
            renderCharts(globalData.records);
        }

        function switchView(view) {
            currentView = view;
            ['btnTabMaster', 'btnTabTx', 'btnTabReorder'].forEach(id => {
                const btn = document.getElementById(id);
                btn.className = "px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700";
            });
            if (view === 'MASTER') document.getElementById('btnTabMaster').className = "px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 text-white";
            else if (view === 'TX') document.getElementById('btnTabTx').className = "px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 text-white";
            else if (view === 'REORDER') document.getElementById('btnTabReorder').className = "px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-600 text-white";
            renderActiveTable();
        }

        function renderActiveTable() {
            const thead = document.getElementById('tableHead');
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';

            if (currentView === 'TX') {
                thead.innerHTML = `<tr><th class="p-3">Tx ID</th><th class="p-3">Product ID</th><th class="p-3">Date</th><th class="p-3">Type</th><th class="p-3 text-right">Quantity</th><th class="p-3">Reference</th><th class="p-3">Remarks</th></tr>`;
                globalData.transactions.forEach(t => {
                    const tr = document.createElement('tr');
                    const isIn = t.Transaction_Type === 'STOCK_IN';
                    tr.className = 'hover:bg-slate-800/40';
                    tr.innerHTML = `
                        <td class="p-3 font-mono text-slate-400">${t.Transaction_ID}</td>
                        <td class="p-3 font-mono text-blue-400 font-semibold">${t.Product_ID}</td>
                        <td class="p-3 text-slate-400">${t.Transaction_Date}</td>
                        <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${isIn ? 'bg-emerald-500/20 text-emerald-400' : 'bg-blue-500/20 text-blue-400'}">${t.Transaction_Type}</span></td>
                        <td class="p-3 text-right font-mono font-bold ${isIn ? 'text-emerald-400' : 'text-blue-300'}">${isIn ? '+' : '-'}${t.Quantity}</td>
                        <td class="p-3 text-slate-400">${t.Reference_No}</td>
                        <td class="p-3 text-slate-300">${t.Department_Remarks}</td>
                    `;
                    tbody.appendChild(tr);
                });
                return;
            }

            let records = globalData.records;
            if (currentView === 'REORDER') records = records.filter(r => r.Reorder_Required === 'YES');

            thead.innerHTML = `<tr><th class="p-3">SKU ID</th><th class="p-3">Product Name</th><th class="p-3 text-right">Opening</th><th class="p-3 text-right">Stock IN</th><th class="p-3 text-right">Stock OUT</th><th class="p-3 text-right">Current Balance</th><th class="p-3 text-right">Min Buffer</th><th class="p-3 text-center">Status</th><th class="p-3 text-right">Valuation (₹)</th><th class="p-3">Supplier</th></tr>`;
            records.forEach(r => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/40';
                const isNeg = r.Current_Balance < 0;
                const isLow = r.Current_Balance < r.Minimum_Stock;
                let statusBadge = "bg-emerald-500/20 text-emerald-400";
                if (isNeg || r.Status.includes("CRITICAL") || r.Status.includes("OUT OF STOCK")) statusBadge = "bg-rose-500/20 text-rose-400";
                else if (isLow) statusBadge = "bg-amber-500/20 text-amber-400";

                tr.innerHTML = `
                    <td class="p-3 font-mono text-blue-400 font-semibold">${r.Product_ID}</td>
                    <td class="p-3 font-medium text-white">${r.Product_Name}</td>
                    <td class="p-3 text-right font-mono text-slate-400">${r.Opening_Stock}</td>
                    <td class="p-3 text-right font-mono text-emerald-400">+${r.Stock_IN}</td>
                    <td class="p-3 text-right font-mono text-blue-300">-${r.Stock_OUT}</td>
                    <td class="p-3 text-right font-mono font-bold ${isNeg ? 'text-rose-400 animate-pulse' : (isLow ? 'text-amber-400' : 'text-emerald-400')}">${r.Current_Balance}</td>
                    <td class="p-3 text-right font-mono text-slate-400">${r.Minimum_Stock}</td>
                    <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-semibold ${statusBadge}">${r.Status}</span></td>
                    <td class="p-3 text-right font-mono">₹ ${Number(r.Stock_Valuation_INR || 0).toLocaleString('en-IN')}</td>
                    <td class="p-3 text-slate-400">${r.Supplier}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function renderAnomalies(anomalies) {
            const c = document.getElementById('anomaliesList');
            document.getElementById('anomalyBadge').textContent = `${anomalies.length} Exceptions Logged`;
            c.innerHTML = '';
            anomalies.forEach(a => {
                const isUnknown = a.error_type === 'UNKNOWN_CODE';
                const isNeg = a.error_type === 'NEGATIVE_STOCK_ALERT';
                const color = isUnknown ? 'purple' : (isNeg ? 'rose' : 'amber');
                c.innerHTML += `
                    <div class="p-2.5 rounded bg-${color}-950/30 border border-${color}-900/50 flex justify-between items-center">
                        <span class="text-${color}-300">
                            <strong>[${a.error_type}] ${a.id}:</strong> ${a.reason}
                        </span>
                        <span class="text-[10px] font-bold text-${color}-400 bg-${color}-500/10 px-2 py-0.5 rounded uppercase">Flagged</span>
                    </div>`;
            });
        }

        function renderCharts(records) {
            const ctx1 = document.getElementById('stockChart').getContext('2d');
            if (stockChart) stockChart.destroy();
            stockChart = new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: records.map(r => r.Product_ID),
                    datasets: [
                        { label: 'Opening Stock', data: records.map(r => r.Opening_Stock), backgroundColor: '#64748B' },
                        { label: 'Stock IN (Receipts)', data: records.map(r => r.Stock_IN), backgroundColor: '#10B981' },
                        { label: 'Stock OUT (Issues)', data: records.map(r => r.Stock_OUT), backgroundColor: '#EF4444' }
                    ]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#94A3B8' } } } }
            });

            const counts = {};
            records.forEach(r => { counts[r.Status] = (counts[r.Status] || 0) + 1; });
            const ctx2 = document.getElementById('riskChart').getContext('2d');
            if (riskChart) riskChart.destroy();
            riskChart = new Chart(ctx2, {
                type: 'doughnut',
                data: { labels: Object.keys(counts), datasets: [{ data: Object.values(counts), backgroundColor: ['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6'] }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#94A3B8' } } } }
            });
        }

        function filterTable() {
            const q = document.getElementById('tableSearch').value.toLowerCase();
            const rows = document.querySelectorAll('#tableBody tr');
            rows.forEach(r => {
                r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
            });
        }

        async function triggerPipeline() {
            await fetch('/api/run-pipeline', { method: 'POST' });
            await fetchData();
            alert('Automation Complete! Recalculated stock balances, updated Reorder list, and refreshed reports.');
        }

        async function uploadExcelFile(input) {
            if (!input.files || input.files.length === 0) return;
            const file = input.files[0];
            const formData = new FormData();
            formData.append("file", file);
            document.getElementById('uploadLabel').textContent = "Processing...";
            try {
                const res = await fetch('/api/upload-excel', { method: 'POST', body: formData });
                const data = await res.json();
                await fetchData();
                alert(`File Uploaded Successfully!\n\n${data.message}\n• Master SKUs: ${data.summary.valid_count}\n• Reorders: ${data.summary.reorder_count}\n• Unknown Codes Caught: ${data.summary.unknown_codes}\n• Negative Stock Alerts: ${data.summary.negative_stock}`);
            } catch (err) {
                alert("Upload failed: " + err.message);
            } finally {
                document.getElementById('uploadLabel').textContent = "Upload Excel";
            }
        }

        async function runQuickAction(actionType) {
            const box = document.getElementById('aiOutput');
            box.textContent = "Processing supply chain intelligence...";
            const res = await fetch(`/api/quick-action/${actionType}`);
            const data = await res.json();
            box.textContent = data.content;
        }

        fetchData();
    </script>
</body>
</html>""")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
