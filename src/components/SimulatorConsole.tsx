import React from "react";
import { Play, FastForward, ShieldAlert, RotateCcw, AlertTriangle, CheckCircle2 } from "lucide-react";

interface SimulatorConsoleProps {
  activeSite: string;
  onSelectSite: (domain: string) => void;
  timerSeconds: number;
  isSimulating: boolean;
  onToggleSimulate: () => void;
  onTriggerWarning: () => void;
  onTriggerIntervention: () => void;
  onReset: () => void;
  warningTriggered: boolean;
  blockedTriggered: boolean;
}

export const SimulatorConsole: React.FC<SimulatorConsoleProps> = ({
  activeSite,
  onSelectSite,
  timerSeconds,
  isSimulating,
  onToggleSimulate,
  onTriggerWarning,
  onTriggerIntervention,
  onReset,
  warningTriggered,
  blockedTriggered,
}) => {
  return (
    <div className="rounded-2xl bg-[#1C1F28] border border-[#2E333D] p-4 text-white shadow-xl">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        {/* Left: Status & Active Domain */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-400">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="font-bold text-sm text-white">Live Distraction Simulator</h4>
              <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Test Mode: 60s Limit
              </span>
            </div>
            <p className="text-xs text-neutral-400 mt-0.5">
              Simulates Chrome/Edge extension heartbeat & intervention flow.
            </p>
          </div>
        </div>

        {/* Center: Monitored Site Selector */}
        <div className="flex items-center gap-1.5 bg-neutral-900/80 p-1 rounded-xl border border-neutral-800">
          {[
            { domain: "instagram.com", label: "Instagram (60s)", icon: "📸" },
            { domain: "youtube.com", label: "YouTube (45m)", icon: "▶️" },
            { domain: "reddit.com", label: "Reddit (20m)", icon: "💬" },
          ].map((s) => (
            <button
              key={s.domain}
              onClick={() => onSelectSite(s.domain)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition cursor-pointer ${
                activeSite === s.domain
                  ? "bg-amber-500 text-black shadow font-bold"
                  : "text-neutral-400 hover:text-white"
              }`}
            >
              <span>{s.icon}</span>
              <span>{s.label}</span>
            </button>
          ))}
        </div>

        {/* Right: Quick Action Controls */}
        <div className="flex items-center gap-2 flex-wrap">
          <div className="px-3 py-1.5 rounded-xl bg-black/50 border border-neutral-800 font-mono text-xs text-amber-400 font-bold">
            ⏱️ {timerSeconds}s / 60s
          </div>

          <button
            onClick={onToggleSimulate}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 cursor-pointer transition shadow ${
              isSimulating
                ? "bg-red-500/20 text-red-300 border border-red-500/30 hover:bg-red-500/30"
                : "bg-emerald-600 hover:bg-emerald-500 text-white"
            }`}
          >
            {isSimulating ? "Pause Timer" : "Start Browsing"}
          </button>

          <button
            onClick={onTriggerWarning}
            className="px-2.5 py-1.5 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-amber-300 text-xs font-semibold cursor-pointer border border-neutral-700 transition"
            title="Fast forward to 30s warning"
          >
            30s Warning ⚠️
          </button>

          <button
            onClick={onTriggerIntervention}
            className="px-2.5 py-1.5 rounded-xl bg-[#E58E26] hover:bg-[#F8B739] text-white text-xs font-bold cursor-pointer transition shadow"
            title="Fast forward to 60s Koala intervention"
          >
            60s Intervention 🐨
          </button>

          <button
            onClick={onReset}
            className="p-1.5 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-neutral-400 hover:text-white transition"
            title="Reset simulation"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Real-time Status Pills */}
      <div className="mt-3 pt-3 border-t border-neutral-800/80 flex items-center justify-between text-xs text-neutral-400">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                warningTriggered ? "bg-amber-400 animate-pulse" : "bg-neutral-600"
              }`}
            ></span>
            30s Warning: {warningTriggered ? "Active" : "Pending"}
          </span>
          <span className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                blockedTriggered ? "bg-red-500 animate-pulse" : "bg-neutral-600"
              }`}
            ></span>
            60s Intervention & Cooldown: {blockedTriggered ? "Blocked" : "Clear"}
          </span>
        </div>
        <span className="text-[11px] text-neutral-500">
          Acceptance flow: 30s Warning ➔ 60s Intervention ➔ Block ➔ Cooldown ➔ Task Redirection
        </span>
      </div>
    </div>
  );
};
