from __future__ import annotations

import os

from app.api.schemas import MatchResult, SearchRequest, SearchResponse
from app.connectors.mock_news import MockNewsConnector
from app.connectors.mock_profiles import MockProfilesConnector
from app.llm.service import LLMService
from app.matcher.candidate_generation import generate_candidate_pairs
from app.matcher.scoring import build_candidate_pair
from app.normalizers.canonical import normalize_record
from app.storage.repository import InMemoryRepository


class SearchService:
    def __init__(self) -> None:
        cache_ttl = int(os.getenv("CACHE_TTL_SECONDS", "300"))
        self.repository = InMemoryRepository(ttl_seconds=cache_ttl)
        self.connectors = [MockProfilesConnector(), MockNewsConnector()]
        self.llm_service = LLMService()

    async def run_search(self, request: SearchRequest) -> SearchResponse:
        cached = self.repository.get_cached(request)
        if cached:
            return cached

        raw_records = []
        for connector in self.connectors:
            raw_records.extend(await connector.search_people(request))

        normalized_records = [normalize_record(record) for record in raw_records]

        left_records = [record for record in normalized_records if record.source == "mock_profiles"]
        right_records = [record for record in normalized_records if record.source == "mock_news"]

        raw_pairs = generate_candidate_pairs(left_records, right_records)
        candidate_pairs = [build_candidate_pair(left, right) for left, right in raw_pairs]

        pair_lookup = {record.source_record_id: record for record in normalized_records}
        results: list[MatchResult] = []
        for candidate in sorted(candidate_pairs, key=lambda item: item.score, reverse=True):
            left = pair_lookup[candidate.left_record_id]
            right = pair_lookup[candidate.right_record_id]
            decision = await self.llm_service.explain_pair(left, right, candidate)
            results.append(
                MatchResult(
                    pair_id=candidate.pair_id,
                    left=left,
                    right=right,
                    candidate=candidate,
                    decision=decision,
                )
            )

        response = SearchResponse(
            search_id=self.repository.create_search_id(),
            status="completed",
            query=request,
            raw_records=raw_records,
            normalized_records=normalized_records,
            candidate_pairs=candidate_pairs,
            results=results,
        )
        return self.repository.save_search(request, response)


_search_service: SearchService | None = None


def get_search_service() -> SearchService:
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
