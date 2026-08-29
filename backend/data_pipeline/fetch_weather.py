import requests
import pandas as pd

LATITUDE = 26.9124
LONGITUDE = 75.7873
START_DATE = "20250101"
END_DATE = "20251231"
PARAMETERS = "ALLSKY_SFC_SW_DWN,WS10M,T2M,CLOUD_AMT"

URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"


def fetch_nasa_power_data():
    params = {
        "parameters": PARAMETERS,
        "community": "RE",
        "longitude": LONGITUDE,
        "latitude": LATITUDE,
        "start": START_DATE,
        "end": END_DATE,
        "format": "JSON",
    }

    response = requests.get(URL, params=params, timeout=60)
    response.raise_for_status()
    data = response.json()

    parameter_data = data["properties"]["parameter"]

    df = pd.DataFrame(
        {
            "solar_irradiance": parameter_data["ALLSKY_SFC_SW_DWN"],
            "wind_speed": parameter_data["WS10M"],
            "temperature": parameter_data["T2M"],
            "cloud_cover": parameter_data["CLOUD_AMT"],
        }
    )

    df.index = pd.to_datetime(df.index, format="%Y%m%d%H")
    df.index.name = "timestamp"
    df = df.reset_index()

    return df


if __name__ == "__main__":
    df = fetch_nasa_power_data()

    df = df.replace(-999, pd.NA)

    df.to_csv("data/weather_raw.csv", index=False)
    print(f"Saved {len(df)} rows to data/weather_raw.csv")
    print(df.head())
