from __future__ import annotations

from app.modules.scan.models import MisclassificationReport, ScanSession


class InMemoryScanRepository:
    def __init__(self) -> None:
        self._sessions: list[ScanSession] = []
        self._reports: list[MisclassificationReport] = []

    def create_session(self, session: ScanSession) -> ScanSession:
        self._sessions.insert(0, session)
        return session

    def list_sessions_by_user(self, user_id: str, limit: int) -> list[ScanSession]:
        rows = [session for session in self._sessions if session.user_id == user_id]
        return rows[:limit]

    def get_session_by_id(self, scan_session_id: str) -> ScanSession | None:
        for session in self._sessions:
            if session.scan_session_id == scan_session_id:
                return session
        return None

    def create_report(self, report: MisclassificationReport) -> MisclassificationReport:
        self._reports.append(report)
        return report


repo = InMemoryScanRepository()
