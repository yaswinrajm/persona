# Xapien Entity Resolution Assistant

An MVP identity-resolution tool that searches two sources for a person name, normalizes messy profile/news data into one schema, compares candidate pairs with interpretable heuristics, and optionally uses an LLM to explain ambiguous matches.

## What it does

- Accepts a person name with optional city and company hints
- Queries two connectors:
  - `mock_profiles`: LinkedIn-style structured records
  - `mock_news`: news/article-style records
- Normalizes both sources into a shared person schema
- Generates candidate pairs using simple blocking rules
- Scores each pair with deterministic signals
- Uses an LLM adapter for gray-area reasoning when enabled
- Returns `same_person`, `uncertain`, or `different_person` with evidence and conflicts

## Quick start

1. Create a virtual environment and install dependencies.
2. Copy `.env.example` to `.env` if you want to enable LLM mode.
3. Run:

```bash
uvicorn app.main:app --reload
```

4. Open `http://127.0.0.1:8000/`.

## Notes

- This version uses an in-memory repository for local demo simplicity.
- The repository interface mirrors the planned `search_queries`, `raw_source_records`, `normalized_records`, `candidate_pairs`, and `match_results` tables so you can swap in PostgreSQL later.
- Redis-style caching is represented by an in-memory TTL cache.
- If `USE_LLM=false` or no API key is configured, the service falls back to a deterministic explanation layer.
