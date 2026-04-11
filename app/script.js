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

// Get local date as YYYY-MM-DD (avoids UTC timezone shift from toISOString)
function localISO(date) {
    const d = date || new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
}

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
    return localISO();
}

// Build { isoDate -> netDelta } and { isoDate -> balanceSnapshot } for all history
function buildDayMaps() {
    const todayISO = localISO();
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
        // snapshot(d) = total - sum of deltas strictly after d
        // suffixSum currently holds sum of deltas for days AFTER allDates[i]
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

// Enumerate all days between two ISO strings (inclusive), using local time
function dayRange(fromISO, toISO) {
    const days = [];
    // Parse as local midnight by splitting manually
    const [fy, fm, fd] = fromISO.split('-').map(Number);
    const [ty, tm, td] = toISO.split('-').map(Number);
    const cur = new Date(fy, fm - 1, fd);
    const end = new Date(ty, tm - 1, td);
    while (cur <= end) {
        const y = cur.getFullYear();
        const m = String(cur.getMonth() + 1).padStart(2, '0');
        const d = String(cur.getDate()).padStart(2, '0');
        days.push(`${y}-${m}-${d}`);
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
                tension: 0.3,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: [],
                pointBorderColor: [],
                pointBorderWidth: 2,
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
                        label: ctx => {
                            const raw = ctx.raw;
                            const delta = raw._delta;
                            const sign = delta > 0 ? '+' : '';
                            return [
                                ' Balance: ' + raw.y.toLocaleString() + ' MAD',
                                ' Change:  ' + sign + delta.toLocaleString() + ' MAD'
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    ticks: {
                        color: '#64748b',
                        font: { size: 9 },
                        maxTicksLimit: 14,
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

    // Build per-transaction points, sorted oldest→newest
    const sorted = [...history].reverse(); // history is newest-first, so reverse = oldest-first

    // Recompute running balance for each transaction from scratch
    // We know the final total; walk forward computing balance after each tx
    // sorted[0] is oldest. balance after sorted[i] = sum of sorted[0..i].val
    // But total = sum of all, so balance after sorted[i] = total - sum of sorted[i+1..end].val
    // Easier: just accumulate forward from 0
    let running = 0;
    const points = sorted.map(item => {
        running += item.val;
        return { val: item.val, balance: running, item };
    });

    // Correction: running may differ from total due to floating point or deleted items
    // Rescale so last point = total
    if (points.length > 0) {
        const diff = total - points[points.length - 1].balance;
        if (Math.abs(diff) > 0.001) {
            points[points.length - 1].balance = total;
        }
    }

    const labels = [];
    const data = [];
    const pointColors = [];
    const pointBorderColors = [];

    points.forEach(p => {
        const dt = new Date((p.item.isoDate || localISO()) + 'T00:00:00');
        labels.push(dt.toLocaleDateString('fr-MA', { day: '2-digit', month: '2-digit' }));
        const color = p.val >= 0 ? '#10b981' : '#ef4444';
        pointColors.push(color);
        pointBorderColors.push(color);
        // Attach delta to data point for tooltip
        data.push({ x: labels[labels.length - 1], y: p.balance, _delta: p.val });
    });

    savingsChart.data.labels = labels;
    savingsChart.data.datasets[0].data = data;
    savingsChart.data.datasets[0].pointBackgroundColor = pointColors;
    savingsChart.data.datasets[0].pointBorderColor = pointBorderColors;
    savingsChart.options.scales.y.max = goal > 0 ? goal : undefined;
    savingsChart.options.parsing = { xAxisKey: 'x', yAxisKey: 'y' };
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
    const isoDate = localISO(nowDate);

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

    const todayISO = localISO();
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

        // Determine color class based on delta
        let colorClass = '';
        if (delta !== undefined) {
            colorClass = delta >= 0 ? ' has-add' : ' has-sub';
        }

        let snapHtml = '', deltaHtml = '';
        if (snap !== undefined) {
            const cls = snap > 0 ? 'pos' : snap < 0 ? 'neg' : 'zero';
            snapHtml = `<div class="cal-snap ${cls}">${Math.round(snap).toLocaleString()}</div>`;
        }
        if (delta !== undefined) {
            const cls  = delta >= 0 ? 'delta-pos' : 'delta-neg';
            const sign = delta > 0 ? '+' : '';
            deltaHtml = `<div class="cal-delta ${cls}">${sign}${Math.round(delta).toLocaleString()}</div>`;
        }

        html += `<div class="cal-cell${isToday ? ' today' : ''}${colorClass}" onclick="onCalCellClick('${iso}', this)" title="${iso}">
            <div class="cal-num">${d}</div>
            ${snapHtml}${deltaHtml}
        </div>`;
    }

    document.getElementById('calGrid').innerHTML = html;
}

let selectedCalISO = null;

function onCalCellClick(iso, el) {
    // Deselect previous
    document.querySelectorAll('.cal-cell.selected').forEach(c => c.classList.remove('selected'));
    if (selectedCalISO === iso) {
        selectedCalISO = null;
        return;
    }
    selectedCalISO = iso;
    el.classList.add('selected');
}
