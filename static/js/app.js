document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = '/api/v1';
    let currentContinent = 'All';

    // Slide-Out Drawer Navigation Handlers
    const sidebar = document.getElementById('app-sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarClose = document.getElementById('sidebar-close');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const navLinks = document.querySelectorAll('.nav-link');
    const tabPanes = document.querySelectorAll('.tab-pane');

    function openSidebar() {
        sidebar.classList.add('open');
        sidebarOverlay.classList.add('active');
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.remove('active');
    }

    if (sidebarToggle) sidebarToggle.addEventListener('click', openSidebar);
    if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeSidebar);

    // Chart.js Chart Instances
    let chartContinent = null;
    let chartChannel = null;
    let chartCategory = null;
    let chartCountry = null;
    let chartRFM = null;
    let chartForecast = null;
    let chartSHAP = null;

    // Navigation Tab Click Handler (Switch view, render visible tab charts & close drawer)
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = link.getAttribute('data-tab');

            navLinks.forEach(l => l.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            link.classList.add('active');
            const targetPane = document.getElementById(`tab-${tabId}`);
            if (targetPane) targetPane.classList.add('active');

            // Close the slide-out drawer so dashboard gets 100% full width
            closeSidebar();

            const pageHeadings = {
                'dashboard': ['Executive Intelligence Dashboard', 'Real-time risk scoring, global multi-continent volume, and financial performance'],
                'simulator': ['Real-Time Fraud Risk Simulator', 'Evaluate transaction attributes against live XGBoost & Isolation Forest models'],
                'transactions': ['Global Auditable Transaction Ledger', 'Sub-second transaction records across global regions'],
                'incidents': ['High-Priority Fraud Incident Queue', 'Compliance Analyst Console for one-click account freezes and SAR filing'],
                'auditor': ['ML Model Health & SHAP Auditor', 'Model validation, confusion matrix accuracy & global SHAP feature importance'],
                'segmentation': ['Customer RFM Behavioral Segmentation', 'K-Means clustering of customer accounts by recency, frequency & monetary risk'],
                'forecasting': ['Financial Intelligence Forecast', 'Predictive time-series trend forecasting with confidence boundaries'],
                'reports': ['Executive Report Generation Suite', 'Automated C-Suite Excel, PowerPoint, and PDF reports']
            };

            if (pageHeadings[tabId]) {
                document.getElementById('page-title').innerText = pageHeadings[tabId][0];
                document.getElementById('page-subtitle').innerText = pageHeadings[tabId][1];
            }

            // Render charts after tab becomes visible (solves hidden 0x0 canvas bug)
            setTimeout(() => {
                if (tabId === 'dashboard') loadKPIs();
                if (tabId === 'transactions') loadTransactions();
                if (tabId === 'incidents') loadIncidents();
                if (tabId === 'auditor') loadAuditorMetrics();
                if (tabId === 'segmentation') loadSegmentation();
                if (tabId === 'forecasting') loadForecast();
            }, 60);
        });
    });

    // Region Pills Filter
    const continentBtns = document.querySelectorAll('.pill-btn');
    continentBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            continentBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentContinent = btn.getAttribute('data-continent');
            loadKPIs();
            loadTransactions();
        });
    });

    // Load KPI Dashboard Analytics
    async function loadKPIs() {
        try {
            const url = currentContinent !== 'All' 
                ? `${API_BASE}/analytics/kpis?continent=${encodeURIComponent(currentContinent)}`
                : `${API_BASE}/analytics/kpis`;

            const res = await fetch(url);
            const data = await res.json();

            document.getElementById('kpi-total-volume').innerText = `$${data.total_volume.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
            document.getElementById('kpi-total-tx').innerText = data.total_transactions.toLocaleString();
            document.getElementById('kpi-fraud-cnt').innerText = data.fraud_count.toLocaleString();
            document.getElementById('kpi-fraud-rate').innerText = `${data.fraud_rate_pct.toFixed(2)}%`;
            document.getElementById('kpi-fraud-exposure').innerText = `$${data.fraud_exposure_dollar.toLocaleString('en-US', {minimumFractionDigits: 2})}`;

            renderContinentChart(data.continent_distribution);
            renderChannelChart(data.channel_breakdown);
            renderCategoryChart(data.category_distribution);
            renderCountryThreatsChart(data.country_distribution);
        } catch (err) {
            console.error('Error loading KPIs:', err);
        }
    }

    // Chart 1: Global Continent Volume Bar Chart (Chart.js)
    function renderContinentChart(contData) {
        const ctx = document.getElementById('canvas-continent-volume');
        if (!ctx) return;

        const labels = contData.map(c => c.continent);
        const vols = contData.map(c => c.amount);

        if (chartContinent) chartContinent.destroy();
        chartContinent = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Processed Volume ($)',
                    data: vols,
                    backgroundColor: 'rgba(14, 165, 233, 0.8)',
                    borderColor: '#0EA5E9',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#94A3B8' } },
                    y: { grid: { color: 'rgba(255, 255, 255, 0.08)' }, ticks: { color: '#94A3B8' } }
                }
            }
        });
    }

    // Chart 2: Channel Breakdown Doughnut Chart (Chart.js)
    function renderChannelChart(channels) {
        const ctx = document.getElementById('canvas-channel-breakdown');
        if (!ctx) return;

        const labels = Object.keys(channels);
        const series = Object.values(channels);

        if (chartChannel) chartChannel.destroy();
        chartChannel = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: series,
                    backgroundColor: ['#0EA5E9', '#6366F1', '#10B981', '#F59E0B'],
                    borderWidth: 2,
                    borderColor: '#0F172A'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#94A3B8', padding: 12 } }
                }
            }
        });
    }

    // Chart 3: Category Volume Horizontal Bar Chart (Chart.js)
    function renderCategoryChart(catData) {
        const ctx = document.getElementById('canvas-category-volume');
        if (!ctx) return;

        const labels = catData.map(c => c.merchant_category);
        const vols = catData.map(c => c.amount);

        if (chartCategory) chartCategory.destroy();
        chartCategory = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Category Exposure ($)',
                    data: vols,
                    backgroundColor: 'rgba(245, 158, 11, 0.8)',
                    borderColor: '#F59E0B',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: 'rgba(255, 255, 255, 0.08)' }, ticks: { color: '#94A3B8' } },
                    y: { grid: { display: false }, ticks: { color: '#94A3B8' } }
                }
            }
        });
    }

    // Chart 4: Country Threat Ingress Bar Chart (Chart.js)
    function renderCountryThreatsChart(countryData) {
        const ctx = document.getElementById('canvas-country-threats');
        if (!ctx) return;

        const labels = countryData.map(c => c.location_country);
        const frauds = countryData.map(c => c.is_fraud_actual);

        if (chartCountry) chartCountry.destroy();
        chartCountry = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Fraud Detections',
                    data: frauds,
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    borderColor: '#EF4444',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#94A3B8' } },
                    y: { grid: { color: 'rgba(255, 255, 255, 0.08)' }, ticks: { color: '#94A3B8' } }
                }
            }
        });
    }

    // Load Incident Action Queue from API
    async function loadIncidents() {
        try {
            const res = await fetch(`${API_BASE}/analytics/incidents`);
            const data = await res.json();
            const tbody = document.getElementById('incidents-table-body');
            tbody.innerHTML = '';

            if (data.incidents.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No high-risk incidents pending.</td></tr>`;
                return;
            }

            data.incidents.forEach(inc => {
                const tr = document.createElement('tr');
                const badgeClass = inc.risk_score > 90 ? 'badge-rose' : 'badge-amber';
                const btnClass = inc.risk_score > 90 ? 'btn-rose' : 'btn-amber';
                const btnLabel = inc.risk_score > 90 ? 'Freeze Account' : 'Trigger 2FA';

                tr.innerHTML = `
                    <td><code>${inc.incident_id}</code></td>
                    <td>${inc.customer_id}</td>
                    <td><strong class="text-rose font-mono">$${inc.amount.toLocaleString()}</strong></td>
                    <td><span class="badge ${badgeClass}">${inc.country}</span></td>
                    <td><span class="badge ${badgeClass}">${inc.risk_score} / 100</span></td>
                    <td style="font-size: 12px; color: var(--text-muted);">${inc.shap_factor}</td>
                    <td>
                        <button class="btn ${btnClass} btn-sm" onclick="alert('Action executed for ${inc.customer_id}: ${btnLabel}. File updated in compliance ledger.')">
                            <i class="fa-solid fa-shield"></i> ${btnLabel}
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            console.error('Error loading incidents:', err);
        }
    }

    // Load Model Auditor Metrics & SHAP Chart from API
    async function loadAuditorMetrics() {
        try {
            const res = await fetch(`${API_BASE}/analytics/auditor`);
            const data = await res.json();

            const ctx = document.getElementById('canvas-shap-importance');
            if (!ctx) return;

            const labels = data.shap_importance.map(s => s.feature);
            const weights = data.shap_importance.map(s => s.importance);

            if (chartSHAP) chartSHAP.destroy();
            chartSHAP = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'SHAP Global Weight Share',
                        data: weights,
                        backgroundColor: 'rgba(99, 102, 241, 0.8)',
                        borderColor: '#6366F1',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { color: 'rgba(255, 255, 255, 0.08)' }, ticks: { color: '#94A3B8' } },
                        y: { grid: { display: false }, ticks: { color: '#94A3B8' } }
                    }
                }
            });
        } catch (err) {
            console.error('Error loading auditor metrics:', err);
        }
    }

    // Load Transactions Table
    async function loadTransactions() {
        const fraudOnly = document.getElementById('chk-fraud-only').checked;
        const searchTerm = document.getElementById('tx-search').value.toLowerCase();

        try {
            const res = await fetch(`${API_BASE}/transactions?limit=50&fraud_only=${fraudOnly}`);
            const data = await res.json();

            const tbody = document.getElementById('tx-table-body');
            tbody.innerHTML = '';

            const filtered = data.transactions.filter(t => {
                return t.transaction_id.toLowerCase().includes(searchTerm) || t.customer_id.toLowerCase().includes(searchTerm);
            });

            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="9" class="text-center py-4 text-muted">No transactions matching filter criteria.</td></tr>`;
                return;
            }

            filtered.forEach(t => {
                const tr = document.createElement('tr');
                const badgeClass = t.risk_level === 'CRITICAL' || t.risk_level === 'HIGH' ? 'badge-rose' : 'badge-emerald';
                
                tr.innerHTML = `
                    <td><code>${t.transaction_id}</code></td>
                    <td>${t.customer_id}</td>
                    <td style="font-size: 11px; color: var(--text-muted);">${t.timestamp}</td>
                    <td><strong class="font-mono">$${t.amount.toFixed(2)}</strong></td>
                    <td>${t.merchant_category}</td>
                    <td>${t.entry_mode}</td>
                    <td><span class="badge" style="background: rgba(255,255,255,0.08);">${t.location_country}</span></td>
                    <td><span class="badge ${badgeClass}">${t.fraud_risk_score.toFixed(1)}</span></td>
                    <td><span class="badge ${badgeClass}">${t.status}</span></td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            console.error('Error loading transactions:', err);
        }
    }

    document.getElementById('chk-fraud-only').addEventListener('change', loadTransactions);
    document.getElementById('tx-search').addEventListener('input', loadTransactions);

    // Live Risk Simulator Form Submit
    document.getElementById('sim-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const payload = {
            amount: parseFloat(document.getElementById('sim-amount').value),
            merchant_category: document.getElementById('sim-category').value,
            location_country: document.getElementById('sim-country').value,
            entry_mode: document.getElementById('sim-entry').value,
            velocity_1h: parseInt(document.getElementById('sim-v1h').value),
            distance_from_home_km: parseFloat(document.getElementById('sim-distance').value)
        };

        try {
            const res = await fetch(`${API_BASE}/ml/score`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            const resultBox = document.getElementById('sim-result-container');
            const isHigh = data.risk_score >= 50.0;
            const badgeClass = isHigh ? 'badge-rose' : 'badge-emerald';
            const colorCode = isHigh ? '#EF4444' : '#10B981';

            resultBox.innerHTML = `
                <div style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 16px;">
                    <span class="badge ${badgeClass}" style="font-size: 13px; padding: 6px 12px;">RECOMMENDED ACTION: ${data.status}</span>
                    <h2 style="font-family: var(--font-heading); margin-top: 14px;">ML Risk Score: <span class="font-mono" style="color: ${colorCode}">${data.risk_score}/100</span></h2>
                    <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Evaluated Risk Level: <strong>${data.risk_level}</strong></p>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 20px;">
                    <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 10px;">
                        <span style="font-size: 11px; color: var(--text-muted);">Supervised XGBoost Prob:</span>
                        <h4 class="font-mono" style="color: var(--accent-cyan); font-size: 18px; margin-top: 4px;">${(data.fraud_probability * 100).toFixed(2)}%</h4>
                    </div>
                    <div style="background: rgba(255,255,255,0.02); padding: 12px; border-radius: 10px;">
                        <span style="font-size: 11px; color: var(--text-muted);">Unsupervised Anomaly Score:</span>
                        <h4 class="font-mono" style="color: var(--accent-indigo); font-size: 18px; margin-top: 4px;">${data.anomaly_score}</h4>
                    </div>
                </div>

                <div style="margin-top: 24px;">
                    <h4 style="font-size: 14px; font-weight: 600;"><i class="fa-solid fa-layer-group text-cyan"></i> Primary SHAP Risk Drivers Identified:</h4>
                    <ul style="margin-top: 10px; padding-left: 20px; font-size: 13px; color: var(--text-muted);">
                        ${data.risk_factors.map(rf => `<li style="margin-bottom: 8px;">${rf}</li>`).join('')}
                    </ul>
                </div>
            `;
        } catch (err) {
            console.error('Error submitting simulator:', err);
        }
    });

    // Customer RFM Segmentation Loader
    async function loadSegmentation() {
        try {
            const res = await fetch(`${API_BASE}/analytics/segmentation`);
            const data = await res.json();

            const ctx = document.getElementById('canvas-rfm-pie');
            if (ctx) {
                const labels = Object.keys(data.segment_distribution);
                const series = Object.values(data.segment_distribution);

                if (chartRFM) chartRFM.destroy();
                chartRFM = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: series,
                            backgroundColor: ['#0EA5E9', '#10B981', '#F59E0B', '#EF4444'],
                            borderWidth: 2,
                            borderColor: '#0F172A'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'bottom', labels: { color: '#94A3B8', padding: 12 } } }
                    }
                });
            }

            const profileBox = document.getElementById('rfm-profiles-container');
            if (profileBox) {
                profileBox.innerHTML = data.segment_profiles.map(p => `
                    <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 14px; margin-bottom: 12px;">
                        <h4 style="color: var(--accent-cyan); font-size: 14px;">${p.segment_label}</h4>
                        <div style="display: flex; gap: 16px; margin-top: 8px; font-size: 12px; color: var(--text-muted);">
                            <span>Avg Monetary: <strong class="font-mono" style="color:white;">$${p.monetary_val.toLocaleString()}</strong></span>
                            <span>Avg Recency: <strong style="color:white;">${p.recency_days} days</strong></span>
                            <span>Fraud Incidents: <strong style="color:#EF4444;">${p.fraud_cnt}</strong></span>
                        </div>
                    </div>
                `).join('');
            }
        } catch (err) {
            console.error('Error loading segmentation:', err);
        }
    }

    // Forecasting Chart Loader
    async function loadForecast() {
        try {
            const res = await fetch(`${API_BASE}/analytics/forecasting?days=30`);
            const data = await res.json();

            const ctx = document.getElementById('canvas-forecast');
            if (!ctx) return;

            const dates = data.forecast_daily.map(f => f.date);
            const revenues = data.forecast_daily.map(f => f.forecast_revenue);

            if (chartForecast) chartForecast.destroy();
            chartForecast = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Projected Daily Revenue ($)',
                        data: revenues,
                        borderColor: '#0EA5E9',
                        backgroundColor: 'rgba(14, 165, 233, 0.15)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { color: 'rgba(255, 255, 255, 0.08)' }, ticks: { color: '#94A3B8' } },
                        y: { grid: { color: 'rgba(255, 255, 255, 0.08)' }, ticks: { color: '#94A3B8' } }
                    }
                }
            });
        } catch (err) {
            console.error('Error loading forecast:', err);
        }
    }

    // Initial Load for Active Tab
    loadKPIs();
    loadTransactions();
});
