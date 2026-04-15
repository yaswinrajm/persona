from __future__ import annotations

from time import time
from uuid import uuid4

from app.api.schemas import SearchRequest, SearchResponse


class InMemoryRepository:
    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self.searches: dict[str, SearchResponse] = {}
        self.cache: dict[str, tuple[float, SearchResponse]] = {}

    def _cache_key(self, request: SearchRequest) -> str:
        return f"{request.name.lower().strip()}|{(request.city or '').lower().strip()}|{(request.company or '').lower().strip()}"

    def get_cached(self, request: SearchRequest) -> SearchResponse | None:
        key = self._cache_key(request)
        cached = self.cache.get(key)
        if not cached:
            return None
        expires_at, response = cached
        if expires_at < time():
            self.cache.pop(key, None)
            return None
        return response

    def save_search(self, request: SearchRequest, response: SearchResponse) -> SearchResponse:
        self.searches[response.search_id] = response
        self.cache[self._cache_key(request)] = (time() + self.ttl_seconds, response)
        return response

    def create_search_id(self) -> str:
        return uuid4().hex

    def get_search(self, search_id: str) -> SearchResponse | None:
        return self.searches.get(search_id)
