import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { KoalaMascot } from "./KoalaMascot";
import { KoalaMood, TodoItem } from "../types";
import { CheckCircle, Play, X, ShieldAlert, ArrowRight } from "lucide-react";

interface InterventionModalProps {
  isOpen: boolean;
  onClose: () => void;
  domain: string;
  recommendedTask: TodoItem | null;
  onStartTask: () => void;
}

export const InterventionModal: React.FC<InterventionModalProps> = ({
  isOpen,
  onClose,
  domain,
  recommendedTask,
  onStartTask,
}) => {
  const [step, setStep] = useState<number>(1);
  const [mood, setMood] = useState<KoalaMood>("warning");

  // Run the 8-step animation sequence requested in Feature 4
  useEffect(() => {
    if (!isOpen) {
      setStep(1);
      setMood("warning");
      return;
    }

    // Step 1 & 2: Koala appears & slides in (warning)
    setMood("warning");
    setStep(2);

    const t1 = setTimeout(() => {
      // Step 3 & 4: Move toward browser & points/gestures
      setStep(4);
      setMood("intervention");
    }, 900);

    const t2 = setTimeout(() => {
      // Step 5 & 6: Close gesture & tab redirected/closed
      setStep(6);
    }, 1800);

    const t3 = setTimeout(() => {
      // Step 7 & 8: Koala returns happy & Todo list appears
      setStep(8);
      setMood("happy");
    }, 2700);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.85, y: 30 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          className="relative w-full max-w-lg rounded-2xl bg-[#181B22] border-2 border-[#E58E26] shadow-2xl p-6 text-white overflow-hidden"
        >
          {/* Header Badge */}
          <div className="flex items-center justify-between pb-3 border-b border-[#282C37]">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold uppercase bg-amber-500/20 text-amber-400 border border-amber-500/30">
                🐨 FocusKoala Intervention
              </span>
              <span className="text-xs text-neutral-400">Step {step}/8</span>
            </div>
            <button
              onClick={onClose}
              className="text-neutral-400 hover:text-white p-1 rounded-lg hover:bg-neutral-800 transition"
              title="Close"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Animated Mascot Area */}
          <div className="py-6 flex flex-col items-center text-center">
            <motion.div
              animate={
                step >= 4 && step < 7
                  ? { x: [0, 20, 0], scale: [1, 1.08, 1] }
                  : step >= 7
                  ? { y: [0, -8, 0] }
                  : { x: [-30, 0] }
              }
              transition={{ duration: 0.6, repeat: step >= 7 ? Infinity : 0, repeatDelay: 1.5 }}
            >
              <KoalaMascot mood={mood} size={130} />
            </motion.div>

            <motion.h3
              key={`headline-${step}`}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-xl font-bold mt-4 text-white"
            >
              {step < 6
                ? `Time's up for ${domain.replace(".com", "")}!`
                : `${domain} is now on a break! 🛑`}
            </motion.h3>

            <motion.p
              key={`sub-${step}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm text-neutral-300 mt-1 max-w-sm"
            >
              {step < 6
                ? "Koala is intervening to protect your attention and redirect you to your goals."
                : "Distracting tab has been safely redirected to your cooldown page."}
            </motion.p>
          </div>

          {/* Step Sequence Indicator */}
          <div className="grid grid-cols-4 gap-1.5 mb-5 text-[10px] text-center font-medium">
            <div className={`p-1.5 rounded ${step >= 2 ? "bg-amber-500/20 text-amber-300 border border-amber-500/30" : "bg-neutral-800 text-neutral-500"}`}>
              1. Slide In
            </div>
            <div className={`p-1.5 rounded ${step >= 4 ? "bg-amber-500/20 text-amber-300 border border-amber-500/30" : "bg-neutral-800 text-neutral-500"}`}>
              2. Gesture
            </div>
            <div className={`p-1.5 rounded ${step >= 6 ? "bg-amber-500/20 text-amber-300 border border-amber-500/30" : "bg-neutral-800 text-neutral-500"}`}>
              3. Block Tab
            </div>
            <div className={`p-1.5 rounded ${step >= 8 ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30" : "bg-neutral-800 text-neutral-500"}`}>
              4. Todo List
            </div>
          </div>

          {/* Task-Aware Redirection Box (Feature 8) */}
          <div className="rounded-xl bg-[#222631] border border-amber-500/30 p-4 mb-5">
            <div className="flex items-center justify-between text-xs font-semibold text-amber-400 uppercase tracking-wider mb-1">
              <span>🐨 RECOMMENDED PRIORITY TASK</span>
              <span className="text-[11px] px-2 py-0.5 rounded bg-red-500/20 text-red-300 border border-red-500/30 font-bold">
                HIGH PRIORITY
              </span>
            </div>
            <div className="text-base font-bold text-white mb-1">
              {recommendedTask ? recommendedTask.title : "Complete 3 DSA problems"}
            </div>
            <p className="text-xs text-neutral-400">
              🐨 &quot;Instagram can wait. Let&apos;s finish what you planned!&quot;
            </p>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                onStartTask();
                onClose();
              }}
              className="flex-1 inline-flex items-center justify-center gap-2 bg-[#E58E26] hover:bg-[#F8B739] text-white font-bold py-3 px-4 rounded-xl shadow-lg transition-all transform hover:-translate-y-0.5 cursor-pointer text-sm"
            >
              <Play className="w-4 h-4 fill-current" />
              Start Task Now
            </button>
            <button
              onClick={onClose}
              className="px-4 py-3 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-sm font-semibold transition"
            >
              Go to Tasks
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
