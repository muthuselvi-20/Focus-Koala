/**
 * FocusKoala Chrome/Edge Extension - Background Service Worker (Manifest V3)
 * Tracks active distracting websites, enforces limits, triggers interventions,
 * and safely redirects/closes tabs without affecting other browser sessions.
 */

const API_BASE = "http://localhost:8000/api";
let monitoredWebsites = [
  { domain: "instagram.com", name: "Instagram", limit_seconds: 60, cooldown_seconds: 120 },
  { domain: "youtube.com", name: "YouTube", limit_seconds: 2700, cooldown_seconds: 1800 },
  { domain: "reddit.com", name: "Reddit", limit_seconds: 1200, cooldown_seconds: 1800 }
];

let activeTabId = null;
let activeDomain = null;
let sessionStartTime = null;

// Fetch updated monitored sites from FastAPI backend
async function syncMonitoredWebsites() {
  try {
    const res = await fetch(`${API_BASE}/config/websites`);
    if (res.ok) {
      monitoredWebsites = await res.json();
    }
  } catch (err) {
    // Keep local cached copy if offline
  }
}

// Clean and extract domain from URL
function getDomainFromUrl(url) {
  if (!url) return null;
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") return null;
    let host = parsed.hostname.toLowerCase();
    if (host.startsWith("www.")) host = host.slice(4);
    return host;
  } catch {
    return null;
  }
}

function findMonitoredConfig(domain) {
  if (!domain) return null;
  return monitoredWebsites.find(site => {
    if (!site.enabled && site.enabled !== undefined) return false;
    const siteDomain = site.domain.toLowerCase().replace("www.", "");
    return domain === siteDomain || domain.endsWith("." + siteDomain);
  });
}

// Check tab state and enforce block or start tracking
async function checkAndHandleTab(tab) {
  if (!tab || !tab.url || !tab.id) return;
  const domain = getDomainFromUrl(tab.url);
  if (!domain) return;

  const config = findMonitoredConfig(domain);
  if (!config) {
    activeDomain = null;
    return;
  }

  // Check if site is currently blocked in SQLite
  try {
    const checkRes = await fetch(`${API_BASE}/check-block?domain=${encodeURIComponent(config.domain)}&record_attempt=true`);
    if (checkRes.ok) {
      const blockData = await checkRes.json();
      if (blockData.is_blocked) {
        // Safely redirect only this tab to FocusKoala blocked page
        const blockedUrl = chrome.runtime.getURL(
          `blocked.html?domain=${encodeURIComponent(config.domain)}&remaining=${blockData.remaining_seconds}&attempts=${blockData.attempts}`
        );
        chrome.tabs.update(tab.id, { url: blockedUrl });
        return;
      }
    }
  } catch (err) {
    // API server may be booting
  }

  // If site is allowed, record as current active tracking
  activeTabId = tab.id;
  activeDomain = config.domain;
  sessionStartTime = Date.now();
}

// Listen for tab activation (user switches tabs)
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  try {
    const tab = await chrome.tabs.get(activeInfo.tabId);
    checkAndHandleTab(tab);
  } catch (err) {}
});

// Listen for tab URL updates (user navigates to instagram.com)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "loading" && changeInfo.url) {
    checkAndHandleTab(tab);
  }
});

// Regular Heartbeat Alarm (runs every 3 seconds to report usage)
chrome.alarms.create("focuskoala_heartbeat", { periodInMinutes: 0.05 }); // ~3 seconds

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name !== "focuskoala_heartbeat") return;

  chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
    if (!tabs || tabs.length === 0) return;
    const tab = tabs[0];
    const domain = getDomainFromUrl(tab.url);
    if (!domain) return;

    const config = findMonitoredConfig(domain);
    if (!config) return;

    try {
      const response = await fetch(`${API_BASE}/track`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          domain: config.domain,
          duration_seconds: 3.0
        })
      });

      if (!response.ok) return;
      const data = await response.json();

      if (data.should_block) {
        // LIMIT REACHED: Intervention!
        // Safely redirect this distracting tab to the blocked page
        const blockedUrl = chrome.runtime.getURL(
          `blocked.html?domain=${encodeURIComponent(config.domain)}&remaining=${data.cooldown_seconds || 120}&attempts=1`
        );
        chrome.tabs.update(tab.id, { url: blockedUrl });
      } else if (data.warning) {
        // Show warning banner inside the tab
        chrome.tabs.sendMessage(tab.id, {
          action: "show_warning",
          message: data.message,
          remaining_seconds: data.remaining_seconds
        }).catch(() => {});
      }
    } catch (err) {
      // Local server might not be running yet
    }
  });
});

// Initial startup sync
syncMonitoredWebsites();
