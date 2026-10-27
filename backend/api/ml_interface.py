"""
ML / RL interface layer — real implementation.
Lives at backend/api/ml_interface.py (sibling of backend/forecasting/, backend/optimization/).
Wires Phase 2 (forecasting) + Phase 3 (RL + SHAP) into the Phase 4 API contract.
Does not modify predict.py / energy_env.py / dqn_agent.py / explain.py — only calls them.
"""

import logging
import math
import time

import requests
import numpy as np
import pandas as pd
import torch
import shap
from datetime import datetime, timedelta

from backend.forecasting.predict import (
    predict_generation as raw_predict_generation,
    predict_demand as raw_predict_demand,
    DEMAND_FEATURES,
)
from backend.optimization.energy_env import EnergyEnv
from backend.optimization.dqn_agent import QNetwork

from .database import SessionLocal
from .models import SensorReading, RecommendationLog

log = logging.getLogger("uvicorn.error")

# ---------- constants (from locked Phase 1/3 config) ----------
LAT, LON = 26.9124, 75.7873
MAX_RATE = 20.0
DEMAND_MAPE = 0.0354  # validation MAPE, used to build an approximate confidence band

# action index -> (action, magnitude_kw), agreed mapping
ACTION_MAP = {
    0: ("charge", MAX_RATE),
    1: ("charge", MAX_RATE / 2),
    2: ("hold", 0.0),
    3: ("discharge", MAX_RATE / 2),
    4: ("discharge", MAX_RATE),
}

FEATURE_NAMES = [
    "soc",
    "solar",
    "wind",
    "demand",
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
    "tariff",
]

# ---------- helpers (defined before use in _background below) ----------


def _tariff(hour: int) -> float:
    if hour in range(6, 10) or hour in range(18, 22):
        return 8.0
    if 10 <= hour < 18:
        return 6.0
    return 4.0


def _now_local() -> datetime:
    # dataset hours are local time (IST, no DST), so live code must use IST too
    return datetime.utcnow() + timedelta(hours=5, minutes=30)


# ---------- load model once at import time (not per-request) ----------
_df = pd.read_csv("data/campus_dataset_final.csv")
_env = EnergyEnv(_df)
_q_net = QNetwork(state_dim=9, action_dim=5)
_q_net.load_state_dict(torch.load("backend/optimization/dqn_model_best.pt"))
_q_net.eval()

# module-level SoC tracker: no real battery sensor exists, so we simulate it
# starting at 50% and updating it as recommendations are issued.
_current_soc = _env.BATTERY_CAPACITY * 0.5

# SHAP explainer built once (KernelExplainer is slow — do not rebuild per request)
# campus_dataset_final.csv does not have soc/hour_sin/tariff etc. as columns —
# derive the 9 model features from the raw columns that do exist, using the
# same normalization as training (see EnergyEnv._get_state).
_background = pd.DataFrame(
    {
        "soc": _df["battery_soc_kwh"] / _env.BATTERY_CAPACITY,
        "solar": _df["solar_kw"] / 100.0,
        "wind": _df["wind_kw"] / 20.0,
        "demand": _df["demand_kw"] / 80.0,
        "hour_sin": np.sin(2 * np.pi * _df["hour_of_day"] / 24),
        "hour_cos": np.cos(2 * np.pi * _df["hour_of_day"] / 24),
        "dow_sin": np.sin(2 * np.pi * _df["day_of_week"] / 7),
        "dow_cos": np.cos(2 * np.pi * _df["day_of_week"] / 7),
        "tariff": _df["hour_of_day"].apply(_tariff) / 8.0,
    }
).sample(n=30, random_state=42)


def _q_values_fn(states: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        return _q_net(torch.FloatTensor(states)).numpy()


def _build_live_state(
    solar_kw: float, wind_kw: float, demand_kw: float, ts: datetime
) -> np.ndarray:
    hour = ts.hour
    dow = ts.weekday()
    return np.array(
        [
            _current_soc / _env.BATTERY_CAPACITY,
            solar_kw / 100.0,
            wind_kw / 20.0,
            demand_kw / 80.0,
            math.sin(2 * math.pi * hour / 24),
            math.cos(2 * math.pi * hour / 24),
            math.sin(2 * math.pi * dow / 7),
            math.cos(2 * math.pi * dow / 7),
            _tariff(hour) / 8.0,
        ],
        dtype=np.float32,
    )


# ---------- weather: cached live fetch with dataset fallback ----------

WEATHER_TTL_SECONDS = 1800
WEATHER_TIMEOUT_SECONDS = 5
_weather_cache = {"at": 0.0, "df": None}


def _fetch_weather() -> pd.DataFrame:
    cached = _weather_cache["df"]
    if cached is not None and time.time() - _weather_cache["at"] < WEATHER_TTL_SECONDS:
        return cached

    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
        f"&hourly=cloudcover,windspeed_10m&forecast_days=2&timezone=Asia%2FKolkata"
    )
    try:
        resp = requests.get(url, timeout=WEATHER_TIMEOUT_SECONDS)
        resp.raise_for_status()
        hourly = resp.json()["hourly"]
    except (requests.RequestException, KeyError, ValueError) as exc:
        log.warning("Open-Meteo unavailable (%s)", type(exc).__name__)
        if cached is not None:
            return cached
        raise

    df = pd.DataFrame(
        {
            "ds": pd.to_datetime(hourly["time"]),
            "cloud_cover": hourly["cloudcover"],
            "wind_speed": hourly["windspeed_10m"],
        }
    )
    _weather_cache["df"] = df
    _weather_cache["at"] = time.time()
    return df


def _fallback_weather(now: datetime) -> pd.DataFrame:
    # last full day of the dataset, matched by hour of day
    last_day = _df.tail(24).set_index("hour_of_day")
    rows = []
    for i in range(48):
        ds = now + timedelta(hours=i)
        r = last_day.loc[ds.hour]
        rows.append(
            {"ds": ds, "cloud_cover": r["cloud_cover"], "wind_speed": r["wind_speed"]}
        )
    return pd.DataFrame(rows)


def _get_weather(now: datetime) -> pd.DataFrame:
    try:
        df = _fetch_weather()
        future = df[df["ds"] >= now]
        if not future.empty:
            return df
    except (requests.RequestException, KeyError, ValueError):
        pass
    log.warning("Using dataset fallback weather")
    return _fallback_weather(now)


# ---------- 1. predict_generation ----------


def predict_generation(hours_ahead: int = 24) -> list[dict]:
    now = _now_local().replace(minute=0, second=0, microsecond=0)

    weather_df = _get_weather(now)
    future_df = (
        weather_df[weather_df["ds"] >= now].head(hours_ahead).reset_index(drop=True)
    )

    fc = raw_predict_generation(future_df)

    points = []
    for i in range(len(fc)):
        row = fc.iloc[i]
        value = float(row["solar_yhat"] + row["wind_yhat"])
        low = float(row["solar_lower"] + row["wind_lower"])
        high = float(row["solar_upper"] + row["wind_upper"])
        points.append(
            {
                "timestamp": future_df["ds"].iloc[i].to_pydatetime(),
                "value": round(value, 2),
                "confidence_low": round(max(0.0, low), 2),
                "confidence_high": round(high, 2),
                "_solar": float(
                    row["solar_yhat"]
                ),  # internal use only, not part of API schema
                "_wind": float(row["wind_yhat"]),
            }
        )
    return points


# ---------- 2. predict_demand ----------


def predict_demand(hours_ahead: int = 24) -> list[dict]:
    now = _now_local().replace(minute=0, second=0, microsecond=0)

    db = SessionLocal()
    try:
        rows = (
            db.query(SensorReading)
            .filter(SensorReading.source_type == "demand")
            .order_by(SensorReading.timestamp.desc())
            .limit(48)
            .all()
        )
    finally:
        db.close()

    hist = pd.DataFrame([{"timestamp": r.timestamp, "value": r.value} for r in rows])
    if len(hist):
        hist = hist.sort_values("timestamp").set_index("timestamp")["value"]
    else:
        # DB has no live demand readings yet (cold start) — fall back to the
        # tail of the training dataset so rolling/lag features still work.
        fallback = _df[["timestamp", "demand_kw"]].tail(48).copy()
        fallback["timestamp"] = pd.to_datetime(fallback["timestamp"])
        hist = fallback.set_index("timestamp")["demand_kw"]

    points = []
    for h in range(hours_ahead):
        ts = now + timedelta(hours=h)
        window = hist[hist.index <= ts]
        row = {
            "hour_of_day": ts.hour,
            "day_of_week": ts.weekday(),
            "is_weekend": int(ts.weekday() >= 5),
            "temperature": 28.0,  # not modeled live yet; matches training-time default climate assumption
            "demand_kw_roll3h": window.tail(3).mean() if len(window) else 20.0,
            "demand_kw_roll24h": window.tail(24).mean() if len(window) else 20.0,
            "demand_kw_lag24h": (
                window.iloc[-24]
                if len(window) >= 24
                else (window.iloc[-1] if len(window) else 20.0)
            ),
        }
        feat_df = pd.DataFrame([row])[DEMAND_FEATURES]
        yhat = float(raw_predict_demand(feat_df)["demand_yhat"].iloc[0])
        band = yhat * DEMAND_MAPE
        points.append(
            {
                "timestamp": ts,
                "value": round(yhat, 2),
                "confidence_low": round(max(0.0, yhat - band), 2),
                "confidence_high": round(yhat + band, 2),
            }
        )
        # feed this point's prediction back into the rolling window for the next step
        hist.loc[ts] = yhat
    return points


# ---------- 3. get_recommendation ----------


def get_recommendation() -> dict:
    global _current_soc
    now = _now_local()

    gen = predict_generation(hours_ahead=1)[0]
    dem = predict_demand(hours_ahead=1)[0]
    state = _build_live_state(gen["_solar"], gen["_wind"], dem["value"], now)
    with torch.no_grad():
        q_vals = _q_net(torch.FloatTensor(state))
        action_idx = int(torch.argmax(q_vals).item())
        confidence = float(torch.softmax(q_vals, dim=0)[action_idx].item())

    action, magnitude = ACTION_MAP[action_idx]

    # update simulated SoC based on the chosen action
    if action == "charge":
        _current_soc = min(_env.BATTERY_CAPACITY, _current_soc + magnitude)
    elif action == "discharge":
        _current_soc = max(0.0, _current_soc - magnitude)

    reason_text = (
        f"Recommended to {action} battery because current generation, demand and "
        f"tariff conditions favor this action to reduce cost and grid dependence."
    )

    # log this recommendation to the shared DB so carbon_analytics.py has
    # real recommendation history to aggregate, instead of dummy data.
    db = SessionLocal()
    try:
        log_row = RecommendationLog(
            timestamp=now,
            action=action,
            target="battery",
            reason_text=reason_text,
            confidence=round(confidence, 2),
        )
        db.add(log_row)
        db.commit()
    finally:
        db.close()

    return {
        "timestamp": now,
        "action": action,
        "target": "battery",
        "confidence": round(confidence, 2),
        "magnitude_kw": magnitude if magnitude > 0 else None,
        "reason_text": reason_text,
    }


# ---------- 4. explain_recommendation ----------


def explain_recommendation() -> dict:
    now = _now_local()
    gen = predict_generation(hours_ahead=1)[0]
    dem = predict_demand(hours_ahead=1)[0]
    state = _build_live_state(gen["_solar"], gen["_wind"], dem["value"], now)

    rec = get_recommendation()
    action_idx = [k for k, v in ACTION_MAP.items() if v[0] == rec["action"]][0]

    explainer = shap.KernelExplainer(
        _q_values_fn, _background[FEATURE_NAMES].values[:30]
    )
    shap_values = explainer.shap_values(state[None, :])
    contributions = (
        shap_values[action_idx][0]
        if isinstance(shap_values, list)
        else shap_values[0][:, action_idx]
    )

    ranked = sorted(zip(FEATURE_NAMES, contributions), key=lambda x: -abs(x[1]))[:4]
    top_factors = [
        {"factor": name, "contribution": round(float(val), 4)} for name, val in ranked
    ]

    return {
        "action": rec["action"],
        "reason_text": rec.get("reason_text", ""),
        "top_factors": top_factors,
    }