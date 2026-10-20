"""
FastAPI backend for the Hybrid Renewable Energy Optimization System.
Sits between the ML/RL core (ml_interface.py -> Phase 2/3) and the
frontend (Phase 6) / database (Phase 5).
"""

import json
import math
import os
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import case, func
from starlette.background import BackgroundTask

from . import ml_interface
from . import models
from . import report_export
from . import schemas
from .carbon_analytics import DEFAULT_EMISSION_FACTOR_KG_PER_KWH
from .database import get_db, init_db

app = FastAPI(
    title="Hybrid Renewable Energy Optimization System API",
    description="Backend API coordinating solar, wind, battery, and grid data.",
    version="1.0.0",
)

# Comma-separated list in ALLOWED_ORIGINS adds deployed frontend URLs.
_origins = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BATTERY_CAPACITY_KWH = 150.0
_METRICS_PATH = Path(__file__).with_name("model_metrics.json")


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


@app.get(
    "/model-performance",
    response_model=schemas.ModelPerformanceResponse,
    tags=["forecast"],
)
def get_model_performance():
    """Stored forecast accuracy metrics from the offline test-set evaluation."""
    try:
        return json.loads(_METRICS_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="model_metrics.json not found")


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
# Live metrics (replay of the seeded DQN-dispatched week, one row per hour)
# ---------------------------------------------------------------------------


@app.get(
    "/metrics/live",
    response_model=schemas.LiveMetricsResponse,
    tags=["metrics"],
)
def get_live_metrics(db: Session = Depends(get_db)):
    """Simulated live snapshot: replays the seeded window by current local hour."""
    S = models.SensorReading
    stamps = [t for (t,) in db.query(S.timestamp).distinct().order_by(S.timestamp)]
    if not stamps:
        raise HTTPException(
            status_code=404, detail="No sensor data. Run seed_from_dataset.py first."
        )

    now = ml_interface._now_local().replace(tzinfo=None)
    hour_index = int((now - datetime(2000, 1, 1)).total_seconds() // 3600)
    ts = stamps[hour_index % len(stamps)]

    latest = {}
    for r in db.query(S).filter(S.timestamp == ts):
        latest[r.source_type] = (r.value, (r.unit or "").lower())

    def kw(kind):
        return float(latest.get(kind, (0.0, ""))[0])

    soc_value, soc_unit = latest.get("battery", (0.0, ""))
    soc_pct = soc_value / BATTERY_CAPACITY_KWH * 100 if soc_unit == "kwh" else soc_value

    return schemas.LiveMetricsResponse(
        timestamp=now,
        solar_kw=kw("solar"),
        wind_kw=kw("wind"),
        demand_kw=kw("demand"),
        battery_soc_pct=round(float(soc_pct), 1),
        grid_draw_kw=kw("grid"),
    )


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


@app.get("/report/pdf", tags=["reports"])
def download_pdf_report(
    start: date | None = Query(None, description="Start date, default earliest"),
    end: date | None = Query(None, description="End date, default latest"),
    db: Session = Depends(get_db),
):
    """PDF carbon summary built from the carbon_savings table."""
    C = models.CarbonSaving
    first, last = db.query(func.min(C.date), func.max(C.date)).one()
    if first is None:
        raise HTTPException(
            status_code=404,
            detail="No carbon_savings rows. Run carbon analytics first.",
        )

    tmp = NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()
    report_export.export_pdf_summary(start or first, end or last, output_path=tmp.name)
    return FileResponse(
        tmp.name,
        media_type="application/pdf",
        filename="carbon_summary.pdf",
        background=BackgroundTask(os.remove, tmp.name),
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
