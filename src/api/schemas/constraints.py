from typing import Any

from pydantic import BaseModel, Field


class ConstraintsSchema(BaseModel):
    max_teaching_days_per_week: int
    max_consecutive_hours: float
    break_after_hours: float
    break_duration_minutes: int
    min_break_minutes_between_events: int
    cluster_preference_weight: float
    prefer_morning_weight: float
    config: dict[str, Any] = Field(default_factory=dict[str, Any])