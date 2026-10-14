"""
Pydantic schemas for request and response validation.
Field shapes here are the CONTRACT the frontend (Phase 6) and ML core
(Phase 2-3) are built against. Do not rename fields without syncing
with both teams.
"""

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


# ---------- Forecast schemas (used by /generation/forecast, /demand/forecast) ----------

class ForecastPoint(BaseModel):
    timestamp: datetime
    value: float = Field(..., description="Forecasted value in kW")
    confidence_low: float = Field(..., description="Lower bound of confidence interval")
    confidence_high: float = Field(..., description="Upper bound of confidence interval")


class ForecastResponse(BaseModel):
    source: str = Field(..., description="'generation' or 'demand'")
    unit: str = "kW"
    generated_at: datetime
    horizon_hours: int
    points: List[ForecastPoint]


# ---------- Recommendation schemas ----------

ActionType = Literal["charge", "discharge", "curtail", "hold", "shift_load", "export_grid"]
TargetType = Literal["battery", "hvac", "grid", "lighting", "workshop_load"]


class RecommendationResponse(BaseModel):
    timestamp: datetime
    action: ActionType
    target: TargetType
    confidence: float = Field(..., ge=0.0, le=1.0)
    magnitude_kw: Optional[float] = Field(
        None, description="Suggested power magnitude for the action, if applicable"
    )


class FactorContribution(BaseModel):
    factor: str
    contribution: float = Field(..., description="Relative contribution, can be negative")


class RecommendationExplanationResponse(BaseModel):
    action: ActionType
    reason_text: str
    top_factors: List[FactorContribution]


# ---------- Sensor data schemas ----------

SourceType = Literal["solar", "wind", "battery", "grid", "demand"]


class SensorDataCreate(BaseModel):
    timestamp: datetime
    source_type: SourceType
    value: float
    unit: str = Field(..., examples=["kW", "kWh", "%"])


class SensorDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    source_type: str
    value: float
    unit: str


# ---------- Historical report schemas ----------


class HistoricalSummary(BaseModel):
    grid_dependence_reduction_pct: float
    co2_saved_kg: float
    total_generation_kwh: float
    total_demand_kwh: float
    self_consumption_pct: float
    is_estimated: bool = Field(
        False,
        description="True if summary uses placeholder values due to insufficient DB data",
    )


class HistoricalReportResponse(BaseModel):
    page: int
    page_size: int
    total_records: int
    summary: HistoricalSummary
    records: List[SensorDataResponse]
