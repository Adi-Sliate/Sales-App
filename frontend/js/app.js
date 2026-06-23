const API_BASE = "http://127.0.0.1:8000/reports";

let currentData = [];
let currentPage = 1;
let pageSize = 25;
let currentReportType = "";

// ================= FORMATTERS =================
function formatMoney(value) {
    const num = Number(value || 0);
    return num.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatQty(value) {
    return Number(value || 0).toLocaleString(undefined, {
        minimumFractionDigits: 3,
        maximumFractionDigits: 3
    });
}

function formatUnits(value) {
    return Number(value || 0).toLocaleString(undefined, {
        minimumFractionDigits: 3,
        maximumFractionDigits: 3
    });
}

// ================= FILTERS =================
function getFilters() {
    return {
        date_from: document.getElementById("dateFrom")?.value || "",
        date_to: document.getElementById("dateTo")?.value || "",
        trans_type: document.getElementById("transType")?.value.trim() || "",
        created_user: document.getElementById("createdUser")?.value.trim() || "",
        terminal_id: document.getElementById("terminalId")?.value.trim() || "",
        item_code: document.getElementById("itemCode")?.value.trim() || "",
        item_name: document.getElementById("itemName")?.value.trim() || "",
        bill_no: document.getElementById("billNo")?.value.trim() || "",
        account_name: document.getElementById("accountName")?.value.trim() || "",
        detail: document.getElementById("detail")?.value.trim() || "",
        comments: document.getElementById("comments")?.value.trim() || ""
    };
}

function buildQuery(params) {
    const urlParams = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== "") {
            urlParams.append(key, value);
        }
    });

    return urlParams.toString();
}

// ================= SUMMARY =================
function setSummary(count, amount, extra, amountLabel = "Total Amount", extraLabel = "Extra Total") {
    const countEl = document.getElementById("cardCount");
    const amountEl = document.getElementById("cardAmount");
    const extraEl = document.getElementById("cardExtra");
    const amountLabelEl = document.getElementById("cardAmountLabel");
    const extraLabelEl = document.getElementById("cardExtraLabel");

    if (countEl) countEl.textContent = count || 0;
    if (amountEl) amountEl.textContent = formatMoney(amount || 0);
    if (extraEl) extraEl.textContent = formatMoney(extra || 0);
    if (amountLabelEl) amountLabelEl.textContent = amountLabel;
    if (extraLabelEl) extraLabelEl.textContent = extraLabel;
}

// ================= PAGINATION =================
function getPaginatedData() {
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return currentData.slice(startIndex, endIndex);
}

function updatePageInfo() {
    const pageInfo = document.getElementById("pageInfo");
    const currentPageText = document.getElementById("currentPageText");

    if (!pageInfo || !currentPageText) return;

    const totalRecords = currentData.length;

    if (totalRecords === 0) {
        pageInfo.textContent = "Showing 0 to 0 of 0 entries";
        currentPageText.textContent = "Page 0 of 0";
        return;
    }

    const startEntry = (currentPage - 1) * pageSize + 1;
    const endEntry = Math.min(currentPage * pageSize, totalRecords);
    const totalPages = Math.ceil(totalRecords / pageSize);

    pageInfo.textContent = `Showing ${startEntry} to ${endEntry} of ${totalRecords} entries`;
    currentPageText.textContent = `Page ${currentPage} of ${totalPages}`;
}

function renderPagination() {
    const pagination = document.getElementById("pagination");
    if (!pagination) return;

    pagination.innerHTML = "";

    const totalPages = Math.ceil(currentData.length / pageSize);

    if (totalPages <= 1) {
        updatePageInfo();
        return;
    }

    const prevLi = document.createElement("li");
    prevLi.className = `page-item ${currentPage === 1 ? "disabled" : ""}`;
    prevLi.innerHTML = `<a class="page-link" href="javascript:void(0)">Previous</a>`;
    prevLi.addEventListener("click", () => {
        if (currentPage > 1) {
            currentPage--;
            renderCurrentPage();
        }
    });
    pagination.appendChild(prevLi);

    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);

    if (currentPage <= 3) {
        endPage = Math.min(5, totalPages);
    }

    if (currentPage > totalPages - 3) {
        startPage = Math.max(1, totalPages - 4);
    }

    for (let i = startPage; i <= endPage; i++) {
        const li = document.createElement("li");
        li.className = `page-item ${i === currentPage ? "active" : ""}`;
        li.innerHTML = `<a class="page-link" href="javascript:void(0)">${i}</a>`;
        li.addEventListener("click", () => {
            currentPage = i;
            renderCurrentPage();
        });
        pagination.appendChild(li);
    }

    const nextLi = document.createElement("li");
    nextLi.className = `page-item ${currentPage === totalPages ? "disabled" : ""}`;
    nextLi.innerHTML = `<a class="page-link" href="javascript:void(0)">Next</a>`;
    nextLi.addEventListener("click", () => {
        if (currentPage < totalPages) {
            currentPage++;
            renderCurrentPage();
        }
    });
    pagination.appendChild(nextLi);

    updatePageInfo();
}

// ================= EMPTY =================
function renderEmptyTable(message = "No data found.") {
    const reportHead = document.getElementById("reportHead");
    const reportBody = document.getElementById("reportBody");

    if (!reportHead || !reportBody) return;

    reportHead.innerHTML = `
        <tr>
            <th>Message</th>
        </tr>
    `;

    reportBody.innerHTML = `
        <tr class="empty-row">
            <td>${message}</td>
        </tr>
    `;
}

// ================= SALES TABLE =================
function renderSalesTable(rows) {
    if (!rows || rows.length === 0) {
        renderEmptyTable("No sales summary data found.");
        return;
    }

    document.getElementById("reportHead").innerHTML = `
        <tr>
            <th>Trans No</th>
            <th>Date</th>
            <th>Type</th>
            <th>Customer</th>
            <th>User</th>
            <th>Terminal</th>
            <th>Net Total</th>
            <th>Discount</th>
            <th>Cash</th>
            <th>Cheque</th>
            <th>Credit</th>
            <th>Cancel</th>
        </tr>
    `;

    document.getElementById("reportBody").innerHTML = rows.map(row => `
        <tr>
            <td>${row.trans_no ?? ""}</td>
            <td>${row.trans_date ? new Date(row.trans_date).toLocaleString() : ""}</td>
            <td>${row.trans_type ?? ""}</td>
            <td>${row.billing_name ?? ""}</td>
            <td>${row.created_user ?? ""}</td>
            <td>${row.terminal_id ?? ""}</td>
            <td class="text-end">${formatMoney(row.net_total)}</td>
            <td class="text-end">${formatMoney(row.discount_amt)}</td>
            <td class="text-end">${formatMoney(row.cash_amt)}</td>
            <td class="text-end">${formatMoney(row.chq_amt)}</td>
            <td class="text-end">${formatMoney(row.credit_amt)}</td>
            <td>${row.cancel_status ?? ""}</td>
        </tr>
    `).join("");
}

// ================= ITEM TABLE =================
function renderItemTable(rows) {
    if (!rows || rows.length === 0) {
        renderEmptyTable("No item summary data found.");
        return;
    }

    document.getElementById("reportHead").innerHTML = `
        <tr>
            <th>Item Code</th>
            <th>Item Name</th>
            <th>Total Qty</th>
            <th>Free Qty</th>
            <th>Total Discount</th>
            <th>Total Amount</th>
        </tr>
    `;

    document.getElementById("reportBody").innerHTML = rows.map(row => `
        <tr>
            <td>${row.item_code ?? ""}</td>
            <td>${row.item_name ?? ""}</td>
            <td class="text-end">${formatQty(row.total_qty)}</td>
            <td class="text-end">${formatQty(row.total_free_qty)}</td>
            <td class="text-end">${formatMoney(row.total_discount)}</td>
            <td class="text-end">${formatMoney(row.total_amount)}</td>
        </tr>
    `).join("");
}

// ================= QUANTITY TABLE =================
function renderQuantityTable(rows) {
    if (!rows || rows.length === 0) {
        renderEmptyTable("No quantity report data found.");
        return;
    }

    document.getElementById("reportHead").innerHTML = `
        <tr>
            <th>Trans No</th>
            <th>Date</th>
            <th>Type</th>
            <th>User</th>
            <th>Item Code</th>
            <th>Item Name</th>
            <th>Qty</th>
            <th>Free Qty</th>
            <th>Rate</th>
            <th>Amount</th>
            <th>Discount</th>
        </tr>
    `;

    document.getElementById("reportBody").innerHTML = rows.map(row => `
        <tr>
            <td>${row.trans_no ?? ""}</td>
            <td>${row.trans_date ? new Date(row.trans_date).toLocaleString() : ""}</td>
            <td>${row.trans_type ?? ""}</td>
            <td>${row.created_user ?? ""}</td>
            <td>${row.item_code ?? ""}</td>
            <td>${row.item_name ?? ""}</td>
            <td class="text-end">${formatQty(row.qty)}</td>
            <td class="text-end">${formatQty(row.free_qty)}</td>
            <td class="text-end">${formatMoney(row.rate)}</td>
            <td class="text-end">${formatMoney(row.amount)}</td>
            <td class="text-end">${formatMoney(row.discount_amt)}</td>
        </tr>
    `).join("");
}

// ================= BILL TABLE =================
function renderBillTable(rows) {
    if (!rows || rows.length === 0) {
        renderEmptyTable("No bill report data found.");
        return;
    }

    document.getElementById("reportHead").innerHTML = `
        <tr>
            <th>Bill No</th>
            <th>Date</th>
            <th>Type</th>
            <th>Customer</th>
            <th>User</th>
            <th>Terminal</th>
            <th>Net Total</th>
            <th>Discount</th>
            <th>Cash</th>
            <th>Cheque</th>
            <th>Credit</th>
            <th>Cancel</th>
            <th>Comments</th>
        </tr>
    `;

    document.getElementById("reportBody").innerHTML = rows.map(row => `
        <tr>
            <td>${row.trans_no ?? ""}</td>
            <td>${row.trans_date ? new Date(row.trans_date).toLocaleString() : ""}</td>
            <td>${row.trans_type ?? ""}</td>
            <td>${row.billing_name ?? ""}</td>
            <td>${row.created_user ?? ""}</td>
            <td>${row.terminal_id ?? ""}</td>
            <td class="text-end">${formatMoney(row.net_total)}</td>
            <td class="text-end">${formatMoney(row.discount_amt)}</td>
            <td class="text-end">${formatMoney(row.cash_amt)}</td>
            <td class="text-end">${formatMoney(row.chq_amt)}</td>
            <td class="text-end">${formatMoney(row.credit_amt)}</td>
            <td>${row.cancel_status ?? ""}</td>
            <td>${row.comments ?? ""}</td>
        </tr>
    `).join("");
}

// ================= GP TABLE =================
function renderGpTable(rows) {
    if (!rows || rows.length === 0) {
        renderEmptyTable("No GP report data found.");
        return;
    }

    document.getElementById("reportHead").innerHTML = `
        <tr>
            <th>Item Code</th>
            <th>Item Name</th>
            <th>Total Qty</th>
            <th>Total Amount</th>
            <th>Total Cost</th>
            <th>Gross Profit</th>
            <th>GP %</th>
        </tr>
    `;

    document.getElementById("reportBody").innerHTML = rows.map(row => `
        <tr>
            <td>${row.item_code ?? ""}</td>
            <td>${row.item_name ?? ""}</td>
            <td class="text-end">${formatQty(row.total_qty)}</td>
            <td class="text-end">${formatMoney(row.total_amount)}</td>
            <td class="text-end">${formatMoney(row.total_cost)}</td>
            <td class="text-end">${formatMoney(row.gross_profit)}</td>
            <td class="text-end">${Number(row.gp_percent || 0).toFixed(2)}%</td>
        </tr>
    `).join("");
}

// ================= STOCK TABLE =================
function renderStockTable(rows) {
    if (!rows || rows.length === 0) {
        renderEmptyTable("No stock report data found.");
        return;
    }

    document.getElementById("reportHead").innerHTML = `
        <tr>
            <th>Code</th>
            <th>Name</th>
            <th>Units</th>
            <th>Rate</th>
            <th>Value</th>
        </tr>
    `;

    document.getElementById("reportBody").innerHTML = rows.map(row => `
        <tr>
            <td>${row.item_code ?? ""}</td>
            <td>${row.item_name ?? ""}</td>
            <td class="text-end">${formatUnits(row.units)}</td>
            <td class="text-end">${formatMoney(row.rate)}</td>
            <td class="text-end">${formatMoney(row.value)}</td>
        </tr>
    `).join("");
}

// ================= EXPENSES TABLE =================
function renderExpensesTable(rows) {
    if (!rows || rows.length === 0) {
        renderEmptyTable("No expenses report data found.");
        return;
    }

    document.getElementById("reportHead").innerHTML = `
        <tr>
            <th>Account Name</th>
            <th>Details</th>
            <th>User</th>
            <th>Comments</th>
            <th>Amount</th>
        </tr>
    `;

    document.getElementById("reportBody").innerHTML = rows.map(row => `
        <tr>
            <td>${row.name ?? ""}</td>
            <td>${row.details ?? ""}</td>
            <td>${row.user ?? ""}</td>
            <td>${row.comments ?? ""}</td>
            <td class="text-end">${formatMoney(row.amount)}</td>
        </tr>
    `).join("");
}

// ================= CURRENT PAGE RENDER =================
function renderCurrentPage() {
    const pageRows = getPaginatedData();
    const badge = document.getElementById("reportTypeBadge");

    if (currentReportType === "sales") {
        renderSalesTable(pageRows);
        if (badge) badge.textContent = "Sales Summary";
    } else if (currentReportType === "item") {
        renderItemTable(pageRows);
        if (badge) badge.textContent = "Item Summary";
    } else if (currentReportType === "quantity") {
        renderQuantityTable(pageRows);
        if (badge) badge.textContent = "Quantity Report";
    } else if (currentReportType === "bill") {
        renderBillTable(pageRows);
        if (badge) badge.textContent = "Bill Report";
    } else if (currentReportType === "gp") {
        renderGpTable(pageRows);
        if (badge) badge.textContent = "GP Report";
    } else if (currentReportType === "stock") {
        renderStockTable(pageRows);
        if (badge) badge.textContent = "Stock Report";
    } else if (currentReportType === "expenses") {
        renderExpensesTable(pageRows);
        if (badge) badge.textContent = "Expenses Report";
    } else {
        renderEmptyTable("No report loaded.");
    }

    renderPagination();
}

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

        const response = await fetch(`${API_BASE}/sales-summary?${query}`);
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

        const response = await fetch(`${API_BASE}/item-summary?${query}`);
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

        const response = await fetch(`${API_BASE}/quantity-report?${query}`);
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

        const response = await fetch(`${API_BASE}/bill-report?${query}`);
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

        const response = await fetch(`${API_BASE}/gp-report?${query}`);
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

        const response = await fetch(`${API_BASE}/stock-report?${query}`);
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

        const response = await fetch(`${API_BASE}/expenses-report?${query}`);
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

// ================= EVENT BINDING =================
document.querySelectorAll(".load-sales-btn").forEach(btn => {
    btn.addEventListener("click", loadSalesSummary);
});

document.querySelectorAll(".load-item-btn").forEach(btn => {
    btn.addEventListener("click", loadItemSummary);
});

document.querySelectorAll(".load-qty-btn").forEach(btn => {
    btn.addEventListener("click", loadQuantityReport);
});

document.querySelectorAll(".load-bill-btn").forEach(btn => {
    btn.addEventListener("click", loadBillReport);
});

document.querySelectorAll(".load-gp-btn").forEach(btn => {
    btn.addEventListener("click", loadGpReport);
});

document.querySelectorAll(".load-stock-btn").forEach(btn => {
    btn.addEventListener("click", loadStockReport);
});

document.querySelectorAll(".load-expenses-btn").forEach(btn => {
    btn.addEventListener("click", loadExpensesReport);
});

document.querySelectorAll(".print-report-btn").forEach(btn => {
    btn.addEventListener("click", printCurrentReport);
});

// ================= PAGE SIZE =================
const pageSizeEl = document.getElementById("pageSize");
if (pageSizeEl) {
    pageSizeEl.addEventListener("change", function () {
        pageSize = Number(this.value);
        currentPage = 1;
        renderCurrentPage();
    });
}

//  =================== PRINT SECTION ===========
function formatPrintDate(dateValue) {
    if (!dateValue) return "";
    const d = new Date(dateValue);
    if (isNaN(d.getTime())) return dateValue;
    return d.toLocaleDateString();
}

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getReportDisplayName() {
    switch (currentReportType) {
        case "sales": return "SALES SUMMARY REPORT";
        case "item": return "ITEM SUMMARY REPORT";
        case "quantity": return "QUANTITY REPORT";
        case "bill": return "BILL REPORT";
        case "gp": return "GP REPORT";
        case "stock": return "STOCK REPORT";
        case "expenses": return "EXPENSES REPORT";
        default: return "REPORT";
    }
}

function getPrintFiltersText() {
    const filters = getFilters();
    const parts = [];

    if (filters.trans_type) parts.push(`Trans Type: ${filters.trans_type}`);
    if (filters.created_user) parts.push(`User: ${filters.created_user}`);
    if (filters.terminal_id) parts.push(`Terminal: ${filters.terminal_id}`);
    if (filters.item_code) parts.push(`Item Code: ${filters.item_code}`);
    if (filters.item_name) parts.push(`Item Name: ${filters.item_name}`);
    if (filters.bill_no) parts.push(`Bill No: ${filters.bill_no}`);

    return parts.join(" | ");
}

function buildPrintTable(rows) {
    const printHead = document.getElementById("printHead");
    const printBody = document.getElementById("printBody");
    const printFoot = document.getElementById("printFoot");

    if (!printHead || !printBody || !printFoot) return;

    printHead.innerHTML = "";
    printBody.innerHTML = "";
    printFoot.innerHTML = "";

    if (!rows || rows.length === 0) {
        printHead.innerHTML = `<tr><th>Message</th></tr>`;
        printBody.innerHTML = `<tr><td>No data found.</td></tr>`;
        return;
    }

    if (currentReportType === "sales") {
        printHead.innerHTML = `
            <tr>
                <th>Trans No</th>
                <th>Date</th>
                <th>Type</th>
                <th>Customer</th>
                <th>User</th>
                <th>Terminal</th>
                <th class="text-end">Net Total</th>
                <th class="text-end">Discount</th>
                <th class="text-end">Cash</th>
                <th class="text-end">Cheque</th>
                <th class="text-end">Credit</th>
                <th>Cancel</th>
            </tr>
        `;

        printBody.innerHTML = rows.map(row => `
            <tr>
                <td>${escapeHtml(row.trans_no ?? "")}</td>
                <td>${escapeHtml(row.trans_date ? new Date(row.trans_date).toLocaleString() : "")}</td>
                <td>${escapeHtml(row.trans_type ?? "")}</td>
                <td>${escapeHtml(row.billing_name ?? "")}</td>
                <td>${escapeHtml(row.created_user ?? "")}</td>
                <td>${escapeHtml(row.terminal_id ?? "")}</td>
                <td class="text-end">${formatMoney(row.net_total)}</td>
                <td class="text-end">${formatMoney(row.discount_amt)}</td>
                <td class="text-end">${formatMoney(row.cash_amt)}</td>
                <td class="text-end">${formatMoney(row.chq_amt)}</td>
                <td class="text-end">${formatMoney(row.credit_amt)}</td>
                <td>${escapeHtml(row.cancel_status ?? "")}</td>
            </tr>
        `).join("");
    }

    else if (currentReportType === "item") {
        printHead.innerHTML = `
            <tr>
                <th>Item Code</th>
                <th>Item Name</th>
                <th class="text-end">Total Qty</th>
                <th class="text-end">Free Qty</th>
                <th class="text-end">Total Discount</th>
                <th class="text-end">Total Amount</th>
            </tr>
        `;

        printBody.innerHTML = rows.map(row => `
            <tr>
                <td>${escapeHtml(row.item_code ?? "")}</td>
                <td>${escapeHtml(row.item_name ?? "")}</td>
                <td class="text-end">${formatQty(row.total_qty)}</td>
                <td class="text-end">${formatQty(row.total_free_qty)}</td>
                <td class="text-end">${formatMoney(row.total_discount)}</td>
                <td class="text-end">${formatMoney(row.total_amount)}</td>
            </tr>
        `).join("");
    }

    else if (currentReportType === "quantity") {
        printHead.innerHTML = `
            <tr>
                <th>Trans No</th>
                <th>Date</th>
                <th>Type</th>
                <th>User</th>
                <th>Item Code</th>
                <th>Item Name</th>
                <th class="text-end">Qty</th>
                <th class="text-end">Free Qty</th>
                <th class="text-end">Rate</th>
                <th class="text-end">Amount</th>
                <th class="text-end">Discount</th>
            </tr>
        `;

        printBody.innerHTML = rows.map(row => `
            <tr>
                <td>${escapeHtml(row.trans_no ?? "")}</td>
                <td>${escapeHtml(row.trans_date ? new Date(row.trans_date).toLocaleString() : "")}</td>
                <td>${escapeHtml(row.trans_type ?? "")}</td>
                <td>${escapeHtml(row.created_user ?? "")}</td>
                <td>${escapeHtml(row.item_code ?? "")}</td>
                <td>${escapeHtml(row.item_name ?? "")}</td>
                <td class="text-end">${formatQty(row.qty)}</td>
                <td class="text-end">${formatQty(row.free_qty)}</td>
                <td class="text-end">${formatMoney(row.rate)}</td>
                <td class="text-end">${formatMoney(row.amount)}</td>
                <td class="text-end">${formatMoney(row.discount_amt)}</td>
            </tr>
        `).join("");
    }

    else if (currentReportType === "bill") {
        printHead.innerHTML = `
            <tr>
                <th>Bill No</th>
                <th>Date</th>
                <th>Type</th>
                <th>Customer</th>
                <th>User</th>
                <th>Terminal</th>
                <th class="text-end">Net Total</th>
                <th class="text-end">Discount</th>
                <th class="text-end">Cash</th>
                <th class="text-end">Cheque</th>
                <th class="text-end">Credit</th>
                <th>Cancel</th>
                <th>Comments</th>
            </tr>
        `;

        printBody.innerHTML = rows.map(row => `
            <tr>
                <td>${escapeHtml(row.trans_no ?? "")}</td>
                <td>${escapeHtml(row.trans_date ? new Date(row.trans_date).toLocaleString() : "")}</td>
                <td>${escapeHtml(row.trans_type ?? "")}</td>
                <td>${escapeHtml(row.billing_name ?? "")}</td>
                <td>${escapeHtml(row.created_user ?? "")}</td>
                <td>${escapeHtml(row.terminal_id ?? "")}</td>
                <td class="text-end">${formatMoney(row.net_total)}</td>
                <td class="text-end">${formatMoney(row.discount_amt)}</td>
                <td class="text-end">${formatMoney(row.cash_amt)}</td>
                <td class="text-end">${formatMoney(row.chq_amt)}</td>
                <td class="text-end">${formatMoney(row.credit_amt)}</td>
                <td>${escapeHtml(row.cancel_status ?? "")}</td>
                <td>${escapeHtml(row.comments ?? "")}</td>
            </tr>
        `).join("");
    }

    else if (currentReportType === "gp") {
        printHead.innerHTML = `
            <tr>
                <th>Item Code</th>
                <th>Item Name</th>
                <th class="text-end">Total Qty</th>
                <th class="text-end">Total Amount</th>
                <th class="text-end">Total Cost</th>
                <th class="text-end">Gross Profit</th>
                <th class="text-end">GP %</th>
            </tr>
        `;

        printBody.innerHTML = rows.map(row => `
            <tr>
                <td>${escapeHtml(row.item_code ?? "")}</td>
                <td>${escapeHtml(row.item_name ?? "")}</td>
                <td class="text-end">${formatQty(row.total_qty)}</td>
                <td class="text-end">${formatMoney(row.total_amount)}</td>
                <td class="text-end">${formatMoney(row.total_cost)}</td>
                <td class="text-end">${formatMoney(row.gross_profit)}</td>
                <td class="text-end">${Number(row.gp_percent || 0).toFixed(2)}%</td>
            </tr>
        `).join("");
    }

    else if (currentReportType === "stock") {
        printHead.innerHTML = `
            <tr>
                <th>Code</th>
                <th>Name</th>
                <th class="text-end">Units</th>
                <th class="text-end">Rate</th>
                <th class="text-end">Value</th>
            </tr>
        `;

        printBody.innerHTML = rows.map(row => `
            <tr>
                <td>${escapeHtml(row.item_code ?? "")}</td>
                <td>${escapeHtml(row.item_name ?? "")}</td>
                <td class="text-end">${formatUnits(row.units)}</td>
                <td class="text-end">${formatMoney(row.rate)}</td>
                <td class="text-end">${formatMoney(row.value)}</td>
            </tr>
        `).join("");
    }

    else if (currentReportType === "expenses") {
        printHead.innerHTML = `
            <tr>
                <th>Account Name</th>
                <th>Details</th>
                <th>User</th>
                <th>Comments</th>
                <th class="text-end">Amount</th>
            </tr>
        `;

        printBody.innerHTML = rows.map(row => `
            <tr>
                <td>${escapeHtml(row.name ?? "")}</td>
                <td>${escapeHtml(row.details ?? "")}</td>
                <td>${escapeHtml(row.user ?? "")}</td>
                <td>${escapeHtml(row.comments ?? "")}</td>
                <td class="text-end">${formatMoney(row.amount)}</td>
            </tr>
        `).join("");
    }
}

function buildPrintSummary() {
    const summaryEl = document.getElementById("printSummary");
    const count = document.getElementById("cardCount")?.textContent || "0";
    const amountLabel = document.getElementById("cardAmountLabel")?.textContent || "Total Amount";
    const amount = document.getElementById("cardAmount")?.textContent || "0.00";
    const extraLabel = document.getElementById("cardExtraLabel")?.textContent || "Extra Total";
    const extra = document.getElementById("cardExtra")?.textContent || "0.00";

    if (!summaryEl) return;

    summaryEl.innerHTML = `
        <div>Record Count: ${escapeHtml(count)}</div>
        <div>${escapeHtml(amountLabel)}: ${escapeHtml(amount)}</div>
        <div>${escapeHtml(extraLabel)}: ${escapeHtml(extra)}</div>
    `;
}

function formatPrintDateTime(value) {
    const d = value ? new Date(value) : new Date();
    if (isNaN(d.getTime())) return "";
    return d.toLocaleString();
}

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getReportDisplayName() {
    switch (currentReportType) {
        case "sales": return "SALES SUMMARY REPORT";
        case "item": return "ITEM SUMMARY REPORT";
        case "quantity": return "QUANTITY REPORT";
        case "bill": return "BILL REPORT";
        case "gp": return "GP REPORT";
        case "stock": return "STOCK REPORT";
        case "expenses": return "EXPENSES REPORT";
        default: return "REPORT";
    }
}

function getPrintFiltersText() {
    const filters = getFilters();
    const parts = [];

    if (filters.date_from || filters.date_to) {
        parts.push(`From : ${filters.date_from || "-"} To : ${filters.date_to || "-"}`);
    }
    if (filters.trans_type) parts.push(`Trans Type : ${filters.trans_type}`);
    if (filters.created_user) parts.push(`User : ${filters.created_user}`);
    if (filters.terminal_id) parts.push(`Terminal : ${filters.terminal_id}`);
    if (filters.item_code) parts.push(`Item Code : ${filters.item_code}`);
    if (filters.item_name) parts.push(`Item Name : ${filters.item_name}`);
    if (filters.bill_no) parts.push(`Bill No : ${filters.bill_no}`);

    return parts;
}

function buildPrintTableHTML(rows) {
    if (!rows || rows.length === 0) {
        return `
            <table class="report-table">
                <thead><tr><th>Message</th></tr></thead>
                <tbody><tr><td>No data found.</td></tr></tbody>
            </table>
        `;
    }

    if (currentReportType === "sales") {
        return `
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Trans No</th>
                        <th>Date</th>
                        <th>Type</th>
                        <th>Customer</th>
                        <th>User</th>
                        <th>Terminal</th>
                        <th class="text-end">Net Total</th>
                        <th class="text-end">Discount</th>
                        <th class="text-end">Cash</th>
                        <th class="text-end">Cheque</th>
                        <th class="text-end">Credit</th>
                        <th>Cancel</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows.map(row => `
                        <tr>
                            <td>${escapeHtml(row.trans_no)}</td>
                            <td>${escapeHtml(row.trans_date ? new Date(row.trans_date).toLocaleString() : "")}</td>
                            <td>${escapeHtml(row.trans_type)}</td>
                            <td>${escapeHtml(row.billing_name)}</td>
                            <td>${escapeHtml(row.created_user)}</td>
                            <td>${escapeHtml(row.terminal_id)}</td>
                            <td class="text-end">${formatMoney(row.net_total)}</td>
                            <td class="text-end">${formatMoney(row.discount_amt)}</td>
                            <td class="text-end">${formatMoney(row.cash_amt)}</td>
                            <td class="text-end">${formatMoney(row.chq_amt)}</td>
                            <td class="text-end">${formatMoney(row.credit_amt)}</td>
                            <td>${escapeHtml(row.cancel_status)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    }

    if (currentReportType === "item") {
        return `
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Item Code</th>
                        <th>Item Name</th>
                        <th class="text-end">Total Qty</th>
                        <th class="text-end">Free Qty</th>
                        <th class="text-end">Total Discount</th>
                        <th class="text-end">Total Amount</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows.map(row => `
                        <tr>
                            <td>${escapeHtml(row.item_code)}</td>
                            <td>${escapeHtml(row.item_name)}</td>
                            <td class="text-end">${formatQty(row.total_qty)}</td>
                            <td class="text-end">${formatQty(row.total_free_qty)}</td>
                            <td class="text-end">${formatMoney(row.total_discount)}</td>
                            <td class="text-end">${formatMoney(row.total_amount)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    }

    if (currentReportType === "quantity") {
        return `
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Trans No</th>
                        <th>Date</th>
                        <th>Type</th>
                        <th>User</th>
                        <th>Item Code</th>
                        <th>Item Name</th>
                        <th class="text-end">Qty</th>
                        <th class="text-end">Free Qty</th>
                        <th class="text-end">Rate</th>
                        <th class="text-end">Amount</th>
                        <th class="text-end">Discount</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows.map(row => `
                        <tr>
                            <td>${escapeHtml(row.trans_no)}</td>
                            <td>${escapeHtml(row.trans_date ? new Date(row.trans_date).toLocaleString() : "")}</td>
                            <td>${escapeHtml(row.trans_type)}</td>
                            <td>${escapeHtml(row.created_user)}</td>
                            <td>${escapeHtml(row.item_code)}</td>
                            <td>${escapeHtml(row.item_name)}</td>
                            <td class="text-end">${formatQty(row.qty)}</td>
                            <td class="text-end">${formatQty(row.free_qty)}</td>
                            <td class="text-end">${formatMoney(row.rate)}</td>
                            <td class="text-end">${formatMoney(row.amount)}</td>
                            <td class="text-end">${formatMoney(row.discount_amt)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    }

    if (currentReportType === "bill") {
        return `
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Bill No</th>
                        <th>Date</th>
                        <th>Type</th>
                        <th>Customer</th>
                        <th>User</th>
                        <th>Terminal</th>
                        <th class="text-end">Net Total</th>
                        <th class="text-end">Discount</th>
                        <th class="text-end">Cash</th>
                        <th class="text-end">Cheque</th>
                        <th class="text-end">Credit</th>
                        <th>Cancel</th>
                        <th>Comments</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows.map(row => `
                        <tr>
                            <td>${escapeHtml(row.trans_no)}</td>
                            <td>${escapeHtml(row.trans_date ? new Date(row.trans_date).toLocaleString() : "")}</td>
                            <td>${escapeHtml(row.trans_type)}</td>
                            <td>${escapeHtml(row.billing_name)}</td>
                            <td>${escapeHtml(row.created_user)}</td>
                            <td>${escapeHtml(row.terminal_id)}</td>
                            <td class="text-end">${formatMoney(row.net_total)}</td>
                            <td class="text-end">${formatMoney(row.discount_amt)}</td>
                            <td class="text-end">${formatMoney(row.cash_amt)}</td>
                            <td class="text-end">${formatMoney(row.chq_amt)}</td>
                            <td class="text-end">${formatMoney(row.credit_amt)}</td>
                            <td>${escapeHtml(row.cancel_status)}</td>
                            <td>${escapeHtml(row.comments)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    }

    if (currentReportType === "gp") {
        return `
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Item Code</th>
                        <th>Item Name</th>
                        <th class="text-end">Total Qty</th>
                        <th class="text-end">Total Amount</th>
                        <th class="text-end">Total Cost</th>
                        <th class="text-end">Gross Profit</th>
                        <th class="text-end">GP %</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows.map(row => `
                        <tr>
                            <td>${escapeHtml(row.item_code)}</td>
                            <td>${escapeHtml(row.item_name)}</td>
                            <td class="text-end">${formatQty(row.total_qty)}</td>
                            <td class="text-end">${formatMoney(row.total_amount)}</td>
                            <td class="text-end">${formatMoney(row.total_cost)}</td>
                            <td class="text-end">${formatMoney(row.gross_profit)}</td>
                            <td class="text-end">${Number(row.gp_percent || 0).toFixed(2)}%</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    }

    if (currentReportType === "stock") {
        return `
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Code</th>
                        <th>Name</th>
                        <th class="text-end">Units</th>
                        <th class="text-end">Rate</th>
                        <th class="text-end">Value</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows.map(row => `
                        <tr>
                            <td>${escapeHtml(row.item_code)}</td>
                            <td>${escapeHtml(row.item_name)}</td>
                            <td class="text-end">${formatUnits(row.units)}</td>
                            <td class="text-end">${formatMoney(row.rate)}</td>
                            <td class="text-end">${formatMoney(row.value)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    }

    if (currentReportType === "expenses") {
        return `
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Account Name</th>
                        <th>Details</th>
                        <th>User</th>
                        <th>Comments</th>
                        <th class="text-end">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows.map(row => `
                        <tr>
                            <td>${escapeHtml(row.name)}</td>
                            <td>${escapeHtml(row.details)}</td>
                            <td>${escapeHtml(row.user)}</td>
                            <td>${escapeHtml(row.comments)}</td>
                            <td class="text-end">${formatMoney(row.amount)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    }

    return "";
}

function buildPrintSummaryHTML() {
    const count = document.getElementById("cardCount")?.textContent || "0";
    const amountLabel = document.getElementById("cardAmountLabel")?.textContent || "Total Amount";
    const amount = document.getElementById("cardAmount")?.textContent || "0.00";
    const extraLabel = document.getElementById("cardExtraLabel")?.textContent || "Extra Total";
    const extra = document.getElementById("cardExtra")?.textContent || "0.00";

    return `
        <div class="summary-line"><strong>Record Count:</strong> ${escapeHtml(count)}</div>
        <div class="summary-line"><strong>${escapeHtml(amountLabel)}:</strong> ${escapeHtml(amount)}</div>
        <div class="summary-line"><strong>${escapeHtml(extraLabel)}:</strong> ${escapeHtml(extra)}</div>
    `;
}

function printCurrentReport() {
    if (!currentReportType || !currentData.length) {
        alert("Please load a report before printing.");
        return;
    }

    const printWindow = window.open("", "_blank", "width=1200,height=800");

    if (!printWindow) {
        alert("Pop-up blocked. Please allow pop-ups for printing.");
        return;
    }

    const title = getReportDisplayName();
    const filterLines = getPrintFiltersText();
    const tableHTML = buildPrintTableHTML(currentData);
    const summaryHTML = buildPrintSummaryHTML();

    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>${title}</title>
            <style>
                @page {
                    size: A4 portrait;
                    margin: 10mm;
                }

                body {
                    font-family: Arial, Helvetica, sans-serif;
                    color: #000;
                    margin: 0;
                    font-size: 12px;
                }

                .report-header {
                    margin-bottom: 10px;
                }

                .report-title {
                    text-align: center;
                    font-size: 18px;
                    font-weight: 700;
                    text-transform: uppercase;
                    margin-bottom: 8px;
                }

                .meta-line {
                    margin-bottom: 3px;
                    font-size: 12px;
                }

                .report-table {
                    width: 100%;
                    border-collapse: collapse;
                    table-layout: fixed;
                    font-size: 11px;
                }

                .report-table th,
                .report-table td {
                    border: 1px solid #000;
                    padding: 4px 6px;
                    vertical-align: top;
                    word-wrap: break-word;
                }

                .report-table thead th {
                    background: #f2f2f2;
                    font-weight: 700;
                    text-align: left;
                }

                .text-end {
                    text-align: right;
                }

                .report-table thead {
                    display: table-header-group;
                }

                .report-table tfoot {
                    display: table-footer-group;
                }

                .report-table tr {
                    page-break-inside: avoid;
                }

                .report-summary {
                    margin-top: 10px;
                    text-align: right;
                    font-size: 12px;
                    line-height: 1.8;
                }

                .signature-row {
                    margin-top: 40px;
                    display: flex;
                    justify-content: space-between;
                    gap: 40px;
                }

                .signature-box {
                    width: 220px;
                    text-align: center;
                    border-top: 1px solid #000;
                    padding-top: 8px;
                }
            </style>
        </head>
        <body>
            <div class="report-header">
                <div class="report-title">${title}</div>
                <div class="meta-line">Printed On : ${formatPrintDateTime()}</div>
                ${filterLines.map(line => `<div class="meta-line">${escapeHtml(line)}</div>`).join("")}
            </div>

            ${tableHTML}

            <div class="report-summary">
                ${summaryHTML}
            </div>

            <div class="signature-row">
                <div class="signature-box">Received By</div>
                <div class="signature-box">Authorized By</div>
            </div>
        </body>
        </html>
    `);

    printWindow.document.close();

    setTimeout(() => {
        printWindow.focus();
        printWindow.print();
    }, 500);
}