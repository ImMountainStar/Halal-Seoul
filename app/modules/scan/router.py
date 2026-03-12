from typing import Literal

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile

from app.modules.auth.dependencies import get_current_user_id
from app.modules.scan.schemas import (
    ReportCreateRequest,
    ReportCreateResponse,
    ScanCreateResponse,
    ScanDetailResponse,
    ScanHistoryResponse,
)
from app.modules.scan.service import service

router = APIRouter()


@router.post("/sessions", response_model=ScanCreateResponse)
async def create_scan_session(
    request: Request,
    image: UploadFile = File(...),
    lang: Literal["ko", "en"] = Form(default="ko"),
    user_id: str = Depends(get_current_user_id),
) -> ScanCreateResponse:
    _ = await image.read()
    trace_id = getattr(request.state, "trace_id", "")
    return service.create_scan(user_id=user_id, lang=lang, trace_id=trace_id)


@router.get("/sessions", response_model=ScanHistoryResponse)
def list_scan_sessions(
    limit: int = Query(default=20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
) -> ScanHistoryResponse:
    return service.list_scans(user_id=user_id, limit=limit)


@router.get("/sessions/{scan_session_id}", response_model=ScanDetailResponse)
def get_scan_session(
    scan_session_id: str,
    user_id: str = Depends(get_current_user_id),
) -> ScanDetailResponse:
    return service.get_scan(user_id=user_id, scan_session_id=scan_session_id)


@router.post("/reports", response_model=ReportCreateResponse)
def create_report(
    payload: ReportCreateRequest,
    user_id: str = Depends(get_current_user_id),
) -> ReportCreateResponse:
    return service.create_report(user_id=user_id, payload=payload)
