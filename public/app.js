// Global state
let currentData = null;
let currentAnalysis = null;

// DOM Elements
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const uploadBtn = document.getElementById('uploadBtn');
const uploadStatus = document.getElementById('uploadStatus');
const resultsSection = document.getElementById('resultsSection');
const previewSection = document.getElementById('previewSection');
const generateReportBtn = document.getElementById('generateReportBtn');
const uploadNewBtn = document.getElementById('uploadNewBtn');
const summaryStats = document.getElementById('summaryStats');

// Event Listeners
uploadArea.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        const fileName = e.target.files[0].name;
        const fileSize = (e.target.files[0].size / 1024).toFixed(2);
        uploadArea.innerHTML = `
            <div class="file-selected">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <p style="color: var(--success-color); font-weight: 600; font-size: 1.2rem; margin: 10px 0;">
                    ✓ File Selected
                </p>
                <p style="color: var(--text-dark); font-weight: 500;">${fileName}</p>
                <p style="color: var(--text-light); font-size: 0.9rem;">${fileSize} KB</p>
                <button class="btn btn-secondary" style="margin-top: 15px;" onclick="document.getElementById('fileInput').click()">
                    Change File
                </button>
            </div>
        `;
        uploadBtn.style.display = 'block';
        uploadBtn.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        const fileName = files[0].name;
        const fileSize = (files[0].size / 1024).toFixed(2);
        uploadArea.innerHTML = `
            <div class="file-selected">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <p style="color: var(--success-color); font-weight: 600; font-size: 1.2rem; margin: 10px 0;">
                    ✓ File Selected
                </p>
                <p style="color: var(--text-dark); font-weight: 500;">${fileName}</p>
                <p style="color: var(--text-light); font-size: 0.9rem;">${fileSize} KB</p>
                <button class="btn btn-secondary" style="margin-top: 15px;" onclick="document.getElementById('fileInput').click()">
                    Change File
                </button>
            </div>
        `;
        uploadBtn.style.display = 'block';
        uploadBtn.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
});

uploadBtn.addEventListener('click', uploadFile);
generateReportBtn.addEventListener('click', generateReport);
uploadNewBtn.addEventListener('click', resetUpload);

// Upload file
async function uploadFile() {
    const file = fileInput.files[0];
    if (!file) {
        showStatus('Please select a file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    showStatus('Analyzing changes... <span class="spinner"></span>', 'loading');
    uploadBtn.disabled = true;

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            currentData = result.data;
            currentAnalysis = result.analysis;

            showStatus(`Successfully analyzed ${result.totalRecords} change records!`, 'success');
            displayResults();
        } else {
            showStatus(`Error: ${result.error}`, 'error');
        }
    } catch (error) {
        showStatus(`Error: ${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = false;
    }
}

// Display results
function displayResults() {
    resultsSection.style.display = 'block';
    previewSection.style.display = 'block';

    // Display summary stats
    summaryStats.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${currentAnalysis.totalChanges}</div>
            <div class="stat-label">Total Changes</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${Object.keys(currentAnalysis.byCategory).length}</div>
            <div class="stat-label">Categories</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${Object.keys(currentAnalysis.byType).length}</div>
            <div class="stat-label">Change Types</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${Object.keys(currentAnalysis.topSystems).length}</div>
            <div class="stat-label">Systems Affected</div>
        </div>
    `;

    // Render charts
    renderCategoryChart();
    renderTimelineChart();

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Render category chart
function renderCategoryChart() {
    const ctx = document.getElementById('categoryChart');
    const labels = Object.keys(currentAnalysis.byCategory);
    const data = Object.values(currentAnalysis.byCategory);

    const colors = [
        '#2196F3', '#4CAF50', '#FF9800', '#F44336',
        '#9C27B0', '#00BCD4', '#795548', '#607D8B'
    ];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: 'white'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Render timeline chart
function renderTimelineChart() {
    const ctx = document.getElementById('timelineChart');
    const labels = Object.keys(currentAnalysis.byMonth);
    const data = Object.values(currentAnalysis.byMonth);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Changes per Month',
                data: data,
                backgroundColor: '#2196F3',
                borderColor: '#1976D2',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Generate interactive report
function generateReport() {
    // Save data to sessionStorage
    sessionStorage.setItem('reportData', JSON.stringify(currentData));
    sessionStorage.setItem('reportAnalysis', JSON.stringify(currentAnalysis));

    // Open report in new window
    window.open('report.html', '_blank');
}

// Reset upload
function resetUpload() {
    fileInput.value = '';
    uploadArea.innerHTML = `
        <div class="upload-prompt">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <p>Click to browse or drag and drop your file here</p>
            <span class="file-types">Supports: XLS, XLSX, TXT (Unicode Text)</span>
        </div>
    `;
    uploadBtn.style.display = 'none';
    uploadStatus.style.display = 'none';
    resultsSection.style.display = 'none';
    previewSection.style.display = 'none';
    currentData = null;
    currentAnalysis = null;
}

// Show status message
function showStatus(message, type) {
    uploadStatus.innerHTML = message;
    uploadStatus.className = `status-message ${type}`;
}
