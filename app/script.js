let total = parseFloat(localStorage.getItem("savings_total")) || 0;
let goal = parseFloat(localStorage.getItem("savings_goal")) || 0;
let deadline = localStorage.getItem("savings_deadline") || "";
let history = JSON.parse(localStorage.getItem("savings_history")) || [];
let lastDeleted = null;
let savingsChart;

window.onload = () => {
    history = history.map(item => typeof item === 'string' ? { 
        text: item, date: new Date().toLocaleDateString('fr-MA'), val: parseFloat(item.replace(/[^-0.9.]/g, '')) 
    } : item);
    document.getElementById("deadlineInput").value = deadline;
    initChart();
    updateUI();
};

function initChart() {
    const ctx = document.getElementById('savingsChart').getContext('2d');
    savingsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Actual',
                    data: [],
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#38bdf8',
                    zIndex: 2
                },
                {
                    label: 'Projection',
                    data: [],
                    borderColor: 'rgba(148, 163, 184, 0.3)', // Lower transparency
                    borderDash: [5, 5],
                    borderWidth: 2,
                    fill: false,
                    pointRadius: 0,
                    zIndex: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { 
                    ticks: { color: '#64748b', font: { size: 8 }, maxRotation: 45, minRotation: 45 }
                },
                y: { 
                    beginAtZero: true,
                    max: goal > 0 ? goal * 1.1 : undefined,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#64748b', font: { size: 9 } }
                }
            }
        }
    });
}

function updateChart() {
    if (!savingsChart) return;

    let chartLabels = [];
    let actualData = [];
    let projectionData = [];

    // 1. Calculate History
    let runningTotal = total;
    let histPoints = [{date: "Today", val: total}];
    history.forEach(item => {
        runningTotal -= item.val;
        histPoints.unshift({date: item.date.split(' ')[0], val: runningTotal});
    });

    // 2. Projection Logic
    const now = new Date();
    const targetDate = deadline ? new Date(deadline) : null;
    
    histPoints.forEach(p => {
        chartLabels.push(p.date);
        actualData.push(p.val);
        projectionData.push(null);
    });

    if (targetDate && targetDate > now) {
        const daysToGoal = Math.ceil((targetDate - now) / (1000 * 60 * 60 * 24));
        projectionData[projectionData.length - 1] = total; // Start projection at current total
        
        // Add one point for the end date
        chartLabels.push(targetDate.toLocaleDateString('fr-MA', {day:'2-digit', month:'2-digit'}));
        actualData.push(null);
        projectionData.push(goal);
    }

    savingsChart.data.labels = chartLabels;
    savingsChart.data.datasets[0].data = actualData;
    savingsChart.data.datasets[1].data = projectionData;
    savingsChart.options.scales.y.max = goal > 0 ? goal * 1.1 : undefined;
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

    const now = new Date();
    const dateStr = now.toLocaleDateString('fr-MA', { day: '2-digit', month: '2-digit' });

    history.unshift({ text: `${type === 'add' ? '+' : '-'} ${amount} MAD`, val: change, date: dateStr });
    if (history.length > 20) history.pop();
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
    
    // Progress Calculation
    const remaining = goal - total;
    const percent = goal > 0 ? (total / goal) * 100 : 0;
    document.getElementById("progressFill").style.width = `${Math.min(percent, 100)}%`;
    document.getElementById("progressText").innerText = `${Math.round(percent)}%`;

    // Deadline Calculation
    if (deadline) {
        const days = Math.ceil((new Date(deadline) - new Date()) / (1000 * 60 * 60 * 24));
        document.getElementById("daysLeft").innerText = days > 0 ? `${days} days left` : "Deadline passed";
    }

    document.getElementById("historyList").innerHTML = history.map((item, i) => `
        <li>
            <span>${item.text} <small style="color:#64748b">(${item.date})</small></span>
            <button class="delete-btn" onclick="deleteTransaction(${i})">×</button>
        </li>
    `).join("");
    updateChart();
}

function updateSettings() {
    const g = parseFloat(document.getElementById("goalInput").value);
    const d = document.getElementById("deadlineInput").value;
    if (!isNaN(g)) goal = g;
    deadline = d;
    saveData();
    updateUI();
}

function saveData() {
    localStorage.setItem("savings_total", total);
    localStorage.setItem("savings_goal", goal);
    localStorage.setItem("savings_deadline", deadline);
    localStorage.setItem("savings_history", JSON.stringify(history));
}

function showUndoNotification() {
    let el = document.getElementById("undoToast") || document.createElement("div");
    el.id = "undoToast"; document.body.appendChild(el);
    el.innerHTML = `Deleted. <button onclick="undoDelete()" style="color:#38bdf8;background:none;border:none;cursor:pointer;font-weight:bold">Undo</button>`;
    el.className = "show";
    setTimeout(() => el.className = "", 4000);
}

function hideUndoNotification() { document.getElementById("undoToast").className = ""; }
function clearAll() { if (confirm("Clear all?")) { localStorage.clear(); location.reload(); } }