"""
FastAPI backend for the Hybrid Renewable Energy Optimization System.
Sits between the ML/RL core (ml_interface.py -> Phase 2/3) and the
frontend (Phase 6) / database (Phase 5).
"""

import math
import random
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import case, func

from . import ml_interface
from . import models
from . import schemas
from .carbon_analytics import DEFAULT_EMISSION_FACTOR_KG_PER_KWH
from .database import get_db, init_db

app = FastAPI(
    title="Hybrid Renewable Energy Optimization System API",
    description="Backend API coordinating solar, wind, battery, and grid data.",
    version="1.0.0",
)

# CORS for Next.js frontend (adjust origins for production deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": "hres-backend"}


# ---------------------------------------------------------------------------
# Forecasting endpoints (backed by Phase 2 via ml_interface)
# ---------------------------------------------------------------------------


@app.get(
    "/generation/forecast", response_model=schemas.ForecastResponse, tags=["forecast"]
)
def get_generation_forecast(hours: int = Query(24, ge=1, le=168)):
    """Next `hours` (default 24) combined solar+wind generation forecast."""
    points = ml_interface.predict_generation(hours_ahead=hours)
    return schemas.ForecastResponse(
        source="generation",
        generated_at=datetime.utcnow(),
        horizon_hours=hours,
        points=points,
    )


@app.get("/demand/forecast", response_model=schemas.ForecastResponse, tags=["forecast"])
def get_demand_forecast(hours: int = Query(24, ge=1, le=168)):
    """Next `hours` (default 24) campus demand forecast."""
    points = ml_interface.predict_demand(hours_ahead=hours)
    return schemas.ForecastResponse(
        source="demand",
        generated_at=datetime.utcnow(),
        horizon_hours=hours,
        points=points,
    )


# ---------------------------------------------------------------------------
# Recommendation endpoints (backed by Phase 3 RL engine via ml_interface)
# ---------------------------------------------------------------------------


@app.get(
    "/recommendation",
    response_model=schemas.RecommendationResponse,
    tags=["recommendation"],
)
def get_recommendation():
    """Current recommended action (charge/discharge/curtail/shift load/etc.)."""
    return ml_interface.get_recommendation()


@app.get(
    "/recommendation/explanation",
    response_model=schemas.RecommendationExplanationResponse,
    tags=["recommendation"],
)
def get_recommendation_explanation():
    """Human-readable explanation + top contributing factors for the current recommendation."""
    return ml_interface.explain_recommendation()


# ---------------------------------------------------------------------------
# Sensor data ingestion (Phase 1 data layer writes here / simulator posts here)
# ---------------------------------------------------------------------------


@app.post(
    "/sensor-data",
    response_model=schemas.SensorDataResponse,
    status_code=201,
    tags=["sensor-data"],
)
def create_sensor_reading(
    reading: schemas.SensorDataCreate, db: Session = Depends(get_db)
):
    """Store a new sensor reading (solar, wind, battery, grid, or demand)."""
    db_reading = models.SensorReading(
        timestamp=reading.timestamp,
        source_type=reading.source_type,
        value=reading.value,
        unit=reading.unit,
    )
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading


# ---------------------------------------------------------------------------
# Historical reporting (Phase 5 carbon analytics can extend the summary calc)
# ---------------------------------------------------------------------------


@app.get(
    "/historical-report",
    response_model=schemas.HistoricalReportResponse,
    tags=["reports"],
)
def get_historical_report(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    source_type: str | None = Query(
        None, description="Filter by solar/wind/battery/grid/demand"
    ),
    db: Session = Depends(get_db),
):
    """Paginated historical sensor data plus summary statistics."""
    query = db.query(models.SensorReading)
    if source_type:
        query = query.filter(models.SensorReading.source_type == source_type)

    total_records = query.count()
    records = (
        query.order_by(models.SensorReading.timestamp.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    summary = _compute_summary(db)

    return schemas.HistoricalReportResponse(
        page=page,
        page_size=page_size,
        total_records=total_records,
        summary=summary,
        records=records,
    )


def _compute_summary(db: Session) -> schemas.HistoricalSummary:
    S = models.SensorReading

    def value_of(kind):
        return func.coalesce(
            func.sum(case((S.source_type == kind, S.value), else_=0.0)), 0.0
        )

    def count_of(kind):
        return func.sum(case((S.source_type == kind, 1), else_=0))

    rows = (
        db.query(
            S.timestamp,
            value_of("solar"),
            value_of("wind"),
            value_of("demand"),
            value_of("grid"),
            count_of("demand"),
            count_of("grid"),
        )
        .group_by(S.timestamp)
        .all()
    )

    total_generation = total_demand = total_grid = 0.0
    baseline_grid = direct_use = 0.0

    # Only timestamps that have both demand and grid readings are comparable.
    for _, solar, wind, demand, grid, n_demand, n_grid in rows:
        if not n_demand or not n_grid:
            continue
        renewable = solar + wind
        total_generation += renewable
        total_demand += demand
        total_grid += grid
        baseline_grid += max(0.0, demand - renewable)
        direct_use += min(renewable, demand)

    is_estimated = total_demand == 0

    if is_estimated:
        return schemas.HistoricalSummary(
            grid_dependence_reduction_pct=0.0,
            co2_saved_kg=0.0,
            total_generation_kwh=0.0,
            total_demand_kwh=0.0,
            self_consumption_pct=0.0,
            is_estimated=True,
        )

    ef = DEFAULT_EMISSION_FACTOR_KG_PER_KWH
    reduction_pct = (
        (baseline_grid - total_grid) / baseline_grid * 100 if baseline_grid > 0 else 0.0
    )
    self_consumption_pct = (
        min(100.0, direct_use / total_generation * 100) if total_generation > 0 else 0.0
    )

    return schemas.HistoricalSummary(
        grid_dependence_reduction_pct=round(reduction_pct, 2),
        co2_saved_kg=round(total_generation * ef, 2),
        total_generation_kwh=round(total_generation, 2),
        total_demand_kwh=round(total_demand, 2),
        self_consumption_pct=round(self_consumption_pct, 2),
        is_estimated=False,
        total_grid_kwh=round(total_grid, 2),
        baseline_grid_kwh=round(baseline_grid, 2),
        grid_dependence_pct=round(total_grid / total_demand * 100, 2),
        optimization_co2_saved_kg=round((baseline_grid - total_grid) * ef, 2),
    )
