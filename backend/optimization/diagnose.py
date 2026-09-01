import pandas as pd
import torch
from backend.optimization.energy_env import EnergyEnv
from backend.optimization.dqn_agent import QNetwork

df = pd.read_csv("data/campus_dataset_final.csv")
env = EnergyEnv(df)

q_net = QNetwork(state_dim=9, action_dim=5)
q_net.load_state_dict(torch.load("backend/optimization/dqn_model_best.pt"))
q_net.eval()

test_starts = [0, 500, 1200, 2500, 4000]

total_surplus_available = 0.0
total_surplus_captured = 0.0
total_deficit = 0.0
total_deficit_covered_by_battery = 0.0

for s in test_starts:
    env.start_idx, env.t = s, 0
    env.soc = env.BATTERY_CAPACITY * 0.5
    state = env._get_state()
    done = False
    while not done:
        row = env.df.iloc[env.start_idx + env.t]
        solar, wind, demand = row["solar_kw"], row["wind_kw"], row["demand_kw"]
        renewable = solar + wind
        renewable_surplus = max(0.0, renewable - demand)
        deficit = max(0.0, demand - renewable)

        with torch.no_grad():
            action = int(torch.argmax(q_net(torch.FloatTensor(state))).item())

        power = env.ACTION_MAP[action]
        soc_before = env.soc

        state, reward, done, info = env.step(action)

        total_surplus_available += renewable_surplus
        if power > 0:
            actual_charge = min(power, env.BATTERY_CAPACITY - soc_before)
            total_surplus_captured += min(actual_charge, renewable_surplus)

        total_deficit += deficit
        if power < 0:
            actual_discharge = min(-power, soc_before)
            total_deficit_covered_by_battery += min(actual_discharge, deficit)

print(f"Renewable surplus available: {total_surplus_available:.1f} kWh")
print(
    f"Renewable surplus captured (charged): {total_surplus_captured:.1f} kWh "
    f"({100*total_surplus_captured/total_surplus_available:.1f}%)"
)
print(f"Total deficit: {total_deficit:.1f} kWh")
print(
    f"Deficit covered by battery: {total_deficit_covered_by_battery:.1f} kWh "
    f"({100*total_deficit_covered_by_battery/total_deficit:.1f}%)"
)


missed_due_to_rate_cap = 0.0
missed_due_to_full_battery = 0.0

for s in test_starts:
    env.start_idx, env.t = s, 0
    env.soc = env.BATTERY_CAPACITY * 0.5
    state = env._get_state()
    done = False
    while not done:
        row = env.df.iloc[env.start_idx + env.t]
        solar, wind, demand = row["solar_kw"], row["wind_kw"], row["demand_kw"]
        renewable_surplus = max(0.0, solar + wind - demand)

        with torch.no_grad():
            action = int(torch.argmax(q_net(torch.FloatTensor(state))).item())

        power = env.ACTION_MAP[action]
        soc_before = env.soc
        room_in_battery = env.BATTERY_CAPACITY - soc_before

        if renewable_surplus > 0 and power > 0:
            actual_charge = min(power, room_in_battery)
            captured = min(actual_charge, renewable_surplus)
            missed = renewable_surplus - captured
            if room_in_battery < renewable_surplus:
                missed_due_to_full_battery += min(
                    missed, renewable_surplus - room_in_battery
                )
            if env.MAX_RATE < renewable_surplus:
                missed_due_to_rate_cap += max(
                    0.0, min(missed, renewable_surplus - env.MAX_RATE)
                )

        state, reward, done, info = env.step(action)

print(f"\nSurplus missed due to full battery: {missed_due_to_full_battery:.1f} kWh")
print(f"Surplus missed due to 10kW/hr rate cap: {missed_due_to_rate_cap:.1f} kWh")
