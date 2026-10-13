from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import Settings, get_settings
from app.repositories.metrics import get_dashboard

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def dashboard(
    period: Literal["24h", "7d", "30d"] = Query(default="24h"),
    settings: Settings = Depends(get_settings),
) -> dict:
    report = get_dashboard(settings.database_path, period)
    if report is None:
        raise HTTPException(status_code=404, detail="No metrics collected yet")
    return report
