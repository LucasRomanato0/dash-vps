from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator, model_validator


class ContainerCounters(BaseModel):
    """Container counts captured at the same instant as the host metrics."""

    model_config = ConfigDict(extra="forbid")

    running: StrictInt = Field(ge=0)
    stopped: StrictInt = Field(ge=0)
    exited: StrictInt = Field(ge=0)
    restarting: StrictInt = Field(ge=0)


class Service(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    online: bool
    latency_ms: float | None = Field(default=None, ge=0)


class Alert(BaseModel):
    model_config = ConfigDict(extra="forbid")
    priority: Literal["info", "warning", "critical"]
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def timestamp_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include timezone")
        return value.astimezone(timezone.utc)


class ProblemContainer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=200)
    state: Literal["running", "stopped", "exited", "restarting"]
    detail: str = Field(default="", max_length=500)


class MetricsSnapshotCreate(BaseModel):
    """Validated payload accepted by the metrics ingestion endpoint."""

    model_config = ConfigDict(extra="forbid")

    collected_at: datetime
    hostname: str = Field(min_length=1, max_length=255)
    cores: StrictInt = Field(default=1, ge=1, le=4096)
    ram_gb: float = Field(default=0, ge=0)
    disk_gb: float = Field(default=0, ge=0)
    os: str = Field(default="", max_length=200)
    region: str = Field(default="", max_length=200)
    cpu_percent: float = Field(ge=0, le=100)
    memory_percent: float = Field(ge=0, le=100)
    disk_percent: float = Field(ge=0, le=100)
    load_1m: float = Field(ge=0)
    uptime_seconds: StrictInt = Field(ge=0)
    containers: ContainerCounters
    services: list[Service] | None = Field(default=None, max_length=100)
    alerts: list[Alert] | None = Field(default=None, max_length=100)
    problem_containers: list[ProblemContainer] | None = Field(default=None, max_length=100)

    @field_validator("collected_at")
    @classmethod
    def collected_at_must_include_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("collected_at must be an ISO 8601 timestamp with timezone")
        return value.astimezone(timezone.utc)

    @field_validator("hostname")
    @classmethod
    def hostname_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("hostname must not be blank")
        return value

    @model_validator(mode="after")
    def alerts_not_after_collection(self):
        if self.alerts and any(alert.timestamp > self.collected_at for alert in self.alerts):
            raise ValueError("alerts cannot be later than collected_at")
        return self


class MetricsSnapshotCreated(BaseModel):
    id: int
    collected_at: datetime
