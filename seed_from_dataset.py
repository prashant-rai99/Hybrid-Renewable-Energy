"""
Seeds sensor_readings with real dataset values, where grid import comes from
running the trained DQN + battery simulation hour by hour.
Run: python seed_from_dataset.py [--reset]
"""

import sys

import pandas as pd
import torch

from backend.api.database import SessionLocal
from backend.api.models import CarbonSaving, SensorReading
from backend.optimization.dqn_agent import QNetwork
from backend.optimization.energy_env import EnergyEnv

HOURS_TO_SEED = 168
MODEL_PATH = "backend/optimization/dqn_model_best.pt"
HOLD_ACTION = 2


def simulate(env, start_idx, hours, policy):
    env.EPISODE_LEN = hours
    env.start_idx = start_idx
    env.t = 0
    env.soc = env.BATTERY_CAPACITY * 0.5
    state = env._get_state()
    grid, cost, socs = [], 0.0, []
    done = False
    while not done:
        action = policy(state)
        state, _, done, info = env.step(action)
        grid.append(info["grid_import"])
        cost += info["cost"]
        socs.append(env.soc)
    return grid, cost, socs


def main():
    reset = "--reset" in sys.argv

    df = pd.read_csv("data/campus_dataset_final.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    env = EnergyEnv(df)
    start_idx = len(df) - HOURS_TO_SEED
    window = df.iloc[start_idx:]

    q_net = QNetwork(state_dim=9, action_dim=5)
    q_net.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    q_net.eval()

    def dqn_policy(state):
        with torch.no_grad():
            return int(torch.argmax(q_net(torch.FloatTensor(state))).item())

    base_grid, base_cost, _ = simulate(
        env, start_idx, HOURS_TO_SEED, lambda s: HOLD_ACTION
    )
    dqn_grid, dqn_cost, socs = simulate(env, start_idx, HOURS_TO_SEED, dqn_policy)
    capacity = env.BATTERY_CAPACITY

    old_formula_grid = (
        (window["demand_kw"] - window["solar_kw"] - window["wind_kw"])
        .clip(lower=0)
        .sum()
    )
    base_total, dqn_total = sum(base_grid), sum(dqn_grid)

    print(f"Battery capacity used: {capacity} kWh")
    print(f"Old formula grid total: {old_formula_grid:.1f} kWh")
    print(f"Baseline (hold) grid:   {base_total:.1f} kWh, cost {base_cost:.1f}")
    print(f"DQN grid:               {dqn_total:.1f} kWh, cost {dqn_cost:.1f}")
    print(f"Grid reduction: {100 * (base_total - dqn_total) / base_total:.1f}%")
    print(f"Cost reduction: {100 * (base_cost - dqn_cost) / base_cost:.1f}%")
    print(
        f"SoC min/max/avg: {min(socs):.1f} / {max(socs):.1f} / {sum(socs)/len(socs):.1f}"
    )

    db = SessionLocal()
    try:
        if reset:
            db.query(SensorReading).delete()
            db.query(CarbonSaving).delete()
            db.commit()
            print("Cleared sensor_readings and carbon_savings.")

        existing = db.query(SensorReading).count()
        if existing > 1:
            print(
                f"sensor_readings already has {existing} rows. Use --reset to reseed."
            )
            return

        rows = []
        for (_, r), grid, soc in zip(window.iterrows(), dqn_grid, socs):
            ts = r["timestamp"].to_pydatetime()
            rows.extend(
                [
                    SensorReading(
                        timestamp=ts,
                        source_type="solar",
                        value=float(r["solar_kw"]),
                        unit="kW",
                    ),
                    SensorReading(
                        timestamp=ts,
                        source_type="wind",
                        value=float(r["wind_kw"]),
                        unit="kW",
                    ),
                    SensorReading(
                        timestamp=ts,
                        source_type="demand",
                        value=float(r["demand_kw"]),
                        unit="kW",
                    ),
                    SensorReading(
                        timestamp=ts, source_type="grid", value=float(grid), unit="kW"
                    ),
                    SensorReading(
                        timestamp=ts,
                        source_type="battery",
                        value=float(soc / capacity * 100),
                        unit="%",
                    ),
                ]
            )

        db.add_all(rows)
        db.commit()
        print(
            f"Seeded {len(rows)} sensor readings ({HOURS_TO_SEED} hours, DQN-dispatched grid, battery SoC)."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
