from __future__ import annotations

import json
import os

import httpx

from app.api.schemas import CandidatePair, MatchExplanation, NormalizedRecord
from app.llm.models import LLMDecision


class LLMService:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.use_llm = os.getenv("USE_LLM", "false").lower() == "true"

    async def explain_pair(
        self,
        left: NormalizedRecord,
        right: NormalizedRecord,
        candidate: CandidatePair,
    ) -> MatchExplanation:
        if self.use_llm and self.api_key:
            try:
                decision = await self._call_llm(left, right, candidate)
            except Exception:
                decision = None
            if decision:
                return MatchExplanation(**decision.model_dump())
        return self._fallback_decision(candidate)

    async def _call_llm(
        self,
        left: NormalizedRecord,
        right: NormalizedRecord,
        candidate: CandidatePair,
    ) -> LLMDecision | None:
        prompt = {
            "instruction": (
                "You are judging whether two records refer to the same real-world person. "
                "Never invent facts. Contradictions are stronger than weak similarities. "
                "Return uncertain if evidence is insufficient."
            ),
            "left": left.model_dump(mode="json"),
            "right": right.model_dump(mode="json"),
            "candidate": candidate.model_dump(mode="json"),
            "response_schema": {
                "verdict": "same_person | uncertain | different_person",
                "confidence": "0.0 - 1.0",
                "matched_fields": ["list of field names"],
                "conflicting_fields": ["list of field names"],
                "explanation": "brief explanation grounded only in the supplied evidence",
            },
        }

        url = f"{self.base_url}/responses"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        body = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": "Return JSON only."}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": json.dumps(prompt)}],
                },
            ],
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()

        text = ""
        for item in payload.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    text += content.get("text", "")

        if not text:
            return None

        return LLMDecision.model_validate_json(text)

    def _fallback_decision(self, candidate: CandidatePair) -> MatchExplanation:
        matched_fields: list[str] = []
        conflicting_fields = list(candidate.signals.conflict_flags)

        if candidate.signals.name_match:
            matched_fields.append("name")
        if candidate.signals.city_match:
            matched_fields.append("location.city")
        if candidate.signals.company_match:
            matched_fields.append("current_company")
        if candidate.signals.role_similarity >= 0.6:
            matched_fields.append("current_title")
        if candidate.signals.skill_overlap >= 0.3:
            matched_fields.append("skills")

        if candidate.routing == "accept":
            verdict = "same_person"
            confidence = max(candidate.score, 0.8)
            explanation = (
                "The records strongly align on multiple structured signals with no material conflicts."
            )
        elif candidate.routing == "reject":
            verdict = "different_person"
            confidence = max(0.75, 1.0 - candidate.score)
            explanation = (
                "The records have material conflicts or too little overlap to support a same-person match."
            )
        else:
            verdict = "uncertain"
            confidence = 0.55
            explanation = (
                "The records share some similarities, but the evidence is mixed or incomplete, so the match remains uncertain."
            )

        return MatchExplanation(
            verdict=verdict,
            confidence=round(min(confidence, 0.99), 2),
            matched_fields=matched_fields,
            conflicting_fields=conflicting_fields,
            explanation=explanation,
        )
