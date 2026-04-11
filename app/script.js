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
    
    months.forEach((m, i) => {
        let opt = new Option(m, i);
        if (i === new Date().getMonth()) opt.selected = true;
        monthSel.add(opt);
    });

    for (let y = 2025; y <= 2034; y++) {
        let opt = new Option(y, y);
        if (y === new Date().getFullYear()) opt.selected = true;
        yearSel.add(opt);
    }
}

function initChart() {
    const ctx = document.getElementById('savingsChart').getContext('2d');
    savingsChart = new Chart(ctx, {
        type: 'line',
        data: { labels: [], datasets: [{ data: [], borderColor: '#38bdf8', backgroundColor: 'rgba(56, 189, 248, 0.1)', fill: true, tension: 0.4, pointRadius: 2 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { display: false } } }
    });
}

function renderCalendar() {
    const grid = document.getElementById("calendarGrid");
    const month = parseInt(document.getElementById("monthSelect").value);
    const year = parseInt(document.getElementById("yearSelect").value);
    grid.innerHTML = "";

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const todayStr = new Date().toLocaleDateString('fr-MA');

    // Calculate all daily balances from the start of time
    const dailyBalances = calculateDailyBalances();

    // Padding for first day of week (Monday start)
    const padding = firstDay === 0 ? 6 : firstDay - 1;
    for (let p = 0; p < padding; p++) grid.appendChild(document.createElement("div"));

    for (let d = 1; d <= daysInMonth; d++) {
        const dateObj = new Date(year, month, d);
        const dateStr = dateObj.toLocaleDateString('fr-MA');
        const data = dailyBalances[dateStr] || { net: 0, balance: 0 };

        const dayEl = document.createElement("div");
        dayEl.className = "cal-day";
        if (dateStr === todayStr) dayEl.classList.add("today");

        const netDisplay = data.net === 0 ? "" : `<div class="net ${data.net > 0 ? 'pos' : 'neg'}">${data.net > 0 ? '+' : ''}${data.net}</div>`;
        
        dayEl.innerHTML = `
            <span>${d}</span>
            ${netDisplay}
            <div class="day-total">${Math.round(data.balance)}</div>
        `;
        grid.appendChild(dayEl);
    }
}

function calculateDailyBalances() {
    // 1. Get all unique dates from history and sort them
    let results = {};
    let runningTotal = total;
    
    // We start from current total and go backward to reconstruct history
    // history[0] is newest
    let dayMap = {};
    
    // Group transactions by date
    history.forEach(h => {
        if (!dayMap[h.date]) dayMap[h.date] = 0;
        dayMap[h.date] += h.val;
    });

    // To find the balance at any date, we subtract changes from the current total
    // But for the calendar, we want the balance *at the end of that day*.
    let sortedDates = Object.keys(dayMap).sort((a,b) => {
        return new Date(b.split('/').reverse().join('-')) - new Date(a.split('/').reverse().join('-'));
    });

    let currentBalance = total;
    // Map today first
    const todayStr = new Date().toLocaleDateString('fr-MA');
    results[todayStr] = { net: dayMap[todayStr] || 0, balance: currentBalance };

    let runningBalance = currentBalance;
    sortedDates.forEach(date => {
        results[date] = { net: dayMap[date], balance: runningBalance };
        runningBalance -= dayMap[date]; // Move backward in time
    });

    return results;
}

function modifySavings(type) {
    const amount = parseFloat(document.getElementById("amountInput").value);
    if (isNaN(amount) || amount <= 0) return;
    const change = type === 'add' ? amount : -amount;
    total += change;
    
    const dateStr = new Date().toLocaleDateString('fr-MA');
    history.unshift({ text: `${type === 'add' ? '+' : '-'} ${amount} MAD`, val: change, date: dateStr });
    
    document.getElementById("amountInput").value = "";
    saveData();
    updateUI();
    triggerBackgroundEffect(type);
}

function updateUI() {
    document.getElementById("displaySavings").innerText = `${total.toLocaleString()} MAD`;
    document.getElementById("goalValue").innerText = goal.toLocaleString();
    const remaining = goal - total;
    document.getElementById("displayRemaining").innerText = `${(remaining > 0 ? remaining : 0).toLocaleString()} MAD left`;
    const percent = goal > 0 ? (total / goal) * 100 : 0;
    document.getElementById("progressFill").style.width = `${Math.min(percent, 100)}%`;
    document.getElementById("progressText").innerText = `${Math.round(percent)}%`;

    document.getElementById("historyList").innerHTML = history.slice(0, 10).map((item, i) => `
        <li><span>${item.text} (${item.date})</span><button class="delete-btn" onclick="deleteTransaction(${i})">×</button></li>
    `).join("");
    
    updateChart();
    renderCalendar();
}

function deleteTransaction(i) {
    total -= history[i].val;
    history.splice(i, 1);
    saveData();
    updateUI();
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

function updateChart() {
    if (!savingsChart) return;
    let running = total;
    let data = [total];
    history.slice(0, 10).forEach(h => { running -= h.val; data.unshift(running); });
    savingsChart.data.labels = new Array(data.length).fill("");
    savingsChart.data.datasets[0].data = data;
    savingsChart.update();
}

function triggerBackgroundEffect(type) {
    const overlay = document.getElementById("bg-overlay");
    overlay.className = type === 'add' ? 'burst-add' : 'burst-sub';
    setTimeout(() => overlay.className = '', 700);
}

function clearAll() { if (confirm("Reset everything?")) { localStorage.clear(); location.reload(); } }