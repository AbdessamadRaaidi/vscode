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

// HELPER: Convert DD/MM/YYYY string to a proper Date object safely
function parseHistoryDate(dateStr) {
    const parts = dateStr.split('/');
    // Format: Day, Month (0-indexed), Year
    return new Date(parts[2], parts[1] - 1, parts[0]);
}

function renderCalendar() {
    const grid = document.getElementById("calendarGrid");
    const month = parseInt(document.getElementById("monthSelect").value);
    const year = parseInt(document.getElementById("yearSelect").value);
    grid.innerHTML = "";

    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const now = new Date();
    // Normalize "now" to midnight for fair comparisons
    const todayNormalized = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    const dayNetMap = {};
    history.forEach(h => {
        if (!dayNetMap[h.date]) dayNetMap[h.date] = 0;
        dayNetMap[h.date] += h.val;
    });

    const padding = firstDay === 0 ? 6 : firstDay - 1;
    for (let p = 0; p < padding; p++) grid.appendChild(document.createElement("div"));

    for (let d = 1; d <= daysInMonth; d++) {
        const dateObj = new Date(year, month, d);
        const dateStr = dateObj.toLocaleDateString('fr-MA');
        
        let displayBalance = "";
        let netHtml = "";

        if (dateObj <= todayNormalized) {
            // Start with the CURRENT TOTAL and go backwards
            let balAtEndOfDay = total;
            
            history.forEach(h => {
                const histDate = parseHistoryDate(h.date);
                // If the history item happened strictly AFTER the day we are rendering,
                // we "undo" that transaction from the current total to see what the balance was back then.
                if (histDate > dateObj) {
                    balAtEndOfDay -= h.val;
                }
            });
            
            displayBalance = Math.round(balAtEndOfDay);

            const net = dayNetMap[dateStr] || 0;
            if (net !== 0) {
                netHtml = `<div class="net ${net > 0 ? 'pos' : 'neg'}">${net > 0 ? '+' : ''}${net}</div>`;
            }
        }

        const dayEl = document.createElement("div");
        dayEl.className = "cal-day" + (dateStr === todayNormalized.toLocaleDateString('fr-MA') ? " today" : "");
        dayEl.innerHTML = `<span>${d}</span>${netHtml}<div class="day-total">${displayBalance}</div>`;
        grid.appendChild(dayEl);
    }
}

function modifySavings(type) {
    const input = document.getElementById("amountInput");
    const amount = parseFloat(input.value);
    if (isNaN(amount) || amount <= 0) return;
    const change = type === 'add' ? amount : -amount;
    total += change;
    
    const now = new Date();
    const dateStr = now.toLocaleDateString('fr-MA');
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
    if (!isNaN(val)) { 
        goal = val; 
        if(savingsChart) savingsChart.options.scales.y.max = goal;
        saveData(); 
        updateUI(); 
    }
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

function clearAll() { if (confirm("Reset everything?")) { localStorage.clear(); location.reload(); } }