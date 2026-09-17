import React, { useState, useEffect } from "react";
import {
  ShieldAlert,
  Clock,
  CheckSquare,
  BarChart3,
  Globe,
  Play,
  RotateCcw,
  Sparkles,
  Flame,
  ArrowRight,
  TrendingDown,
  Info,
  Code2,
  Sliders,
  Settings,
  AlertTriangle,
  Zap,
} from "lucide-react";
import { KoalaMascot } from "./components/KoalaMascot";
import { InterventionModal } from "./components/InterventionModal";
import { BlockedPageSimulator } from "./components/BlockedPageSimulator";
import { SimulatorConsole } from "./components/SimulatorConsole";
import { TodoSection } from "./components/TodoSection";
import { ExtensionViewer } from "./components/ExtensionViewer";
import { FocusModeModal } from "./components/FocusModeModal";
import { KoalaMood, TodoItem, WebsiteConfig, DistractionInsight, FocusModeState } from "./types";

export default function App() {
  // Navigation
  const [activeTab, setActiveTab] = useState<"dashboard" | "simulator" | "mascot" | "tasks" | "insights" | "websites" | "extension">("dashboard");

  // Koala State
  const [mascotMood, setMascotMood] = useState<KoalaMood>("idle");

  // Website Configs
  const [websites, setWebsites] = useState<WebsiteConfig[]>([
    {
      id: "ig",
      domain: "instagram.com",
      name: "Instagram",
      limit_seconds: 60,
      cooldown_seconds: 120,
      enabled: true,
      used_seconds: 31 * 60,
      is_blocked: false,
    },
    {
      id: "yt",
      domain: "youtube.com",
      name: "YouTube",
      limit_seconds: 2700,
      cooldown_seconds: 1800,
      enabled: true,
      used_seconds: 18 * 60,
      is_blocked: false,
    },
    {
      id: "rd",
      domain: "reddit.com",
      name: "Reddit",
      limit_seconds: 1200,
      cooldown_seconds: 1800,
      enabled: true,
      used_seconds: 7 * 60,
      is_blocked: false,
    },
  ]);

  // Todo Items (Feature 7 & 8)
  const [todos, setTodos] = useState<TodoItem[]>([
    {
      id: "1",
      title: "Complete 3 DSA problems",
      completed: false,
      priority: "high",
      created_at: new Date().toISOString(),
    },
    {
      id: "2",
      title: "Study Random Forest",
      completed: false,
      priority: "medium",
      created_at: new Date().toISOString(),
    },
    {
      id: "3",
      title: "Finish ML project",
      completed: false,
      priority: "high",
      created_at: new Date().toISOString(),
    },
    {
      id: "4",
      title: "Revise Python OOP",
      completed: true,
      priority: "low",
      created_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
    },
  ]);

  // Focus Mode State (Feature 12)
  const [focusMode, setFocusMode] = useState<FocusModeState>({
    active: false,
    remaining_seconds: 0,
    task: "",
  });
  const [isFocusModalOpen, setIsFocusModalOpen] = useState(false);

  // Distraction Simulator State
  const [simDomain, setSimDomain] = useState<string>("instagram.com");
  const [simTimer, setSimTimer] = useState<number>(0);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [simWarningActive, setSimWarningActive] = useState<boolean>(false);
  const [simBlockedActive, setSimBlockedActive] = useState<boolean>(false);
  const [simAttempts, setSimAttempts] = useState<number>(1);
  const [isInterventionModalOpen, setIsInterventionModalOpen] = useState<boolean>(false);

  // Floating in-page warning banner (Feature 3)
  const [showWarningBanner, setShowWarningBanner] = useState<boolean>(false);

  // Top recommended incomplete task (Feature 8)
  const topTask = todos.find((t) => !t.completed && t.priority === "high") ||
    todos.find((t) => !t.completed) ||
    null;

  // Simulator interval loop
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isSimulating) {
      interval = setInterval(() => {
        setSimTimer((prev) => {
          const next = prev + 1;

          // 30 seconds -> warning in test mode (Feature 3)
          if (next >= 30 && next < 60 && !simWarningActive) {
            setSimWarningActive(true);
            setShowWarningBanner(true);
            setMascotMood("warning");
          }

          // 60 seconds -> limit reached, intervention trigger! (Feature 3 & 4)
          if (next >= 60 && !simBlockedActive) {
            setIsSimulating(false);
            setSimBlockedActive(true);
            setIsInterventionModalOpen(true);
            setMascotMood("intervention");
            // Mark site as blocked
            setWebsites((current) =>
              current.map((w) => (w.domain === simDomain ? { ...w, is_blocked: true } : w))
            );
            return 60;
          }

          return next;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isSimulating, simWarningActive, simBlockedActive, simDomain]);

  // Focus mode countdown
  useEffect(() => {
    let fTimer: NodeJS.Timeout;
    if (focusMode.active && focusMode.remaining_seconds > 0) {
      fTimer = setInterval(() => {
        setFocusMode((prev) => {
          if (prev.remaining_seconds <= 1) {
            return { active: false, remaining_seconds: 0, task: "" };
          }
          return { ...prev, remaining_seconds: prev.remaining_seconds - 1 };
        });
      }, 1000);
    }
    return () => clearInterval(fTimer);
  }, [focusMode.active, focusMode.remaining_seconds]);

  // Simulation Controls
  const handleTrigger30sWarning = () => {
    setSimTimer(30);
    setSimWarningActive(true);
    setShowWarningBanner(true);
    setMascotMood("warning");
  };

  const handleTrigger60sIntervention = () => {
    setSimTimer(60);
    setIsSimulating(false);
    setSimBlockedActive(true);
    setIsInterventionModalOpen(true);
    setMascotMood("intervention");
    setWebsites((current) =>
      current.map((w) => (w.domain === simDomain ? { ...w, is_blocked: true } : w))
    );
  };

  const handleResetSimulation = () => {
    setIsSimulating(false);
    setSimTimer(0);
    setSimWarningActive(false);
    setSimBlockedActive(false);
    setShowWarningBanner(false);
    setIsInterventionModalOpen(false);
    setMascotMood("idle");
    setWebsites((current) => current.map((w) => ({ ...w, is_blocked: false })));
  };

  const handleStartFocusMode = (minutes: number, task: string) => {
    setFocusMode({
      active: true,
      remaining_seconds: minutes * 60,
      task,
    });
    setWebsites((current) => current.map((w) => ({ ...w, is_blocked: true })));
  };

  const handleStopFocusMode = () => {
    setFocusMode({ active: false, remaining_seconds: 0, task: "" });
    setWebsites((current) => current.map((w) => ({ ...w, is_blocked: false })));
  };

  const handleToggleTodo = (id: string) => {
    setTodos((prev) =>
      prev.map((t) =>
        t.id === id
          ? {
              ...t,
              completed: !t.completed,
              completed_at: !t.completed ? new Date().toISOString() : null,
            }
          : t
      )
    );
  };

  const handleAddTodo = (title: string, priority: "high" | "medium" | "low") => {
    const newItem: TodoItem = {
      id: String(Date.now()),
      title,
      completed: false,
      priority,
      created_at: new Date().toISOString(),
    };
    setTodos((prev) => [newItem, ...prev]);
  };

  const handleDeleteTodo = (id: string) => {
    setTodos((prev) => prev.filter((t) => t.id !== id));
  };

  // Format time mm:ss
  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div className="min-h-screen bg-[#0F1117] text-neutral-100 flex flex-col font-sans">
      {/* Top Floating Warning Banner (Simulation of extension content.js) */}
      {showWarningBanner && (
        <div className="fixed top-4 right-4 z-40 bg-[#1E1B18]/95 border border-[#E58E26] text-white py-2.5 px-4 rounded-xl shadow-2xl flex items-center gap-3 animate-bounce">
          <span className="text-2xl">🐨</span>
          <div>
            <div className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">
              FocusKoala Warning (30s reached)
            </div>
            <div className="text-xs font-medium">
              &quot;You have 30 seconds left on {simDomain}.&quot;
            </div>
          </div>
          <button
            onClick={() => setShowWarningBanner(false)}
            className="text-neutral-400 hover:text-white text-xs ml-2 cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}

      {/* Main Header */}
      <header className="border-b border-[#222733] bg-[#141720]/90 backdrop-blur sticky top-0 z-30 px-6 py-3.5">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <KoalaMascot mood={mascotMood} size={42} />
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-black tracking-tight text-white">FocusKoala</h1>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  Agent v1.0
                </span>
              </div>
              <p className="text-xs text-neutral-400">
                Desktop Productivity Agent &bull; Distraction Guard &bull; Task Redirection
              </p>
            </div>
          </div>

          {/* Quick Active Focus Mode Bar */}
          {focusMode.active ? (
            <div className="flex items-center gap-3 bg-amber-500/10 border border-amber-500/30 px-3.5 py-1.5 rounded-xl">
              <span className="text-amber-400 font-mono font-bold text-sm">
                🎯 {formatTime(focusMode.remaining_seconds)}
              </span>
              <span className="text-xs text-neutral-300 max-w-xs truncate font-medium">
                {focusMode.task}
              </span>
              <button
                onClick={handleStopFocusMode}
                className="text-xs text-red-400 hover:text-red-300 font-semibold cursor-pointer underline ml-1"
              >
                End
              </button>
            </div>
          ) : (
            <button
              onClick={() => setIsFocusModalOpen(true)}
              className="inline-flex items-center gap-1.5 bg-[#E58E26] hover:bg-[#F8B739] text-white text-xs font-bold px-3.5 py-2 rounded-xl shadow transition cursor-pointer"
            >
              <Zap className="w-3.5 h-3.5" /> Start Focus Mode
            </button>
          )}
        </div>
      </header>

      {/* Navigation Sub-bar */}
      <div className="border-b border-[#222733] bg-[#10121A] px-6 py-2">
        <div className="max-w-7xl mx-auto flex gap-2 overflow-x-auto text-xs font-medium">
          {[
            { id: "dashboard", label: "📊 Dashboard Overview" },
            { id: "simulator", label: "🧪 Live Acceptance Simulator" },
            { id: "mascot", label: "🐨 Koala Mascot & Animations" },
            { id: "tasks", label: "📝 Today's Tasks" },
            { id: "insights", label: "💡 Distraction Patterns & Insights" },
            { id: "websites", label: "🌐 Website Limits (60s Test)" },
            { id: "extension", label: "🧩 Chrome / Edge Extension" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3 py-1.5 rounded-lg whitespace-nowrap transition cursor-pointer ${
                activeTab === tab.id
                  ? "bg-amber-500/20 text-amber-300 font-bold border border-amber-500/40"
                  : "text-neutral-400 hover:text-neutral-200 hover:bg-neutral-800"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Interactive Simulator Console Header (Always visible for testing convenience) */}
        <SimulatorConsole
          activeSite={simDomain}
          onSelectSite={(domain) => {
            setSimDomain(domain);
            handleResetSimulation();
          }}
          timerSeconds={simTimer}
          isSimulating={isSimulating}
          onToggleSimulate={() => setIsSimulating(!isSimulating)}
          onTriggerWarning={handleTrigger30sWarning}
          onTriggerIntervention={handleTrigger60sIntervention}
          onReset={handleResetSimulation}
          warningTriggered={simWarningActive}
          blockedTriggered={simBlockedActive}
        />

        {/* TAB 1: MAIN DASHBOARD OVERVIEW */}
        {activeTab === "dashboard" && (
          <div className="space-y-6">
            {/* 4 Core Metric Cards (Feature 11 & 13) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="rounded-2xl bg-[#181B22] border border-[#282C37] border-t-4 border-t-emerald-500 p-5">
                <div className="flex items-center justify-between text-neutral-400 text-xs font-bold uppercase tracking-wider">
                  <span>Today&apos;s Focus</span>
                  <Clock className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="text-3xl font-extrabold text-white mt-2">2h 18m</div>
                <p className="text-xs text-emerald-400 mt-1 flex items-center gap-1">
                  <Sparkles className="w-3 h-3" /> +35m from focused work
                </p>
              </div>

              <div className="rounded-2xl bg-[#181B22] border border-[#282C37] border-t-4 border-t-red-500 p-5">
                <div className="flex items-center justify-between text-neutral-400 text-xs font-bold uppercase tracking-wider">
                  <span>Today&apos;s Distraction</span>
                  <TrendingDown className="w-4 h-4 text-red-400" />
                </div>
                <div className="text-3xl font-extrabold text-white mt-2">31m</div>
                <p className="text-xs text-neutral-400 mt-1">
                  Across Instagram, YouTube, Reddit
                </p>
              </div>

              <div className="rounded-2xl bg-[#181B22] border border-[#282C37] border-t-4 border-t-amber-500 p-5">
                <div className="flex items-center justify-between text-neutral-400 text-xs font-bold uppercase tracking-wider">
                  <span>Time Recovered</span>
                  <Flame className="w-4 h-4 text-amber-400" />
                </div>
                <div className="text-3xl font-extrabold text-amber-400 mt-2">47m</div>
                <p className="text-xs text-amber-300 mt-1">
                  🐨 &quot;You recovered 47 minutes today!&quot;
                </p>
              </div>

              <div className="rounded-2xl bg-[#181B22] border border-[#282C37] border-t-4 border-t-blue-500 p-5">
                <div className="flex items-center justify-between text-neutral-400 text-xs font-bold uppercase tracking-wider">
                  <span>Tasks Completed</span>
                  <CheckSquare className="w-4 h-4 text-blue-400" />
                </div>
                <div className="text-3xl font-extrabold text-white mt-2">
                  {todos.filter((t) => t.completed).length}
                </div>
                <p className="text-xs text-blue-300 mt-1">
                  {todos.filter((t) => !t.completed).length} tasks remaining
                </p>
              </div>
            </div>

            {/* Two Columns: Website Usage & Today's Tasks */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Website Usage Card */}
              <div className="rounded-2xl bg-[#181B22] border border-[#2E333D] p-5">
                <div className="flex items-center justify-between pb-3 border-b border-[#282C37]">
                  <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4 text-amber-400" />
                    <h3 className="font-bold text-base text-white">Website Usage</h3>
                  </div>
                  <button
                    onClick={() => setActiveTab("websites")}
                    className="text-xs text-amber-400 hover:underline cursor-pointer"
                  >
                    Configure Limits &rarr;
                  </button>
                </div>

                <div className="space-y-3 mt-4">
                  {websites.map((w) => {
                    const mins = Math.round(w.used_seconds / 60);
                    const limitMins = Math.round(w.limit_seconds / 60);
                    const pct = Math.min(100, Math.round((w.used_seconds / w.limit_seconds) * 100));

                    return (
                      <div
                        key={w.id}
                        className="p-3.5 rounded-xl bg-neutral-900 border border-neutral-800 space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-base font-bold text-white">{w.name}</span>
                            <span className="text-xs text-neutral-400">({w.domain})</span>
                          </div>

                          <div className="flex items-center gap-2">
                            {w.is_blocked ? (
                              <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase bg-red-500/20 text-red-300 border border-red-500/30">
                                🛑 BLOCKED
                              </span>
                            ) : (
                              <span className="text-xs font-bold text-neutral-200">
                                {w.limit_seconds === 60 ? `${w.limit_seconds}s limit (test)` : `${mins}m / ${limitMins}m`}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Progress Bar */}
                        <div className="w-full bg-neutral-800 h-2 rounded-full overflow-hidden">
                          <div
                            className={`h-full transition-all duration-500 ${
                              w.is_blocked
                                ? "bg-red-500"
                                : pct >= 80
                                ? "bg-amber-500"
                                : "bg-emerald-500"
                            }`}
                            style={{ width: `${w.is_blocked ? 100 : pct}%` }}
                          ></div>
                        </div>

                        <div className="flex justify-between text-[11px] text-neutral-400">
                          <span>Cooldown: {w.cooldown_seconds < 120 ? `${w.cooldown_seconds}s` : `${w.cooldown_seconds / 60}m`}</span>
                          <span>{w.is_blocked ? "Cooldown in progress" : `${100 - pct}% remaining`}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Tasks Preview */}
              <TodoSection
                todos={todos}
                onToggleTodo={handleToggleTodo}
                onAddTodo={handleAddTodo}
                onDeleteTodo={handleDeleteTodo}
              />
            </div>

            {/* Pattern Advice Banner (Feature 10) */}
            <div className="rounded-2xl bg-amber-500/10 border border-amber-500/30 p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <KoalaMascot mood="idle" size={56} />
                <div>
                  <h4 className="font-bold text-sm text-amber-300 uppercase tracking-wide">
                    Distraction Pattern Engine Detected:
                  </h4>
                  <p className="text-sm font-semibold text-white mt-0.5">
                    🐨 &quot;You often lose focus around 2 PM. Your DSA task is waiting.&quot;
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsFocusModalOpen(true)}
                className="bg-[#E58E26] hover:bg-[#F8B739] text-white font-bold text-xs py-2 px-4 rounded-xl shadow cursor-pointer transition whitespace-nowrap"
              >
                Start Focus Mode 🎯
              </button>
            </div>
          </div>
        )}

        {/* TAB 2: LIVE ACCEPTANCE SIMULATOR */}
        {activeTab === "simulator" && (
          <div className="space-y-6">
            <div className="p-4 rounded-2xl bg-[#181B22] border border-[#2E333D] text-xs text-neutral-300">
              <h3 className="text-sm font-bold text-white mb-1">
                🎯 Core User Journey Acceptance Test
              </h3>
              <p className="text-neutral-400 mb-3">
                Watch the exact user flow requested in the specification happen in real-time:
              </p>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-2 text-center text-[11px] font-medium">
                <div className={`p-2 rounded-lg border ${simTimer > 0 ? "bg-neutral-800 border-amber-500/50 text-amber-300" : "bg-neutral-900 border-neutral-800 text-neutral-500"}`}>
                  1. Open Instagram
                </div>
                <div className={`p-2 rounded-lg border ${simTimer >= 30 ? "bg-neutral-800 border-amber-500/50 text-amber-300" : "bg-neutral-900 border-neutral-800 text-neutral-500"}`}>
                  2. 30s Warning
                </div>
                <div className={`p-2 rounded-lg border ${simTimer >= 60 ? "bg-neutral-800 border-amber-500/50 text-amber-300" : "bg-neutral-900 border-neutral-800 text-neutral-500"}`}>
                  3. 60s Intervention
                </div>
                <div className={`p-2 rounded-lg border ${simBlockedActive ? "bg-neutral-800 border-red-500/50 text-red-300" : "bg-neutral-900 border-neutral-800 text-neutral-500"}`}>
                  4. Tab Blocked
                </div>
                <div className={`p-2 rounded-lg border ${simBlockedActive ? "bg-neutral-800 border-amber-500/50 text-amber-300" : "bg-neutral-900 border-neutral-800 text-neutral-500"}`}>
                  5. Cooldown 120s
                </div>
                <div className={`p-2 rounded-lg border ${simBlockedActive ? "bg-neutral-800 border-emerald-500/50 text-emerald-300" : "bg-neutral-900 border-neutral-800 text-neutral-500"}`}>
                  6. Task Redirection
                </div>
              </div>
            </div>

            {simBlockedActive ? (
              <BlockedPageSimulator
                domain={simDomain}
                initialRemainingSeconds={120}
                initialAttempts={simAttempts}
                recommendedTask={topTask}
                onStartTask={() => {
                  setActiveTab("tasks");
                }}
                onCooldownExpired={() => {
                  setSimBlockedActive(false);
                  setSimTimer(0);
                  setWebsites((curr) =>
                    curr.map((w) => (w.domain === simDomain ? { ...w, is_blocked: false } : w))
                  );
                }}
              />
            ) : (
              <div className="text-center py-16 px-4 rounded-2xl bg-[#14161D] border border-[#2E333D]">
                <KoalaMascot mood={mascotMood} size={110} className="mx-auto" />
                <h3 className="text-lg font-bold text-white mt-4">
                  {simTimer === 0
                    ? "Ready to test FocusKoala?"
                    : `Tracking ${simDomain}: ${simTimer} seconds`}
                </h3>
                <p className="text-xs text-neutral-400 mt-1 max-w-md mx-auto">
                  Click &apos;Start Browsing&apos; or jump directly to &apos;30s Warning&apos; or &apos;60s Intervention&apos; using the simulator console above.
                </p>

                <div className="flex items-center justify-center gap-3 mt-6">
                  <button
                    onClick={() => setIsSimulating(!isSimulating)}
                    className="bg-[#E58E26] hover:bg-[#F8B739] text-white font-bold py-2.5 px-6 rounded-xl text-xs transition cursor-pointer shadow"
                  >
                    {isSimulating ? "Pause Simulation" : "Start Browsing Instagram (60s Test)"}
                  </button>
                  <button
                    onClick={handleTrigger60sIntervention}
                    className="bg-neutral-800 hover:bg-neutral-700 text-neutral-200 font-semibold py-2.5 px-5 rounded-xl text-xs transition cursor-pointer border border-neutral-700"
                  >
                    Trigger 60s Intervention Now
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 3: KOALA MASCOT & ANIMATION STUDIO */}
        {activeTab === "mascot" && (
          <div className="space-y-6">
            <div className="rounded-2xl bg-[#181B22] border border-[#2E333D] p-6">
              <h3 className="text-lg font-bold text-white">
                🐨 2D Animated Koala Mascot Showcase (Feature 4)
              </h3>
              <p className="text-xs text-neutral-400 mt-1">
                FocusKoala communicates clearly through 5 distinct emotional states and fluid 8-step intervention animations.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-5 gap-4 mt-6">
                {[
                  { mood: "idle", label: "Idle State", desc: "Gentle smile, waiting" },
                  { mood: "warning", label: "Warning State", desc: "Alert eyebrows, 30s left" },
                  { mood: "intervention", label: "Intervention State", desc: "Pointing paw & break tag" },
                  { mood: "happy", label: "Happy State", desc: "Rosy cheeks, sparkles" },
                  { mood: "disappointed", label: "Disappointed State", desc: "Half-lidded: Nice try 😐" },
                ].map((item) => (
                  <button
                    key={item.mood}
                    onClick={() => setMascotMood(item.mood as any)}
                    className={`p-4 rounded-xl border flex flex-col items-center text-center transition cursor-pointer ${
                      mascotMood === item.mood
                        ? "bg-amber-500/15 border-amber-500 text-amber-300"
                        : "bg-neutral-900 border-neutral-800 text-neutral-400 hover:border-neutral-700 hover:text-white"
                    }`}
                  >
                    <KoalaMascot mood={item.mood as any} size={90} />
                    <div className="font-bold text-xs mt-3 text-white">{item.label}</div>
                    <div className="text-[11px] text-neutral-400 mt-1">{item.desc}</div>
                  </button>
                ))}
              </div>

              <div className="mt-6 pt-5 border-t border-neutral-800 flex items-center justify-between">
                <div>
                  <h4 className="font-bold text-sm text-white">
                    Test the 8-Step Intervention Sequence
                  </h4>
                  <p className="text-xs text-neutral-400">
                    1. Appears &rarr; 2. Slides in &rarr; 3. Moves to browser &rarr; 4. Gestures &rarr; 5. Closes tab &rarr; 6. Block &rarr; 7. Returns &rarr; 8. Todo list
                  </p>
                </div>
                <button
                  onClick={() => setIsInterventionModalOpen(true)}
                  className="bg-[#E58E26] hover:bg-[#F8B739] text-white text-xs font-bold py-2.5 px-4 rounded-xl cursor-pointer transition shadow"
                >
                  Play Intervention Sequence 🎬
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: TASKS & TASK-AWARE REDIRECTION */}
        {activeTab === "tasks" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <TodoSection
                todos={todos}
                onToggleTodo={handleToggleTodo}
                onAddTodo={handleAddTodo}
                onDeleteTodo={handleDeleteTodo}
              />
            </div>

            {/* Task-Aware Redirection Card (Feature 8) */}
            <div className="space-y-4">
              <div className="rounded-2xl bg-gradient-to-b from-[#1E232F] to-[#161822] border border-amber-500/30 p-5">
                <div className="flex items-center gap-2 text-xs font-bold text-amber-400 uppercase tracking-wider mb-2">
                  <Sparkles className="w-4 h-4" /> Feature 8: Task-Aware Redirection
                </div>
                <p className="text-xs text-neutral-300">
                  When a distracting site is blocked, FocusKoala automatically extracts your highest-priority incomplete task and redirects your momentum directly into it.
                </p>

                <div className="mt-4 p-3.5 rounded-xl bg-neutral-900/90 border border-neutral-800">
                  <div className="text-[10px] text-amber-400 font-bold uppercase">
                    CURRENT RECOMMENDED TASK
                  </div>
                  <div className="text-base font-bold text-white mt-1">
                    {topTask ? topTask.title : "All tasks complete! Great job!"}
                  </div>
                  <div className="text-xs text-neutral-400 mt-1">
                    Priority: <span className="font-bold text-amber-300">{topTask?.priority.toUpperCase() || "N/A"}</span>
                  </div>
                </div>

                <button
                  onClick={() => handleTrigger60sIntervention()}
                  className="w-full mt-4 bg-neutral-800 hover:bg-neutral-700 text-amber-300 font-bold text-xs py-2.5 rounded-xl border border-neutral-700 transition cursor-pointer"
                >
                  Test Redirection on Instagram Block
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: INSIGHTS & PATTERN ENGINE */}
        {activeTab === "insights" && (
          <div className="space-y-6">
            <div className="rounded-2xl bg-[#181B22] border border-[#2E333D] p-6">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <span>🐨</span> Your Insights (Feature 10 & 14)
              </h3>
              <p className="text-xs text-neutral-400 mt-1">
                Rule-based statistical pattern detection (no external LLM/cloud APIs).
              </p>

              {/* Pattern Advice Card */}
              <div className="my-5 p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
                <div className="text-xs font-bold text-amber-400 uppercase tracking-wider">
                  STATISTICAL PATTERN DETECTED
                </div>
                <div className="text-base font-bold text-white mt-1">
                  🐨 &quot;You often lose focus around 2 PM.&quot;
                </div>
                <p className="text-xs text-neutral-300 mt-1">
                  &quot;Your {topTask?.title || "next task"} is waiting.&quot;
                </p>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-neutral-900 border border-neutral-800">
                  <div className="text-[11px] font-bold text-neutral-400 uppercase">Most Distracting</div>
                  <div className="text-xl font-bold text-white mt-1">Instagram — 42m</div>
                </div>
                <div className="p-4 rounded-xl bg-neutral-900 border border-neutral-800">
                  <div className="text-[11px] font-bold text-neutral-400 uppercase">Peak Distraction</div>
                  <div className="text-xl font-bold text-white mt-1">2 PM</div>
                </div>
                <div className="p-4 rounded-xl bg-neutral-900 border border-neutral-800">
                  <div className="text-[11px] font-bold text-neutral-400 uppercase">Reopen Attempts</div>
                  <div className="text-xl font-bold text-white mt-1">5</div>
                </div>
                <div className="p-4 rounded-xl bg-neutral-900 border border-neutral-800">
                  <div className="text-[11px] font-bold text-neutral-400 uppercase">Time Recovered</div>
                  <div className="text-xl font-bold text-amber-400 mt-1">47m</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 6: WEBSITE LIMITS & RULES */}
        {activeTab === "websites" && (
          <div className="rounded-2xl bg-[#181B22] border border-[#2E333D] p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#282C37]">
              <div>
                <h3 className="text-lg font-bold text-white">Website Limits & Rules</h3>
                <p className="text-xs text-neutral-400">
                  Configure distracting websites, limits, and cooldowns.
                </p>
              </div>
              <span className="text-xs font-bold px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                Test Mode: Instagram 60s / 120s cooldown
              </span>
            </div>

            <div className="divide-y divide-neutral-800">
              {websites.map((site) => (
                <div key={site.id} className="py-4 flex items-center justify-between">
                  <div>
                    <div className="font-bold text-sm text-white">{site.name}</div>
                    <div className="text-xs text-neutral-400">{site.domain}</div>
                  </div>

                  <div className="flex items-center gap-6 text-xs">
                    <div>
                      <span className="text-neutral-500 block text-[10px] uppercase font-bold">Limit</span>
                      <span className="text-white font-semibold">
                        {site.limit_seconds < 120 ? `${site.limit_seconds}s (test)` : `${site.limit_seconds / 60}m`}
                      </span>
                    </div>

                    <div>
                      <span className="text-neutral-500 block text-[10px] uppercase font-bold">Cooldown</span>
                      <span className="text-white font-semibold">
                        {site.cooldown_seconds < 120 ? `${site.cooldown_seconds}s` : `${site.cooldown_seconds / 60}m`}
                      </span>
                    </div>

                    <div>
                      <span className="text-neutral-500 block text-[10px] uppercase font-bold">Status</span>
                      <span className="text-emerald-400 font-semibold">Enabled</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 7: EXTENSION & INSTALLATION */}
        {activeTab === "extension" && <ExtensionViewer />}
      </main>

      {/* Intervention Modal (Full Koala Animation Sequence) */}
      <InterventionModal
        isOpen={isInterventionModalOpen}
        onClose={() => setIsInterventionModalOpen(false)}
        domain={simDomain}
        recommendedTask={topTask}
        onStartTask={() => {
          setIsInterventionModalOpen(false);
          setActiveTab("tasks");
        }}
      />

      {/* Focus Mode Configuration Dialog */}
      <FocusModeModal
        isOpen={isFocusModalOpen}
        onClose={() => setIsFocusModalOpen(false)}
        onStartFocus={handleStartFocusMode}
        defaultTask={topTask?.title || "Complete 3 DSA problems"}
      />
    </div>
  );
}
