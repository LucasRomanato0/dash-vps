from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.database import initialize_database
from app.routes.health import router as health_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    initialize_database(settings.database_path)
    yield


app = FastAPI(title="dash-vps API", version="0.1.0", lifespan=lifespan)
app.include_router(health_router, prefix="/api/v1")
