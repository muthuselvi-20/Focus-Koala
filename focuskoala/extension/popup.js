const API_BASE = "http://localhost:8000/api";

async function loadPopup() {
  try {
    const res = await fetch(`${API_BASE}/todos`);
    if (res.ok) {
      const data = await res.json();
      if (data.recommended_task) {
        document.getElementById("popup-task").textContent = data.recommended_task.title;
      }
    }
  } catch (e) {}

  try {
    const siteRes = await fetch(`${API_BASE}/config/websites`);
    if (siteRes.ok) {
      const sites = await siteRes.json();
      const listEl = document.getElementById("monitored-list");
      listEl.innerHTML = "";
      sites.slice(0, 4).forEach(s => {
        const item = document.createElement("div");
        item.className = "site-item";
        const limitStr = s.limit_seconds < 120 ? `${s.limit_seconds}s` : `${Math.round(s.limit_seconds / 60)}m`;
        const coolStr = s.cooldown_seconds < 120 ? `${s.cooldown_seconds}s` : `${Math.round(s.cooldown_seconds / 60)}m`;
        item.innerHTML = `
          <span>🌐 ${s.name}</span>
          <span style="color: var(--accent-light);">${limitStr} / ${coolStr}</span>
        `;
        listEl.appendChild(item);
      });
    }
  } catch (e) {}
}

document.getElementById("quick-focus-btn").onclick = async () => {
  try {
    await fetch(`${API_BASE}/focus-mode/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ duration_minutes: 30 })
    });
    alert("🐨 Focus Mode activated for 30 minutes!");
  } catch (e) {
    alert("Could not connect to FocusKoala desktop agent.");
  }
};

document.getElementById("open-app-btn").onclick = () => {
  window.open("http://localhost:3000", "_blank");
};

loadPopup();
