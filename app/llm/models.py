from __future__ import annotations

from pydantic import BaseModel, Field

from app.api.schemas import Verdict


class LLMDecision(BaseModel):
    verdict: Verdict
    confidence: float = Field(ge=0.0, le=1.0)
    matched_fields: list[str]
    conflicting_fields: list[str]
    explanation: str
