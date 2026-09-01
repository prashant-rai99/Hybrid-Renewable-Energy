import pandas as pd

df = pd.read_csv("data/campus_dataset_final.csv", parse_dates=["timestamp"])

for mult in [1, 2, 3]:
    gen = mult * (df["solar_kw"] + df["wind_kw"])
    net = gen - df["demand_kw"]

    surplus = net[net > 0].sum()
    deficit = -net[net < 0].sum()

    print(f"{mult}x capacity -> surplus={surplus:.1f} kWh, deficit={deficit:.1f} kWh")
