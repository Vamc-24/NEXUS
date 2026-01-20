// dashboard.js - Revamped for Unified Portal Access with URL State

document.addEventListener('DOMContentLoaded', () => {
    checkAdminSession(); // Updated Security Check

    // Set Institute Name Header (Custom Branding)
    const instName = sessionStorage.getItem('institute_name') || 'AITS';
    const headerEl = document.getElementById('dashboard-institute-name');
    if (headerEl) headerEl.innerText = instName;

    initializeDashboard();
});

function checkAdminSession() {
    const token = sessionStorage.getItem('admin_token');
    if (!token) {
        window.location.href = 'admin_login.html'; // Redirect to Admin Login, not Index
    }
}

// Logout Function
function logout() {
    // Smooth Fade Out
    document.body.style.transition = 'opacity 0.6s ease';
    document.body.style.opacity = '0';

    setTimeout(() => {
        sessionStorage.removeItem('admin_token');
        sessionStorage.removeItem('institute_id'); // Optional: Clear institute too if 'Total Logout' desired
        window.location.href = 'index.html';
    }, 600);
}

// ---------------------------------------------------------
// 1. Navigation & State Management
// ---------------------------------------------------------
function initializeDashboard() {
    const params = new URLSearchParams(window.location.search);
    const role = params.get('role') || 'Admin';

    // Update Role Badge
    const roleLabel = document.getElementById('header-role-label');
    if (roleLabel) roleLabel.innerText = role.toUpperCase();

    // 1. Restore View from URL
    const view = params.get('view') || 'dashboard';
    switchView(view, false); // false = don't push state on initial load

    // 2. Restore Filter from URL
    const filter = params.get('filter') || 'All';
    currentFilter = filter;
    updateFilterUI(filter);

    // 3. Auto-load Data
    fetchLatestResults();
}

// Switch Sidebar Views
function switchView(viewName, pushState = true) {
    // 1. Update URL
    if (pushState) {
        const url = new URL(window.location);
        url.searchParams.set('view', viewName);
        window.history.pushState({}, '', url);
    }

    // 2. Update Sidebar Active State
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('onclick')?.includes(`'${viewName}'`)) {
            item.classList.add('active');
        }
    });

    console.log(`Switched to ${viewName}`);

    // View Logic
    if (viewName === 'reports') {
        const pdfSection = document.getElementById('report-download-section');
        if (pdfSection) pdfSection.scrollIntoView({ behavior: 'smooth' });
    } else if (viewName === 'notifications') {
        const alerts = document.getElementById('notifications-target');
        if (alerts) alerts.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else if (viewName === 'analytics') {
        // Renamed 'Ratings' in UI, but ID logic remains for grid/charts
        const grid = document.querySelector('.grid-2');
        if (grid) grid.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
        window.scrollTo({ top: 0, behavior: 'smooth' }); // Dashboard / Home
    }
}

// Firebase Configuration (Frontend)
// Note: Core data storage is handled by the Python Backend (storage.py)
// This frontend connection is initialized as requested.
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-analytics.js";

const firebaseConfig = {
    apiKey: "AIzaSyDZG2bka3fV7IYzr-DRMf13ZLVxyXM4Dz8",
    authDomain: "nexus-ai-project-ca36d.firebaseapp.com",
    projectId: "nexus-ai-project-ca36d",
    storageBucket: "nexus-ai-project-ca36d.firebasestorage.app",
    messagingSenderId: "1064011591904",
    appId: "1:1064011591904:web:28f48e7f5e95e1f9a96085",
    measurementId: "G-NN9YKZEB0E"
};

try {
    const app = initializeApp(firebaseConfig);
    const analytics = getAnalytics(app);
    console.log("Firebase Frontend Initialized");
} catch (e) {
    console.warn("Firebase Init Error (Check module support in dashboard.html):", e);
}

// Global Filter State
let currentFilter = 'All';
let latestResults = null;

function filterResults(sentiment) {
    currentFilter = sentiment;

    // Update URL
    const url = new URL(window.location);
    url.searchParams.set('filter', sentiment);
    window.history.pushState({}, '', url);

    updateFilterUI(sentiment);

    if (latestResults) {
        renderResults(latestResults);
    }
}

function updateFilterUI(filter) {
    document.querySelectorAll('.btn-sm').forEach(btn => {
        if (btn.innerText.includes(filter) || (filter === 'All' && btn.innerText === 'All')) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// Handle Browser Back/Forward
window.addEventListener('popstate', () => {
    const params = new URLSearchParams(window.location.search);
    const view = params.get('view') || 'dashboard';
    const filter = params.get('filter') || 'All';

    switchView(view, false);
    currentFilter = filter;
    updateFilterUI(filter);
    if (latestResults) renderResults(latestResults);
});


// ---------------------------------------------------------
// 2. Data Fetching & Rendering
// ---------------------------------------------------------

async function fetchLatestResults() {
    try {
        const instituteId = sessionStorage.getItem('institute_id');
        const query = instituteId ? `?institute_id=${instituteId}` : '';
        const response = await fetch(`/api/results${query}`);
        const data = await response.json();
        if (data && data.clusters && data.clusters.length > 0) {
            latestResults = data;
            renderDashboard(data);
        } else {
            // Handle empty state explicitly so UI initializes
            latestResults = { clusters: [] };
            renderDashboard({ clusters: [] });
        }


    } catch (e) {
        console.log("Awaiting Analysis...", e);
    } finally {
        // Always try to fetch stats for dynamic real-time data
        fetchStats();
    }
}

async function fetchStats() {
    try {
        const instituteId = sessionStorage.getItem('institute_id');
        const query = instituteId ? `?institute_id=${instituteId}` : '';
        const response = await fetch(`/api/stats${query}`);
        const stats = await response.json();
        renderCharts(stats);

        // Update Total Volume KPI from direct stats if available
        if (stats.total !== undefined) {
            const kpiTotal = document.getElementById('kpi-total');
            if (kpiTotal) kpiTotal.innerText = stats.total.toLocaleString();
        }
    } catch (e) {
        console.error("Failed to fetch stats", e);
    }
}

function renderDashboard(data) {
    updateKPIS(data);
    renderResults(data);
    renderCriticalAlerts(data);
}

// ---------------------------------------------------------
// Chart.js Rendering
// ---------------------------------------------------------
let deptChartInstance = null;
let problemChartInstance = null;

function renderCharts(stats) {
    const ctxDept = document.getElementById('deptChart');
    const ctxProb = document.getElementById('problemChart');

    if (ctxDept) {
        if (deptChartInstance) deptChartInstance.destroy();

        // Parse Role Data
        const roles = stats.roles || {};
        const roleLabels = Object.keys(roles);
        const roleData = Object.values(roles);

        deptChartInstance = new Chart(ctxDept, {
            type: 'bar',
            data: {
                labels: roleLabels.length ? roleLabels : ['No Data'],
                datasets: [{
                    label: 'Feedback Volume',
                    data: roleData.length ? roleData : [0],
                    backgroundColor: [
                        '#3b82f6', '#8b5cf6', '#a259ff', '#f59e0b', '#22c55e'
                    ],
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#888', precision: 0 } },
                    x: { grid: { display: false }, ticks: { color: '#888' } }
                }
            }
        });
    }

    if (ctxProb) {
        if (problemChartInstance) problemChartInstance.destroy();

        // Parse Category Data
        const cats = stats.categories || {};
        const catLabels = Object.keys(cats);
        const catData = Object.values(cats);

        problemChartInstance = new Chart(ctxProb, {
            type: 'doughnut',
            data: {
                labels: catLabels.length ? catLabels : ['Empty'],
                datasets: [{
                    data: catData.length ? catData : [1], // Placeholder 1 if empty to show ring
                    backgroundColor: [
                        'rgba(249, 115, 22, 0.8)', // Orange
                        'rgba(168, 85, 247, 0.8)', // Purple
                        'rgba(34, 197, 94, 0.8)',  // Green
                        'rgba(239, 68, 68, 0.8)',  // Red
                        '#3b82f6', '#eab308'
                    ],
                    borderColor: '#18181b',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right', labels: { color: '#ccc', font: { size: 10 } } }
                }
            }
        });
    }
}


function updateKPIS(data) {
    // 1. Total Feedbacks
    const totalVolume = data.clusters.reduce((acc, c) => acc + (c.count || 0), 0) || 0;
    if (document.getElementById('kpi-total')) document.getElementById('kpi-total').innerText = totalVolume.toLocaleString();

    // 2. Unique Issues
    if (document.getElementById('kpi-unique')) document.getElementById('kpi-unique').innerText = data.clusters.length;

    // 3. Solved (Mock)
    if (document.getElementById('kpi-solved')) document.getElementById('kpi-solved').innerText = Math.floor(totalVolume * 0.4);

    // 4. Critical Alerts (calculated in renderCriticalAlerts)
}


function renderResults(data) {
    const container = document.getElementById('dashboard-content');
    if (!container) return;

    container.innerHTML = '';

    const filtered = data.clusters.filter(c => {
        const sentiment = c.solutions[0]?.sentiment || "Neutral";
        return currentFilter === 'All' || sentiment === currentFilter;
    });

    if (filtered.length === 0) {
        container.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 40px;">No signals matching '${currentFilter}'</div>`;
        return;
    }

    filtered.forEach((cluster, index) => {
        const sol = cluster.solutions[0];
        const sentiment = sol?.sentiment || "Neutral";
        let color = '#a1a1aa'; // Neutral
        if (sentiment === 'Positive') color = '#22c55e';
        if (sentiment === 'Negative') color = '#ef4444';

        const card = document.createElement('div');
        card.className = 'stat-widget fade-in';
        card.style.marginBottom = '24px';
        card.style.borderLeft = `4px solid ${color}`;
        card.style.animationDelay = `${index * 0.1}s`;

        // Detailed AI Layout
        card.innerHTML = `
            <!-- 1. Regenerated Problem Statement -->
            <div style="margin-bottom: 20px;">
                <h6 style="color: var(--text-muted); text-transform: uppercase; font-size: 0.75rem; margin-bottom: 8px;">
                    <i class="fa-solid fa-rotate"></i> REGENERATED PROBLEM STATEMENT
                </h6>
                <h3 style="font-size: 1.2rem; line-height: 1.5; color: white;">
                    "${cluster.problem_statement}"
                </h3>
                <div style="margin-top: 10px; display: flex; gap: 10px;">
                    <span class="tag" style="background: rgba(255,255,255,0.05); color: #ccc;">${cluster.theme}</span>
                    <span class="tag" style="background: rgba(255,255,255,0.05); color: #ccc;">${cluster.count} Reports</span>
                </div>
            </div>

            <!-- 2. AI Solution (One Line) -->
            <div style="background: rgba(255, 255, 255, 0.03); padding: 16px; border-radius: 8px; margin-bottom: 16px; border: 1px solid rgba(255, 255, 255, 0.05);">
                <h6 style="color: var(--primary-orange); font-size: 0.75rem; margin-bottom: 5px;">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> AI GENERATED SOLUTION
                </h6>
                <p style="font-size: 1.1rem; font-weight: 600; color: #fff;">
                    ${sol.solution_title}
                </p>
            </div>

            <!-- 3. Step-by-Step Process -->
            <div style="margin-bottom: 20px;">
                <h6 style="color: var(--text-muted); font-size: 0.75rem; margin-bottom: 10px;">IMPLEMENTATION PROCESS</h6>
                <ul style="color: #d4d4d8; font-size: 0.95rem; line-height: 1.8; padding-left: 20px;">
                    ${sol.steps ? sol.steps.map(step => `<li>${step}</li>`).join('') : '<li>Analysis pending...</li>'}
                </ul>
            </div>

            <!-- 4. Estimated Cost -->
            <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                     <span style="display: block; font-size: 0.8rem; color: var(--text-muted);">ESTIMATED COST</span>
                     <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.2rem; color: #22c55e;">
                        ₹ ${sol.total_estimated_cost || 'N/A'}
                     </span>
                </div>

            </div>
        `;

        container.appendChild(card);
    });
}

function renderCriticalAlerts(data) {
    const container = document.getElementById('critical-alerts-content');
    if (!container) return;

    container.innerHTML = '';
    const urgentKeywords = ['food', 'ragging', 'harassment', 'safety', 'hygiene', 'poison'];

    const alerts = data.clusters.filter(c => {
        const text = c.problem_statement.toLowerCase();
        const sentiment = c.solutions[0]?.sentiment || "Neutral";
        return sentiment === 'Negative' && urgentKeywords.some(k => text.includes(k));
    });

    document.getElementById('kpi-alerts').innerText = alerts.length;
    if (document.getElementById('alert-count')) document.getElementById('alert-count').innerText = alerts.length;

    if (alerts.length > 0) {
        alerts.forEach(alertItem => {
            const div = document.createElement('div');
            div.className = 'stat-widget fade-in';
            div.style.padding = '16px';
            div.style.background = 'rgba(239, 68, 68, 0.1)';
            div.style.border = '1px solid rgba(239, 68, 68, 0.3)';
            div.innerHTML = `
                <h5 style="color: #fca5a5; margin-bottom: 5px; font-size: 0.9rem;">
                    <i class="fa-solid fa-bell"></i> ${alertItem.theme}
                </h5>
                <p style="color: #fff; font-size: 0.85rem;">${alertItem.problem_statement.substring(0, 60)}...</p>
                <button class="btn-sm" style="margin-top: 5px; width: 100%; background: rgba(239,68,68,0.2); border: none; color: white;">Investigate</button>
            `;
            container.appendChild(div);
        });
    } else {
        container.innerHTML = `<p class="text-muted" style="font-size: 0.9rem; padding: 10px;">All systems nominal.</p>`;
    }
}

// ---------------------------------------------------------
// 3. Actions
// ---------------------------------------------------------

async function exportReport(type) {
    if (!latestResults) return alert("System initializing... please wait.");

    const btn = event.currentTarget;
    const oldText = btn.innerHTML;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Generating...`;

    try {
        const response = await fetch(`/api/export/${type}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ results: latestResults })
        });
        const data = await response.json();
        if (data.url) {
            const link = document.createElement('a');
            link.href = data.url;
            link.download = data.url.split('/').pop();
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    } catch (e) {
        alert("Export failed.");
    } finally {
        btn.innerHTML = oldText;
    }
}

function logout() {
    sessionStorage.clear();
    window.location.href = '/';
}
