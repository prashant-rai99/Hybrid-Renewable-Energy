import numpy as np
import pandas as pd
import torch

from backend.optimization.dqn_agent import DQNAgent
from backend.optimization.energy_env import EnergyEnv

df = pd.read_csv("data/campus_dataset_final.csv")
month = pd.to_datetime(df["timestamp"]).dt.month
n = len(df)
test_lo = int(df.index[month >= 10][0])
L = EnergyEnv.EPISODE_LEN
test_starts = list(range(test_lo, n - L + 1, L))
env = EnergyEnv(df)
CAP = int(env.BATTERY_CAPACITY)
SMIN = int(env.SOC_MIN_FRAC * CAP)
POWERS = [env.ACTION_MAP[a] for a in range(5)]


def tariff(h):
    return env._tariff(h)


def grid_for(solar, wind, demand, p):
    net = demand - solar - wind
    if p < 0:
        net += p
    g = max(0.0, net)
    if p > 0:
        g += max(0.0, p - max(0.0, -net))
    return g


def apply_power(soc, p):
    if p > 0:
        return min(p, CAP - soc)
    return -min(-p, max(0, soc - SMIN))


def dp_window(start, objective):
    rows = df.iloc[start : start + L]
    sol, win, dem = (
        rows["solar_kw"].values,
        rows["wind_kw"].values,
        rows["demand_kw"].values,
    )
    hrs = rows["hour_of_day"].values
    socs = list(range(SMIN, CAP + 1))
    V = {s: 0.0 for s in socs}
    for t in range(L - 1, -1, -1):
        newV = {}
        tf = tariff(hrs[t])
        for s in socs:
            best = 1e18
            for p in POWERS:
                pa = apply_power(s, p)
                g = grid_for(sol[t], win[t], dem[t], pa)
                c = g * tf if objective == "cost" else g + 1e-4 * g * tf
                v = c + V[int(round(s + pa))]
                if v < best:
                    best = v
            newV[s] = best
        V = newV
    soc, cost, grid = CAP // 2, 0.0, 0.0
    for t in range(L):
        tf = tariff(hrs[t])
        best, bp = 1e18, 0
        for p in POWERS:
            pa = apply_power(soc, p)
            g = grid_for(sol[t], win[t], dem[t], pa)
            c = g * tf if objective == "cost" else g + 1e-4 * g * tf
            v = c + Vs[objective][t + 1][int(round(soc + pa))]
            if v < best:
                best, bp = v, pa
        g = grid_for(sol[t], win[t], dem[t], bp)
        cost += g * tf
        grid += g
        soc += bp
    return cost, grid


def dp_window_full(start, objective):
    global Vs
    rows = df.iloc[start : start + L]
    sol, win, dem = (
        rows["solar_kw"].values,
        rows["wind_kw"].values,
        rows["demand_kw"].values,
    )
    hrs = rows["hour_of_day"].values
    socs = list(range(SMIN, CAP + 1))
    table = [None] * (L + 1)
    table[L] = {s: 0.0 for s in socs}
    for t in range(L - 1, -1, -1):
        tf = tariff(hrs[t])
        cur = {}
        for s in socs:
            best = 1e18
            for p in POWERS:
                pa = apply_power(s, p)
                g = grid_for(sol[t], win[t], dem[t], pa)
                c = g * tf if objective == "cost" else g + 1e-4 * g * tf
                v = c + table[t + 1][int(round(s + pa))]
                if v < best:
                    best = v
            cur[s] = best
        table[t] = cur
    Vs = {objective: table}
    return dp_window(start, objective)


def run_policy(start, policy):
    env.start_idx, env.t = start, 0
    env.soc = env.BATTERY_CAPACITY * 0.5
    state = env._get_state()
    cost = grid = 0.0
    counts = {}
    done = False
    while not done:
        hour = int(df.iloc[start + env.t]["hour_of_day"])
        a = policy(state)
        counts[(tariff(hour), a)] = counts.get((tariff(hour), a), 0) + 1
        state, _, done, info = env.step(a)
        cost += info["cost"]
        grid += info["grid_import"]
    return cost, grid, counts


def hold(state):
    return 2


def rule(state):
    surplus = state[1] * 100 + state[2] * 20 - state[3] * 80
    if surplus >= 20:
        return 0
    if surplus >= 10:
        return 1
    if state[8] >= 1.0:
        return 4
    return 2


agent = DQNAgent(state_dim=9, action_dim=5)
agent.q_net.load_state_dict(
    torch.load("backend/optimization/heldout_arb50/dqn_seed42_best.pt")
)


def dqn(state):
    with torch.no_grad():
        return int(torch.argmax(agent.q_net(torch.FloatTensor(state))).item())


def mean_policy(policy):
    r = [run_policy(s, policy) for s in test_starts]
    counts = {}
    for _, _, c in r:
        for k, v in c.items():
            counts[k] = counts.get(k, 0) + v
    return np.mean([x[0] for x in r]), np.mean([x[1] for x in r]), counts


bc, bg, _ = mean_policy(hold)
print(f"baseline: cost {bc:.1f}, grid {bg:.1f}")
for name, pol in [("rule", rule), ("dqn seed42", dqn)]:
    c, g, counts = mean_policy(pol)
    print(f"{name}: cost red {100*(bc-c)/bc:.1f}%, grid red {100*(bg-g)/bg:.1f}%")
    for tf in (4.0, 6.0, 8.0):
        tot = sum(v for (t, a), v in counts.items() if t == tf)
        share = [round(100 * counts.get((tf, a), 0) / tot) for a in range(5)]
        print(
            f"   tariff {tf}: % of hours [chg20, chg10, hold, dis10, dis20] = {share}"
        )

for obj in ("cost", "grid"):
    res = [dp_window_full(s, obj) for s in test_starts]
    c, g = np.mean([r[0] for r in res]), np.mean([r[1] for r in res])
    print(
        f"ceiling (perfect foresight, optimise {obj}): cost red {100*(bc-c)/bc:.1f}%, grid red {100*(bg-g)/bg:.1f}%"
    )
