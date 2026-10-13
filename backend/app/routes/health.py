import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.database import get_connection


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Return a stable readiness response for the API."""
    try:
        with get_connection(settings.database_path) as connection:
            connection.execute("SELECT 1").fetchone()
    except (sqlite3.Error, OSError):
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    return {
        "status": "ok",
        "service": "dash-vps-api",
        "database": "sqlite",
    }
