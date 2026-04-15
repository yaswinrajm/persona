from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.api.schemas import SearchRequest, SearchResponse
from app.services.search import get_search_service


router = APIRouter()
TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "templates" / "index.html"


@router.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(TEMPLATE_PATH)


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/search", response_model=SearchResponse)
async def run_search(payload: SearchRequest) -> SearchResponse:
    service = get_search_service()
    return await service.run_search(payload)


@router.get("/search/{search_id}", response_model=SearchResponse)
async def get_search(search_id: str) -> SearchResponse:
    service = get_search_service()
    result = service.repository.get_search(search_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Search not found")
    return result
