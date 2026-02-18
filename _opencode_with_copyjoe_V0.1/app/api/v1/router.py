from fastapi import APIRouter

from app.api.v1 import copy, export, files, history, meta, rag, web

api_router = APIRouter()
api_router.include_router(copy.router, tags=["copy"])
api_router.include_router(files.router, tags=["files"])
api_router.include_router(rag.router, tags=["rag"])
api_router.include_router(web.router, tags=["web"])
api_router.include_router(export.router, tags=["export"])
api_router.include_router(meta.router, tags=["meta"])
api_router.include_router(history.router, tags=["history"])
