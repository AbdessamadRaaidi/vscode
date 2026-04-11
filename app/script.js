let total = parseFloat(localStorage.getItem("savings_total")) || 0;
let goal = parseFloat(localStorage.getItem("savings_goal")) || 0;
let history = JSON.parse(localStorage.getItem("savings_history")) || [];
let lastDeleted = null;
let savingsChart;

window.onload = () => {
    setupSelectors();
    initChart();
    updateUI();
};

function setupSelectors() {
    const monthSel = document.getElementById("monthSelect");
    const yearSel = document.getElementById("yearSelect");
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    months.forEach((m, i) => monthSel.add(new Option(m, i)));
    for (let y = 2025; y <= 2034; y++) yearSel.add(new Option(y, y));
    monthSel.value = new Date().getMonth();
    yearSel.value = new Date().getFullYear();
}

function initChart() {
    const ctx = document.getElementById('savingsChart').getContext('2d');
    savingsChart = new Chart(ctx, {
        type: 'line',
        data: { labels: [], datasets: [{ 
            data: [], borderColor: '#38bdf8', backgroundColor: 'rgba(56, 189, 248, 0.1)', 
            fill: true, tension: 0.4, pointRadius: 4, pointBackgroundColor: '#38bdf8' 
        }] },
        options: { 
            responsive: true, maintainAspectRatio: false, 
            plugins: { legend: { display: false } }, 
            scales: { x: { display: false }, y: { display: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b', font: { size: 9 } } } } 
        }
    });
}

function updateChart() {
    if (!savingsChart) return;
    let running = total;
    let chartData = [total];
    let labels = ["Now"];
    history.slice(0, 15).forEach(item => {
        running -= item.val;
        chartData.unshift(running);
        labels.unshift(item.date);
    });
    savingsChart.data.labels = labels;
    savingsChart.data.datasets[0].data = chartData;
    savingsChart.update();
}

function renderCalendar() {
    const grid = document.getElementById("calendarGrid");
    const month = parseInt(document.getElementById("monthSelect").value);
    const year = parseInt(document.getElementById("yearSelect").value);
    grid.innerHTML = "";

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const todayStr = new Date().toLocaleDateString('fr-MA');

    const dayMap = {};
    history.forEach(h => {
        if (!dayMap[h.date]) dayMap[h.date] = 0;
        dayMap[h.date] += h.val;
    });

    // Reconstruct balances for the month
    const dailyBalances = {};
    let simTotal = total;
    dailyBalances[todayStr] = simTotal;
    
    // Sort history by date descending to walk backward
    let sortedHistory = [...history].sort((a,b) => new Date(b.date.split('/').reverse().join('-')) - new Date(a.date.split('/').reverse().join('-')));
    sortedHistory.forEach(h => {
        simTotal -= h.val;
        dailyBalances[h.date] = simTotal + h.val; // Balance at END of that day
    });

    const padding = firstDay === 0 ? 6 : firstDay - 1;
    for (let p = 0; p < padding; p++) grid.appendChild(document.createElement("div"));

    for (let d = 1; d <= daysInMonth; d++) {
        const dateObj = new Date(year, month, d);
        const dateStr = dateObj.toLocaleDateString('fr-MA');
        const net = dayMap[dateStr] || 0;
        
        // FIND PREVIOUS BALANCE logic: find last day with activity before or on this day
        let displayBalance = 0;
        let checkDate = new Date(dateObj);
        while(checkDate >= new Date(2025,0,1)) {
            let dStr = checkDate.toLocaleDateString('fr-MA');
            if (dailyBalances[dStr] !== undefined) {
                displayBalance = dailyBalances[dStr];
                break;
            }
            checkDate.setDate(checkDate.getDate() - 1);
        }

        const dayEl = document.createElement("div");
        dayEl.className = "cal-day" + (dateStr === todayStr ? " today" : "");
        const netHtml = net !== 0 ? `<div class="net ${net > 0 ? 'pos' : 'neg'}">${net > 0 ? '+' : ''}${net}</div>` : "";
        dayEl.innerHTML = `<span>${d}</span>${netHtml}<div class="day-total">${Math.round(displayBalance)}</div>`;
        grid.appendChild(dayEl);
    }
}

function modifySavings(type) {
    const input = document.getElementById("amountInput");
    const amount = parseFloat(input.value);
    if (isNaN(amount) || amount <= 0) return;
    const change = type === 'add' ? amount : -amount;
    total += change;
    const dateStr = new Date().toLocaleDateString('fr-MA');
    history.unshift({ text: `${type === 'add' ? '+' : '-'} ${amount} MAD`, val: change, date: dateStr });
    input.value = "";
    saveData();
    updateUI();
    triggerBackgroundEffect(type);
}

function deleteTransaction(i) {
    lastDeleted = { item: history[i], index: i };
    total -= history[i].val;
    history.splice(i, 1);
    saveData();
    updateUI();
    showUndo();
}

function showUndo() {
    const toast = document.getElementById("undoToast");
    toast.innerHTML = `Deleted. <button onclick="undo()" style="color:#38bdf8;background:none;border:none;font-weight:bold;cursor:pointer">Undo</button>`;
    toast.className = "show";
    setTimeout(() => toast.className = "", 5000);
}

function undo() {
    if (!lastDeleted) return;
    total += lastDeleted.item.val;
    history.splice(lastDeleted.index, 0, lastDeleted.item);
    lastDeleted = null;
    document.getElementById("undoToast").className = "";
    saveData();
    updateUI();
}

function updateUI() {
    document.getElementById("displaySavings").innerText = `${total.toLocaleString()} MAD`;
    document.getElementById("goalValue").innerText = goal.toLocaleString();
    document.getElementById("displayRemaining").innerText = `${Math.max(0, goal - total).toLocaleString()} MAD left`;
    const percent = goal > 0 ? (total / goal) * 100 : 0;
    document.getElementById("progressFill").style.width = `${Math.min(percent, 100)}%`;
    document.getElementById("progressText").innerText = `${Math.round(percent)}%`;
    document.getElementById("historyList").innerHTML = history.slice(0, 10).map((item, i) => `
        <li><span>${item.text} (${item.date})</span><button class="delete-btn" onclick="deleteTransaction(${i})">×</button></li>
    `).join("");
    updateChart();
    renderCalendar();
}

function updateGoal() {
    const val = parseFloat(document.getElementById("goalInput").value);
    if (!isNaN(val)) { goal = val; saveData(); updateUI(); }
}

function saveData() {
    localStorage.setItem("savings_total", total);
    localStorage.setItem("savings_goal", goal);
    localStorage.setItem("savings_history", JSON.stringify(history));
}

function triggerBackgroundEffect(type) {
    const overlay = document.getElementById("bg-overlay");
    overlay.className = type === 'add' ? 'burst-add' : 'burst-sub';
    setTimeout(() => overlay.className = '', 700);
}

function clearAll() { if (confirm("Reset?")) { localStorage.clear(); location.reload(); } }