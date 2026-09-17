export type KoalaMood = "idle" | "warning" | "intervention" | "happy" | "disappointed";

export interface WebsiteConfig {
  id: string;
  domain: string;
  name: string;
  limit_seconds: number;
  cooldown_seconds: number;
  enabled: boolean;
  used_seconds: number;
  is_blocked: boolean;
}

export interface TodoItem {
  id: string;
  title: string;
  completed: boolean;
  priority: "high" | "medium" | "low";
  created_at: string;
  completed_at?: string | null;
}

export interface FocusModeState {
  active: boolean;
  remaining_seconds: number;
  task: string;
}

export interface DistractionInsight {
  most_distracting_website: string;
  most_distracting_duration: string;
  peak_distraction_hour: string;
  reopen_attempts: number;
  time_recovered: string;
  tasks_completed: number;
  pattern_message: string;
}
