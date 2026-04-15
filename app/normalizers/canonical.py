from __future__ import annotations

from datetime import datetime, timezone

from app.api.schemas import Location, NormalizedRecord, RawRecord


CITY_ALIASES = {
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
    "bombay": "Mumbai",
    "mumbai": "Mumbai",
}

COMPANY_ALIASES = {
    "tcs": "Tata Consultancy Services",
    "tata consultancy services": "Tata Consultancy Services",
    "infosys": "Infosys",
    "tata": "Tata",
}

SKILL_ALIASES = {
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai/ml": "Machine Learning",
    "aws": "AWS",
    "python": "Python",
}


def normalize_whitespace(value: str | None) -> str | None:
    if value is None:
        return None
    collapsed = " ".join(value.strip().split())
    return collapsed or None


def normalize_city(city: str | None) -> str | None:
    city = normalize_whitespace(city)
    if city is None:
        return None
    return CITY_ALIASES.get(city.lower(), city.title())


def normalize_company(company: str | None) -> str | None:
    company = normalize_whitespace(company)
    if company is None:
        return None
    return COMPANY_ALIASES.get(company.lower(), company)


def normalize_skill(skill: str) -> str:
    clean = normalize_whitespace(skill) or skill
    return SKILL_ALIASES.get(clean.lower(), clean.title())


def split_name(name: str) -> tuple[str, str]:
    parts = [part for part in name.lower().split() if part]
    if not parts:
        return "", ""
    return parts[0], parts[-1]


def normalize_record(record: RawRecord) -> NormalizedRecord:
    payload = record.payload
    if record.source == "mock_profiles":
        profile_summary = normalize_whitespace(payload.get("summary"))
        article_context = None
    else:
        profile_summary = None
        article_context = normalize_whitespace(payload.get("context"))

    skills = [normalize_skill(skill) for skill in payload.get("skills", [])]
    past_companies = [
        normalized
        for company in payload.get("past_companies", [])
        if (normalized := normalize_company(company))
    ]

    return NormalizedRecord(
        source=record.source,
        source_record_id=record.source_record_id,
        name=normalize_whitespace(payload.get("name")) or "Unknown",
        aliases=[],
        location=Location(
            city=normalize_city(payload.get("city")),
            country=normalize_whitespace(payload.get("country")),
        ),
        current_title=normalize_whitespace(payload.get("title")),
        current_company=normalize_company(payload.get("company")),
        past_companies=past_companies,
        skills=sorted(set(skills)),
        education=[],
        profile_summary=profile_summary,
        article_context=article_context,
        source_url=payload.get("url"),
        captured_at=datetime.now(timezone.utc),
    )
