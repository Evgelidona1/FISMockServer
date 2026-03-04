from datetime import datetime
import json
from typing import List, Optional
from fastapi import FastAPI, File, HTTPException, Depends, Form, Header, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from fismock.common.commons import validate_bearer
class FileResult(BaseModel):
    akdId: str
    externalId: str
    externalCreatedDate: datetime
    sha512: str
class Tag(BaseModel):
    tag: str
class FileRequest(BaseModel):
    fileName: str
    description: str
    externalId: str
    tags: List[str]
    externalCreatedDate: datetime
class SignResult(BaseModel):
    signResultDate: datetime
    signResult: bool
    signResultString: str
    signResultSystem: str
    signCommonName: str
    signatureDocumentHash: str
    signerCertificateFrom: datetime
    signerCertificateTo: datetime
    signatureDate: datetime
    signerCertificateIssuerName: str
    signerCertificateSerialNumber: str
class AttachmentsRequest(BaseModel):
    fileName: str
    description: str
    type: str
    signResults: Optional[List[SignResult]] = None
class AttachmentResult(BaseModel):
    akdId: str
    sha512: str
class Error(BaseModel):
    dateTime: datetime
    message: str
class SetAttachmentsModel(BaseModel):
    status: str
    fileResult: FileResult
    attachmentsResult: List[AttachmentResult]
    errors: List[Error]
    message: str
class SetAttachmentsModelRequest(BaseModel):
    author: str
    sourceSystem: str
    file: FileRequest
    attachments: List[AttachmentsRequest]

def set_error(result_code: int, errors: Error, message: str):
    payload = SetAttachmentsModel(status="ERROR", 
                                  fileResult=FileResult(akdId="0d609904-9bc2-dc58-38a6-8c07a6f635c5", externalId="10001", externalCreatedDate=datetime.now(), sha512="fe6afa677bff22c74ee339d89c76b0c78df120489c0a7e804f16722ae818ce6f3431914658"), 
                                  attachmentsResult=[AttachmentResult(akdId="0d609904-9bc2-dc58-38a6-8c07a6f635c5", sha512="6e694a2292fc9e517ead77d41a658d9e35a94fe607d7c2bfad5f28c3446b9612239dd86fc"), 
                                                     AttachmentResult(akdId="0d609904-9bc2-dc58-38a6-8c07a6f635c5", sha512="ec7d569975f0e73c64741b8fd88a3356ff15116e15a8975de9c628982ce7bc951cf5ed6803")], 
                                  errors=[errors], 
                                  message=message).model_dump(mode="json")
    return JSONResponse(status_code=result_code, content=payload)

def set_attachments(app: FastAPI):
    # Эндпоинт для загрузки файла с приложениями
    @app.post("/psbfs/api/v1.1/files/attachments")
    async def set_attachments(meta: str = Form(...),
                              file: UploadFile = File(...),
                              attachment: List[UploadFile] = File(default_factory=list),
                              authorization: Optional[str] = Header(default=None)):
        try:
            token = validate_bearer(authorization)
        except HTTPException:
            return set_error(401, Error(dateTime=datetime.now(), message="Unauthorized"), "Incorrect authorization data")
        if token == "forbidden":
            return set_error(403, Error(dateTime=datetime.now(), message="Forbidden"), "User has no permission to the service")
        try:
            body_fields = SetAttachmentsModelRequest.model_validate((json.loads(meta)))
        except Exception:
            return set_error(400, Error(dateTime=datetime.now(), message="Incorrect structure of request"), "Request error")
        if body_fields.author.startswith("missing"):
            return set_error(404, Error(dateTime=datetime.now(), message="Not Found"), "File not found")
        if body_fields.author.startswith("1"):
            return set_error(500, Error(dateTime=datetime.now(), message="Server error"), "Internal server error")
        
        payload = SetAttachmentsModel(status="SUCCESS", 
                                      fileResult=FileResult(akdId="0d609904-9bc2-dc58-38a6-8c07a6f635c5", externalId="10001", externalCreatedDate=datetime.now(), sha512="fe6afa677bff22c74ee339d89c76b0c78df120489c0a7e804f16722ae818ce6f3431914658"), 
                                      attachmentsResult=[AttachmentResult(akdId="0d609904-9bc2-dc58-38a6-8c07a6f635c5", sha512="6e694a2292fc9e517ead77d41a658d9e35a94fe607d7c2bfad5f28c3446b9612239dd86fc"), 
                                                         AttachmentResult(akdId="0d609904-9bc2-dc58-38a6-8c07a6f635c5", sha512="ec7d569975f0e73c64741b8fd88a3356ff15116e15a8975de9c628982ce7bc951cf5ed6803")], 
                                      errors=[], 
                                      message="Successful file uploading").model_dump(mode="json")
        return JSONResponse(status_code=200, content=payload)