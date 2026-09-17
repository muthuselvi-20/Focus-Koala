/**
 * FocusKoala Blocked Page Handler
 * Handles live cooldown countdown, reopen attempt escalation, and task-aware redirection.
 */

const API_BASE = "http://localhost:8000/api";

const urlParams = new URLSearchParams(window.location.search);
const targetDomain = urlParams.get("domain") || "instagram.com";

let remainingSeconds = parseInt(urlParams.get("remaining") || "120", 10);
let attemptCount = parseInt(urlParams.get("attempts") || "1", 10);
let countdownInterval = null;

const timerEl = document.getElementById("cooldown-timer");
const headlineEl = document.getElementById("blocked-headline");
const quoteEl = document.getElementById("blocked-quote");
const attemptEl = document.getElementById("attempt-info");
const taskTitleEl = document.getElementById("task-title");
const startTaskBtn = document.getElementById("start-task-btn");
const openDashBtn = document.getElementById("view-dashboard-btn");

function formatTime(totalSecs) {
  if (totalSecs <= 0) return "00:00";
  const m = Math.floor(totalSecs / 60);
  const s = totalSecs % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function updateUI() {
  timerEl.textContent = formatTime(remainingSeconds);
  attemptEl.textContent = `Reopen attempt: ${attemptCount}`;

  const cleanName = targetDomain.replace(".com", "").replace("www.", "");
  const capName = cleanName.charAt(0).toUpperCase() + cleanName.slice(1);

  if (attemptCount <= 1) {
    headlineEl.textContent = "Nice try! 😄";
    quoteEl.textContent = `"${capName} is currently on a break."`;
  } else if (attemptCount === 2) {
    headlineEl.textContent = "Nice try 😐";
    quoteEl.textContent = `"${capName} can wait. Let's finish your task!"`;
  } else {
    headlineEl.textContent = `Notice from FocusKoala 🐨`;
    quoteEl.textContent = `"You have tried opening ${capName} ${attemptCount} times."`;
  }
}

// Fetch live block status and task recommendation from FastAPI
async function syncBlockData() {
  try {
    const res = await fetch(`${API_BASE}/check-block?domain=${encodeURIComponent(targetDomain)}&record_attempt=false`);
    if (res.ok) {
      const data = await res.json();
      if (data.remaining_seconds !== undefined) {
        remainingSeconds = Math.max(0, data.remaining_seconds);
      }
      if (data.attempts !== undefined) {
        attemptCount = data.attempts;
      }
      if (data.recommended_task && data.recommended_task.title) {
        taskTitleEl.textContent = data.recommended_task.title;
      }
      updateUI();
    }
  } catch (err) {
    // offline or backend starting
  }
}

// Live Countdown
function startCountdown() {
  updateUI();
  clearInterval(countdownInterval);

  countdownInterval = setInterval(() => {
    remainingSeconds--;
    if (remainingSeconds <= 0) {
      clearInterval(countdownInterval);
      timerEl.textContent = "00:00";
      headlineEl.textContent = "Cooldown Expired! 🎉";
      quoteEl.textContent = `"${targetDomain} is now available again."`;
      startTaskBtn.textContent = "Return to Browsing";
      startTaskBtn.onclick = () => {
        window.location.href = `https://${targetDomain}`;
      };
      return;
    }
    timerEl.textContent = formatTime(remainingSeconds);
  }, 1000);
}

startTaskBtn.onclick = () => {
  // Task-aware redirection: open task or local dashboard
  window.open("http://localhost:3000", "_blank");
};

openDashBtn.onclick = () => {
  window.open("http://localhost:3000", "_blank");
};

syncBlockData();
startCountdown();
