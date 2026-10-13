from fastapi import APIRouter, Depends, status

from app.config import Settings, get_settings
from app.repositories.metrics import create_snapshot
from app.schemas.metrics import MetricsSnapshotCreate, MetricsSnapshotCreated


router = APIRouter(tags=["metrics"])


@router.post(
    "/metrics",
    response_model=MetricsSnapshotCreated,
    status_code=status.HTTP_201_CREATED,
)
def ingest_metrics(
    snapshot: MetricsSnapshotCreate,
    settings: Settings = Depends(get_settings),
) -> MetricsSnapshotCreated:
    """Validate and persist one VPS metrics snapshot."""
    snapshot_id = create_snapshot(settings.database_path, snapshot)
    return MetricsSnapshotCreated(id=snapshot_id, collected_at=snapshot.collected_at)
