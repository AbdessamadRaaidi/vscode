window.onload = function() {
    if (localStorage.getItem("mad_goal")) {
        document.getElementById("goalInput").value = localStorage.getItem("mad_goal");
        document.getElementById("savingsInput").value = localStorage.getItem("mad_current");
        updateDisplay();
    }
};

function saveData() {
    const goal = document.getElementById("goalInput").value;
    const savings = document.getElementById("savingsInput").value;

    localStorage.setItem("mad_goal", goal);
    localStorage.setItem("mad_current", savings);

    updateDisplay();
}

function updateDisplay() {
    const goal = parseFloat(localStorage.getItem("mad_goal")) || 0;
    const savings = parseFloat(localStorage.getItem("mad_current")) || 0;
    const remaining = goal - savings;
    const percentage = goal > 0 ? (savings / goal) * 100 : 0;

    document.getElementById("displaySavings").innerText = `${savings.toLocaleString()} MAD`;
    document.getElementById("displayRemaining").innerText = `${(remaining > 0 ? remaining : 0).toLocaleString()} MAD`;
    
    const fill = document.getElementById("progressFill");
    fill.style.width = `${Math.min(percentage, 100)}%`;
    document.getElementById("progressText").innerText = `${Math.round(percentage)}%`;
}