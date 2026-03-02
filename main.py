from fastapi import FastAPI
from set_attachments import set_attachments
from get_attachments import get_attachments
from set_client_info import set_client_info
app = FastAPI()

set_attachments(app)
get_attachments(app)
set_client_info(app)