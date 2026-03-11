// Global data
let allData = [];
let filteredData = [];
let charts = {};

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadReportData();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    document.getElementById('applyFiltersBtn').addEventListener('click', applyFilters);
    document.getElementById('resetFiltersBtn').addEventListener('click', resetFilters);
    document.getElementById('exportBtn').addEventListener('click', exportToCSV);
}

// Load data from sessionStorage
function loadReportData() {
    const dataStr = sessionStorage.getItem('reportData');
    const analysisStr = sessionStorage.getItem('reportAnalysis');

    if (!dataStr || !analysisStr) {
        document.body.innerHTML = `
            <div style="text-align: center; padding: 100px;">
                <h1>No Report Data Found</h1>
                <p>Please upload a file first from the main page.</p>
                <button onclick="window.location.href='/'" class="btn btn-primary">Go to Upload Page</button>
            </div>
        `;
        return;
    }

    allData = JSON.parse(dataStr);
    filteredData = [...allData];

    // Set report metadata
    document.getElementById('reportDate').textContent = new Date().toLocaleDateString('en-GB', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    document.getElementById('footerDate').textContent = new Date().toLocaleDateString('en-GB');

    // Populate category filter (multi-select)
    const categories = [...new Set(allData.map(d => d.category).filter(Boolean))].sort();
    const categoryFilter = document.getElementById('categoryFilter');
    categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        categoryFilter.appendChild(option);
    });

    // Populate type filter (multi-select)
    const types = [...new Set(allData.map(d => d.type_of_change).filter(Boolean))].sort();
    const typeFilter = document.getElementById('typeFilter');
    types.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        typeFilter.appendChild(option);
    });

    // Set date range filters
    const dates = allData.map(d => d.start_date_obj).filter(Boolean).map(d => new Date(d));
    if (dates.length > 0) {
        const minDate = new Date(Math.min(...dates));
        const maxDate = new Date(Math.max(...dates));
        document.getElementById('dateFromFilter').value = formatDateInput(minDate);
        document.getElementById('dateToFilter').value = formatDateInput(maxDate);
    }

    // Initial render
    updateDisplay();
}

// Apply filters
function applyFilters() {
    // Get selected categories (multi-select)
    const categorySelect = document.getElementById('categoryFilter');
    const selectedCategories = Array.from(categorySelect.selectedOptions).map(opt => opt.value);

    // Get selected types (multi-select)
    const typeSelect = document.getElementById('typeFilter');
    const selectedTypes = Array.from(typeSelect.selectedOptions).map(opt => opt.value);

    const dateFrom = document.getElementById('dateFromFilter').value;
    const dateTo = document.getElementById('dateToFilter').value;

    filteredData = allData.filter(item => {
        // Category filter (multi-select)
        if (selectedCategories.length > 0 && !selectedCategories.includes(item.category)) {
            return false;
        }

        // Type filter (multi-select)
        if (selectedTypes.length > 0 && !selectedTypes.includes(item.type_of_change)) {
            return false;
        }

        // Date filter - BYPASS for Standard Changes
        // Standard changes are always included regardless of date range
        const isStandardChange = item.type_of_change &&
            item.type_of_change.toLowerCase().includes('standard');

        if (!isStandardChange && item.start_date_obj) {
            const itemDate = new Date(item.start_date_obj);

            if (dateFrom) {
                const fromDate = new Date(dateFrom);
                if (itemDate < fromDate) return false;
            }

            if (dateTo) {
                const toDate = new Date(dateTo);
                toDate.setHours(23, 59, 59, 999); // End of day
                if (itemDate > toDate) return false;
            }
        }

        return true;
    });

    updateDisplay();
}

// Reset filters
function resetFilters() {
    // Clear category multi-select
    document.getElementById('categoryFilter').selectedIndex = -1;

    // Clear type multi-select
    document.getElementById('typeFilter').selectedIndex = -1;

    // Reset to original date range
    const dates = allData.map(d => d.start_date_obj).filter(Boolean).map(d => new Date(d));
    if (dates.length > 0) {
        const minDate = new Date(Math.min(...dates));
        const maxDate = new Date(Math.max(...dates));
        document.getElementById('dateFromFilter').value = formatDateInput(minDate);
        document.getElementById('dateToFilter').value = formatDateInput(maxDate);
    }

    filteredData = [...allData];
    updateDisplay();
}

// Update all display elements
function updateDisplay() {
    updateSummaryStats();
    renderCharts();
    renderTable();
    generateInsights();
}

// Update summary statistics
function updateSummaryStats() {
    const categories = new Set(filteredData.map(d => d.category).filter(Boolean));
    const systems = new Set(filteredData.map(d => d.system_application).filter(Boolean));
    const dates = filteredData.map(d => d.start_date_obj).filter(Boolean).map(d => new Date(d));

    document.getElementById('totalChanges').textContent = filteredData.length;
    document.getElementById('recordCount').textContent = `Showing ${filteredData.length} of ${allData.length} records`;
    document.getElementById('totalCategories').textContent = categories.size;
    document.getElementById('totalSystems').textContent = systems.size;

    if (dates.length > 0) {
        const minDate = new Date(Math.min(...dates));
        const maxDate = new Date(Math.max(...dates));
        document.getElementById('dateRange').textContent =
            `${minDate.toLocaleDateString('en-GB')} - ${maxDate.toLocaleDateString('en-GB')}`;
    } else {
        document.getElementById('dateRange').textContent = '-';
    }
}

// Safely destroy a chart by canvas ID
function destroyChart(canvasId) {
    const existing = Chart.getChart(canvasId);
    if (existing) {
        existing.destroy();
    }
}

// Render all charts
function renderCharts() {
    // Destroy all existing charts by canvas ID to prevent reuse errors
    destroyChart('categoryChart');
    destroyChart('typeChart');
    destroyChart('systemsChart');
    destroyChart('impactChart');
    charts = {};

    // Category chart
    renderCategoryChart();

    // Type chart
    renderTypeChart();

    // Systems chart
    renderSystemsChart();

    // Impact chart
    renderImpactChart();
}

// Category chart
function renderCategoryChart() {
    const categoryCounts = {};
    filteredData.forEach(item => {
        const cat = item.category || 'Unknown';
        categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
    });

    const ctx = document.getElementById('categoryChart');
    charts.category = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(categoryCounts),
            datasets: [{
                data: Object.values(categoryCounts),
                backgroundColor: [
                    '#2196F3', '#4CAF50', '#FF9800', '#F44336',
                    '#9C27B0', '#00BCD4', '#795548', '#607D8B'
                ],
                borderWidth: 2,
                borderColor: 'white'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'right' }
            }
        }
    });
}

// Type chart
function renderTypeChart() {
    const typeCounts = {};
    filteredData.forEach(item => {
        const type = item.type_of_change || 'Unknown';
        typeCounts[type] = (typeCounts[type] || 0) + 1;
    });

    const ctx = document.getElementById('typeChart');
    charts.type = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(typeCounts),
            datasets: [{
                data: Object.values(typeCounts),
                backgroundColor: ['#2196F3', '#4CAF50', '#FF9800', '#F44336'],
                borderWidth: 2,
                borderColor: 'white'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'right' }
            }
        }
    });
}


// Systems chart
function renderSystemsChart() {
    const systemCounts = {};
    filteredData.forEach(item => {
        const sys = item.system_application || 'Unknown';
        systemCounts[sys] = (systemCounts[sys] || 0) + 1;
    });

    // Get top 10
    const sorted = Object.entries(systemCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    const ctx = document.getElementById('systemsChart');
    charts.systems = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sorted.map(s => s[0]),
            datasets: [{
                label: 'Changes',
                data: sorted.map(s => s[1]),
                backgroundColor: '#2196F3',
                borderColor: '#1976D2',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Impact chart
function renderImpactChart() {
    const impactCounts = {};
    filteredData.forEach(item => {
        const impact = item.impact_description || 'Unknown';
        impactCounts[impact] = (impactCounts[impact] || 0) + 1;
    });

    const ctx = document.getElementById('impactChart');
    charts.impact = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(impactCounts),
            datasets: [{
                label: 'Count',
                data: Object.values(impactCounts),
                backgroundColor: ['#4CAF50', '#FF9800', '#F44336', '#2196F3', '#9C27B0'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Render table
function renderTable() {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    // Sort filtered data from earliest to latest
    const sortedData = [...filteredData].sort((a, b) => {
        const dateA = a.start_date_obj ? new Date(a.start_date_obj) : new Date(0);
        const dateB = b.start_date_obj ? new Date(b.start_date_obj) : new Date(0);
        return dateA - dateB; // Ascending order (earliest first)
    });

    sortedData.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.id || '-'}</td>
            <td>${item.start_date_formatted || '-'}</td>
            <td>${item.category || '-'}</td>
            <td>${item.type_of_change || '-'}</td>
            <td>${item.subject || '-'}</td>
            <td>${item.system_application || '-'}</td>
            <td>${item.impact_description || '-'}</td>
            <td style="max-width: 400px;">
                <div style="background: #e3f2fd; padding: 8px; margin-bottom: 8px; border-radius: 4px; border-left: 3px solid #2196F3;">
                    <div style="font-weight: bold; color: #1976D2; font-size: 0.9em; margin-bottom: 4px;">
                        📋 Basic Summary of Change
                    </div>
                    <div style="font-style: italic; color: #555; font-size: 0.85em;">
                        ${item.explanation || 'No summary available'}
                    </div>
                    <div style="font-size: 0.75em; color: #999; margin-top: 4px;">
                        (not included in PDF export)
                    </div>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Generate insights
function generateInsights() {
    const insightsContent = document.getElementById('insightsContent');
    const insights = [];

    // Most active category
    const categoryCounts = {};
    filteredData.forEach(item => {
        const cat = item.category || 'Unknown';
        categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
    });
    const topCategory = Object.entries(categoryCounts).sort((a, b) => b[1] - a[1])[0];
    if (topCategory) {
        insights.push({
            title: 'Most Active Category',
            text: `${topCategory[0]} had the most changes with ${topCategory[1]} records (${Math.round(topCategory[1] / filteredData.length * 100)}% of total).`
        });
    }

    // Most impacted system
    const systemCounts = {};
    filteredData.forEach(item => {
        const sys = item.system_application || 'Unknown';
        systemCounts[sys] = (systemCounts[sys] || 0) + 1;
    });
    const topSystem = Object.entries(systemCounts).sort((a, b) => b[1] - a[1])[0];
    if (topSystem) {
        insights.push({
            title: 'Most Impacted System',
            text: `${topSystem[0]} had ${topSystem[1]} changes, making it the most frequently modified system.`
        });
    }

    // Change type distribution
    const typeCounts = {};
    filteredData.forEach(item => {
        const type = item.type_of_change || 'Unknown';
        typeCounts[type] = (typeCounts[type] || 0) + 1;
    });
    const typeDistribution = Object.entries(typeCounts)
        .map(([type, count]) => `${type}: ${count}`)
        .join(', ');
    insights.push({
        title: 'Change Type Distribution',
        text: typeDistribution
    });

    // Busiest period
    const monthCounts = {};
    filteredData.forEach(item => {
        if (item.start_date_obj) {
            const date = new Date(item.start_date_obj);
            const key = date.toLocaleDateString('en-GB', { year: 'numeric', month: 'long' });
            monthCounts[key] = (monthCounts[key] || 0) + 1;
        }
    });
    const busiestMonth = Object.entries(monthCounts).sort((a, b) => b[1] - a[1])[0];
    if (busiestMonth) {
        insights.push({
            title: 'Busiest Period',
            text: `${busiestMonth[0]} was the busiest month with ${busiestMonth[1]} changes.`
        });
    }

    // Render insights
    insightsContent.innerHTML = insights.map(insight => `
        <div class="insight-item">
            <strong>${insight.title}</strong>
            <p>${insight.text}</p>
        </div>
    `).join('');
}

// Export to PDF
async function exportToCSV() {
    try {
        // Prompt user for password to protect the PDF
        const password = prompt('Enter a password to protect the PDF:\n\n(This password will be required to open the PDF file)');

        // User cancelled or entered empty password
        if (!password || password.trim().length === 0) {
            alert('PDF export cancelled. A password is required to protect the document.');
            return;
        }

        // Confirm password
        const confirmPassword = prompt('Confirm password:');
        if (password !== confirmPassword) {
            alert('Passwords do not match. Please try again.');
            return;
        }

        // Show loading state
        const exportBtn = document.getElementById('exportBtn');
        const originalText = exportBtn.innerHTML;
        exportBtn.innerHTML = '⏳ Generating PDF...';
        exportBtn.disabled = true;

        // Get current filters - collect all selected options
        const categorySelect = document.getElementById('categoryFilter');
        const selectedCategories = Array.from(categorySelect.selectedOptions).map(opt => opt.value);

        const typeSelect = document.getElementById('typeFilter');
        const selectedTypes = Array.from(typeSelect.selectedOptions).map(opt => opt.value);

        // Get all available options to determine if "All" are selected
        const allCategories = Array.from(categorySelect.options).map(opt => opt.value);
        const allTypes = Array.from(typeSelect.options).map(opt => opt.value);

        const filters = {
            categories: selectedCategories,
            types: selectedTypes,
            allCategories: allCategories,
            allTypes: allTypes,
            dateFrom: document.getElementById('dateFromFilter').value,
            dateTo: document.getElementById('dateToFilter').value
        };

        // Send request to server with password
        const response = await fetch('/api/export-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: filteredData,
                filters: filters,
                password: password
            })
        });

        if (!response.ok) {
            throw new Error('Failed to generate PDF');
        }

        // Download the PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `change-report-${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        // Restore button
        exportBtn.innerHTML = originalText;
        exportBtn.disabled = false;

        // Inform user about password protection
        alert(`✅ PDF exported successfully!\n\n🔒 This PDF is password-protected.\nYou will need to enter the password you just set to open it.\n\nSecurity features enabled:\n• Password required to view\n• Printing allowed\n• Copying/editing disabled`);

    } catch (error) {
        console.error('Error exporting PDF:', error);
        alert('Failed to export PDF. Please try again.');

        // Restore button
        const exportBtn = document.getElementById('exportBtn');
        exportBtn.innerHTML = 'Export to PDF';
        exportBtn.disabled = false;
    }
}

// Helper function to format date for input
function formatDateInput(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}
