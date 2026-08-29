import pickle
import pandas as pd
import xgboost as xgb

with open("backend/forecasting/solar_model.pkl", "rb") as f:
    solar_model = pickle.load(f)

with open("backend/forecasting/wind_model.pkl", "rb") as f:
    wind_model = pickle.load(f)

demand_model = xgb.XGBRegressor()
demand_model.load_model("backend/forecasting/demand_model.json")

DEMAND_FEATURES = [
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "temperature",
    "demand_kw_roll3h",
    "demand_kw_roll24h",
    "demand_kw_lag24h",
]


def predict_generation(future_df: pd.DataFrame) -> pd.DataFrame:
    """
    future_df must have: ds, cloud_cover, wind_speed
    Returns solar + wind forecast with confidence intervals.
    """
    solar_input = future_df[["ds", "cloud_cover"]]
    solar_fc = solar_model.predict(solar_input)
    solar_fc = solar_fc[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    solar_fc[["yhat", "yhat_lower", "yhat_upper"]] = solar_fc[
        ["yhat", "yhat_lower", "yhat_upper"]
    ].clip(lower=0)
    solar_fc = solar_fc.rename(
        columns={
            "yhat": "solar_yhat",
            "yhat_lower": "solar_lower",
            "yhat_upper": "solar_upper",
        }
    )

    wind_input = future_df[["ds", "wind_speed"]]
    wind_fc = wind_model.predict(wind_input)
    wind_fc = wind_fc[["yhat", "yhat_lower", "yhat_upper"]].copy()
    wind_fc = wind_fc.clip(lower=0)
    wind_fc = wind_fc.rename(
        columns={
            "yhat": "wind_yhat",
            "yhat_lower": "wind_lower",
            "yhat_upper": "wind_upper",
        }
    )

    return pd.concat(
        [solar_fc.reset_index(drop=True), wind_fc.reset_index(drop=True)], axis=1
    )


def predict_demand(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    features_df must contain DEMAND_FEATURES columns.
    Returns point forecast.
    """
    X = features_df[DEMAND_FEATURES]
    yhat = demand_model.predict(X)
    return pd.DataFrame({"demand_yhat": yhat})
