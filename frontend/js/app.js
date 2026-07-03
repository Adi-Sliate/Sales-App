// ============================================
// API Configuration
// ============================================

// BACKEND URL with /api prefix
const API_BASE_URL = 'https://salesapp-bsc7be9t.b4a.run/api';

// ================= LOADERS =================

async function loadSalesSummary() {
    try {
        const filters = getFilters();

        if (!filters.date_from || !filters.date_to) {
            alert("Please select From Date and To Date.");
            return;
        }

        const query = buildQuery({
            date_from: filters.date_from,
            date_to: filters.date_to,
            trans_type: filters.trans_type,
            created_user: filters.created_user,
            terminal_id: filters.terminal_id
        });

        // ✅ CORRECT: /reports/sales-summary
        const response = await fetch(`${API_BASE_URL}/reports/sales-summary?${query}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const result = await response.json();

        currentData = result.data || [];
        currentPage = 1;
        currentReportType = "sales";

        setSummary(
            result.count || 0,
            result.total_net || 0,
            result.total_discount || 0,
            "Total Net",
            "Total Discount"
        );

        renderCurrentPage();
    } catch (error) {
        console.error("Error loading sales summary:", error);
        alert("Failed to load sales summary.");
    }
}

async function loadItemSummary() {
    try {
        const filters = getFilters();

        if (!filters.date_from || !filters.date_to) {
            alert("Please select From Date and To Date.");
            return;
        }

        const query = buildQuery({
            date_from: filters.date_from,
            date_to: filters.date_to,
            item_code: filters.item_code,
            item_name: filters.item_name,
            trans_type: filters.trans_type,
            created_user: filters.created_user
        });

        // ✅ CORRECT: /reports/item-summary
        const response = await fetch(`${API_BASE_URL}/reports/item-summary?${query}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const result = await response.json();

        currentData = result.data || [];
        currentPage = 1;
        currentReportType = "item";

        setSummary(
            result.count || 0,
            result.total_amount || 0,
            result.total_qty || 0,
            "Total Amount",
            "Total Qty"
        );

        renderCurrentPage();
    } catch (error) {
        console.error("Error loading item summary:", error);
        alert("Failed to load item summary.");
    }
}

async function loadQuantityReport() {
    try {
        const filters = getFilters();

        if (!filters.date_from || !filters.date_to) {
            alert("Please select From Date and To Date.");
            return;
        }

        const query = buildQuery({
            date_from: filters.date_from,
            date_to: filters.date_to,
            item_code: filters.item_code,
            item_name: filters.item_name,
            trans_type: filters.trans_type,
            created_user: filters.created_user
        });

        // ✅ CORRECT: /reports/quantity-report
        const response = await fetch(`${API_BASE_URL}/reports/quantity-report?${query}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const result = await response.json();

        currentData = result.data || [];
        currentPage = 1;
        currentReportType = "quantity";

        setSummary(
            result.count || 0,
            result.total_amount || 0,
            result.total_qty || 0,
            "Total Amount",
            "Total Qty"
        );

        renderCurrentPage();
    } catch (error) {
        console.error("Error loading quantity report:", error);
        alert("Failed to load quantity report.");
    }
}

async function loadBillReport() {
    try {
        const filters = getFilters();

        if (!filters.date_from || !filters.date_to) {
            alert("Please select From Date and To Date.");
            return;
        }

        const query = buildQuery({
            date_from: filters.date_from,
            date_to: filters.date_to,
            trans_type: filters.trans_type,
            created_user: filters.created_user,
            terminal_id: filters.terminal_id,
            bill_no: filters.bill_no
        });

        // ✅ CORRECT: /reports/bill-report
        const response = await fetch(`${API_BASE_URL}/reports/bill-report?${query}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const result = await response.json();

        currentData = result.data || [];
        currentPage = 1;
        currentReportType = "bill";

        setSummary(
            result.count || 0,
            result.total_net || 0,
            result.total_discount || 0,
            "Total Net",
            "Total Discount"
        );

        renderCurrentPage();
    } catch (error) {
        console.error("Error loading bill report:", error);
        alert("Failed to load bill report.");
    }
}

async function loadGpReport() {
    try {
        const filters = getFilters();

        if (!filters.date_from || !filters.date_to) {
            alert("Please select From Date and To Date.");
            return;
        }

        const query = buildQuery({
            date_from: filters.date_from,
            date_to: filters.date_to,
            item_code: filters.item_code,
            item_name: filters.item_name,
            trans_type: filters.trans_type,
            created_user: filters.created_user
        });

        // ✅ CORRECT: /reports/gp-report
        const response = await fetch(`${API_BASE_URL}/reports/gp-report?${query}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const result = await response.json();

        currentData = result.data || [];
        currentPage = 1;
        currentReportType = "gp";

        setSummary(
            result.count || 0,
            result.total_gp || 0,
            result.total_cost || 0,
            "Total GP",
            "Total Cost"
        );

        renderCurrentPage();
    } catch (error) {
        console.error("Error loading GP report:", error);
        alert("Failed to load GP report.");
    }
}

async function loadStockReport() {
    try {
        const filters = getFilters();

        const query = buildQuery({
            item_code: filters.item_code,
            item_name: filters.item_name
        });

        // ✅ CORRECT: /reports/stock-report
        const response = await fetch(`${API_BASE_URL}/reports/stock-report?${query}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const result = await response.json();

        currentData = result.data || [];
        currentPage = 1;
        currentReportType = "stock";

        setSummary(
            result.count || 0,
            result.total_value || 0,
            result.total_units || 0,
            "Total Value",
            "Total Units"
        );

        renderCurrentPage();
    } catch (error) {
        console.error("Error loading stock report:", error);
        alert("Failed to load stock report.");
    }
}

async function loadExpensesReport() {
    try {
        const filters = getFilters();

        if (!filters.date_from || !filters.date_to) {
            alert("Please select From Date and To Date.");
            return;
        }

        const query = buildQuery({
            date_from: filters.date_from,
            date_to: filters.date_to,
            name: filters.account_name,
            detail: filters.detail,
            user: filters.created_user,
            comments: filters.comments
        });

        // ✅ CORRECT: /reports/expenses-report
        const response = await fetch(`${API_BASE_URL}/reports/expenses-report?${query}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const result = await response.json();

        currentData = result.data || [];
        currentPage = 1;
        currentReportType = "expenses";

        setSummary(
            result.count || 0,
            result.total_amount || 0,
            0,
            "Total Amount",
            "Extra Total"
        );

        renderCurrentPage();
    } catch (error) {
        console.error("Error loading expenses report:", error);
        alert("Failed to load expenses report.");
    }
}
