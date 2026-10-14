"""
SQLAlchemy ORM models.
sensor_readings: Phase 4 API layer (unchanged, do not break existing endpoints).
recommendations_log, carbon_savings: Phase 5 tables, merged onto the same Base/engine.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Index
from sqlalchemy.sql import func

from .database import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    source_type = Column(
        String(32), nullable=False, index=True
    )  # solar | wind | battery | grid | demand
    value = Column(Float, nullable=False)
    unit = Column(String(16), nullable=False)  # e.g. kW, kWh, %
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_sensor_readings_type_time", "source_type", "timestamp"),
    )


class RecommendationLog(Base):
    __tablename__ = "recommendations_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=func.now, index=True)
    action = Column(String(30), nullable=False)  # charge | discharge | hold
    target = Column(String(30), nullable=False)  # battery | grid | load
    reason_text = Column(String(500), nullable=False)
    confidence = Column(Float, nullable=False)  # 0.0 - 1.0

    def __repr__(self):
        return f"<RecommendationLog id={self.id} {self.action}->{self.target}>"


class CarbonSaving(Base):
    __tablename__ = "carbon_savings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    kwh_from_renewable = Column(Float, nullable=False)
    kwh_from_grid = Column(Float, nullable=False)
    co2_saved_kg = Column(Float, nullable=False)
    grid_dependence_pct = Column(Float, nullable=False)

    def __repr__(self):
        return f"<CarbonSaving {self.date} co2_saved={self.co2_saved_kg}kg>"
