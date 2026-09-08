from typing import Optional
from pydantic import BaseModel, Field


class RerouteRequest(BaseModel):
    target_depot_id: Optional[str] = Field(default=None)


class OperationalActionRequest(BaseModel):
    note: Optional[str] = Field(default=None, max_length=500)


class IncidentResolutionRequest(BaseModel):
    reason: str = Field(..., description="Root cause reason for excursion or incident")
    corrective_action: str = Field(..., description="Action taken to correct or mitigate")
    notes: Optional[str] = Field(default="", max_length=1000)
    user: Optional[str] = Field(default="OPERATOR_HQ", max_length=100)


class IncidentTransitionRequest(BaseModel):
    status: str = Field(..., description="OPEN, INVESTIGATING, ACTION_REQUIRED, or RESOLVED")
    notes: Optional[str] = Field(default="", max_length=500)
    user: Optional[str] = Field(default="OPERATOR_HQ", max_length=100)
