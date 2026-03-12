from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class IngredientResult:
    ingredient_result_id: str
    raw_text: str
    normalized_text: str
    status: str
    confidence: float
    reason: str | None
    source_title: str | None
    source_url: str | None


@dataclass
class ScanSession:
    scan_session_id: str
    user_id: str
    success: bool
    lang: str
    ocr_engine: str
    ocr_attempt_count: int
    ingredient_count: int
    overall_risk: str
    latency_ms: int
    trace_id: str
    created_at: datetime
    ingredients: list[IngredientResult]


@dataclass
class MisclassificationReport:
    report_id: str
    scan_session_id: str
    ingredient_result_id: str | None
    reporter_user_id: str
    requested_status: str
    reason: str
