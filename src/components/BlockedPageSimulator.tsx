import React, { useState, useEffect } from "react";
import { KoalaMascot } from "./KoalaMascot";
import { KoalaMood, TodoItem } from "../types";
import { Play, RotateCcw, AlertTriangle, ArrowRight, ExternalLink } from "lucide-react";

interface BlockedPageSimulatorProps {
  domain: string;
  initialRemainingSeconds: number;
  initialAttempts: number;
  recommendedTask: TodoItem | null;
  onStartTask: () => void;
  onCooldownExpired: () => void;
}

export const BlockedPageSimulator: React.FC<BlockedPageSimulatorProps> = ({
  domain,
  initialRemainingSeconds,
  initialAttempts,
  recommendedTask,
  onStartTask,
  onCooldownExpired,
}) => {
  const [remaining, setRemaining] = useState<number>(initialRemainingSeconds);
  const [attempts, setAttempts] = useState<number>(initialAttempts);

  useEffect(() => {
    setRemaining(initialRemainingSeconds);
  }, [initialRemainingSeconds]);

  useEffect(() => {
    setAttempts(initialAttempts);
  }, [initialAttempts]);

  useEffect(() => {
    if (remaining <= 0) return;
    const timer = setInterval(() => {
      setRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          onCooldownExpired();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [remaining, onCooldownExpired]);

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  // Reopen attempt messages as requested in Feature 9
  const cleanName = domain.replace(".com", "");
  const capName = cleanName.charAt(0).toUpperCase() + cleanName.slice(1);

  let headline = "Nice try! 😄";
  let koalaQuote = `"${capName} is currently on a break."`;
  let mood: KoalaMood = "warning";

  if (attempts === 1) {
    headline = "Nice try! 😄";
    koalaQuote = `"${capName} is on a break."`;
    mood = "warning";
  } else if (attempts === 2) {
    headline = "Nice try 😐";
    koalaQuote = `"${capName} can wait. Focus on your goal!"`;
    mood = "disappointed";
  } else {
    headline = `Notice from FocusKoala 🐨`;
    koalaQuote = `"You have tried opening ${capName} ${attempts} times."`;
    mood = "disappointed";
  }

  const handleSimulateReopen = () => {
    setAttempts((prev) => prev + 1);
  };

  const handleFastForward = () => {
    setRemaining(5);
  };

  return (
    <div className="rounded-2xl bg-[#14161D] border border-[#2E333D] p-6 text-white max-w-xl mx-auto shadow-2xl">
      {/* Simulation Controls Banner */}
      <div className="mb-4 pb-3 border-b border-neutral-800 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></span>
          <span className="font-semibold text-neutral-300">Live Blocked Page Preview (`blocked.html`)</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleSimulateReopen}
            className="px-2.5 py-1 rounded bg-neutral-800 hover:bg-neutral-700 text-amber-300 text-xs font-medium cursor-pointer transition"
          >
            + Try Reopen ({attempts})
          </button>
          <button
            onClick={handleFastForward}
            className="px-2.5 py-1 rounded bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-xs font-medium cursor-pointer transition"
          >
            ⏩ Fast-Forward (5s)
          </button>
        </div>
      </div>

      <div className="text-center py-2">
        <KoalaMascot mood={mood} size={110} className="mx-auto" />
        <div className="mt-3 inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-500/15 text-amber-400 border border-amber-500/30">
          Cooldown Active &bull; Reopen Attempt {attempts}
        </div>

        <h2 className="text-2xl font-black mt-3 text-white">{headline}</h2>
        <p className="text-sm italic text-neutral-400 mt-1">{koalaQuote}</p>
      </div>

      {/* Countdown Timer */}
      <div className="my-5 p-4 rounded-xl bg-black/40 border border-neutral-800 text-center">
        <div className="text-[11px] font-bold tracking-widest text-neutral-400 uppercase">
          REMAINING COOLDOWN
        </div>
        <div className="text-5xl font-extrabold font-mono text-amber-400 my-1 tracking-wider">
          {formatTime(remaining)}
        </div>
        <p className="text-xs text-neutral-500">
          {remaining > 0 ? "Access is persistently blocked until cooldown expires." : "Access restored!"}
        </p>
      </div>

      {/* Today's Recommended Task */}
      <div className="rounded-xl bg-amber-500/5 border border-amber-500/25 p-4 mb-5 text-left">
        <div className="text-[10px] font-bold text-amber-400 tracking-wider uppercase mb-1">
          TODAY&apos;S HIGHEST PRIORITY TASK
        </div>
        <div className="text-lg font-bold text-white">
          {recommendedTask ? recommendedTask.title : "Complete 3 DSA problems"}
        </div>
        <p className="text-xs text-neutral-400 mt-0.5">
          FocusKoala believes in you. Let&apos;s make real progress instead of scrolling!
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={onStartTask}
          className="flex-1 inline-flex items-center justify-center gap-2 bg-[#E58E26] hover:bg-[#F8B739] text-white font-bold py-3 px-4 rounded-xl shadow-lg transition cursor-pointer"
        >
          <Play className="w-4 h-4 fill-current" />
          Start Task 🚀
        </button>
      </div>
    </div>
  );
};
