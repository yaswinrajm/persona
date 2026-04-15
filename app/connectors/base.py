from __future__ import annotations

from abc import ABC, abstractmethod

from app.api.schemas import RawRecord, SearchRequest


class SourceConnector(ABC):
    source_name: str

    @abstractmethod
    async def search_people(self, request: SearchRequest) -> list[RawRecord]:
        raise NotImplementedError
