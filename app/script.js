let total = parseFloat(localStorage.getItem("savings_total")) || 0;
let goal = parseFloat(localStorage.getItem("savings_goal")) || 0;
let history = JSON.parse(localStorage.getItem("savings_history")) || [];

window.onload = updateUI;

function modifySavings(type) {
    const input = document.getElementById("amountInput");
    const val = parseFloat(input.value);

    if (isNaN(val) || val <= 0) return;

    if (type === 'add') {
        total += val;
        history.unshift(`+ ${val} MAD`);
    } else {
        total -= val;
        history.unshift(`- ${val} MAD`);
    }

    if (history.length > 5) history.pop(); // Keep only last 5 entries
    
    input.value = "";
    saveData();
    updateUI();
}

function updateGoal() {
    const goalVal = parseFloat(document.getElementById("goalInput").value);
    if (!isNaN(goalVal)) {
        goal = goalVal;
        saveData();
        updateUI();
        document.getElementById("goalInput").value = "";
    }
}

function saveData() {
    localStorage.setItem("savings_total", total);
    localStorage.setItem("savings_goal", goal);
    localStorage.setItem("savings_history", JSON.stringify(history));
}

function updateUI() {
    document.getElementById("displaySavings").innerText = `${total.toLocaleString()} MAD`;
    document.getElementById("goalValue").innerText = goal.toLocaleString();
    
    const remaining = goal - total;
    document.getElementById("displayRemaining").innerText = `${(remaining > 0 ? remaining : 0).toLocaleString()} MAD left`;

    const percent = goal > 0 ? (total / goal) * 100 : 0;
    document.getElementById("progressFill").style.width = `${Math.min(percent, 100)}%`;
    document.getElementById("progressText").innerText = `${Math.round(percent)}%`;

    const historyList = document.getElementById("historyList");
    historyList.innerHTML = history.map(item => `<li>${item}</li>`).join("");
}

function clearAll() {
    if (confirm("Delete all data?")) {
        localStorage.clear();
        location.reload();
    }
}