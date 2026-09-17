import React, { useState } from "react";
import { TodoItem } from "../types";
import { Check, Plus, Trash2, Tag, AlertCircle } from "lucide-react";

interface TodoSectionProps {
  todos: TodoItem[];
  onToggleTodo: (id: string) => void;
  onAddTodo: (title: string, priority: "high" | "medium" | "low") => void;
  onDeleteTodo: (id: string) => void;
}

export const TodoSection: React.FC<TodoSectionProps> = ({
  todos,
  onToggleTodo,
  onAddTodo,
  onDeleteTodo,
}) => {
  const [newTitle, setNewTitle] = useState("");
  const [priority, setPriority] = useState<"high" | "medium" | "low">("medium");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    onAddTodo(newTitle.trim(), priority);
    setNewTitle("");
  };

  const priorityColors = {
    high: "text-red-400 bg-red-500/10 border-red-500/30",
    medium: "text-amber-400 bg-amber-500/10 border-amber-500/30",
    low: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
  };

  return (
    <div className="rounded-2xl bg-[#181B22] border border-[#2E333D] p-5 text-white">
      <div className="flex items-center justify-between pb-3 border-b border-[#282C37]">
        <div className="flex items-center gap-2">
          <span className="text-lg">📝</span>
          <h3 className="font-bold text-base text-white">Today&apos;s Tasks</h3>
        </div>
        <span className="text-xs text-neutral-400">
          {todos.filter((t) => t.completed).length}/{todos.length} completed
        </span>
      </div>

      {/* Add Task Form */}
      <form onSubmit={handleSubmit} className="flex gap-2 my-4">
        <input
          type="text"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          placeholder="Add a new task..."
          className="flex-1 px-3 py-2 rounded-xl bg-neutral-900 border border-neutral-700 text-xs text-white placeholder-neutral-500 focus:border-amber-500 focus:outline-none"
        />
        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value as any)}
          className="px-2.5 py-2 rounded-xl bg-neutral-900 border border-neutral-700 text-xs text-white"
        >
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <button
          type="submit"
          className="px-4 py-2 rounded-xl bg-[#E58E26] hover:bg-[#F8B739] text-white font-bold text-xs flex items-center gap-1 cursor-pointer transition shadow"
        >
          <Plus className="w-3.5 h-3.5" /> Add
        </button>
      </form>

      {/* Task List */}
      <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
        {todos.map((todo) => (
          <div
            key={todo.id}
            className={`flex items-center justify-between p-3 rounded-xl border transition ${
              todo.completed
                ? "bg-neutral-900/40 border-neutral-800 opacity-60"
                : "bg-neutral-900/90 border-neutral-800 hover:border-neutral-700"
            }`}
          >
            <div className="flex items-center gap-3 flex-1 min-w-0 mr-2">
              <button
                onClick={() => onToggleTodo(todo.id)}
                className={`w-5 h-5 rounded-md flex items-center justify-center border cursor-pointer transition ${
                  todo.completed
                    ? "bg-emerald-500 border-emerald-500 text-white"
                    : "border-neutral-600 hover:border-amber-500 bg-neutral-800"
                }`}
              >
                {todo.completed && <Check className="w-3.5 h-3.5 stroke-[3]" />}
              </button>
              <span
                className={`text-xs font-medium truncate ${
                  todo.completed ? "line-through text-neutral-500" : "text-neutral-200"
                }`}
              >
                {todo.title}
              </span>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                  priorityColors[todo.priority]
                }`}
              >
                {todo.priority}
              </span>
              <button
                onClick={() => onDeleteTodo(todo.id)}
                className="text-neutral-500 hover:text-red-400 p-1 rounded transition"
                title="Delete task"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
