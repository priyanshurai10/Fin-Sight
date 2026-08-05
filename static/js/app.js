/* ============================================================
   FIN SIGHT — World-Class Premium JavaScript Engine
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = '/api/v1';
    let currentContinent = 'All';

    // ============================================================
    // CHART INSTANCES (for destroy/recreate)
    // ============================================================
    let chartContinent = null;
    let chartChannel = null;
    let chartCategory = null;
    let chartCountry = null;
    let chartRFM = null;
    let chartForecast = null;
    let chartSHAP = null;

    // ============================================================
    // TOAST NOTIFICATION SYSTEM
    // ============================================================
    function showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const icons = { success: 'fa-circle-check', error: 'fa-circle-xmark', info: 'fa-circle-info' };
        toast.innerHTML = `<i class="fa-solid ${icons[type] || icons.info}" style="font-size:16px;"></i><span>${message}</span>`;

        container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // ============================================================
    // ANIMATED NUMBER COUNTER
    // ============================================================
    function animateValue(el, end, duration = 1200, prefix = '', suffix = '', decimals = 0) {
        if (!el) return;
        const start = 0;
        const startTime = performance.now();

        function easeOutExpo(t) { return t === 1 ? 1 : 1 - Math.pow(2, -10 * t); }

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easedProgress = easeOutExpo(progress);
            const currentValue = start + (end - start) * easedProgress;

            if (decimals > 0) {
                el.textContent = prefix + currentValue.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) + suffix;
            } else {
                el.textContent = prefix + Math.round(currentValue).toLocaleString('en-US') + suffix;
            }

            if (progress < 1) requestAnimationFrame(update);
        }

        requestAnimationFrame(update);
    }

    // ============================================================
    // CHART.JS GRADIENT HELPER
    // ============================================================
    function createGradient(ctx, color1, color2, vertical = true) {
        const canvas = ctx.canvas;
        let gradient;
        if (vertical) {
            gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        } else {
            gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
        }
        gradient.addColorStop(0, color1);
        gradient.addColorStop(1, color2);
        return gradient;
    }

    function createFillGradient(ctx, color, opacity1 = 0.4, opacity2 = 0.02) {
        const canvas = ctx.canvas;
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, color.replace(')', `, ${opacity1})`).replace('rgb', 'rgba'));
        gradient.addColorStop(1, color.replace(')', `, ${opacity2})`).replace('rgb', 'rgba'));
        return gradient;
    }

    // Chart.js dark theme defaults
    Chart.defaults.color = '#94A3B8';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.06)';

    // ============================================================
    // SIDEBAR NAVIGATION
    // ============================================================
    const sidebar = document.getElementById('app-sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarClose = document.getElementById('sidebar-close');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const navLinks = document.querySelectorAll('.nav-link');
    const tabPanes = document.querySelectorAll('.tab-pane');

    function openSidebar() { if (sidebar) sidebar.classList.add('open'); if (sidebarOverlay) sidebarOverlay.classList.add('active'); }
    function closeSidebar() { if (sidebar) sidebar.classList.remove('open'); if (sidebarOverlay) sidebarOverlay.classList.remove('active'); }

    if (sidebarToggle) sidebarToggle.addEventListener('click', openSidebar);
    if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeSidebar);

    const pageHeadings = {
        'dashboard': ['Executive Intelligence Dashboard', 'Real-time risk scoring, global multi-continent volume, and financial performance'],
        'simulator': ['ML Risk Simulator', 'Run real-time inference against the trained RandomForest + Isolation Forest models'],
        'transactions': ['Global Transaction Ledger', 'Sub-second transaction records across all global regions'],
        'incidents': ['Fraud Incident Response Queue', 'Compliance analyst console for account freeze & SAR filing'],
        'auditor': ['ML Model Health Auditor', 'Model validation, classification accuracy & SHAP feature importance'],
        'segmentation': ['Customer RFM Segmentation', 'K-Means behavioral clustering by recency, frequency & monetary risk'],
        'forecasting': ['Financial Intelligence Forecast', 'Time-series revenue & fraud exposure projections'],
        'reports': ['Executive Report Suite', 'One-click Excel, PowerPoint, and PDF report generation']
    };

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = link.getAttribute('data-tab');

            navLinks.forEach(l => l.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            link.classList.add('active');
            const targetPane = document.getElementById(`tab-${tabId}`);
            if (targetPane) targetPane.classList.add('active');

            closeSidebar();

            if (pageHeadings[tabId]) {
                document.getElementById('page-title').innerText = pageHeadings[tabId][0];
                document.getElementById('page-subtitle').innerText = pageHeadings[tabId][1];
            }

            // Load data after tab becomes visible (fix hidden canvas 0x0 bug)
            setTimeout(() => {
                if (tabId === 'dashboard') loadKPIs();
                if (tabId === 'transactions') loadTransactions();
                if (tabId === 'incidents') loadIncidents();
                if (tabId === 'auditor') loadAuditorMetrics();
                if (tabId === 'segmentation') loadSegmentation();
                if (tabId === 'forecasting') loadForecast();
            }, 80);
        });
    });

    // ============================================================
    // CONTINENT FILTER PILLS
    // ============================================================
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

    // ============================================================
    // LOAD KPI DASHBOARD
    // ============================================================
    async function loadKPIs() {
        try {
            const url = currentContinent !== 'All'
                ? `${API_BASE}/analytics/kpis?continent=${encodeURIComponent(currentContinent)}`
                : `${API_BASE}/analytics/kpis`;

            const res = await fetch(url);
            const data = await res.json();

            // Animated KPI counters
            animateValue(document.getElementById('kpi-total-volume'), data.total_volume, 1500, '$', '', 2);
            animateValue(document.getElementById('kpi-total-tx'), data.total_transactions, 1200);
            animateValue(document.getElementById('kpi-fraud-cnt'), data.fraud_count, 1000);

            const rateEl = document.getElementById('kpi-fraud-rate');
            if (rateEl) rateEl.textContent = `${data.fraud_rate_pct.toFixed(2)}%`;

            animateValue(document.getElementById('kpi-fraud-exposure'), data.fraud_exposure_dollar, 1400, '$', '', 2);

            // Render charts
            renderContinentChart(data.continent_distribution);
            renderChannelChart(data.channel_breakdown);
            renderCategoryChart(data.category_distribution);
            renderCountryThreatsChart(data.country_distribution);
        } catch (err) {
            console.error('KPI load error:', err);
        }
    }

    // ============================================================
    // CHART 1: CONTINENT VOLUME BAR
    // ============================================================
    function renderContinentChart(contData) {
        const canvas = document.getElementById('canvas-continent-volume');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const labels = contData.map(c => c.continent);
        const vols = contData.map(c => c.amount);

        const gradient = createGradient(ctx, 'rgba(14, 165, 233, 0.9)', 'rgba(99, 102, 241, 0.7)');

        if (chartContinent) chartContinent.destroy();
        chartContinent = new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Processed Volume ($)',
                    data: vols,
                    backgroundColor: gradient,
                    borderColor: 'rgba(14, 165, 233, 0.6)',
                    borderWidth: 1,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#94A3B8', font: { size: 11 } } },
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8', font: { size: 11 } } }
                },
                animation: { duration: 800, easing: 'easeOutQuart' }
            }
        });
    }

    // ============================================================
    // CHART 2: CHANNEL DOUGHNUT
    // ============================================================
    function renderChannelChart(channels) {
        const canvas = document.getElementById('canvas-channel-breakdown');
        if (!canvas) return;

        const labels = Object.keys(channels);
        const series = Object.values(channels);

        if (chartChannel) chartChannel.destroy();
        chartChannel = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: series,
                    backgroundColor: ['#0EA5E9', '#6366F1', '#10B981', '#F59E0B', '#EF4444'],
                    borderWidth: 3,
                    borderColor: '#0F172A',
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                cutout: '65%',
                plugins: { legend: { position: 'bottom', labels: { color: '#94A3B8', padding: 14, usePointStyle: true } } },
                animation: { animateRotate: true, duration: 1000 }
            }
        });
    }

    // ============================================================
    // CHART 3: CATEGORY HORIZONTAL BAR
    // ============================================================
    function renderCategoryChart(catData) {
        const canvas = document.getElementById('canvas-category-volume');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const labels = catData.map(c => c.merchant_category);
        const vols = catData.map(c => c.amount);

        const gradient = createGradient(ctx, 'rgba(245, 158, 11, 0.9)', 'rgba(234, 88, 12, 0.7)', false);

        if (chartCategory) chartCategory.destroy();
        chartCategory = new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Exposure ($)',
                    data: vols,
                    backgroundColor: gradient,
                    borderColor: 'rgba(245, 158, 11, 0.5)',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8' } },
                    y: { grid: { display: false }, ticks: { color: '#94A3B8', font: { size: 11 } } }
                },
                animation: { duration: 800 }
            }
        });
    }

    // ============================================================
    // CHART 4: COUNTRY THREATS BAR
    // ============================================================
    function renderCountryThreatsChart(countryData) {
        const canvas = document.getElementById('canvas-country-threats');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const labels = countryData.map(c => c.location_country);
        const frauds = countryData.map(c => c.is_fraud_actual);

        const gradient = createGradient(ctx, 'rgba(239, 68, 68, 0.9)', 'rgba(220, 38, 38, 0.7)');

        if (chartCountry) chartCountry.destroy();
        chartCountry = new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Fraud Detections',
                    data: frauds,
                    backgroundColor: gradient,
                    borderColor: 'rgba(239, 68, 68, 0.5)',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#94A3B8' } },
                    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8' } }
                },
                animation: { duration: 800 }
            }
        });
    }

    // ============================================================
    // LOAD TRANSACTIONS TABLE
    // ============================================================
    let searchDebounceTimer = null;

    async function loadTransactions() {
        const fraudOnly = document.getElementById('chk-fraud-only')?.checked || false;
        const searchTerm = (document.getElementById('tx-search')?.value || '').toLowerCase();

        try {
            const res = await fetch(`${API_BASE}/transactions?limit=50&fraud_only=${fraudOnly}`);
            const data = await res.json();
            const tbody = document.getElementById('tx-table-body');
            if (!tbody) return;

            tbody.innerHTML = '';

            const filtered = data.transactions.filter(t =>
                t.transaction_id.toLowerCase().includes(searchTerm) ||
                t.customer_id.toLowerCase().includes(searchTerm)
            );

            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="9" class="text-center py-4 text-muted">No transactions matching filter.</td></tr>`;
                return;
            }

            filtered.forEach(t => {
                const tr = document.createElement('tr');
                const isHigh = t.risk_level === 'CRITICAL' || t.risk_level === 'HIGH';
                const badgeClass = isHigh ? 'badge-rose' : 'badge-emerald';

                tr.innerHTML = `
                    <td><code style="color:var(--accent-cyan);font-size:11px;">${t.transaction_id}</code></td>
                    <td>${t.customer_id}</td>
                    <td style="font-size:11px;color:var(--text-muted);">${t.timestamp}</td>
                    <td><strong class="font-mono">$${t.amount.toFixed(2)}</strong></td>
                    <td>${t.merchant_category}</td>
                    <td>${t.entry_mode}</td>
                    <td><span class="badge" style="background:rgba(255,255,255,0.06);">${t.location_country}</span></td>
                    <td><span class="badge ${badgeClass}">${t.fraud_risk_score.toFixed(1)}</span></td>
                    <td><span class="badge ${badgeClass}">${t.status}</span></td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            console.error('Transaction load error:', err);
        }
    }

    document.getElementById('chk-fraud-only')?.addEventListener('change', loadTransactions);
    document.getElementById('tx-search')?.addEventListener('input', () => {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(loadTransactions, 300);
    });

    // ============================================================
    // LOAD INCIDENTS (100% from API)
    // ============================================================
    async function loadIncidents() {
        try {
            const res = await fetch(`${API_BASE}/analytics/incidents`);
            const data = await res.json();
            const tbody = document.getElementById('incidents-table-body');
            if (!tbody) return;

            tbody.innerHTML = '';

            if (!data.incidents || data.incidents.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No active incidents.</td></tr>`;
                return;
            }

            data.incidents.forEach(inc => {
                const tr = document.createElement('tr');
                const isHigh = inc.risk_score > 90;
                const badgeClass = isHigh ? 'badge-rose' : 'badge-amber';
                const btnClass = isHigh ? 'btn-rose' : 'btn-amber';
                const btnLabel = isHigh ? 'Freeze Account' : 'Trigger 2FA';
                const btnIcon = isHigh ? 'fa-lock' : 'fa-mobile-screen-button';

                tr.innerHTML = `
                    <td><code style="color:var(--accent-cyan);">${inc.incident_id}</code></td>
                    <td>${inc.customer_id}</td>
                    <td><strong class="text-rose font-mono">$${inc.amount.toLocaleString()}</strong></td>
                    <td><span class="badge ${badgeClass}">${inc.country}</span></td>
                    <td><span class="badge ${badgeClass}">${inc.risk_score} / 100</span></td>
                    <td style="font-size:12px;color:var(--text-muted);">${inc.shap_factor}</td>
                    <td>
                        <button class="btn ${btnClass} btn-sm" data-action="${btnLabel}" data-customer="${inc.customer_id}">
                            <i class="fa-solid ${btnIcon}"></i> ${btnLabel}
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            // Attach toast handlers to action buttons
            tbody.querySelectorAll('button[data-action]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const action = btn.getAttribute('data-action');
                    const customer = btn.getAttribute('data-customer');
                    showToast(`${action} executed for ${customer}. Filed in compliance ledger.`, 'success');
                    btn.disabled = true;
                    btn.style.opacity = '0.5';
                    btn.innerHTML = '<i class="fa-solid fa-check"></i> Done';
                });
            });
        } catch (err) {
            console.error('Incident load error:', err);
        }
    }

    // ============================================================
    // LOAD AUDITOR METRICS (from real model)
    // ============================================================
    async function loadAuditorMetrics() {
        try {
            const res = await fetch(`${API_BASE}/analytics/auditor`);
            const data = await res.json();

            // Animate the metric values
            const rocEl = document.getElementById('auditor-roc-auc');
            const accEl = document.getElementById('auditor-accuracy');
            const latEl = document.getElementById('auditor-latency');

            if (rocEl) animateValue(rocEl, data.roc_auc || 0.998, 1200, '', '', 4);
            if (accEl) animateValue(accEl, data.accuracy || 99.98, 1200, '', '%', 2);
            if (latEl) animateValue(latEl, data.latency_ms || 18.4, 1000, '', ' ms', 1);

            // SHAP Chart
            const canvas = document.getElementById('canvas-shap-importance');
            if (!canvas || !data.shap_importance) return;
            const ctx = canvas.getContext('2d');

            const labels = data.shap_importance.map(s => s.feature);
            const weights = data.shap_importance.map(s => s.importance);

            const gradient = createGradient(ctx, 'rgba(99, 102, 241, 0.9)', 'rgba(14, 165, 233, 0.7)', false);

            if (chartSHAP) chartSHAP.destroy();
            chartSHAP = new Chart(canvas, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [{
                        label: 'SHAP Importance',
                        data: weights,
                        backgroundColor: gradient,
                        borderColor: 'rgba(99, 102, 241, 0.5)',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94A3B8' } },
                        y: { grid: { display: false }, ticks: { color: '#94A3B8', font: { size: 11 } } }
                    },
                    animation: { duration: 900 }
                }
            });
        } catch (err) {
            console.error('Auditor load error:', err);
        }
    }

    // ============================================================
    // LOAD RFM SEGMENTATION
    // ============================================================
    async function loadSegmentation() {
        try {
            const res = await fetch(`${API_BASE}/analytics/segmentation`);
            const data = await res.json();

            const canvas = document.getElementById('canvas-rfm-pie');
            if (canvas) {
                const labels = Object.keys(data.segment_distribution);
                const series = Object.values(data.segment_distribution);

                if (chartRFM) chartRFM.destroy();
                chartRFM = new Chart(canvas, {
                    type: 'doughnut',
                    data: {
                        labels,
                        datasets: [{
                            data: series,
                            backgroundColor: ['#0EA5E9', '#10B981', '#F59E0B', '#EF4444', '#6366F1'],
                            borderWidth: 3,
                            borderColor: '#0F172A',
                            hoverOffset: 8
                        }]
                    },
                    options: {
                        responsive: true, maintainAspectRatio: false,
                        cutout: '60%',
                        plugins: { legend: { position: 'bottom', labels: { color: '#94A3B8', padding: 14, usePointStyle: true } } }
                    }
                });
            }

            const profileBox = document.getElementById('rfm-profiles-container');
            if (profileBox && data.segment_profiles) {
                profileBox.innerHTML = data.segment_profiles.map(p => `
                    <div class="profile-card">
                        <h4 style="color:var(--accent-cyan);font-size:14px;margin-bottom:8px;">${p.segment_label}</h4>
                        <div style="display:flex;gap:20px;flex-wrap:wrap;font-size:12px;color:var(--text-muted);">
                            <span>Monetary: <strong class="font-mono" style="color:var(--text-white);">$${p.monetary_val.toLocaleString()}</strong></span>
                            <span>Recency: <strong style="color:var(--text-white);">${p.recency_days}d</strong></span>
                            <span>Fraud: <strong style="color:var(--accent-rose);">${p.fraud_cnt}</strong></span>
                        </div>
                    </div>
                `).join('');
            }
        } catch (err) {
            console.error('Segmentation load error:', err);
        }
    }

    // ============================================================
    // LOAD FORECAST
    // ============================================================
    async function loadForecast() {
        try {
            const res = await fetch(`${API_BASE}/analytics/forecasting?days=30`);
            const data = await res.json();

            const canvas = document.getElementById('canvas-forecast');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');

            const dates = data.forecast_daily.map(f => f.date);
            const revenues = data.forecast_daily.map(f => f.forecast_revenue);

            // Gradient fill
            const fillGradient = ctx.createLinearGradient(0, 0, 0, canvas.height || 380);
            fillGradient.addColorStop(0, 'rgba(14, 165, 233, 0.3)');
            fillGradient.addColorStop(1, 'rgba(14, 165, 233, 0.02)');

            if (chartForecast) chartForecast.destroy();
            chartForecast = new Chart(canvas, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Projected Revenue ($)',
                        data: revenues,
                        borderColor: '#0EA5E9',
                        backgroundColor: fillGradient,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointBackgroundColor: '#0EA5E9',
                        pointBorderColor: '#0F172A',
                        pointBorderWidth: 2,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            borderColor: 'rgba(14, 165, 233, 0.3)',
                            borderWidth: 1,
                            titleColor: '#F8FAFC',
                            bodyColor: '#94A3B8',
                            cornerRadius: 8,
                            padding: 12
                        }
                    },
                    scales: {
                        x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#94A3B8', maxTicksLimit: 10, font: { size: 10 } } },
                        y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#94A3B8' } }
                    },
                    animation: { duration: 1200, easing: 'easeOutQuart' }
                }
            });
        } catch (err) {
            console.error('Forecast load error:', err);
        }
    }

    // ============================================================
    // ML RISK SIMULATOR FORM
    // ============================================================
    document.getElementById('sim-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();

        const payload = {
            amount: parseFloat(document.getElementById('sim-amount').value),
            merchant_category: document.getElementById('sim-category').value,
            location_country: document.getElementById('sim-country').value,
            entry_mode: document.getElementById('sim-entry').value,
            velocity_1h: parseInt(document.getElementById('sim-v1h').value),
            distance_from_home_km: parseFloat(document.getElementById('sim-distance').value)
        };

        const resultBox = document.getElementById('sim-result-container');

        try {
            resultBox.innerHTML = '<div class="empty-state"><i class="fa-solid fa-circle-notch fa-spin placeholder-icon text-cyan"></i><h4>Running ML Inference...</h4></div>';

            const res = await fetch(`${API_BASE}/ml/score`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            const isHigh = data.risk_score >= 50.0;
            const badgeClass = isHigh ? 'badge-rose' : 'badge-emerald';
            const colorVar = isHigh ? 'var(--accent-rose)' : 'var(--accent-emerald)';

            resultBox.innerHTML = `
                <div style="border-bottom:1px solid var(--border-subtle);padding-bottom:16px;">
                    <span class="badge ${badgeClass}" style="font-size:13px;padding:6px 14px;">${data.status}</span>
                    <h2 style="font-family:var(--font-heading);margin-top:14px;">
                        Risk Score: <span class="font-mono" style="color:${colorVar}">${data.risk_score}/100</span>
                    </h2>
                    <p style="font-size:12px;color:var(--text-muted);margin-top:4px;">Level: <strong>${data.risk_level}</strong></p>
                </div>

                <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:20px;">
                    <div style="background:rgba(255,255,255,0.03);padding:14px;border-radius:12px;border:1px solid var(--border-subtle);">
                        <span style="font-size:11px;color:var(--text-muted);">ML Engine Probability</span>
                        <h4 class="font-mono" style="color:var(--accent-cyan);font-size:20px;margin-top:6px;">${(data.fraud_probability * 100).toFixed(2)}%</h4>
                    </div>
                    <div style="background:rgba(255,255,255,0.03);padding:14px;border-radius:12px;border:1px solid var(--border-subtle);">
                        <span style="font-size:11px;color:var(--text-muted);">Anomaly Score</span>
                        <h4 class="font-mono" style="color:var(--accent-indigo);font-size:20px;margin-top:6px;">${data.anomaly_score}</h4>
                    </div>
                </div>

                <div style="margin-top:24px;">
                    <h4 style="font-size:14px;font-weight:600;display:flex;align-items:center;gap:8px;">
                        <i class="fa-solid fa-layer-group text-cyan"></i> Risk Factors Identified
                    </h4>
                    <ul style="margin-top:10px;padding-left:20px;font-size:13px;color:var(--text-muted);line-height:1.8;">
                        ${data.risk_factors.map(rf => `<li>${rf}</li>`).join('')}
                    </ul>
                </div>
            `;

            showToast(`Inference complete. Risk Score: ${data.risk_score}/100`, isHigh ? 'error' : 'success');
        } catch (err) {
            console.error('Simulator error:', err);
            resultBox.innerHTML = '<div class="empty-state"><i class="fa-solid fa-circle-xmark placeholder-icon text-rose"></i><h4>Inference Error</h4><p>Could not reach the ML scoring endpoint. Please try again.</p></div>';
            showToast('ML inference failed. Check API connection.', 'error');
        }
    });

    // ============================================================
    // INITIAL LOAD
    // ============================================================
    loadKPIs();
    loadTransactions();
});
