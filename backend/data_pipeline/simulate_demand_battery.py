import numpy as np
import pandas as pd

BATTERY_CAPACITY_KWH = 50
CHARGE_DISCHARGE_LIMIT_KW = 10

PEAK_LOAD_KW = 80


def simulate_demand(df):
    hour = df["timestamp"].dt.hour
    is_weekend = df["timestamp"].dt.dayofweek >= 5

    # Base daily pattern: low at night, peak in working hours
    daily_pattern = 0.3 + 0.7 * np.exp(-((hour - 14) ** 2) / (2 * 4**2))
    weekend_factor = np.where(is_weekend, 0.6, 1.0)

    # Mild temperature correlation (AC load rises with heat)
    temp_factor = 1 + 0.01 * (df["temperature"] - 25).clip(lower=0)

    noise = np.random.normal(1.0, 0.05, len(df))

    demand_kw = PEAK_LOAD_KW * daily_pattern * weekend_factor * temp_factor * noise
    return demand_kw.clip(lower=0)


def simulate_battery(df):
    soc = np.zeros(len(df))
    soc[0] = BATTERY_CAPACITY_KWH * 0.5  # start at 50% charge

    net_power = df["solar_kw"] + df["wind_kw"] - df["demand_kw"]

    for i in range(1, len(df)):
        power_flow = np.clip(
            net_power.iloc[i], -CHARGE_DISCHARGE_LIMIT_KW, CHARGE_DISCHARGE_LIMIT_KW
        )
        new_soc = soc[i - 1] + power_flow
        soc[i] = np.clip(new_soc, 0, BATTERY_CAPACITY_KWH)

    return soc


if __name__ == "__main__":
    df = pd.read_csv("data/generation_simulated.csv", parse_dates=["timestamp"])

    df["demand_kw"] = simulate_demand(df)
    df["battery_soc_kwh"] = simulate_battery(df)
    df["battery_soc_pct"] = (df["battery_soc_kwh"] / BATTERY_CAPACITY_KWH) * 100

    df.to_csv("data/campus_dataset.csv", index=False)
    print(f"Saved {len(df)} rows to data/campus_dataset.csv")
    print(
        df[["timestamp", "solar_kw", "wind_kw", "demand_kw", "battery_soc_pct"]].head(
            10
        )
    )
