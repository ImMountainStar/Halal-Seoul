from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.core.config import settings
from app.core.exceptions import BadRequestError, UnauthorizedError
from app.modules.scan.models import IngredientResult, MisclassificationReport, ScanSession
from app.modules.scan.repository import repo
from app.modules.scan.schemas import (
    ReportCreateRequest,
    ReportCreateResponse,
    ScanCreateResponse,
    ScanDetailResponse,
    ScanHistoryItem,
    ScanHistoryResponse,
)


class ScanService:
    def create_scan(self, user_id: str, lang: str, trace_id: str) -> ScanCreateResponse:
        created_at = datetime.now(UTC)
        ingredient = IngredientResult(
            ingredient_result_id=str(uuid4()),
            raw_text="gelatin",
            normalized_text="gelatin",
            status="mashbooh",
            confidence=0.97,
            reason="animal source not specified",
            source_title=None,
            source_url=None,
        )
        session = ScanSession(
            scan_session_id=str(uuid4()),
            user_id=user_id,
            success=True,
            lang=lang,
            ocr_engine=settings.scan_ocr_engine,
            ocr_attempt_count=1,
            ingredient_count=1,
            overall_risk="mashbooh",
            latency_ms=1820,
            trace_id=trace_id,
            created_at=created_at,
            ingredients=[ingredient],
        )
        repo.create_session(session)
        return self._to_create_response(session)

    def list_scans(self, user_id: str, limit: int) -> ScanHistoryResponse:
        if limit < 1 or limit > 100:
            raise BadRequestError("limit must be between 1 and 100")

        items = [self._to_history_item(session) for session in repo.list_sessions_by_user(user_id, limit)]
        return ScanHistoryResponse(items=items, next_cursor=None)

    def get_scan(self, user_id: str, scan_session_id: str) -> ScanDetailResponse:
        session = repo.get_session_by_id(scan_session_id)
        if not session:
            raise BadRequestError("Scan session not found")
        if session.user_id != user_id:
            raise UnauthorizedError("Not allowed to access this scan session")
        return self._to_detail_response(session)

    def create_report(self, user_id: str, payload: ReportCreateRequest) -> ReportCreateResponse:
        session = repo.get_session_by_id(payload.scan_session_id)
        if not session:
            raise BadRequestError("Scan session not found")
        if session.user_id != user_id:
            raise UnauthorizedError("Not allowed to report this scan session")

        matched = next(
            (ingredient for ingredient in session.ingredients if ingredient.ingredient_result_id == payload.ingredient_result_id),
            None,
        )
        if not matched:
            raise BadRequestError("Ingredient result not found")

        report = MisclassificationReport(
            report_id=str(uuid4()),
            scan_session_id=payload.scan_session_id,
            ingredient_result_id=payload.ingredient_result_id,
            reporter_user_id=user_id,
            requested_status=payload.reported_status,
            reason=payload.reason,
        )
        repo.create_report(report)
        return ReportCreateResponse(
            report_id=report.report_id,
            scan_session_id=report.scan_session_id,
            ingredient_result_id=report.ingredient_result_id or "",
            current_status="received",
            requested_status=report.requested_status,
            reason=report.reason,
        )

    def _to_create_response(self, session: ScanSession) -> ScanCreateResponse:
        return ScanCreateResponse(
            scan_session_id=session.scan_session_id,
            success=session.success,
            lang=session.lang,
            ocr_attempt_count=session.ocr_attempt_count,
            latency_ms=session.latency_ms,
            ingredient_count=session.ingredient_count,
            overall_risk=session.overall_risk,
            trace_id=session.trace_id,
            created_at=session.created_at,
            ingredients=self._to_ingredient_responses(session.ingredients, include_ids=False),
        )

    def _to_history_item(self, session: ScanSession) -> ScanHistoryItem:
        return ScanHistoryItem(
            scan_session_id=session.scan_session_id,
            success=session.success,
            lang=session.lang,
            ocr_attempt_count=session.ocr_attempt_count,
            ingredient_count=session.ingredient_count,
            overall_risk=session.overall_risk,
            latency_ms=session.latency_ms,
            created_at=session.created_at,
        )

    def _to_detail_response(self, session: ScanSession) -> ScanDetailResponse:
        return ScanDetailResponse(
            scan_session_id=session.scan_session_id,
            success=session.success,
            lang=session.lang,
            ocr_attempt_count=session.ocr_attempt_count,
            ingredient_count=session.ingredient_count,
            overall_risk=session.overall_risk,
            latency_ms=session.latency_ms,
            trace_id=session.trace_id,
            created_at=session.created_at,
            ingredients=self._to_ingredient_responses(session.ingredients, include_ids=True),
        )

    def _to_ingredient_responses(self, ingredients: list[IngredientResult], include_ids: bool):
        from app.modules.scan.schemas import IngredientResultResponse

        return [
            IngredientResultResponse(
                ingredient_result_id=ingredient.ingredient_result_id if include_ids else None,
                raw_text=ingredient.raw_text,
                normalized_text=ingredient.normalized_text,
                status=ingredient.status,
                confidence=ingredient.confidence,
                reason=ingredient.reason,
                source_title=ingredient.source_title,
                source_url=ingredient.source_url,
            )
            for ingredient in ingredients
        ]


service = ScanService()
