import React, { useState } from "react";
import { Copy, Check, Download, ExternalLink, Code2, FolderCheck } from "lucide-react";

export const ExtensionViewer: React.FC = () => {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"manifest" | "background" | "blocked" | "install">("install");

  const files = {
    manifest: `{
  "manifest_version": 3,
  "name": "FocusKoala 🐨",
  "version": "1.0.0",
  "description": "Smart productivity agent with Koala interventions, website limits, and task redirection.",
  "permissions": ["tabs", "storage", "alarms"],
  "host_permissions": [
    "http://localhost:8000/*",
    "http://127.0.0.1:8000/*",
    "*://*.instagram.com/*",
    "*://*.youtube.com/*",
    "*://*.reddit.com/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_popup": "popup.html"
  }
}`,
    background: `// FocusKoala Background Service Worker
const API_BASE = "http://localhost:8000/api";

// Regular heartbeat sends active domain usage to local Python agent
chrome.alarms.create("focuskoala_heartbeat", { periodInMinutes: 0.05 });
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name !== "focuskoala_heartbeat") return;
  chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
    if (!tabs || !tabs[0]) return;
    const tab = tabs[0];
    const domain = getDomain(tab.url);
    if (!domain) return;
    
    const res = await fetch(\`\${API_BASE}/track\`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ domain, duration_seconds: 3.0 })
    });
    const data = await res.json();
    if (data.should_block) {
      // Safely close/redirect tab without killing other tabs
      const blockedUrl = chrome.runtime.getURL(\`blocked.html?domain=\${domain}&remaining=\${data.cooldown_seconds || 120}\`);
      chrome.tabs.update(tab.id, { url: blockedUrl });
    }
  });
});`,
    blocked: `<!-- FocusKoala Cooldown Blocked Page (Feature 5, 8, 9) -->
<!DOCTYPE html>
<html>
<body>
  <div class="blocked-card">
    <div class="koala-avatar">🐨</div>
    <h1>Nice try! 😄</h1>
    <p>"Instagram is currently on a break."</p>
    <div class="timer">01:42</div>
    <div class="task-box">
      <span>TODAY'S HIGHEST PRIORITY TASK</span>
      <h2>Complete 3 DSA problems</h2>
      <button id="start-task-btn">Start Task 🚀</button>
    </div>
  </div>
</body>
</html>`
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="rounded-2xl bg-[#181B22] border border-[#2E333D] p-6 text-white">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#282C37]">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <span>🧩</span> Chrome & Edge Extension (Manifest V3)
          </h2>
          <p className="text-xs text-neutral-400 mt-1">
            Located in <code className="text-amber-400 bg-neutral-800 px-1.5 py-0.5 rounded">focuskoala/extension/</code>. Ready to load directly into your browser.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 font-semibold border border-emerald-500/30 flex items-center gap-1">
            <FolderCheck className="w-3.5 h-3.5" /> Manifest V3 Ready
          </span>
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex gap-2 my-4">
        {[
          { id: "install", label: "Installation Guide" },
          { id: "manifest", label: "manifest.json" },
          { id: "background", label: "background.js" },
          { id: "blocked", label: "blocked.html" },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id as any)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
              activeTab === t.id
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                : "bg-neutral-800 text-neutral-400 hover:text-white"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === "install" ? (
        <div className="space-y-4 py-2 text-sm text-neutral-300">
          <div className="p-4 rounded-xl bg-neutral-900 border border-neutral-800 space-y-3">
            <h4 className="font-bold text-white flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-amber-500 text-black flex items-center justify-center text-xs font-black">1</span>
              Load in Chrome or Edge
            </h4>
            <ol className="list-decimal list-inside space-y-2 text-xs text-neutral-300 pl-2">
              <li>Open Chrome and navigate to <code className="text-amber-400 bg-black/50 px-1.5 py-0.5 rounded">chrome://extensions</code> (or <code className="text-amber-400 bg-black/50 px-1.5 py-0.5 rounded">edge://extensions</code>).</li>
              <li>Toggle <strong>Developer mode</strong> in the top right corner.</li>
              <li>Click <strong>Load unpacked</strong> button.</li>
              <li>Select the directory: <code className="text-amber-400 bg-black/50 px-1.5 py-0.5 rounded">focuskoala/extension</code>.</li>
            </ol>
          </div>

          <div className="p-4 rounded-xl bg-neutral-900 border border-neutral-800 space-y-2">
            <h4 className="font-bold text-white flex items-center gap-2">
              <span className="w-5 h-5 rounded-full bg-amber-500 text-black flex items-center justify-center text-xs font-black">2</span>
              Start the Python Desktop Agent
            </h4>
            <div className="flex items-center justify-between bg-black/60 p-3 rounded-lg border border-neutral-800 font-mono text-xs text-amber-300">
              <code>python run.py</code>
              <button
                onClick={() => copyToClipboard("python run.py", "cmd")}
                className="text-neutral-400 hover:text-white"
              >
                {copiedKey === "cmd" ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-xs text-neutral-400">
              Starts the local FastAPI backend (`http://localhost:8000`) and the PySide6 Desktop Dashboard.
            </p>
          </div>
        </div>
      ) : (
        <div className="relative">
          <pre className="p-4 rounded-xl bg-neutral-950 border border-neutral-800 text-xs text-neutral-300 font-mono overflow-x-auto max-h-80">
            {files[activeTab as keyof typeof files]}
          </pre>
          <button
            onClick={() => copyToClipboard(files[activeTab as keyof typeof files], activeTab)}
            className="absolute top-3 right-3 p-2 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-neutral-200 transition cursor-pointer"
            title="Copy Code"
          >
            {copiedKey === activeTab ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
      )}
    </div>
  );
};
