import pandas as pd
from prophet import Prophet

# Load train/test data
train_df = pd.read_csv("data/train.csv", parse_dates=["timestamp"])
test_df = pd.read_csv("data/test.csv", parse_dates=["timestamp"])

train_prophet = train_df[["timestamp", "solar_kw", "cloud_cover"]].rename(
    columns={"timestamp": "ds", "solar_kw": "y"}
)
test_prophet = test_df[["timestamp", "solar_kw", "cloud_cover"]].rename(
    columns={"timestamp": "ds", "solar_kw": "y"}
)

model = Prophet(
    daily_seasonality=True,
    yearly_seasonality=True,
    weekly_seasonality=False,
    interval_width=0.90, 
)
model.add_regressor("cloud_cover")
model.fit(train_prophet)

import pickle

with open("backend/forecasting/solar_model.pkl", "wb") as f:
    pickle.dump(model, f)

future = test_prophet[["ds", "cloud_cover"]]
forecast = model.predict(future)

from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import numpy as np

y_true = test_prophet["y"].values
y_pred = forecast["yhat"].clip(lower=0).values

mape = mean_absolute_percentage_error(
    y_true[y_true > 1], y_pred[y_true > 1]
) 
rmse = np.sqrt(mean_squared_error(y_true, y_pred))

print(f"Solar Forecast - MAPE: {mape:.4f}, RMSE: {rmse:.4f}")

result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
result["yhat"] = result["yhat"].clip(lower=0)
result["yhat_lower"] = result["yhat_lower"].clip(lower=0)
result.to_csv("data/solar_forecast.csv", index=False)

print("Saved forecast to data/solar_forecast.csv")
