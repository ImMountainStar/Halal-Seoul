from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    trace_id: str | None = None
