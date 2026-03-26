async function fetchHistory() {
    try {
        const response = await fetch("/history"); // JSON endpoint from FastAPI
        const data = await response.json();
        const tbody = document.querySelector("#history-table tbody");
        if (!tbody) return;

        tbody.innerHTML = "";  // Clear table

        data.history.forEach(item => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${item.timestamp}</td>
                <td>${item.tweet}</td>
                <td>${item.sentiment}</td>
                <td>${item.confidence}%</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error("Error fetching history:", error);
    }
}

// Update history every 5 seconds
setInterval(fetchHistory, 5000);
