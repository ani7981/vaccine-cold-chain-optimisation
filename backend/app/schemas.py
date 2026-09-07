from typing import Optional
from pydantic import BaseModel, Field


class RerouteRequest(BaseModel):
    target_depot_id: Optional[str] = Field(default=None)


class OperationalActionRequest(BaseModel):
    note: Optional[str] = Field(default=None, max_length=500)
