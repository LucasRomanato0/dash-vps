from datetime import datetime
from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field, JsonValue, StrictInt, field_validator


JsonObject: TypeAlias = dict[str, JsonValue]


class ContainerCounters(BaseModel):
    """Container counts captured at the same instant as the host metrics."""

    model_config = ConfigDict(extra="forbid")

    running: StrictInt = Field(ge=0)
    stopped: StrictInt = Field(ge=0)
    exited: StrictInt = Field(ge=0)
    restarting: StrictInt = Field(ge=0)


class MetricsSnapshotCreate(BaseModel):
    """Validated payload accepted by the metrics ingestion endpoint."""

    model_config = ConfigDict(extra="forbid")

    collected_at: datetime
    hostname: str = Field(min_length=1)
    cpu_percent: float = Field(ge=0, le=100)
    memory_percent: float = Field(ge=0, le=100)
    disk_percent: float = Field(ge=0, le=100)
    load_1m: float = Field(ge=0)
    uptime_seconds: StrictInt = Field(ge=0)
    containers: ContainerCounters
    services: list[JsonObject] | None = None
    alerts: list[JsonObject] | None = None
    problem_containers: list[JsonObject] | None = None

    @field_validator("collected_at")
    @classmethod
    def collected_at_must_include_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("collected_at must be an ISO 8601 timestamp with timezone")
        return value

    @field_validator("hostname")
    @classmethod
    def hostname_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("hostname must not be blank")
        return value


class MetricsSnapshotCreated(BaseModel):
    id: int
    collected_at: datetime

