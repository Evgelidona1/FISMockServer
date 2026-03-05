from datetime import datetime
import json
from typing import List, Optional
from fastapi import FastAPI, File, HTTPException, Depends, Body, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from pydantic_core import ErrorDetails

from fismock.common.commons import validate_bearer

class ClientManager(BaseModel):
    managerKindCode: str
    tabNumber: str
class Client(BaseModel):
    localId: str
    type: str
    clientSapId: str
    idealClientSapId: str
    clientTypeId: str
    isResident: bool
    isTaxResident: bool
    fullName: str
    shortName: str
    regNumber: str
    regDate: str
    lastName: str
    name: str
    patronymic: str
    birthDate: str
    passportSeries: str
    passportNumber: str
    snils: str
    inn: str
    kpp: str
    kio: str
    registredRF: bool
    dossierBarcode: str
    innNewTerritory: str
    akdCreatedDate: datetime
    akdCreatedBy: str
    akdLastModifiedDate: datetime
    akdLastModifiedBy: str
    id: str
    editMark: bool
    akdId: str
    businessSegmentCode: str
    clientManagers: List[ClientManager]
    employee: bool
    vip: bool
    comment: str
class Package(BaseModel):
    localId: str
    type: str
    productSapId: str
    productTypeId: str
    contractNum: str
    contractDate: datetime
class Attachment(BaseModel):
    fileId: str
    typeOriginalId: str
    typeAssuranceId: str
    officeid: str
    akdCreatedDate: datetime
    akdCreatedBy: str
    akdId: str
    deleteLink: bool
class Holding(BaseModel):
    localId: str
    holdingIdealId: str
    holdingRealId: str
class Document(BaseModel):
    localId: str
    docTypeCode: str
    docName: str
    docNumber: str
    docDate: datetime
    conditionMonitoring: str
    dateMonitoring: datetime
    creditCompany: str
    personName: str
    agentName: str
    period: str
    numberLineReports: List[str]
    numberLineBalances: List[str]
    invoices: List[str]
    validity: datetime
    docYear: int
    docQuarter: int
    docVisit: datetime
    comment: str
    comments: List[str]
    text_comment: str
    secrecyStamp: str
    accessUsers: List[str]
    storageSecretDocument: str
    dateState: datetime
    periodStart: datetime
    periodEnd: datetime
    addedBy: str
    numberAgreement: str
    dateAgreement: datetime
    attachments: List[Attachment]
    signElectronicFlag: bool
class Object(BaseModel):
    type: str
    refLocalId: str
class RelatedObjectsGroup(BaseModel):
    type: str
    refLocalId: str
    objects: List[Object]
class SetClientInfoModelRequest(BaseModel):
    requestId: str
    fromSystem: str
    remoteUser: str
    clients: Optional[List[Client]] = None
    packages: Optional[List[Package]] = None
    documents: Optional[List[Document]] = None
    holdings: Optional[List[Holding]] = None
    relatedObjectsGroups: Optional[List[RelatedObjectsGroup]] = None
class ObjectResult(BaseModel):
    localId: Optional[str] = None
    status: str
    message: str
    errors: Optional[List[str]] = None
    objectId: Optional[str] = None
class SetClientInfoModel(BaseModel):
    requestId: str
    status: str
    errorsCount: int
    clientResults: List[ObjectResult]
    packageResults: List[ObjectResult]
    documentResults: List[ObjectResult]
    holdingResults: List[ObjectResult]

def set_error_validate(request_id: str, result_code: int, errors: List[ErrorDetails]):
    client_results: List[ObjectResult] = []
    package_results: List[ObjectResult] = []
    document_results: List[ObjectResult] = []
    holding_results: List[ObjectResult] = []
    object_result: ObjectResult
    for error in errors:
        object_result = ObjectResult(status = "ERROR", message = error["msg"])
        match (error["loc"][0]):
            case 'clients':
                client_results.append(object_result)
            case 'packages':
                package_results.append(object_result)
            case 'documents':
                document_results.append(object_result)
            case 'holdings':
                holding_results.append(object_result)
    payload = SetClientInfoModel(requestId=request_id,
                                 status="ERROR", 
                                 errorsCount=len(errors),
                                 clientResults = client_results,
                                 packageResults = package_results,
                                 documentResults = document_results,
                                 holdingResults = holding_results).model_dump(mode="json")
    return JSONResponse(status_code=result_code, content=payload)
def set_error(request_id: str, result_code: int, errors: List[str], message: str):
    payload = SetClientInfoModel(requestId=request_id,
                                 status=message, 
                                 errorsCount=len(errors),
                                 clientResults = [],
                                 packageResults = [],
                                 documentResults = [],
                                 holdingResults = []).model_dump(mode="json")
    return JSONResponse(status_code=result_code, content=payload)


def set_client_info(app: FastAPI):
    # Эндпойнт для создания/редактирования досье
    @app.post("/api/v2/dossier")
    async def set_client_info(body: SetClientInfoModelRequest = Body(...), authorization: Optional[str] = Header(default=None)):
        try:
            token = validate_bearer(authorization)
        except HTTPException:
            return set_error(body.requestId, 401, ["Unauthorized"], "Incorrect authorization data")
        if token == "forbidden":
            return set_error(body.requestId, 403, ["Forbidden"], "User has no permission to the service")
        if not body:
            return set_error(body.requestId, 400, ["Body is null"], "Request error")
        try:
            body_fields = SetClientInfoModelRequest.model_validate((body))
        except ValidationError as e:
            return set_error_validate(body_fields.requestId, 400, e.errors())
        values: List = []
        if body_fields.clients:
            values.extend(c.localId for c in body_fields.clients)
        if body_fields.packages:
            values.extend(p.localId for p in body_fields.packages)
        if body_fields.documents:
            values.extend(p.localId for p in body_fields.documents)
        if body_fields.holdings:
            values.extend(p.localId for p in body_fields.holdings)
        #values = [body_fields.clients.localId, body_fields.packages.localId, body_fields.documents.localId, body_fields.holdings.localId]
        if len(values) != len(set(values)):
            return set_error(body_fields.requestId, 400, ["Double localId was found in one of types: clients, packages, documents, holdings"], "Request error")
        errors: List[str] = []
        errorsCount: int = 0

        
        if body_fields.remoteUser.startswith("missing"):
            return set_error(body_fields.requestId, 404, ["Not Found"], "File not found")
        if body_fields.remoteUser.startswith("1"):
            return set_error(body_fields.requestId, 500, ["Server error"], "Internal server error")

        payload = SetClientInfoModel(requestId="c9f8fff5-8ca8-4502-a55e-2ca775c1ebec",
                                 status="Completed", 
                                 errorsCount=0,
                                 clientResults = [ObjectResult(localId="CLIENT-1", status="OK", message="Клиент успешно изменен", errors=[], objectId="e884a832-5662-2076-b040-9f71681fa35d")],
                                 packageResults = [ObjectResult(localId="PRODUCT-1", status="OK", message="Продукт ЮЛ успешно обновлен", errors=[], objectId="063d37d9-e5f0-5e80-8e06-c6aa0011df3b"),
                                                   ObjectResult(localId="tranche-1", status="OK", message="Транш успешно обновлен", errors=[], objectId="c1d2d663-e332-4b43-20ca-67773eedd4e3")],
                                 documentResults = [ObjectResult(localId="DOC-1", status="OK", message="Документ успешно изменен", errors=[], objectId="ba1436b5-c699-f52f-edf7-81fd2b7338ad")],
                                 holdingResults = []).model_dump(mode="json")
        return JSONResponse(status_code=200, content=payload)