import numpy as np
import pandas as pd

train = pd.read_csv("data/train.csv", parse_dates=["timestamp"])
test = pd.read_csv("data/test.csv", parse_dates=["timestamp"])
print(
    f"train {len(train)} rows {train['timestamp'].min()} -> {train['timestamp'].max()}"
)
print(f"test  {len(test)} rows {test['timestamp'].min()} -> {test['timestamp'].max()}")

TARGETS = {
    "solar": ("solar_kw", "data/solar_forecast.csv", 1.0),
    "wind": ("wind_kw", "data/wind_forecast.csv", 0.5),
    "demand": ("demand_kw", "data/demand_forecast.csv", None),
}


def mape(y, p):
    return 100 * np.mean(np.abs(y - p) / np.abs(y))


def rmse(y, p):
    return float(np.sqrt(np.mean((y - p) ** 2)))


for name, (col, path, thr) in TARGETS.items():
    fc = pd.read_csv(path, parse_dates=["ds"])
    assert len(fc) == len(test), name
    y = test[col].to_numpy()
    p = fc["yhat"].to_numpy()
    lo, hi = fc["yhat_lower"].to_numpy(), fc["yhat_upper"].to_numpy()
    naive = np.full(len(y), np.nan)
    naive[24:] = y[:-24]
    active = np.ones(len(y), bool) if thr is None else y > thr
    inside = (y >= lo) & (y <= hi)
    valid = ~np.isnan(naive)
    m = valid & active
    print(f"\n{name}: {active.sum()} active of {len(y)} hours")
    print(
        f"  coverage (nominal 90%): all hours {inside.mean() * 100:.1f}%, "
        f"active hours {inside[active].mean() * 100:.1f}%, "
        f"mean band width {np.mean((hi - lo)[active]):.2f} kW"
    )
    print(
        f"  model : MAPE {mape(y[m], p[m]):.2f}%  RMSE {rmse(y[valid], p[valid]):.4f}"
    )
    print(
        f"  naive : MAPE {mape(y[m], naive[m]):.2f}%  RMSE {rmse(y[valid], naive[valid]):.4f}"
    )
