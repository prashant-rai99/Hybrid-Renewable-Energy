import pandas as pd

# System capacity assumptions (campus-scale)
SOLAR_CAPACITY_KW = 100
SOLAR_EFFICIENCY = 0.80

WIND_CAPACITY_KW = 20
CUT_IN_SPEED = 3
RATED_SPEED = 12
CUT_OUT_SPEED = 25


def simulate_solar(irradiance_series):
    return SOLAR_CAPACITY_KW * (irradiance_series / 1000) * SOLAR_EFFICIENCY


def simulate_wind(wind_speed_series):
    wind_kw = pd.Series(0.0, index=wind_speed_series.index)

    rated_mask = (wind_speed_series >= RATED_SPEED) & (
        wind_speed_series <= CUT_OUT_SPEED
    )
    wind_kw[rated_mask] = WIND_CAPACITY_KW

    ramp_mask = (wind_speed_series >= CUT_IN_SPEED) & (wind_speed_series < RATED_SPEED)
    wind_kw[ramp_mask] = WIND_CAPACITY_KW * (
        wind_speed_series[ramp_mask] ** 3 / RATED_SPEED**3
    )

    return wind_kw


if __name__ == "__main__":
    df = pd.read_csv("data/weather_raw.csv", parse_dates=["timestamp"])

    df["solar_kw"] = simulate_solar(df["solar_irradiance"])
    df["wind_kw"] = simulate_wind(df["wind_speed"])

    df.to_csv("data/generation_simulated.csv", index=False)
    print(f"Saved {len(df)} rows to data/generation_simulated.csv")
    print(df[["timestamp", "solar_kw", "wind_kw"]].head(10))
