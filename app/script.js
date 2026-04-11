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
        data: { labels: [], datasets: [{ 
            data: [], 
            borderColor: '#38bdf8', 
            backgroundColor: 'rgba(56, 189, 248, 0.1)', 
            fill: true, 
            tension: 0.4, 
            pointRadius: 3,
            pointBackgroundColor: '#38bdf8' 
        }] },
        options: { 
            responsive: true, 
            maintainAspectRatio: false, 
            plugins: { legend: { display: false } }, 
            scales: { x: { display: false }, y: { display: false } } 
        }
    });
}

function updateChart() {
    if (!savingsChart) return;
    let running = total;
    let dataPoints = [total];
    // Map last 15 history items to get graph points
    history.slice(0, 15).forEach(h => {
        running -= h.val;
        dataPoints.unshift(running);
    });
    savingsChart.data.labels = new Array(dataPoints.length).fill("");
    savingsChart.data.datasets[0].data = dataPoints;
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

    // Logic to calculate balance for every day of the month
    const dayMap = {};
    history.forEach(h => {
        if (!dayMap[h.date]) dayMap[h.date] = 0;
        dayMap[h.date] += h.val;
    });

    // To calculate daily balances accurately, we need to know the total at the end of EACH day
    const padding = firstDay === 0 ? 6 : firstDay - 1;
    for (let p = 0; p < padding; p++) grid.appendChild(document.createElement("div"));

    // Calculation: Walk through all days from start of history to end of selected month
    let runningBalance = total;
    const dailyBalances = {};
    
    // Simulating history to find what the balance was on specific dates
    let simulatedTotal = total;
    dailyBalances[new Date().toLocaleDateString('fr-MA')] = simulatedTotal;
    
    let histCopy = [...history].sort((a,b) => new Date(b.date.split('/').reverse().join('-')) - new Date(a.date.split('/').reverse().join('-')));
    
    histCopy.forEach(h => {
        simulatedTotal -= h.val;
        dailyBalances[h.date] = simulatedTotal;
    });

    for (let d = 1; d <= daysInMonth; d++) {
        const dateObj = new Date(year, month, d);
        const dateStr = dateObj.toLocaleDateString('fr-MA');
        const net = dayMap[dateStr] || 0;
        
        // Find balance for this day (or closest previous day with activity)
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
    const remaining = Math.max(0, goal - total);
    document.getElementById("displayRemaining").innerText = `${remaining.toLocaleString()} MAD left`;
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

function clearAll() { if (confirm("Clear all data?")) { localStorage.clear(); location.reload(); } }