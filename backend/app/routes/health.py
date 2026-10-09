from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return a stable readiness response for the API."""
    return {
        "status": "ok",
        "service": "dash-vps-api",
        "database": "sqlite",
    }
