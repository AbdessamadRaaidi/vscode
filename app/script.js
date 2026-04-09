let total = parseFloat(localStorage.getItem("savings_total")) || 0;
let goal = parseFloat(localStorage.getItem("savings_goal")) || 0;
let history = JSON.parse(localStorage.getItem("savings_history")) || [];

window.onload = function() {
    migrateOldData(); // Ensures you don't lose old data
    updateUI();
};

function migrateOldData() {
    // This checks if history items are just strings (old style) and converts them
    history = history.map(item => {
        if (typeof item === 'string') {
            return {
                text: item,
                date: new Date().toLocaleDateString('fr-MA') // Sets today's date for old items
            };
        }
        return item;
    });
    saveData();
}

function modifySavings(type) {
    const input = document.getElementById("amountInput");
    const val = parseFloat(input.value);

    if (isNaN(val) || val <= 0) return;

    // Get current date and time
    const now = new Date();
    const dateStr = now.toLocaleDateString('fr-MA', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    if (type === 'add') {
        total += val;
        history.unshift({ text: `+ ${val} MAD`, date: dateStr });
    } else {
        total -= val;
        history.unshift({ text: `- ${val} MAD`, date: dateStr });
    }

    if (history.length > 10) history.pop(); // Increased to 10 entries
    
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

// Replace your updateUI function with this one
function updateUI() {
    document.getElementById("displaySavings").innerText = `${total.toLocaleString()} MAD`;
    document.getElementById("goalValue").innerText = goal.toLocaleString();
    
    const remaining = goal - total;
    document.getElementById("displayRemaining").innerText = `${(remaining > 0 ? remaining : 0).toLocaleString()} MAD left`;

    const percent = goal > 0 ? (total / goal) * 100 : 0;
    document.getElementById("progressFill").style.width = `${Math.min(percent, 100)}%`;
    document.getElementById("progressText").innerText = `${Math.round(percent)}%`;

    const historyList = document.getElementById("historyList");
    
    historyList.innerHTML = history.map((item, index) => `
        <li>
            <div class="history-item-left">
                <span>${item.text}</span>
                <span style="font-size: 0.7rem; color: #64748b;">${item.date}</span>
            </div>
            <button class="delete-btn" onclick="deleteTransaction(${index})">×</button>
        </li>
    `).join("");
}

// Add this new function to handle deleting
function deleteTransaction(index) {
    const item = history[index];
    
    // Reverse the math
    const amount = parseFloat(item.text.replace(/[^-0.9.]/g, ''));
    
    // If it was +100, we subtract 100. If it was -100, we add 100.
    total -= amount;

    // Remove from history array
    history.splice(index, 1);

    saveData();
    updateUI();
}

function clearAll() {
    if (confirm("Delete all data? This cannot be undone.")) {
        localStorage.clear();
        location.reload();
    }
}