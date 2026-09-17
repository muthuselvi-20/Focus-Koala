"""
FocusKoala FastAPI Server
Provides local REST API endpoints for the Chrome/Edge extension and desktop client.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os

from focuskoala.desktop.agent import FocusKoalaAgent
from focuskoala.desktop.rules import normalize_domain
from focuskoala.api.schemas import (
    TrackUsageRequest,
    WebsiteCreateRequest,
    WebsiteUpdateRequest,
    TodoCreateRequest,
    TodoUpdateRequest,
    FocusModeRequest
)

agent = FocusKoalaAgent()

app = FastAPI(
    title="FocusKoala Agent API",
    description="Local productivity agent backend for FocusKoala browser extension and desktop UI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "agent": "FocusKoala 🐨", "version": "1.0.0"}


# --- Tracking & Limits ---
@app.post("/api/track")
def track_usage(req: TrackUsageRequest):
    """
    Called by browser extension to report active browsing on monitored domain.
    Returns status, warning flag, should_block flag, and recommended task if blocked.
    """
    result = agent.process_heartbeat(req.domain, req.duration_seconds)
    return result


@app.get("/api/check-block")
def check_block(domain: str = Query(..., description="Domain to check"), record_attempt: bool = Query(False)):
    """
    Checks if a domain is blocked. If record_attempt is True (user navigated to blocked URL),
    increments reopen attempt counter and returns dynamic Koala message + highest priority todo!
    """
    clean = normalize_domain(domain)
    if record_attempt:
        return agent.blocker.record_reopen_attempt(clean)
    else:
        status = agent.blocker.is_blocked(clean)
        top_task = agent.todo_manager.get_top_recommended_task()
        return {
            "domain": clean,
            "is_blocked": status["is_blocked"],
            "remaining_seconds": status["remaining_seconds"],
            "remaining_formatted": status["remaining_formatted"],
            "attempts": status["attempts"],
            "reason": status["reason"],
            "recommended_task": top_task
        }


@app.post("/api/record-attempt")
def record_attempt(domain: str = Query(...)):
    """Record a user attempt to open a blocked website."""
    clean = normalize_domain(domain)
    return agent.blocker.record_reopen_attempt(clean)


# --- Websites Configuration ---
@app.get("/api/config/websites")
def get_monitored_websites():
    """Returns list of websites monitored by FocusKoala for browser extension."""
    return agent.db.get_websites()


@app.post("/api/websites")
def add_website(req: WebsiteCreateRequest):
    name = req.name or req.domain.split(".")[0].capitalize()
    return agent.db.add_website(
        domain=req.domain,
        name=name,
        limit_seconds=req.limit_seconds,
        cooldown_seconds=req.cooldown_seconds,
        enabled=req.enabled
    )


@app.put("/api/websites/{domain}")
def update_website(domain: str, req: WebsiteUpdateRequest):
    clean = normalize_domain(domain)
    res = agent.db.update_website(
        clean,
        limit_seconds=req.limit_seconds,
        cooldown_seconds=req.cooldown_seconds,
        enabled=req.enabled
    )
    if not res:
        raise HTTPException(status_code=404, detail="Website not found")
    return res


@app.delete("/api/websites/{domain}")
def delete_website(domain: str):
    clean = normalize_domain(domain)
    deleted = agent.db.remove_website(clean)
    if not deleted:
        raise HTTPException(status_code=404, detail="Website not found")
    return {"deleted": True, "domain": clean}


# --- Todos & Task-Aware Redirection ---
@app.get("/api/todos")
def get_todos():
    return {
        "todos": agent.todo_manager.get_all(),
        "recommended_task": agent.todo_manager.get_top_recommended_task()
    }


@app.post("/api/todos")
def create_todo(req: TodoCreateRequest):
    return agent.todo_manager.add(req.title, req.priority)


@app.put("/api/todos/{todo_id}")
def update_todo(todo_id: str, req: TodoUpdateRequest):
    res = agent.todo_manager.update(todo_id, req.title, req.priority, req.completed)
    if not res:
        raise HTTPException(status_code=404, detail="Todo not found")
    return res


@app.post("/api/todos/{todo_id}/toggle")
def toggle_todo(todo_id: str):
    res = agent.todo_manager.toggle(todo_id)
    if not res:
        raise HTTPException(status_code=404, detail="Todo not found")
    return res


@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: str):
    deleted = agent.todo_manager.delete(todo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"deleted": True}


# --- Focus Mode (Feature 12) ---
@app.post("/api/focus-mode/start")
def start_focus_mode(req: FocusModeRequest):
    return agent.start_focus_mode(req.duration_minutes, req.task)


@app.post("/api/focus-mode/stop")
def stop_focus_mode():
    return agent.stop_focus_mode()


@app.get("/api/focus-mode/status")
def focus_mode_status():
    return agent.get_focus_mode_status()


# --- Dashboard, Insights & Time Recovery ---
@app.get("/api/stats/summary")
def get_dashboard_summary():
    return agent.get_dashboard_summary()


@app.get("/api/insights")
def get_insights():
    return agent.pattern_engine.get_insights()


@app.get("/api/recovery")
def get_recovery():
    return agent.pattern_engine.get_time_recovery()


# --- Manual Block / Unblock (for testing) ---
@app.post("/api/block")
def block_site(domain: str, cooldown_seconds: int = 120):
    clean = normalize_domain(domain)
    return agent.blocker.block_domain(clean, cooldown_seconds)


@app.post("/api/unblock")
def unblock_site(domain: str):
    clean = normalize_domain(domain)
    return {"unblocked": agent.blocker.unblock(clean), "domain": clean}
