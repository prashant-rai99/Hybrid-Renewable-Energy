"""
carbon_analytics.py
Turns raw sensor_readings into the reportable impact numbers:
CO2 saved, grid dependence percentage, and daily/weekly rollups
into the carbon_savings table.
"""

from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import SensorReading, CarbonSaving
from .database import SessionLocal

# ---------------------------------------------------------------------------
# Emission factor
# ---------------------------------------------------------------------------
# Default value: 0.82 kg CO2 per kWh (approximate India grid average, CEA
# baseline figures are commonly cited in this range). This is an
# approximation for prototype/hackathon use only -- for the research paper,
# replace this with a properly cited figure from the latest CEA CO2 Baseline
# Database or equivalent authoritative source, and reference it there.
DEFAULT_EMISSION_FACTOR_KG_PER_KWH = 0.82


def calculate_co2_saved(
    renewable_kwh: float,
    grid_kwh: float,
    emission_factor: float = DEFAULT_EMISSION_FACTOR_KG_PER_KWH,
) -> float:
    """
    CO2 saved (kg) = renewable energy used (kWh) x emission factor (kg CO2/kWh).

    This represents the emissions that would have been produced had the
    renewable_kwh been drawn from the grid instead.
    """
    if renewable_kwh < 0:
        raise ValueError("renewable_kwh cannot be negative")
    if grid_kwh < 0:
        raise ValueError("grid_kwh cannot be negative")

    co2_saved_kg = renewable_kwh * emission_factor
    return round(co2_saved_kg, 3)


def calculate_grid_dependence_reduction(
    baseline_grid_kwh: float,
    actual_grid_kwh: float,
) -> float:
    """
    Percentage reduction in grid dependence versus a baseline (e.g. a
    pre-optimization period, or a "no renewables" scenario).

    Returns a percentage: positive means less grid dependence than baseline,
    negative means more grid dependence than baseline.
    """
    if baseline_grid_kwh < 0 or actual_grid_kwh < 0:
        raise ValueError("kWh values cannot be negative")
    if baseline_grid_kwh == 0:
        # No baseline grid usage to compare against.
        return 0.0

    reduction_pct = ((baseline_grid_kwh - actual_grid_kwh) / baseline_grid_kwh) * 100
    return round(reduction_pct, 2)


def calculate_grid_dependence_pct(renewable_kwh: float, grid_kwh: float) -> float:
    """
    Share of total energy consumption that came from the grid, as a percentage.
    Used to fill carbon_savings.grid_dependence_pct for a given day/week.
    """
    total_kwh = renewable_kwh + grid_kwh
    if total_kwh == 0:
        return 0.0
    return round((grid_kwh / total_kwh) * 100, 2)


# ---------------------------------------------------------------------------
# Aggregation: sensor_readings -> carbon_savings
# ---------------------------------------------------------------------------
def _sum_energy_for_period(
    session: Session, start_dt: datetime, end_dt: datetime
) -> tuple[float, float]:
    """
    Sum solar+wind readings as renewable kWh, and grid readings as grid kWh,
    for the given [start_dt, end_dt) window. Returns (renewable_kwh, grid_kwh).
    """
    renewable_kwh = (
        session.query(func.coalesce(func.sum(SensorReading.value), 0.0))
        .filter(
            SensorReading.source_type.in_(["solar", "wind"]),
            SensorReading.timestamp >= start_dt,
            SensorReading.timestamp < end_dt,
        )
        .scalar()
    )
    grid_kwh = (
        session.query(func.coalesce(func.sum(SensorReading.value), 0.0))
        .filter(
            SensorReading.source_type == "grid",
            SensorReading.timestamp >= start_dt,
            SensorReading.timestamp < end_dt,
        )
        .scalar()
    )
    return round(float(renewable_kwh), 3), round(float(grid_kwh), 3)


def aggregate_daily(session: Session, target_date: date) -> Optional[CarbonSaving]:
    """
    Roll up all sensor_readings for target_date into a single carbon_savings
    row. If a row for that date already exists, it is updated in place
    (idempotent -- safe to re-run for the same day).
    """
    start_dt = datetime(target_date.year, target_date.month, target_date.day)
    end_dt = start_dt + timedelta(days=1)

    renewable_kwh, grid_kwh = _sum_energy_for_period(session, start_dt, end_dt)
    if renewable_kwh == 0.0 and grid_kwh == 0.0:
        return None  # nothing to aggregate for this date

    co2_saved = calculate_co2_saved(renewable_kwh, grid_kwh)
    grid_dependence = calculate_grid_dependence_pct(renewable_kwh, grid_kwh)

    existing = session.query(CarbonSaving).filter(CarbonSaving.date == target_date).first()
    if existing:
        existing.kwh_from_renewable = renewable_kwh
        existing.kwh_from_grid = grid_kwh
        existing.co2_saved_kg = co2_saved
        existing.grid_dependence_pct = grid_dependence
        row = existing
    else:
        row = CarbonSaving(
            date=target_date,
            kwh_from_renewable=renewable_kwh,
            kwh_from_grid=grid_kwh,
            co2_saved_kg=co2_saved,
            grid_dependence_pct=grid_dependence,
        )
        session.add(row)

    session.commit()
    return row


def aggregate_weekly(session: Session, week_start: date) -> dict:
    """
    Roll up 7 days starting at week_start. Does not write a single
    carbon_savings row (schema is daily-grained); instead it aggregates
    the 7 daily rows via aggregate_daily and returns a weekly summary dict,
    which is what report_export.py uses for weekly reports.
    """
    daily_rows = []
    for offset in range(7):
        day = week_start + timedelta(days=offset)
        row = aggregate_daily(session, day)
        if row:
            daily_rows.append(row)

    total_renewable = round(sum(r.kwh_from_renewable for r in daily_rows), 3)
    total_grid = round(sum(r.kwh_from_grid for r in daily_rows), 3)
    total_co2_saved = round(sum(r.co2_saved_kg for r in daily_rows), 3)
    avg_grid_dependence = (
        round(sum(r.grid_dependence_pct for r in daily_rows) / len(daily_rows), 2)
        if daily_rows
        else 0.0
    )

    return {
        "week_start": week_start,
        "week_end": week_start + timedelta(days=6),
        "days_aggregated": len(daily_rows),
        "total_kwh_from_renewable": total_renewable,
        "total_kwh_from_grid": total_grid,
        "total_co2_saved_kg": total_co2_saved,
        "avg_grid_dependence_pct": avg_grid_dependence,
    }


def run_aggregation_for_all_data(session: Session) -> int:
    """
    Convenience function for testing: finds the earliest and latest sensor
    reading dates and runs aggregate_daily for every day in that range.
    Returns the number of days aggregated.
    """
    earliest = session.query(func.min(SensorReading.timestamp)).scalar()
    latest = session.query(func.max(SensorReading.timestamp)).scalar()
    if not earliest or not latest:
        return 0

    current_day = earliest.date()
    last_day = latest.date()
    count = 0
    while current_day <= last_day:
        if aggregate_daily(session, current_day):
            count += 1
        current_day += timedelta(days=1)
    return count


if __name__ == "__main__":
    # Quick manual test: run this after db_models.py has created sample data.
    db = SessionLocal()
    try:
        days_done = run_aggregation_for_all_data(db)
        print(f"Aggregated {days_done} day(s) into carbon_savings.")

        for row in db.query(CarbonSaving).order_by(CarbonSaving.date).all():
            print(
                f"{row.date} | renewable={row.kwh_from_renewable}kWh "
                f"grid={row.kwh_from_grid}kWh co2_saved={row.co2_saved_kg}kg "
                f"grid_dependence={row.grid_dependence_pct}%"
            )
    finally:
        db.close()
