"""
API v1 路由汇总
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.discover import router as discover_router
from app.api.v1.match import router as match_router
from app.api.v1.chat import router as chat_router
from app.api.v1.report import router as report_router
from app.api.v1.upload import router as upload_router
from app.api.v1.ws import router as ws_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(discover_router)
api_v1_router.include_router(match_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(report_router)
api_v1_router.include_router(upload_router)
api_v1_router.include_router(ws_router)
