let total = parseFloat(localStorage.getItem("savings_total")) || 0;
let goal = parseFloat(localStorage.getItem("savings_goal")) || 0;
let history = JSON.parse(localStorage.getItem("savings_history")) || [];
let lastDeleted = null;
let savingsChart;

window.onload = () => {
    history = history.map(item => typeof item === 'string' ? { 
        text: item, date: new Date().toLocaleDateString('fr-MA'), val: parseFloat(item.replace(/[^-0.9.]/g, '')) 
    } : item);
    initChart();
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
                pointRadius: 4,
                pointBackgroundColor: '#38bdf8'
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
                x: { display: false },
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

function updateChart() {
    if (!savingsChart) return;
    let runningTotal = total;
    let chartData = [total];
    let chartLabels = ["Now"];
    history.forEach(item => {
        runningTotal -= item.val;
        chartData.unshift(runningTotal);
        chartLabels.unshift(item.date);
    });
    savingsChart.data.labels = chartLabels;
    savingsChart.data.datasets[0].data = chartData;
    savingsChart.options.scales.y.max = goal > 0 ? goal : undefined;
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
    const dateStr = now.toLocaleDateString('fr-MA', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });

    history.unshift({ text: `${type === 'add' ? '+' : '-'} ${amount} MAD`, val: change, date: dateStr });
    if (history.length > 15) history.pop();
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
    const remaining = goal - total;
    document.getElementById("displayRemaining").innerText = `${(remaining > 0 ? remaining : 0).toLocaleString()} MAD left`;
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