from datetime import datetime, timezone

from app.api.schemas import Location, NormalizedRecord
from app.matcher.scoring import score_pair


def build_record(
    record_id: str,
    name: str,
    city: str | None,
    company: str | None,
    title: str | None,
    skills: list[str],
) -> NormalizedRecord:
    return NormalizedRecord(
        source="test",
        source_record_id=record_id,
        name=name,
        aliases=[],
        location=Location(city=city, country="India"),
        current_title=title,
        current_company=company,
        past_companies=[],
        skills=skills,
        education=[],
        profile_summary=None,
        article_context=None,
        source_url="https://example.com/record",
        captured_at=datetime.now(timezone.utc),
    )


def test_same_person_signals_score_high() -> None:
    left = build_record("a", "Rahul Sharma", "Bengaluru", "Infosys", "Software Engineer", ["Python", "Machine Learning"])
    right = build_record("b", "Rahul Sharma", "Bengaluru", "Infosys", "Senior Engineer", ["Python", "Machine Learning"])

    result = score_pair(left, right)

    assert result.score >= 0.8
    assert result.routing == "accept"


def test_conflicts_reduce_score() -> None:
    left = build_record("a", "Rahul Sharma", "Mumbai", "Tata", "Product Manager", ["Strategy"])
    right = build_record("b", "Rahul Sharma", "Bengaluru", "Infosys", "Senior Engineer", ["Machine Learning"])

    result = score_pair(left, right)

    assert "city_conflict" in result.signals.conflict_flags
    assert "company_conflict" in result.signals.conflict_flags
    assert result.routing == "reject"
