from datetime import datetime
from typing import Literal

from pydantic import BaseModel


ScanLang = Literal["ko", "en"]
ScanStatus = Literal["halal", "haram", "mashbooh", "unknown"]


class IngredientResultResponse(BaseModel):
    ingredient_result_id: str | None = None
    raw_text: str
    normalized_text: str
    status: ScanStatus
    confidence: float
    reason: str | None = None
    source_title: str | None = None
    source_url: str | None = None


class ScanCreateResponse(BaseModel):
    scan_session_id: str
    success: bool
    lang: ScanLang
    ocr_attempt_count: int
    latency_ms: int
    ingredient_count: int
    overall_risk: ScanStatus
    trace_id: str
    created_at: datetime
    ingredients: list[IngredientResultResponse]


class ScanHistoryItem(BaseModel):
    scan_session_id: str
    success: bool
    lang: ScanLang
    ocr_attempt_count: int
    ingredient_count: int
    overall_risk: ScanStatus
    latency_ms: int
    created_at: datetime


class ScanHistoryResponse(BaseModel):
    items: list[ScanHistoryItem]
    next_cursor: str | None = None


class ScanDetailResponse(BaseModel):
    scan_session_id: str
    success: bool
    lang: ScanLang
    ocr_attempt_count: int
    ingredient_count: int
    overall_risk: ScanStatus
    latency_ms: int
    trace_id: str
    created_at: datetime
    ingredients: list[IngredientResultResponse]


class ReportCreateRequest(BaseModel):
    scan_session_id: str
    ingredient_result_id: str
    reported_status: ScanStatus
    reason: str


class ReportCreateResponse(BaseModel):
    report_id: str
    scan_session_id: str
    ingredient_result_id: str
    current_status: Literal["received"]
    requested_status: ScanStatus
    reason: str
