// ZtionSec Frontend JavaScript Application

// Configuration
const API_BASE_URL = 'https://your-ztionsec-api.onrender.com/api/v1';

// Global variables
let currentScanType = 'basic';
let scanHistory = [];

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadStats();
    loadScanHistory();
    setupEventListeners();
});

// Initialize application
function initializeApp() {
    console.log('ZtionSec Frontend initialized');
    
    // Set up smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Setup event listeners
function setupEventListeners() {
    // Scan type selection
    document.querySelectorAll('.scan-type-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.scan-type-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentScanType = this.dataset.type;
        });
    });

    // Scan form submission
    document.getElementById('scanForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const url = document.getElementById('targetUrl').value;
        if (url) {
            startScan(url, currentScanType);
        }
    });

    // Breach check form submission
    document.getElementById('breachForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById('breachEmail').value;
        if (email) {
            checkDataBreach(email);
        }
    });
}

// Load platform statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats/`);
        if (response.ok) {
            const stats = await response.json();
            updateStatsDisplay(stats);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        // Use default values if API is not available
        updateStatsDisplay({
            total_scans: 1250,
            total_findings: 3847,
            recent_scans_24h: 23
        });
    }
}

// Update statistics display
function updateStatsDisplay(stats) {
    document.getElementById('totalScans').textContent = stats.total_scans || 0;
    document.getElementById('totalFindings').textContent = stats.total_findings || 0;
    document.getElementById('recentScans').textContent = stats.recent_scans_24h || 0;
}

// Start security scan
async function startScan(url, scanType) {
    showLoadingSpinner();
    hideResults();
    
    try {
        const endpoint = getScanEndpoint(scanType);
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        if (response.ok) {
            const result = await response.json();
            displayScanResults(result, scanType);
            loadScanHistory(); // Refresh history
        } else {
            throw new Error(`Scan failed: ${response.statusText}`);
        }
    } catch (error) {
        console.error('Scan error:', error);
        displayError('Scan failed. Please try again or check if the backend API is running.');
    } finally {
        hideLoadingSpinner();
    }
}

// Get scan endpoint based on type
function getScanEndpoint(scanType) {
    const endpoints = {
        'basic': '/scan/basic/',
        'advanced': '/scan/advanced/',
        'budget': '/scan/budget/',
        'p4': '/scan/p4/'
    };
    return endpoints[scanType] || endpoints['basic'];
}

// Display scan results
function displayScanResults(result, scanType) {
    const resultsContainer = document.getElementById('resultsContent');
    let html = '';

    if (result.success) {
        html = generateResultsHTML(result, scanType);
    } else {
        html = `<div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle"></i> 
            ${result.error || 'Scan failed'}
        </div>`;
    }

    resultsContainer.innerHTML = html;
    showResults();
}

// Generate results HTML based on scan type
function generateResultsHTML(result, scanType) {
    switch (scanType) {
        case 'basic':
            return generateBasicResultsHTML(result);
        case 'advanced':
            return generateAdvancedResultsHTML(result);
        case 'budget':
            return generateBudgetResultsHTML(result);
        case 'p4':
            return generateP4ResultsHTML(result);
        default:
            return generateBasicResultsHTML(result);
    }
}

// Generate basic scan results HTML
function generateBasicResultsHTML(result) {
    const scan = result.scan_result;
    const score = scan.security_score || 0;
    const grade = scan.grade || 'F';
    
    return `
        <div class="row">
            <div class="col-md-4">
                <div class="text-center">
                    <div class="security-score ${getScoreClass(score)}">${score}/100</div>
                    <h4>Security Score</h4>
                    <span class="badge bg-${getGradeBadgeClass(grade)} fs-6">Grade: ${grade}</span>
                </div>
            </div>
            <div class="col-md-8">
                <h5>Security Headers</h5>
                <div class="row">
                    <div class="col-sm-6">
                        ${generateHeaderStatus('HSTS', scan.has_hsts)}
                        ${generateHeaderStatus('CSP', scan.has_csp)}
                        ${generateHeaderStatus('X-Frame-Options', scan.has_xframe)}
                    </div>
                    <div class="col-sm-6">
                        ${generateHeaderStatus('XSS Protection', scan.has_xss_protection)}
                        ${generateHeaderStatus('Content-Type', scan.has_content_type)}
                    </div>
                </div>
                
                <h5 class="mt-3">SSL Information</h5>
                <p><strong>SSL Valid:</strong> ${scan.ssl_valid ? '✅ Yes' : '❌ No'}</p>
                ${scan.ssl_issuer ? `<p><strong>Issuer:</strong> ${scan.ssl_issuer}</p>` : ''}
                ${scan.ssl_grade ? `<p><strong>SSL Grade:</strong> ${scan.ssl_grade}</p>` : ''}
            </div>
        </div>
    `;
}

// Generate advanced scan results HTML
function generateAdvancedResultsHTML(result) {
    const scan = result.scan_data;
    const findings = scan.findings || [];
    
    return `
        <div class="row mb-4">
            <div class="col-md-3 text-center">
                <div class="security-score ${getScoreClass(scan.security_score)}">${scan.security_score}/100</div>
                <h5>Security Score</h5>
                <span class="risk-badge risk-${scan.risk_level}">${scan.risk_level}</span>
            </div>
            <div class="col-md-9">
                <div class="row">
                    <div class="col-sm-6">
                        <div class="stat-item">
                            <span class="text-danger">${scan.critical_findings}</span> Critical
                        </div>
                        <div class="stat-item">
                            <span class="text-warning">${scan.high_findings}</span> High
                        </div>
                    </div>
                    <div class="col-sm-6">
                        <div class="stat-item">
                            <span class="text-info">${scan.medium_findings}</span> Medium
                        </div>
                        <div class="stat-item">
                            <span class="text-secondary">${scan.low_findings}</span> Low
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <h5>Security Findings</h5>
        <div class="findings-list">
            ${findings.map(finding => generateFindingHTML(finding)).join('')}
        </div>
    `;
}

// Generate budget scan results HTML
function generateBudgetResultsHTML(result) {
    const findings = result.findings || [];
    const report = result.report || {};
    
    return `
        <div class="row mb-4">
            <div class="col-md-6">
                <h5>Budget Analysis</h5>
                <p><strong>Total Issues Found:</strong> ${findings.length}</p>
                <p><strong>Estimated Bounty:</strong> ${report.estimated_bounty_potential || 'N/A'}</p>
                <p><strong>Difficulty:</strong> ${report.difficulty_level || 'N/A'}</p>
            </div>
            <div class="col-md-6">
                <h5>Time Investment</h5>
                <p><strong>Expected Time:</strong> ${report.time_investment || 'N/A'}</p>
                <p><strong>Success Rate:</strong> High (Easy targets)</p>
            </div>
        </div>
        
        <h5>Budget-Friendly Vulnerabilities</h5>
        <div class="findings-list">
            ${findings.map(finding => generateBudgetFindingHTML(finding)).join('')}
        </div>
    `;
}

// Generate P4 scan results HTML
function generateP4ResultsHTML(result) {
    const results = result.results || {};
    const vulnerabilities = result.vulnerabilities || [];
    
    return `
        <h5>P4 Category Analysis</h5>
        <div class="row">
            ${Object.entries(results).map(([category, data]) => `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6>${formatCategoryName(category)}</h6>
                            <p class="mb-1">Issues: ${data.issues_found || 0}</p>
                            <p class="mb-0">Risk: ${data.risk_level || 'Low'}</p>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
        
        ${vulnerabilities.length > 0 ? `
            <h5 class="mt-4">Vulnerabilities Found</h5>
            <div class="findings-list">
                ${vulnerabilities.map(vuln => generateVulnerabilityHTML(vuln)).join('')}
            </div>
        ` : ''}
    `;
}

// Generate finding HTML
function generateFindingHTML(finding) {
    return `
        <div class="card result-card severity-${finding.severity} mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="card-title">${finding.title}</h6>
                        <p class="card-text">${finding.description}</p>
                        <small class="text-muted">Category: ${finding.category}</small>
                    </div>
                    <span class="badge bg-${getSeverityBadgeClass(finding.severity)}">${finding.severity}</span>
                </div>
                ${finding.recommendation ? `
                    <div class="mt-2">
                        <strong>Recommendation:</strong> ${finding.recommendation}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Generate budget finding HTML
function generateBudgetFindingHTML(finding) {
    return `
        <div class="card result-card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="card-title">${finding.title}</h6>
                        <p class="card-text">${finding.description}</p>
                        <small class="text-muted">Bounty Potential: ${finding.bounty_potential}</small>
                    </div>
                    <span class="badge bg-success">${finding.difficulty}</span>
                </div>
                ${finding.proof_of_concept ? `
                    <div class="mt-2">
                        <strong>PoC:</strong> ${finding.proof_of_concept}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Generate vulnerability HTML
function generateVulnerabilityHTML(vuln) {
    return `
        <div class="card result-card mb-3">
            <div class="card-body">
                <h6 class="card-title">${vuln.title}</h6>
                <p class="card-text">${vuln.description}</p>
                <div class="d-flex justify-content-between">
                    <small class="text-muted">Category: ${vuln.category}</small>
                    <span class="badge bg-warning">${vuln.severity}</span>
                </div>
            </div>
        </div>
    `;
}

// Check data breach
async function checkDataBreach(email) {
    try {
        const response = await fetch(`${API_BASE_URL}/breach/check/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        });

        if (response.ok) {
            const result = await response.json();
            displayBreachResults(result);
        } else {
            throw new Error(`Breach check failed: ${response.statusText}`);
        }
    } catch (error) {
        console.error('Breach check error:', error);
        displayBreachError('Breach check failed. Please try again.');
    }
}

// Display breach results
function displayBreachResults(result) {
    const resultsContainer = document.getElementById('breachResults');
    const breachData = result.breach_result;
    
    let html = '';
    if (breachData.breaches_found > 0) {
        html = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>⚠️ ${breachData.breaches_found} breach(es) found!</strong>
                <p class="mt-2">${breachData.breach_details}</p>
            </div>
        `;
    } else {
        html = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle"></i>
                <strong>✅ No breaches found</strong>
                <p class="mt-2">Your email was not found in any known data breaches.</p>
            </div>
        `;
    }
    
    resultsContainer.innerHTML = html;
    resultsContainer.style.display = 'block';
}

// Display breach error
function displayBreachError(message) {
    const resultsContainer = document.getElementById('breachResults');
    resultsContainer.innerHTML = `
        <div class="alert alert-warning">
            <i class="fas fa-exclamation-triangle"></i>
            ${message}
        </div>
    `;
    resultsContainer.style.display = 'block';
}

// Load scan history
async function loadScanHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/scans/history/`);
        if (response.ok) {
            const history = await response.json();
            displayScanHistory(history);
        }
    } catch (error) {
        console.error('Error loading scan history:', error);
        displayScanHistory({ advanced_scans: [] }); // Show empty history
    }
}

// Display scan history
function displayScanHistory(history) {
    const tbody = document.querySelector('#historyTable tbody');
    const scans = history.advanced_scans || [];
    
    if (scans.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    No scan history available
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = scans.map(scan => `
        <tr>
            <td>${scan.url}</td>
            <td>${formatDate(scan.scan_date)}</td>
            <td>
                <span class="badge bg-${getScoreBadgeClass(scan.security_score)}">
                    ${scan.security_score}/100
                </span>
            </td>
            <td>
                <span class="risk-badge risk-${scan.risk_level}">
                    ${scan.risk_level}
                </span>
            </td>
            <td>${scan.total_findings}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewScanDetails(${scan.id})">
                    <i class="fas fa-eye"></i> View
                </button>
            </td>
        </tr>
    `).join('');
}

// View scan details
async function viewScanDetails(scanId) {
    try {
        const response = await fetch(`${API_BASE_URL}/scans/${scanId}/`);
        if (response.ok) {
            const details = await response.json();
            // For now, just show an alert. In a full implementation, 
            // you'd open a modal or navigate to a details page
            alert(`Scan details for ${details.scan.url}\nFindings: ${details.findings.length}`);
        }
    } catch (error) {
        console.error('Error loading scan details:', error);
        alert('Error loading scan details');
    }
}

// Utility functions
function scrollToSection(sectionId) {
    document.getElementById(sectionId).scrollIntoView({
        behavior: 'smooth'
    });
}

function showLoadingSpinner() {
    document.getElementById('loadingSpinner').style.display = 'block';
}

function hideLoadingSpinner() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

function showResults() {
    document.getElementById('scanResults').style.display = 'block';
}

function hideResults() {
    document.getElementById('scanResults').style.display = 'none';
}

function displayError(message) {
    const resultsContainer = document.getElementById('resultsContent');
    resultsContainer.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle"></i> ${message}
        </div>
    `;
    showResults();
}

function getScoreClass(score) {
    if (score >= 90) return 'score-excellent';
    if (score >= 70) return 'score-good';
    if (score >= 50) return 'score-fair';
    return 'score-poor';
}

function getGradeBadgeClass(grade) {
    const gradeClasses = {
        'A': 'success',
        'B': 'primary',
        'C': 'warning',
        'D': 'danger',
        'F': 'dark'
    };
    return gradeClasses[grade] || 'secondary';
}

function getSeverityBadgeClass(severity) {
    const severityClasses = {
        'critical': 'danger',
        'high': 'warning',
        'medium': 'info',
        'low': 'secondary',
        'info': 'light'
    };
    return severityClasses[severity] || 'secondary';
}

function getScoreBadgeClass(score) {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
}

function generateHeaderStatus(name, status) {
    return `
        <p>
            <strong>${name}:</strong> 
            ${status ? '<span class="text-success">✅ Present</span>' : '<span class="text-danger">❌ Missing</span>'}
        </p>
    `;
}

function formatCategoryName(category) {
    return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
}
