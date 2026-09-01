import numpy as np
import pandas as pd


class EnergyEnv:
    """Custom RL environment for battery/grid optimization (Gym-style API)."""

    BATTERY_CAPACITY = 100
    MAX_RATE = 20
    EPISODE_LEN = 168

    ACTION_MAP = {0: MAX_RATE, 1: MAX_RATE / 2, 2: 0.0, 3: -MAX_RATE / 2, 4: -MAX_RATE}
    CO2_PER_KWH_GRID = 0.82

    def __init__(self, df: pd.DataFrame):
        self.df = df.reset_index(drop=True)
        self.max_start = len(self.df) - self.EPISODE_LEN - 1

    def _tariff(self, hour):
        if hour in [6, 7, 8, 9, 18, 19, 20, 21]:
            return 8.0
        elif 10 <= hour < 18:
            return 6.0
        else:
            return 4.0

    def reset(self):
        self.start_idx = np.random.randint(0, self.max_start)
        self.t = 0
        self.soc = self.BATTERY_CAPACITY * 0.5
        return self._get_state()

    def _get_state(self):
        row = self.df.iloc[self.start_idx + self.t]
        hour, dow = row["hour_of_day"], row["day_of_week"]
        return np.array(
            [
                self.soc / self.BATTERY_CAPACITY,
                row["solar_kw"] / 100.0,
                row["wind_kw"] / 20.0,
                row["demand_kw"] / 80.0,
                np.sin(2 * np.pi * hour / 24),
                np.cos(2 * np.pi * hour / 24),
                np.sin(2 * np.pi * dow / 7),
                np.cos(2 * np.pi * dow / 7),
                self._tariff(hour) / 8.0,
            ],
            dtype=np.float32,
        )

    def step(self, action):
        row = self.df.iloc[self.start_idx + self.t]
        solar, wind, demand, hour = (
            row["solar_kw"],
            row["wind_kw"],
            row["demand_kw"],
            row["hour_of_day"],
        )
        renewable = solar + wind
        tariff = self._tariff(hour)

        power = self.ACTION_MAP[action]
        if power > 0:
            power = min(power, self.BATTERY_CAPACITY - self.soc)
        else:
            power = -min(-power, self.soc)
        self.soc += power

        # net_demand: +ve = deficit (need grid), -ve = surplus
        net_demand = demand - renewable
        if power < 0:
            net_demand += power
        grid_import = max(0.0, net_demand)
        if power > 0:
            surplus = max(0.0, -net_demand)
            grid_import += max(0.0, power - surplus)

        cost = grid_import * tariff
        emissions = grid_import * self.CO2_PER_KWH_GRID
        wear_penalty = abs(power) / self.MAX_RATE

        renewable_surplus = max(0.0, renewable - demand)

        shift_bonus = 0.0
        if power < 0:
            if tariff >= 8.0:
                shift_bonus += (-power / self.MAX_RATE) * 15.0
            else:
                shift_bonus -= (-power / self.MAX_RATE) * 10.0
        if power > 0:
            if renewable_surplus > 0:
                # charging from actual renewable surplus -> strongest incentive
                shift_bonus += min(power, renewable_surplus) / self.MAX_RATE * 90.0
            elif tariff <= 4.0:
                # fallback: charge from cheap grid power if no renewable surplus
                shift_bonus += (power / self.MAX_RATE) * 10.0

        low_soc_penalty = 20.0 if self.soc < 0.2 * self.BATTERY_CAPACITY else 0.0

        reward = (
            -cost
            - 0.5 * emissions
            - 0.15 * wear_penalty
            + shift_bonus
            - low_soc_penalty
        ) / 10.0

        self.t += 1
        done = self.t >= self.EPISODE_LEN
        info = {"grid_import": grid_import, "cost": cost, "emissions": emissions}
        next_state = self._get_state() if not done else None
        return next_state, reward, done, info
