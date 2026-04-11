let total = parseFloat(localStorage.getItem("savings_total")) || 0;
let goal = parseFloat(localStorage.getItem("savings_goal")) || 0;
let history = JSON.parse(localStorage.getItem("savings_history")) || [];
let lastDeleted = null;
let savingsChart;
let chartPeriodDays = 7; // default period

// Calendar state
let calYear, calMonth;
const now = new Date();
calYear = now.getFullYear();
calMonth = now.getMonth();

window.onload = () => {
    history = history.map(item => typeof item === 'string' ? { 
        text: item, date: new Date().toLocaleDateString('fr-MA'), val: parseFloat(item.replace(/[^-0.9.]/g, '')) 
    } : item);
    initChart();
    renderCalDayNames();

    // Wire period buttons
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            chartPeriodDays = parseInt(btn.dataset.days);
            updateChart();
        });
    });

    updateUI();
};

function initChart() {
    const ctx = document.getElementById('savingsChart').getContext('2d');
    savingsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointBackgroundColor: '#38bdf8',
                spanGaps: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
                legend: { display: false },
                tooltip: { enabled: true, callbacks: { label: (c) => c.parsed.y + ' MAD' } }
            },
            scales: {
                x: {
                    display: true,
                    ticks: {
                        color: '#64748b',
                        font: { size: 9 },
                        maxTicksLimit: 8,
                        maxRotation: 0
                    },
                    grid: { display: false }
                },
                y: { 
                    beginAtZero: true,
                    max: goal > 0 ? goal : undefined,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#64748b', font: { size: 9 } }
                }
            }
        }
    });
}

function getISOFromItem(item) {
    if (item.isoDate) return item.isoDate;
    if (item.date) {
        const parts = item.date.split(/[\/ ]/);
        if (parts.length >= 2) {
            const day   = parts[0].padStart(2, '0');
            const month = parts[1].padStart(2, '0');
            const year  = parts[2] && parts[2].length === 4 ? parts[2] : new Date().getFullYear();
            return `${year}-${month}-${day}`;
        }
    }
    return new Date().toISOString().slice(0, 10);
}

function updateChart() {
    if (!savingsChart) return;

    const todayISO = new Date().toISOString().slice(0, 10);

    // Build daily delta map for ALL history
    const dayDeltas = {};
    history.forEach(item => {
        const iso = getISOFromItem(item);
        dayDeltas[iso] = (dayDeltas[iso] || 0) + item.val;
    });

    // Find earliest date across all history
    const allHistDates = Object.keys(dayDeltas).sort();
    const earliestISO  = allHistDates[0] || todayISO;

    // Determine window start
    let windowStart;
    if (chartPeriodDays === 0) {
        windowStart = earliestISO; // All
    } else {
        const d = new Date();
        d.setDate(d.getDate() - (chartPeriodDays - 1));
        windowStart = d.toISOString().slice(0, 10);
    }

    // Build full list of days from windowStart → today
    const days = [];
    const cur = new Date(windowStart);
    const end = new Date(todayISO);
    while (cur <= end) {
        days.push(cur.toISOString().slice(0, 10));
        cur.setDate(cur.getDate() + 1);
    }

    // Reconstruct balance for each day in window
    // snapshot(d) = total - sum of vals on days AFTER d
    const allDates = Object.keys(dayDeltas).sort();

    const labels = [];
    const data   = [];

    days.forEach(d => {
        let snap = total;
        allDates.forEach(d2 => { if (d2 > d) snap -= dayDeltas[d2]; });
        // Only include days that are at or after the earliest transaction,
        // or today (so the line always ends at present)
        if (d >= earliestISO || d === todayISO) {
            // Format label
            const dt = new Date(d);
            const label = dt.toLocaleDateString('fr-MA', { day: '2-digit', month: '2-digit' });
            labels.push(label);
            data.push(snap);
        } else {
            labels.push('');
            data.push(null);
        }
    });

    savingsChart.data.labels = labels;
    savingsChart.data.datasets[0].data = data;
    savingsChart.options.scales.y.max = goal > 0 ? goal : undefined;
    savingsChart.options.scales.x.display = days.length <= 60;
    savingsChart.update();
}

function modifySavings(type) {
    const input = document.getElementById("amountInput");
    const amount = parseFloat(input.value);
    if (isNaN(amount) || amount <= 0) return;

    const change = type === 'add' ? amount : -amount;
    total += change;
    triggerBackgroundEffect(type);

    const btn = document.querySelector(`.${type}-btn`);
    btn.classList.add('btn-active-press');
    setTimeout(() => btn.classList.remove('btn-active-press'), 200);

    const nowDate = new Date();
    const dateStr = nowDate.toLocaleDateString('fr-MA', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
    // Store ISO date for calendar lookup (YYYY-MM-DD)
    const isoDate = nowDate.toISOString().slice(0, 10);

    history.unshift({ text: `${type === 'add' ? '+' : '-'} ${amount} MAD`, val: change, date: dateStr, isoDate });
    if (history.length > 50) history.pop();
    input.value = "";
    saveData();
    updateUI();
}

function triggerBackgroundEffect(type) {
    const overlay = document.getElementById("bg-overlay");
    overlay.className = type === 'add' ? 'burst-add' : 'burst-sub';
    setTimeout(() => overlay.className = '', 700);
}

function deleteTransaction(index) {
    lastDeleted = { item: history[index], index: index };
    total -= history[index].val;
    history.splice(index, 1);
    saveData();
    updateUI();
    showUndoNotification();
}

function undoDelete() {
    if (!lastDeleted) return;
    total += lastDeleted.item.val;
    history.splice(lastDeleted.index, 0, lastDeleted.item);
    lastDeleted = null;
    hideUndoNotification();
    saveData();
    updateUI();
}

function updateUI() {
    document.getElementById("displaySavings").innerText = `${total.toLocaleString()} MAD`;
    document.getElementById("goalValue").innerText = goal.toLocaleString();
    const remaining = Math.max(goal - total, 0);
    document.getElementById("displayRemaining").innerText = `${remaining.toLocaleString()} MAD left`;
    if (document.getElementById("statGoal"))     document.getElementById("statGoal").innerText = `${goal.toLocaleString()} MAD`;
    if (document.getElementById("statRemaining")) document.getElementById("statRemaining").innerText = `${remaining.toLocaleString()} MAD`;
    const percent = goal > 0 ? (total / goal) * 100 : 0;
    document.getElementById("progressFill").style.width = `${Math.min(percent, 100)}%`;
    document.getElementById("progressText").innerText = `${Math.round(percent)}%`;

    document.getElementById("historyList").innerHTML = history.map((item, i) => `
        <li>
            <div class="history-item-left">
                <span>${item.text}</span>
                <span style="font-size: 0.7rem; color: #64748b;">${item.date}</span>
            </div>
            <button class="delete-btn" onclick="deleteTransaction(${i})">×</button>
        </li>
    `).join("");
    updateChart();
    renderCalendar();
}

function updateGoal() {
    const goalVal = parseFloat(document.getElementById("goalInput").value);
    if (!isNaN(goalVal)) { goal = goalVal; saveData(); updateUI(); document.getElementById("goalInput").value = ""; }
}

function saveData() {
    localStorage.setItem("savings_total", total);
    localStorage.setItem("savings_goal", goal);
    localStorage.setItem("savings_history", JSON.stringify(history));
}

function showUndoNotification() {
    let el = document.getElementById("undoToast") || document.createElement("div");
    el.id = "undoToast"; document.body.appendChild(el);
    el.innerHTML = `Deleted. <button onclick="undoDelete()" style="background:#38bdf8;border:none;padding:5px;border-radius:5px;cursor:pointer;font-weight:bold">Undo</button>`;
    el.className = "show";
    setTimeout(() => { if(el.className === "show") el.className = ""; }, 5000);
}

function hideUndoNotification() { document.getElementById("undoToast").className = ""; }
function clearAll() { if (confirm("Clear all?")) { localStorage.clear(); location.reload(); } }

document.addEventListener('mousemove', (e) => {
    const buttons = document.querySelectorAll('.add-btn, .sub-btn, .goal-btn');
    buttons.forEach(btn => {
        const rect = btn.getBoundingClientRect();
        const distance = Math.sqrt(Math.pow(e.clientX - (rect.left + rect.width / 2), 2) + Math.pow(e.clientY - (rect.top + rect.height / 2), 2));
        const intensity = Math.max(0, 1 - (distance / 200));
        btn.style.transform = `scale(${1 + (0.1 * intensity)})`;
    });
});

// ─── CALENDAR ────────────────────────────────────────────────────────────────

function renderCalDayNames() {
    const names = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];
    document.getElementById('calDayNames').innerHTML = names.map(n =>
        `<div class="cal-day-name">${n}</div>`
    ).join('');
}

function changeMonth(dir) {
    calMonth += dir;
    if (calMonth > 11) { calMonth = 0; calYear++; }
    if (calMonth < 0)  { calMonth = 11; calYear--; }
    renderCalendar();
}

function renderCalendar() {
    const monthNames = ['January','February','March','April','May','June',
                        'July','August','September','October','November','December'];
    document.getElementById('calTitle').textContent = `${monthNames[calMonth]} ${calYear}`;

    const todayISO = new Date().toISOString().slice(0, 10);

    // ── Build daily delta map from history ──────────────────────────────────
    // Each history item may have an isoDate (new items) or just a `date`
    // string in fr-MA format like "12/04 14:30". We'll try to parse both.
    const dayDeltas = {}; // isoDate -> net change that day

    history.forEach(item => {
        let iso = item.isoDate || null;

        // Fallback: try to parse the fr-MA date string "DD/MM HH:MM" or "DD/MM/YYYY"
        if (!iso && item.date) {
            const parts = item.date.split(/[\/ ]/);
            if (parts.length >= 2) {
                const day   = parts[0].padStart(2, '0');
                const month = parts[1].padStart(2, '0');
                // If year is present use it, otherwise assume current year
                const year  = parts[2] && parts[2].length === 4 ? parts[2] : new Date().getFullYear();
                iso = `${year}-${month}-${day}`;
            }
        }

        if (!iso) iso = todayISO; // last-resort fallback
        dayDeltas[iso] = (dayDeltas[iso] || 0) + item.val;
    });

    // ── Reconstruct end-of-day balance snapshots ─────────────────────────────
    // total = current balance = sum of ALL history vals
    // snapshot(d) = total minus sum of vals on dates STRICTLY after d
    const allDates = Object.keys(dayDeltas).sort();
    const snapshots = {};
    allDates.forEach(d => {
        let snap = total;
        allDates.forEach(d2 => { if (d2 > d) snap -= dayDeltas[d2]; });
        snapshots[d] = snap;
    });
    // Always show today's snapshot as current total
    if (history.length > 0 || total !== 0) {
        snapshots[todayISO] = snapshots[todayISO] !== undefined ? snapshots[todayISO] : total;
    }

    // ── Render cells ─────────────────────────────────────────────────────────
    const firstDow = new Date(calYear, calMonth, 1).getDay(); // 0=Sun
    const startOffset = (firstDow + 6) % 7; // Monday-based
    const daysInMonth = new Date(calYear, calMonth + 1, 0).getDate();

    let html = '';
    for (let i = 0; i < startOffset; i++) html += '<div class="cal-cell empty"></div>';

    for (let d = 1; d <= daysInMonth; d++) {
        const iso = `${calYear}-${String(calMonth + 1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
        const isToday = iso === todayISO;
        const snap    = snapshots[iso];
        const delta   = dayDeltas[iso];

        let totalHtml = '', deltaHtml = '';

        if (snap !== undefined) {
            const cls = snap > 0 ? 'pos' : snap < 0 ? 'neg' : 'zero';
            totalHtml = `<div class="cal-snap ${cls}">${Math.round(snap)}</div>`;
        }
        if (delta !== undefined) {
            const cls  = delta >= 0 ? 'delta-pos' : 'delta-neg';
            const sign = delta > 0 ? '+' : '';
            deltaHtml = `<div class="cal-delta ${cls}">${sign}${Math.round(delta)}</div>`;
        }

        html += `
            <div class="cal-cell${isToday ? ' today' : ''}">
                <div class="cal-num">${d}</div>
                ${totalHtml}
                ${deltaHtml}
            </div>`;
    }

    document.getElementById('calGrid').innerHTML = html;
}