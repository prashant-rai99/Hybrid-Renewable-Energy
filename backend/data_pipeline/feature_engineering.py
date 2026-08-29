import pandas as pd
import numpy as np

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

    for col in ["solar_kw", "wind_kw", "demand_kw"]:
        df[f"{col}_roll3h"] = df[col].rolling(window=3, min_periods=1).mean()
        df[f"{col}_roll24h"] = df[col].rolling(window=24, min_periods=1).mean()

    for col in ["solar_kw", "wind_kw", "demand_kw"]:
        df[f"{col}_lag24h"] = df[col].shift(24)

    df = df.dropna().reset_index(drop=True)

    df.to_csv("data/campus_dataset_final.csv", index=False)
    print(f"Saved {len(df)} rows to data/campus_dataset_final.csv")
    print(df.columns.tolist())
