from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.qrcode_service import QRCodeService
from app.services.sorter_service import SorterService

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_qrcode_service(db: Session = Depends(get_db)):
    sorter_service = SorterService()
    return QRCodeService(sorter_service, db)

def get_sorter_service():
    return SorterService()