// Load data when the page opens
window.onload = function() {
    if (localStorage.getItem("savingsGoal")) {
        document.getElementById("goalInput").value = localStorage.getItem("savingsGoal");
        document.getElementById("savingsInput").value = localStorage.getItem("currentSavings");
        updateDisplay();
    }
};

function saveData() {
    const goal = document.getElementById("goalInput").value;
    const savings = document.getElementById("savingsInput").value;

    // Save to LocalStorage (Persists even if PC is closed)
    localStorage.setItem("savingsGoal", goal);
    localStorage.setItem("currentSavings", savings);

    updateDisplay();
    alert("Progress Saved!");
}

function updateDisplay() {
    const goal = parseFloat(localStorage.getItem("savingsGoal")) || 0;
    const savings = parseFloat(localStorage.getItem("currentSavings")) || 0;
    const remaining = goal - savings;
    const percentage = goal > 0 ? (savings / goal) * 100 : 0;

    document.getElementById("displaySavings").innerText = `$${savings}`;
    document.getElementById("displayRemaining").innerText = `$${remaining > 0 ? remaining : 0}`;
    document.getElementById("progressFill").style.width = `${Math.min(percentage, 100)}%`;
}