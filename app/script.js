let total = parseFloat(localStorage.getItem("savings_total")) || 0;
let goal = parseFloat(localStorage.getItem("savings_goal")) || 0;
let history = JSON.parse(localStorage.getItem("savings_history")) || [];
let lastDeleted = null; // To store the item for Undo

window.onload = () => {
    // Migration check for old data formats
    history = history.map(item => typeof item === 'string' ? { text: item, date: new Date().toLocaleDateString('fr-MA'), val: parseFloat(item.replace(/[^-0.9.]/g, '')) } : item);
    updateUI();
};

function modifySavings(type) {
    const input = document.getElementById("amountInput");
    const amount = parseFloat(input.value);
    if (isNaN(amount) || amount <= 0) return;

    const change = type === 'add' ? amount : -amount;
    total += change;
    
    const now = new Date();
    const dateStr = now.toLocaleDateString('fr-MA', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });

    history.unshift({
        text: `${type === 'add' ? '+' : '-'} ${amount} MAD`,
        val: change, // Store the raw number for easy math later
        date: dateStr
    });

    if (history.length > 15) history.pop();
    input.value = "";
    saveData();
    updateUI();
}

function deleteTransaction(index) {
    // Save for Undo feature
    lastDeleted = { item: history[index], index: index };
    
    // Update Total: Subtract the value (Subtracting a negative adds it back)
    total -= history[index].val;
    
    history.splice(index, 1);
    saveData();
    updateUI();
    showUndoNotification();
}

function undoDelete() {
    if (!lastDeleted) return;
    
    total += lastDeleted.item.val; // Put the money back
    history.splice(lastDeleted.index, 0, lastDeleted.item); // Put the item back
    
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

    const historyList = document.getElementById("historyList");
    historyList.innerHTML = history.map((item, i) => `
        <li>
            <div class="history-item-left">
                <span>${item.text}</span>
                <span style="font-size: 0.7rem; color: #64748b;">${item.date}</span>
            </div>
            <button class="delete-btn" onclick="deleteTransaction(${i})">×</button>
        </li>
    `).join("");
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

// Undo Notification Logic
function showUndoNotification() {
    let el = document.getElementById("undoToast");
    if(!el) {
        el = document.createElement("div");
        el.id = "undoToast";
        document.body.appendChild(el);
    }
    el.innerHTML = `Transaction deleted. <button onclick="undoDelete()">Undo</button>`;
    el.className = "show";
    setTimeout(() => { if(el.className === "show") hideUndoNotification(); }, 5000);
}

function hideUndoNotification() {
    const el = document.getElementById("undoToast");
    if(el) el.className = "";
}

function clearAll() { if (confirm("Delete all data?")) { localStorage.clear(); location.reload(); } }
document.addEventListener('mousemove', (e) => {
    const buttons = document.querySelectorAll('.add-btn, .sub-btn, .btn-small');
    
    // 1. Find the "Active" button (the one closest to the mouse)
    let closestBtn = null;
    let minDistance = 200; // Only focus if within 200px

    buttons.forEach(btn => {
        const rect = btn.getBoundingClientRect();
        const btnX = rect.left + rect.width / 2;
        const btnY = rect.top + rect.height / 2;
        const distance = Math.sqrt(Math.pow(e.clientX - btnX, 2) + Math.pow(e.clientY - btnY, 2));

        if (distance < minDistance) {
            minDistance = distance;
            closestBtn = btn;
        }
        
        // Reset every button FIRST to prevent the "stuck bright" bug
        btn.style.transform = `scale(1)`;
        btn.style.boxShadow = `none`;
        btn.style.backgroundColor = "";
        btn.classList.remove('float-active');
    });

    // 2. Only apply effects to the single closest button
    if (closestBtn) {
        const intensity = 1 - (minDistance / 200);
        const scale = 1 + (0.12 * intensity);
        
        closestBtn.style.transform = `scale(${scale})`;

        if (closestBtn.classList.contains('add-btn')) {
            // Smooth Green Glow
            closestBtn.style.backgroundColor = `rgb(${16 + (40 * intensity)}, ${185 * intensity + 50}, ${129 * intensity + 50})`;
            closestBtn.style.boxShadow = `0 10px 20px rgba(16, 185, 129, ${0.4 * intensity})`;
        } else if (closestBtn.classList.contains('sub-btn')) {
            // Smooth Red Glow
            closestBtn.style.backgroundColor = `rgb(${239 * intensity + 50}, ${68 * intensity}, ${68 * intensity})`;
            closestBtn.style.boxShadow = `0 10px 20px rgba(239, 68, 68, ${0.4 * intensity})`;
        }

        // Only float if really close
        if (intensity > 0.85) {
            closestBtn.classList.add('float-active');
        }
    }
});