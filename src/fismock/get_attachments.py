import io
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse

from fismock.common.commons import set_error, validate_bearer

def get_attachments(app: FastAPI):
    # Эндпойнт для скачивания файла
    @app.get("/api/v1.1/files/{id}/binaries")
    async def get_attachments(id: str, authorization: Optional[str] = Header(default=None)):
        try:
            token = validate_bearer(authorization)
        except HTTPException:
            return set_error(401, ["Unauthorized"], "Incorrect authorization data")
        if token == "forbidden":
            return set_error(403, ["Forbidden"], "User has no permission to the service")
        if id.startswith("missing"):
            return set_error(404, ["Not Found"], "File not found")
        if id.startswith("1"):
            return set_error(500, ["Server error"], "Internal server error")
        data = b'\xcf\xf0\xe8\xe2\xe5\xf2, \xec\xe8\xf0!'
        return StreamingResponse(
            io.BytesIO(data),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{id}.bin"'
            },
        )