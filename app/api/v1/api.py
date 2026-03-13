from fastapi import APIRouter

from app.api.v1.endpoints import health, qrcode, sort, system

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(health.router)
api_router.include_router(qrcode.router)
api_router.include_router(sort.router)

