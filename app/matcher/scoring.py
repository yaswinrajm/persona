from __future__ import annotations

from dataclasses import dataclass

from app.api.schemas import CandidatePair, NormalizedRecord, PairSignals
from app.normalizers.canonical import split_name


ROLE_TOKENS = {
    "engineer": {"engineer", "developer"},
    "product": {"product", "manager"},
}


@dataclass(slots=True)
class ScoreBreakdown:
    score: float
    signals: PairSignals
    routing: str


def _tokenize(value: str | None) -> set[str]:
    if not value:
        return set()
    return {token.strip(" ,.-").lower() for token in value.split() if token.strip(" ,.-")}


def _role_similarity(left: str | None, right: str | None) -> float:
    left_tokens = _tokenize(left)
    right_tokens = _tokenize(right)
    if not left_tokens or not right_tokens:
        return 0.0

    if left_tokens == right_tokens:
        return 1.0

    for group in ROLE_TOKENS.values():
        if left_tokens & group and right_tokens & group:
            return 0.7

    overlap = len(left_tokens & right_tokens)
    return overlap / max(len(left_tokens | right_tokens), 1)


def _skill_overlap(left: list[str], right: list[str]) -> float:
    left_set = {item.lower() for item in left}
    right_set = {item.lower() for item in right}
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / len(left_set | right_set)


def score_pair(left: NormalizedRecord, right: NormalizedRecord) -> ScoreBreakdown:
    left_first, left_last = split_name(left.name)
    right_first, right_last = split_name(right.name)

    name_match = left.name.lower() == right.name.lower()
    first_name_match = left_first == right_first
    last_name_match = left_last == right_last and bool(left_last)
    city_match = bool(left.location.city and right.location.city and left.location.city == right.location.city)
    company_match = bool(
        left.current_company
        and right.current_company
        and left.current_company == right.current_company
    )
    role_similarity = _role_similarity(left.current_title, right.current_title)
    skill_overlap = _skill_overlap(left.skills, right.skills)

    conflict_flags: list[str] = []
    missing_flags: list[str] = []

    if left.location.city and right.location.city and left.location.city != right.location.city:
        conflict_flags.append("city_conflict")
    elif not left.location.city or not right.location.city:
        missing_flags.append("missing_location")

    if left.current_company and right.current_company and left.current_company != right.current_company:
        conflict_flags.append("company_conflict")
    elif not left.current_company or not right.current_company:
        missing_flags.append("missing_company")

    score = 0.0
    if name_match:
        score += 0.35
    elif first_name_match and last_name_match:
        score += 0.25
    elif last_name_match:
        score += 0.1

    if city_match:
        score += 0.2
    if company_match:
        score += 0.2

    score += role_similarity * 0.15
    score += skill_overlap * 0.1

    if "city_conflict" in conflict_flags:
        score -= 0.2
    if "company_conflict" in conflict_flags:
        score -= 0.3

    score = max(0.0, min(round(score, 2), 1.0))

    if score >= 0.8 and not conflict_flags:
        routing = "accept"
    elif score <= 0.3 or len(conflict_flags) >= 2:
        routing = "reject"
    else:
        routing = "llm_review"

    return ScoreBreakdown(
        score=score,
        routing=routing,
        signals=PairSignals(
            name_match=name_match,
            first_name_match=first_name_match,
            last_name_match=last_name_match,
            city_match=city_match,
            company_match=company_match,
            role_similarity=round(role_similarity, 2),
            skill_overlap=round(skill_overlap, 2),
            conflict_flags=conflict_flags,
            missing_flags=missing_flags,
        ),
    )


def build_candidate_pair(
    left: NormalizedRecord,
    right: NormalizedRecord,
) -> CandidatePair:
    scored = score_pair(left, right)
    return CandidatePair(
        pair_id=f"{left.source_record_id}_{right.source_record_id}",
        left_record_id=left.source_record_id,
        right_record_id=right.source_record_id,
        score=scored.score,
        signals=scored.signals,
        routing=scored.routing,
    )
