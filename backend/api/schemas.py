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
    confidence_high: float = Field(
        ..., description="Upper bound of confidence interval"
    )


class ForecastResponse(BaseModel):
    source: str = Field(..., description="'generation' or 'demand'")
    unit: str = "kW"
    generated_at: datetime
    horizon_hours: int
    points: List[ForecastPoint]


# ---------- Recommendation schemas ----------

ActionType = Literal[
    "charge", "discharge", "curtail", "hold", "shift_load", "export_grid"
]
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
    contribution: float = Field(
        ..., description="Relative contribution, can be negative"
    )


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
    grid_dependence_reduction_pct: float = Field(
        ..., description="Reduction in grid import vs a no-battery baseline, in percent"
    )
    co2_saved_kg: float = Field(
        ...,
        description="CO2 offset by renewable generation (not specific to optimization)",
    )
    total_generation_kwh: float
    total_demand_kwh: float
    self_consumption_pct: float = Field(
        ..., description="Share of renewable generation consumed directly, in percent"
    )
    is_estimated: bool = Field(
        False,
        description="True if summary uses placeholder values due to insufficient DB data",
    )
    total_grid_kwh: float = 0.0
    baseline_grid_kwh: float = Field(
        0.0, description="Grid import without battery dispatch (hold baseline)"
    )
    grid_dependence_pct: float = Field(
        0.0, description="Actual grid import as a share of total demand, in percent"
    )
    optimization_co2_saved_kg: float = Field(
        0.0, description="CO2 avoided by dispatch optimization vs the baseline"
    )


class HistoricalReportResponse(BaseModel):
    page: int
    page_size: int
    total_records: int
    summary: HistoricalSummary
    records: List[SensorDataResponse]
