from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.deps import rag_service, settings
from app.api.v1.router import api_router
from app.core.errors import AppException, app_exception_handler, unhandled_exception_handler
from app.schemas.common import HealthResponse

cfg = settings()
base_dir = Path(__file__).resolve().parent
frontend_dist_dir = base_dir.parent / "frontend" / "dist"
frontend_assets_dir = frontend_dist_dir / "assets"


@asynccontextmanager
async def lifespan(_: FastAPI):
    cfg.upload_path.mkdir(parents=True, exist_ok=True)
    cfg.converted_path.mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(
    title=cfg.app_name,
    version=cfg.app_version,
    description="Copyjoe API - FastAPI + LangChain + RAG",
    lifespan=lifespan,
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(api_router, prefix=cfg.api_v1_prefix)

if frontend_assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=frontend_assets_dir), name="frontend-assets")

app.mount("/static", StaticFiles(directory=base_dir / "static"), name="static")


@app.get("/", include_in_schema=False)
def landing_page() -> FileResponse:
    frontend_index = frontend_dist_dir / "index.html"
    if frontend_index.exists():
        return FileResponse(frontend_index)
    return FileResponse(base_dir / "static" / "index.html")


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=cfg.app_name,
        version=cfg.app_version,
        provider=cfg.llm_provider,
        rag_backend=rag_service().backend,
    )
