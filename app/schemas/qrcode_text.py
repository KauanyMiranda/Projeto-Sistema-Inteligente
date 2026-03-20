from pydantic import BaseModel

class QRCodeTextRequest(BaseModel):
    payload: str