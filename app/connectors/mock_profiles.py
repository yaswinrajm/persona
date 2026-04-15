from __future__ import annotations

from app.api.schemas import RawRecord, SearchRequest
from app.connectors.base import SourceConnector


MOCK_PROFILES = [
    {
        "id": "profile-1",
        "name": "Rahul Sharma",
        "city": "Bangalore",
        "country": "India",
        "title": "Software Engineer",
        "company": "Infosys",
        "past_companies": ["Wipro"],
        "skills": ["Python", "ML", "AWS"],
        "summary": "Backend engineer focused on machine learning systems.",
        "url": "https://profiles.example/rahul-sharma-1",
    },
    {
        "id": "profile-2",
        "name": "Rahul Sharma",
        "city": "Mumbai",
        "country": "India",
        "title": "Product Manager",
        "company": "Tata",
        "past_companies": ["Jio"],
        "skills": ["Strategy", "Operations"],
        "summary": "Product leader working on fintech workflows.",
        "url": "https://profiles.example/rahul-sharma-2",
    },
    {
        "id": "profile-3",
        "name": "Rahul S. Sharma",
        "city": "Pune",
        "country": "India",
        "title": "Data Engineer",
        "company": "Tata Consultancy Services",
        "past_companies": [],
        "skills": ["Python", "Data Engineering", "Airflow"],
        "summary": "Builds data platforms for enterprise analytics.",
        "url": "https://profiles.example/rahul-sharma-3",
    },
]


class MockProfilesConnector(SourceConnector):
    source_name = "mock_profiles"

    async def search_people(self, request: SearchRequest) -> list[RawRecord]:
        name_query = request.name.lower().strip()
        records: list[RawRecord] = []
        for profile in MOCK_PROFILES:
            if name_query in profile["name"].lower():
                records.append(
                    RawRecord(
                        source=self.source_name,
                        source_record_id=profile["id"],
                        payload=profile,
                    )
                )
        return records
