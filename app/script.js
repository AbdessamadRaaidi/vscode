let total = parseFloat(localStorage.getItem("savings_total")) || 0;
let goal  = parseFloat(localStorage.getItem("savings_goal"))  || 0;
let history = JSON.parse(localStorage.getItem("savings_history")) || [];
let lastDeleted = null;
let savingsChart;

// Calendar state
let calYear, calMonth;
const _now = new Date();
calYear  = _now.getFullYear();
calMonth = _now.getMonth();

window.onload = () => {
    history = history.map(item => typeof item === 'string' ? {
        text: item,
        date: new Date().toLocaleDateString('fr-MA'),
        val: parseFloat(item.replace(/[^-0-9.]/g, ''))
    } : item);
    initChart();
    renderCalDayNames();
    updateUI();
};

// ─── HELPERS ──────────────────────────────────────────────────────────────────

function getISOFromItem(item) {
    if (item.isoDate) return item.isoDate;
    if (item.date) {
        const parts = item.date.split(/[\/ ]/);
        if (parts.length >= 2) {
            const day   = parts[0].padStart(2, '0');
            const month = parts[1].padStart(2, '0');
            const year  = (parts[2] && parts[2].length === 4) ? parts[2] : new Date().getFullYear();
            return `${year}-${month}-${day}`;
        }
    }
    return new Date().toISOString().slice(0, 10);
}

// Build { isoDate -> netDelta } and { isoDate -> balanceSnapshot } for all history
function buildDayMaps() {
    const todayISO = new Date().toISOString().slice(0, 10);
    const dayDeltas = {};
    history.forEach(item => {
        const iso = getISOFromItem(item);
        dayDeltas[iso] = (dayDeltas[iso] || 0) + item.val;
    });
    // snapshot(d) = balance at end of day d
    // Walk dates descending, subtracting deltas from total as we go back in time
    const allDates = Object.keys(dayDeltas).sort();
    const snapshots = {};
    let suffixSum = 0;
    for (let i = allDates.length - 1; i >= 0; i--) {
        snapshots[allDates[i]] = total - suffixSum;
        suffixSum += dayDeltas[allDates[i]];
    }
    if (snapshots[todayISO] === undefined && total !== 0) {
        // Today has no transaction; find the most recent snapshot to carry forward
        let latest = null;
        for (let i = allDates.length - 1; i >= 0; i--) {
            if (allDates[i] <= todayISO) { latest = snapshots[allDates[i]]; break; }
        }
        if (latest !== null) snapshots[todayISO] = latest;
    }
    if (total !== 0 && snapshots[todayISO] === undefined) {
        snapshots[todayISO] = total;
    }
    return { dayDeltas, snapshots, allDates };
}

// Enumerate all days between two ISO strings (inclusive)
function dayRange(fromISO, toISO) {
    const days = [];
    const cur = new Date(fromISO);
    const end = new Date(toISO);
    while (cur <= end) {
        days.push(cur.toISOString().slice(0, 10));
        cur.setDate(cur.getDate() + 1);
    }
    return days;
}

// ─── CHART ────────────────────────────────────────────────────────────────────

function initChart() {
    const ctx = document.getElementById('savingsChart').getContext('2d');
    savingsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56,189,248,0.08)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 5,
                pointBackgroundColor: '#38bdf8',
                spanGaps: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 300 },
            plugins: {
                legend: { display: false },
                tooltip: {
                    enabled: true,
                    callbacks: {
                        title: ctx => ctx[0].label,
                        label: ctx => ' ' + ctx.parsed.y.toLocaleString() + ' MAD'
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    ticks: {
                        color: '#64748b',
                        font: { size: 9 },
                        maxTicksLimit: 12,
                        maxRotation: 0,
                        autoSkip: true
                    },
                    grid: { color: 'rgba(255,255,255,0.04)' }
                },
                y: {
                    beginAtZero: true,
                    max: goal > 0 ? goal : undefined,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: {
                        color: '#64748b',
                        font: { size: 9 },
                        callback: v => v.toLocaleString()
                    }
                }
            }
        }
    });
}

function updateChart() {
    if (!savingsChart) return;

    const todayISO = new Date().toISOString().slice(0, 10);
    const { snapshots, allDates } = buildDayMaps();

    // Always show all time: from earliest transaction to today
    const fromISO = allDates.length > 0 ? allDates[0] : todayISO;
    const days = dayRange(fromISO, todayISO);

    const labels = [];
    const data   = [];

    const sortedSnaps = allDates
        .filter(d => snapshots[d] !== undefined)
        .map(d => [d, snapshots[d]]);

    let snapIdx = 0;
    let lastSnap = null;

    days.forEach(d => {
        const dt = new Date(d + 'T00:00:00');
        labels.push(dt.toLocaleDateString('fr-MA', { day: '2-digit', month: '2-digit' }));

        while (snapIdx < sortedSnaps.length && sortedSnaps[snapIdx][0] <= d) {
            lastSnap = sortedSnaps[snapIdx][1];
            snapIdx++;
        }

        data.push(snapshots[d] !== undefined ? snapshots[d] : lastSnap);
    });

    savingsChart.data.labels = labels;
    savingsChart.data.datasets[0].data = data;
    savingsChart.options.scales.y.max = goal > 0 ? goal : undefined;
    savingsChart.update();
}

// ─── SAVINGS ACTIONS ──────────────────────────────────────────────────────────

function modifySavings(type) {
    const input  = document.getElementById("amountInput");
    const amount = parseFloat(input.value);
    if (isNaN(amount) || amount <= 0) return;

    const change = type === 'add' ? amount : -amount;
    total += change;
    triggerBackgroundEffect(type);

    const btn = document.querySelector(`.${type}-btn`);
    btn.classList.add('btn-active-press');
    setTimeout(() => btn.classList.remove('btn-active-press'), 200);

    const nowDate = new Date();
    const dateStr = nowDate.toLocaleDateString('fr-MA', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    const isoDate = nowDate.toISOString().slice(0, 10);

    history.unshift({ text: `${type === 'add' ? '+' : '-'} ${amount} MAD`, val: change, date: dateStr, isoDate });
    if (history.length > 200) history.pop();
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
    lastDeleted = { item: history[index], index };
    total -= history[index].val;
    history.splice(index, 1);
    saveData(); updateUI(); showUndoNotification();
}

function undoDelete() {
    if (!lastDeleted) return;
    total += lastDeleted.item.val;
    history.splice(lastDeleted.index, 0, lastDeleted.item);
    lastDeleted = null;
    hideUndoNotification();
    saveData(); updateUI();
}

// ─── UI UPDATE ────────────────────────────────────────────────────────────────

function updateUI() {
    document.getElementById("displaySavings").innerText = `${total.toLocaleString()} MAD`;
    document.getElementById("goalValue").innerText = goal.toLocaleString();
    const remaining = Math.max(goal - total, 0);
    document.getElementById("displayRemaining").innerText = `${remaining.toLocaleString()} MAD left`;
    if (document.getElementById("statGoal"))      document.getElementById("statGoal").innerText      = `${goal.toLocaleString()} MAD`;
    if (document.getElementById("statRemaining")) document.getElementById("statRemaining").innerText = `${remaining.toLocaleString()} MAD`;
    const percent = goal > 0 ? (total / goal) * 100 : 0;
    document.getElementById("progressFill").style.width = `${Math.min(percent, 100)}%`;
    document.getElementById("progressText").innerText   = `${Math.round(percent)}%`;

    document.getElementById("historyList").innerHTML = history.map((item, i) => `
        <li>
            <div class="history-item-left">
                <span>${item.text}</span>
                <span style="font-size:0.7rem;color:#64748b;">${item.date}</span>
            </div>
            <button class="delete-btn" onclick="deleteTransaction(${i})">×</button>
        </li>
    `).join("");

    updateChart();
    renderCalendar();
}

function updateGoal() {
    const v = parseFloat(document.getElementById("goalInput").value);
    if (!isNaN(v)) { goal = v; saveData(); updateUI(); document.getElementById("goalInput").value = ""; }
}

function saveData() {
    localStorage.setItem("savings_total",   total);
    localStorage.setItem("savings_goal",    goal);
    localStorage.setItem("savings_history", JSON.stringify(history));
}

function showUndoNotification() {
    const el = document.getElementById("undoToast");
    el.innerHTML = `Deleted. <button onclick="undoDelete()" style="background:#38bdf8;border:none;padding:5px 10px;border-radius:6px;cursor:pointer;font-weight:bold;color:#000">Undo</button>`;
    el.className = "show";
    setTimeout(() => { if (el.className === "show") el.className = ""; }, 5000);
}
function hideUndoNotification() { document.getElementById("undoToast").className = ""; }
function clearAll() { if (confirm("Clear all?")) { localStorage.clear(); location.reload(); } }

document.addEventListener('mousemove', (e) => {
    document.querySelectorAll('.add-btn, .sub-btn, .goal-btn').forEach(btn => {
        const rect = btn.getBoundingClientRect();
        const dist = Math.sqrt((e.clientX - (rect.left + rect.width/2))**2 + (e.clientY - (rect.top + rect.height/2))**2);
        const intensity = Math.max(0, 1 - dist / 200);
        btn.style.transform = `scale(${1 + 0.1 * intensity})`;
    });
});

// ─── CALENDAR ─────────────────────────────────────────────────────────────────

function renderCalDayNames() {
    document.getElementById('calDayNames').innerHTML =
        ['Mo','Tu','We','Th','Fr','Sa','Su'].map(n => `<div class="cal-day-name">${n}</div>`).join('');
}

function changeMonth(dir) {
    calMonth += dir;
    if (calMonth > 11) { calMonth = 0; calYear++; }
    if (calMonth < 0)  { calMonth = 11; calYear--; }
    renderCalendar();
}

function renderCalendar() {
    const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    document.getElementById('calTitle').textContent = `${monthNames[calMonth]} ${calYear}`;

    const todayISO = new Date().toISOString().slice(0, 10);
    const { dayDeltas, snapshots } = buildDayMaps();

    const firstDow   = new Date(calYear, calMonth, 1).getDay();
    const startOffset = (firstDow + 6) % 7;
    const daysInMonth = new Date(calYear, calMonth + 1, 0).getDate();

    let html = '';
    for (let i = 0; i < startOffset; i++) html += '<div class="cal-cell empty"></div>';

    for (let d = 1; d <= daysInMonth; d++) {
        const iso     = `${calYear}-${String(calMonth+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
        const isToday = iso === todayISO;
        const snap    = snapshots[iso];
        const delta   = dayDeltas[iso];

        let snapHtml = '', deltaHtml = '';
        if (snap !== undefined) {
            const cls = snap > 0 ? 'pos' : snap < 0 ? 'neg' : 'zero';
            snapHtml = `<div class="cal-snap ${cls}">${Math.round(snap)}</div>`;
        }
        if (delta !== undefined) {
            const cls  = delta >= 0 ? 'delta-pos' : 'delta-neg';
            const sign = delta > 0 ? '+' : '';
            deltaHtml = `<div class="cal-delta ${cls}">${sign}${Math.round(delta)}</div>`;
        }

        html += `<div class="cal-cell${isToday ? ' today' : ''}">
            <div class="cal-num">${d}</div>
            ${snapHtml}${deltaHtml}
        </div>`;
    }

    document.getElementById('calGrid').innerHTML = html;
}
