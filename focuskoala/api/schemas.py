"""
Pydantic Schemas for FocusKoala FastAPI
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any


class TrackUsageRequest(BaseModel):
    domain: str
    duration_seconds: float = 3.0
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class CheckBlockRequest(BaseModel):
    domain: str
    record_attempt: bool = False


class WebsiteCreateRequest(BaseModel):
    domain: str
    name: Optional[str] = None
    limit_seconds: int = 60
    cooldown_seconds: int = 120
    enabled: bool = True


class WebsiteUpdateRequest(BaseModel):
    limit_seconds: Optional[int] = None
    cooldown_seconds: Optional[int] = None
    enabled: Optional[bool] = None


class TodoCreateRequest(BaseModel):
    title: str
    priority: str = "medium"


class TodoUpdateRequest(BaseModel):
    title: Optional[str] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None


class FocusModeRequest(BaseModel):
    duration_minutes: int = 30
    task: Optional[str] = None
