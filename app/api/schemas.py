from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


Verdict = Literal["same_person", "uncertain", "different_person"]
RoutingDecision = Literal["accept", "reject", "llm_review"]
SearchStatus = Literal["completed"]


class SearchRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    city: str | None = Field(default=None, max_length=120)
    company: str | None = Field(default=None, max_length=120)


class Location(BaseModel):
    city: str | None = None
    country: str | None = None


class RawRecord(BaseModel):
    source: str
    source_record_id: str
    payload: dict


class NormalizedRecord(BaseModel):
    source: str
    source_record_id: str
    name: str
    aliases: list[str] = Field(default_factory=list)
    location: Location = Field(default_factory=Location)
    current_title: str | None = None
    current_company: str | None = None
    past_companies: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    profile_summary: str | None = None
    article_context: str | None = None
    source_url: HttpUrl | None = None
    captured_at: datetime


class PairSignals(BaseModel):
    name_match: bool
    first_name_match: bool
    last_name_match: bool
    city_match: bool
    company_match: bool
    role_similarity: float
    skill_overlap: float
    conflict_flags: list[str] = Field(default_factory=list)
    missing_flags: list[str] = Field(default_factory=list)


class CandidatePair(BaseModel):
    pair_id: str
    left_record_id: str
    right_record_id: str
    score: float
    signals: PairSignals
    routing: RoutingDecision


class MatchExplanation(BaseModel):
    verdict: Verdict
    confidence: float = Field(ge=0.0, le=1.0)
    matched_fields: list[str] = Field(default_factory=list)
    conflicting_fields: list[str] = Field(default_factory=list)
    explanation: str


class MatchResult(BaseModel):
    pair_id: str
    left: NormalizedRecord
    right: NormalizedRecord
    candidate: CandidatePair
    decision: MatchExplanation


class SearchResponse(BaseModel):
    search_id: str
    status: SearchStatus
    query: SearchRequest
    raw_records: list[RawRecord]
    normalized_records: list[NormalizedRecord]
    candidate_pairs: list[CandidatePair]
    results: list[MatchResult]
