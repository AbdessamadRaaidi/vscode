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
            scales: { 
                x: { display: false }, 
                y: { 
                    display: true, 
                    beginAtZero: true,
                    max: goal > 0 ? goal : undefined, 
                    grid: { color: 'rgba(255,255,255,0.05)' }, 
                    ticks: { color: '#64748b', font: { size: 9 } } 
                } 
            } 
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

// Robust date parser for DD/MM/YYYY
function parseDMY(s) {
    const b = s.split(/\D/);
    return new Date(b[2], b[1] - 1, b[0]);
}

function renderCalendar() {
    const grid = document.getElementById("calendarGrid");
    const month = parseInt(document.getElementById("monthSelect").value);
    const year = parseInt(document.getElementById("yearSelect").value);
    grid.innerHTML = "";

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const now = new Date();
    const todayStr = now.toLocaleDateString('fr-MA');

    // 1. Calculate the 'Starting Balance' (Balance before the first history item)
    let historySum = history.reduce((acc, curr) => acc + curr.val, 0);
    let startBalance = total - historySum;

    // 2. Build a Timeline: Map every date that has a transaction to its NET change
    const dailyNet = {};
    history.forEach(h => {
        if (!dailyNet[h.date]) dailyNet[h.date] = 0;
        dailyNet[h.date] += h.val;
    });

    // 3. Generate all days from 2025-01-01 to the end of the selected month
    // This ensures we carry the balance forward correctly through the months.
    let runningBalance = startBalance;
    const balanceTimeline = {};
    
    let iterDate = new Date(2025, 0, 1);
    const endOfSelectedMonth = new Date(year, month, daysInMonth);

    while (iterDate <= endOfSelectedMonth) {
        let dKey = iterDate.toLocaleDateString('fr-MA');
        if (dailyNet[dKey]) {
            runningBalance += dailyNet[dKey];
        }
        balanceTimeline[dKey] = runningBalance;
        iterDate.setDate(iterDate.getDate() + 1);
    }

    // 4. Render Grid
    const padding = firstDay === 0 ? 6 : firstDay - 1;
    for (let p = 0; p < padding; p++) grid.appendChild(document.createElement("div"));

    for (let d = 1; d <= daysInMonth; d++) {
        const dateObj = new Date(year, month, d);
        const dateStr = dateObj.toLocaleDateString('fr-MA');
        const isFuture = dateObj > now && dateStr !== todayStr;
        
        let displayVal = "";
        let netHtml = "";

        if (!isFuture) {
            displayVal = Math.round(balanceTimeline[dateStr] || runningBalance);
            const net = dailyNet[dateStr] || 0;
            if (net !== 0) {
                netHtml = `<div class="net ${net > 0 ? 'pos' : 'neg'}">${net > 0 ? '+' : ''}${net}</div>`;
            }
        }

        const dayEl = document.createElement("div");
        dayEl.className = "cal-day" + (dateStr === todayStr ? " today" : "");
        dayEl.innerHTML = `<span>${d}</span>${netHtml}<div class="day-total">${displayVal}</div>`;
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
    updateChart