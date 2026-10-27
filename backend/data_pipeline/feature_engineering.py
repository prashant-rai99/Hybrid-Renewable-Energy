import shutil
from pathlib import Path

import numpy as np
import pandas as pd

FINAL = Path("data/campus_dataset_final.csv")
OLD_COPY = Path("data/campus_dataset_final_old.csv")
KEY_COLS = ["solar_kw", "wind_kw", "demand_kw", "hour_of_day", "day_of_week"]

if __name__ == "__main__":
    df = pd.read_csv("data/campus_dataset.csv", parse_dates=["timestamp"])

    # Missing value check (NASA POWER uses -999 for missing)
    df = df.replace(-999, np.nan)
    missing_counts = df.isna().sum()
    if missing_counts.sum() > 0:
        print("Missing values found:\n", missing_counts[missing_counts > 0])
        df = df.interpolate(method="linear").ffill().bfill()

    df["hour_of_day"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Rolling windows use past hours only (shift(1)) to avoid target leakage
    for col in ["solar_kw", "wind_kw", "demand_kw"]:
        past = df[col].shift(1)
        df[f"{col}_roll3h"] = past.rolling(window=3, min_periods=1).mean()
        df[f"{col}_roll24h"] = past.rolling(window=24, min_periods=1).mean()

    for col in ["solar_kw", "wind_kw", "demand_kw"]:
        df[f"{col}_lag24h"] = df[col].shift(24)

    df = df.dropna().reset_index(drop=True)

    if FINAL.exists():
        old = pd.read_csv(FINAL, parse_dates=["timestamp"])
        same = (
            len(old) == len(df)
            and (old["timestamp"] == df["timestamp"]).all()
            and all(np.allclose(old[c], df[c]) for c in KEY_COLS)
        )
        print("Key columns identical to old file:", same)
        if not same:
            raise SystemExit("Mismatch with existing file, not overwriting.")
        shutil.copy(FINAL, OLD_COPY)
        print(f"Old file copied to {OLD_COPY}")

    df.to_csv(FINAL, index=False)
    print(f"Saved {len(df)} rows to {FINAL}")
    print(df.columns.tolist())
