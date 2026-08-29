import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import numpy as np

train_df = pd.read_csv("data/train.csv", parse_dates=["timestamp"])
test_df = pd.read_csv("data/test.csv", parse_dates=["timestamp"])

train_prophet = train_df[["timestamp", "wind_kw", "wind_speed"]].rename(
    columns={"timestamp": "ds", "wind_kw": "y"}
)
test_prophet = test_df[["timestamp", "wind_kw", "wind_speed"]].rename(
    columns={"timestamp": "ds", "wind_kw": "y"}
)

model = Prophet(
    daily_seasonality=True,
    yearly_seasonality=True,
    weekly_seasonality=False,
    interval_width=0.90,
)
model.add_regressor("wind_speed")
model.fit(train_prophet)

import pickle

with open("backend/forecasting/wind_model.pkl", "wb") as f:
    pickle.dump(model, f)

future = test_prophet[["ds", "wind_speed"]]
forecast = model.predict(future)

y_true = test_prophet["y"].values
y_pred = forecast["yhat"].clip(lower=0).values

mape = mean_absolute_percentage_error(y_true[y_true > 0.5], y_pred[y_true > 0.5])
rmse = np.sqrt(mean_squared_error(y_true, y_pred))

print(f"Wind Forecast - MAPE: {mape:.4f}, RMSE: {rmse:.4f}")

result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
result["yhat"] = result["yhat"].clip(lower=0)
result["yhat_lower"] = result["yhat_lower"].clip(lower=0)
result.to_csv("data/wind_forecast.csv", index=False)

print("Saved forecast to data/wind_forecast.csv")
