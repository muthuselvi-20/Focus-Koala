import React, { useState } from "react";
import { X, Target, Clock, ShieldAlert } from "lucide-react";

interface FocusModeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStartFocus: (minutes: number, task: string) => void;
  defaultTask: string;
}

export const FocusModeModal: React.FC<FocusModeModalProps> = ({
  isOpen,
  onClose,
  onStartFocus,
  defaultTask,
}) => {
  const [selectedMinutes, setSelectedMinutes] = useState<number>(30);
  const [customMins, setCustomMins] = useState<string>("45");
  const [taskName, setTaskName] = useState<string>(defaultTask || "Complete 3 DSA problems");
  const [isCustom, setIsCustom] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleStart = () => {
    const mins = isCustom ? parseInt(customMins, 10) || 30 : selectedMinutes;
    onStartFocus(mins, taskName);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl bg-[#181B22] border border-[#2E333D] p-6 text-white shadow-2xl">
        <div className="flex items-center justify-between pb-3 border-b border-[#282C37]">
          <div className="flex items-center gap-2">
            <span className="text-xl">🎯</span>
            <h3 className="font-bold text-lg text-white">Start Focus Mode</h3>
          </div>
          <button onClick={onClose} className="text-neutral-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="py-4 space-y-4">
          <div>
            <label className="block text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">
              Focus Goal / Task
            </label>
            <input
              type="text"
              value={taskName}
              onChange={(e) => setTaskName(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-neutral-900 border border-neutral-700 text-sm text-white focus:border-amber-500 focus:outline-none"
              placeholder="What are you focusing on?"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">
              Duration
            </label>
            <div className="grid grid-cols-4 gap-2">
              {[30, 60, 90].map((m) => (
                <button
                  key={m}
                  onClick={() => {
                    setSelectedMinutes(m);
                    setIsCustom(false);
                  }}
                  className={`py-2 px-3 rounded-lg text-xs font-bold transition cursor-pointer ${
                    !isCustom && selectedMinutes === m
                      ? "bg-amber-500 text-black shadow"
                      : "bg-neutral-800 text-neutral-300 hover:bg-neutral-700"
                  }`}
                >
                  {m}m
                </button>
              ))}
              <button
                onClick={() => setIsCustom(true)}
                className={`py-2 px-3 rounded-lg text-xs font-bold transition cursor-pointer ${
                  isCustom
                    ? "bg-amber-500 text-black shadow"
                    : "bg-neutral-800 text-neutral-300 hover:bg-neutral-700"
                }`}
              >
                Custom
              </button>
            </div>
            {isCustom && (
              <div className="mt-3 flex items-center gap-2">
                <input
                  type="number"
                  min="5"
                  max="300"
                  value={customMins}
                  onChange={(e) => setCustomMins(e.target.value)}
                  className="w-24 px-3 py-1.5 rounded-lg bg-neutral-900 border border-neutral-700 text-sm text-white"
                />
                <span className="text-xs text-neutral-400">minutes</span>
              </div>
            )}
          </div>

          <div className="rounded-xl bg-amber-500/10 border border-amber-500/20 p-3 flex items-start gap-2.5 text-xs text-amber-300">
            <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5" />
            <span>
              All configured distracting websites (Instagram, YouTube, Reddit) will be blocked during Focus Mode.
            </span>
          </div>
        </div>

        <div className="flex gap-3 pt-2">
          <button
            onClick={handleStart}
            className="flex-1 bg-[#E58E26] hover:bg-[#F8B739] text-white font-bold py-2.5 px-4 rounded-xl text-sm transition shadow cursor-pointer"
          >
            Start {isCustom ? customMins : selectedMinutes}m Focus Session
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2.5 rounded-xl bg-neutral-800 hover:bg-neutral-700 text-sm font-semibold text-neutral-300"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};
