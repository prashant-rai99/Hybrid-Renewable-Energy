import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error

train_df = pd.read_csv("data/train.csv", parse_dates=["timestamp"])
test_df = pd.read_csv("data/test.csv", parse_dates=["timestamp"])

features = [
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "temperature",
    "demand_kw_roll3h",
    "demand_kw_roll24h",
    "demand_kw_lag24h",
]
target = "demand_kw"

X_train, y_train = train_df[features], train_df[target]
X_test, y_test = test_df[features], test_df[target]

# Point forecast
model = xgb.XGBRegressor(n_estimators=300, max_depth=5, learning_rate=0.05)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

mape = mean_absolute_percentage_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"Demand Forecast - MAPE: {mape:.4f}, RMSE: {rmse:.4f}")

# Quantile models for confidence interval (5th and 95th percentile)
model_lower = xgb.XGBRegressor(
    objective="reg:quantileerror",
    quantile_alpha=0.05,
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
)
model_upper = xgb.XGBRegressor(
    objective="reg:quantileerror",
    quantile_alpha=0.95,
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
)
model_lower.fit(X_train, y_train)
model_upper.fit(X_train, y_train)

y_lower = model_lower.predict(X_test)
y_upper = model_upper.predict(X_test)

result = pd.DataFrame(
    {
        "ds": test_df["timestamp"],
        "yhat": y_pred,
        "yhat_lower": y_lower,
        "yhat_upper": y_upper,
    }
)
result.to_csv("data/demand_forecast.csv", index=False)
print("Saved forecast to data/demand_forecast.csv")

model.save_model("backend/forecasting/demand_model.json")
