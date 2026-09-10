import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from opspulse.db.models import IncidentSeverity, IncidentStatus, ServiceStatus


class ServiceBase(BaseModel):
    name: str = Field(max_length=120)
    description: str = ""
    endpoint_url: str = ""


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    status: ServiceStatus | None = None
    description: str | None = None


class ServiceOut(ServiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: ServiceStatus
    created_at: datetime
    updated_at: datetime


class IncidentBase(BaseModel):
    title: str = Field(max_length=200)
    description: str = ""
    severity: IncidentSeverity = IncidentSeverity.medium


class IncidentCreate(IncidentBase):
    service_id: uuid.UUID


class IncidentUpdate(BaseModel):
    status: IncidentStatus | None = None
    description: str | None = None


class IncidentOut(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    service_id: uuid.UUID
    status: IncidentStatus
    created_at: datetime
    resolved_at: datetime | None = None


class HealthOut(BaseModel):
    status: str
    database: bool
    demo_mode: bool


# --- AI Incident Assistant -------------------------------------------------


class MetricSample(BaseModel):
    name: str = Field(max_length=80)
    value: float
    unit: str = Field(default="", max_length=20)


class AlertContext(BaseModel):
    name: str = Field(max_length=120)
    severity: str = Field(default="warning", max_length=20)
    description: str = Field(default="", max_length=500)


class DeploymentContext(BaseModel):
    service_name: str = Field(max_length=120)
    version: str = Field(default="unknown", max_length=60)
    environment: str = Field(default="development", max_length=40)


class IncidentAnalysisRequest(BaseModel):
    """Bounded, sanitized context handed to the AI Incident Assistant.

    Size limits and log sanitization are enforced here so the assistant
    never receives unbounded or raw operational data.
    """

    alert: AlertContext
    metrics: list[MetricSample] = Field(default_factory=list, max_length=20)
    log_excerpt: str = Field(default="", max_length=4000)
    deployment: DeploymentContext


class IncidentAnalysisResponse(BaseModel):
    summary: str
    likely_cause: str
    supporting_evidence: list[str]
    recommended_actions: list[str]
    confidence: str  # low | medium | high
    insufficient_evidence_warning: str | None = None
    source: str  # bedrock | mock | fallback
