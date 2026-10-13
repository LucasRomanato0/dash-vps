import secrets

from fastapi import Depends, Header, HTTPException, status

from app.config import Settings, get_settings


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing bearer token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_ingest_token(
    authorization: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    """Authorize metrics ingestion without exposing the configured token."""
    configured_token = settings.ingest_token
    if configured_token is None or not configured_token.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Metrics ingestion is not configured",
        )

    if authorization is None:
        raise unauthorized()

    scheme, separator, supplied_token = authorization.partition(" ")
    if (
        separator != " "
        or scheme.lower() != "bearer"
        or not supplied_token
        or supplied_token.strip() != supplied_token
        or not secrets.compare_digest(
            supplied_token.encode("utf-8"), configured_token.encode("utf-8")
        )
    ):
        raise unauthorized()
