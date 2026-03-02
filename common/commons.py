from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, Response
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    status: str = "Error"
    errors: List[str]
    message: str
class CommonResponse(BaseModel):
    response_body: Optional[str] = None
    response_body_binary: Optional[bytes] = None
    result_code: int
    result_dt: datetime
    success: bool
    result_message: str


def set_error(result_code: int, errors: List[str], message: str):
    payload = ErrorResponse(status="Error", errors=errors, message=message)
    result = CommonResponse(response_body=payload.model_dump_json(), result_code=result_code, result_dt=datetime.now(), success=False, result_message=payload.message)
    return Response(content=result.model_dump_json(),status_code=result_code,media_type="application/json")
def validate_bearer(auth: Optional[str]) -> str:
    if not auth:
        raise HTTPException(status_code=401)
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401)
    token = auth.removeprefix("Bearer ").strip()
    if not token or token in {"invalid", "expired"}:
        raise HTTPException(status_code=401)
    return token