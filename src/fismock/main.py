from fastapi import FastAPI
from fismock.set_attachments import set_attachments
from fismock.get_attachments import get_attachments
from fismock.set_client_info import set_client_info
app = FastAPI()

set_attachments(app)
get_attachments(app)
set_client_info(app)