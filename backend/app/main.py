from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import initialize_database
from app.routes.health import router as health_router
from app.routes.metrics import router as metrics_router
from app.routes.dashboard import router as dashboard_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    initialize_database(settings.database_path)
    yield


app = FastAPI(title="dash-vps API", version="0.1.0", lifespan=lifespan)
app.include_router(health_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")

settings = get_settings()
origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
if origins:
    if "*" in origins:
        raise ValueError("DASH_VPS_CORS_ORIGINS requires explicit origins")
    app.add_middleware(CORSMiddleware, allow_origins=origins,
                       allow_methods=["GET", "POST"],
                       allow_headers=["Authorization", "Content-Type"],
                       allow_credentials=False)

static_dir = settings.static_dir or Path(__file__).resolve().parents[1] / "dist"
if static_dir.is_dir() and (static_dir / "index.html").is_file():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(static_dir / "index.html")
