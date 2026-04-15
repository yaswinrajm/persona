from __future__ import annotations

from app.api.schemas import RawRecord, SearchRequest
from app.connectors.base import SourceConnector


MOCK_NEWS = [
    {
        "id": "news-1",
        "headline": "Rahul Sharma from Bengaluru speaks at ML systems conference",
        "name": "Rahul Sharma",
        "city": "Bengaluru",
        "country": "India",
        "company": "Infosys",
        "title": "Senior Engineer",
        "skills": ["Machine Learning", "Python"],
        "context": "Rahul Sharma, a senior engineer at Infosys in Bengaluru, spoke about MLOps.",
        "url": "https://news.example/rahul-ml-conference",
    },
    {
        "id": "news-2",
        "headline": "Rahul Sharma joins Tata strategy summit in Mumbai",
        "name": "Rahul Sharma",
        "city": "Mumbai",
        "country": "India",
        "company": "Tata",
        "title": "Product Manager",
        "skills": ["Strategy"],
        "context": "Rahul Sharma, a product manager at Tata in Mumbai, discussed operating models.",
        "url": "https://news.example/rahul-strategy-summit",
    },
    {
        "id": "news-3",
        "headline": "Rahul Sharma attends regional technology panel",
        "name": "Rahul Sharma",
        "city": "India",
        "country": "India",
        "company": None,
        "title": "Engineer",
        "skills": ["Technology"],
        "context": "Rahul Sharma appeared on a broad technology panel without additional identifying details.",
        "url": "https://news.example/rahul-tech-panel",
    },
]


class MockNewsConnector(SourceConnector):
    source_name = "mock_news"

    async def search_people(self, request: SearchRequest) -> list[RawRecord]:
        name_query = request.name.lower().strip()
        records: list[RawRecord] = []
        for article in MOCK_NEWS:
            if name_query in article["name"].lower():
                records.append(
                    RawRecord(
                        source=self.source_name,
                        source_record_id=article["id"],
                        payload=article,
                    )
                )
        return records
