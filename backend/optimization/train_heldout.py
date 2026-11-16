import json
import os
import random
import sys
import time

import numpy as np
import pandas as pd
import torch

from backend.optimization.dqn_agent import DQNAgent
from backend.optimization.energy_env import EnergyEnv

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 42
EPISODES = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
ARB_W = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
SCREEN = len(sys.argv) > 4 and sys.argv[4] == "screen"
TARGET_UPDATE_EVERY = 10
EVAL_EVERY = 50
VAL_STRIDE = 24
OUT_DIR = f"backend/optimization/heldout_arb{int(ARB_W)}"

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
os.makedirs(OUT_DIR, exist_ok=True)
EnergyEnv.ARB_W = ARB_W

df = pd.read_csv("data/campus_dataset_final.csv")
month = pd.to_datetime(df["timestamp"]).dt.month
n = len(df)
val_lo = int(df.index[month >= 9][0])
test_lo = int(df.index[month >= 10][0])
L = EnergyEnv.EPISODE_LEN
val_starts = list(range(val_lo, test_lo - L + 1, VAL_STRIDE))
test_starts = list(range(test_lo, n - L + 1, L))
print(f"train [0,{val_lo}) val [{val_lo},{test_lo}) test [{test_lo},{n})")
print(
    f"val windows: {len(val_starts)}, test windows: {len(test_starts)}, ARB_W={ARB_W}"
)

train_env = EnergyEnv(df, start_range=(0, val_lo - L))
eval_env = EnergyEnv(df)
agent = DQNAgent(state_dim=9, action_dim=5)


def run(start, policy):
    env = eval_env
    env.start_idx, env.t = start, 0
    env.soc = env.BATTERY_CAPACITY * 0.5
    state = env._get_state()
    cost = em = grid = 0.0
    done = False
    while not done:
        state, _, done, info = env.step(policy(state))
        cost += info["cost"]
        em += info["emissions"]
        grid += info["grid_import"]
    return cost, em, grid


def dqn_policy(state):
    with torch.no_grad():
        return int(torch.argmax(agent.q_net(torch.FloatTensor(state))).item())


def hold_policy(state):
    return 2


def rule_policy(state):
    surplus = state[1] * 100 + state[2] * 20 - state[3] * 80
    if surplus >= 20:
        return 0
    if surplus >= 10:
        return 1
    if state[8] >= 1.0:
        return 4
    return 2


def mean_over(starts, policy):
    return np.mean([run(s, policy) for s in starts], axis=0)


def red(b, x):
    return [100 * (b[0] - x[0]) / b[0], 100 * (b[2] - x[2]) / b[2]]


best_val = float("inf")
best_path = f"{OUT_DIR}/dqn_seed{SEED}_best.pt"
t0 = time.time()

for ep in range(EPISODES):
    state = train_env.reset()
    total_reward = 0
    done = False
    while not done:
        action = agent.act(state)
        next_state, reward, done, _ = train_env.step(action)
        agent.remember(state, action, reward, next_state, done)
        agent.replay()
        state = next_state if next_state is not None else state
        total_reward += reward

    if agent.epsilon > agent.epsilon_min:
        agent.epsilon *= agent.epsilon_decay
    if ep % TARGET_UPDATE_EVERY == 0:
        agent.update_target()

    if ep % EVAL_EVERY == 0:
        v = mean_over(val_starts, dqn_policy)
        if v[0] < best_val:
            best_val = v[0]
            torch.save(agent.q_net.state_dict(), best_path)
        print(
            f"ep {ep}, reward={total_reward:.1f}, eps={agent.epsilon:.3f}, "
            f"val_cost={v[0]:.1f}, val_grid={v[2]:.1f}, best_cost={best_val:.1f}, "
            f"elapsed={time.time() - t0:.0f}s"
        )

agent.q_net.load_state_dict(torch.load(best_path))

if SCREEN:
    vb = mean_over(val_starts, hold_policy)
    vr = mean_over(val_starts, rule_policy)
    vd = mean_over(val_starts, dqn_policy)
    out = {
        "arb_w": ARB_W,
        "seed": SEED,
        "val_rule_cost_grid_pct": red(vb, vr),
        "val_dqn_cost_grid_pct": red(vb, vd),
    }
    with open(f"{OUT_DIR}/screen_seed{SEED}.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    sys.exit(0)

base = mean_over(test_starts, hold_policy)
rule = mean_over(test_starts, rule_policy)
dqn = mean_over(test_starts, dqn_policy)

result = {
    "seed": SEED,
    "arb_w": ARB_W,
    "episodes": EPISODES,
    "seconds": round(time.time() - t0),
    "baseline": base.tolist(),
    "rule_based": rule.tolist(),
    "dqn": dqn.tolist(),
    "dqn_vs_baseline_cost_grid_pct": red(base, dqn),
    "rule_vs_baseline_cost_grid_pct": red(base, rule),
}
with open(f"{OUT_DIR}/result_seed{SEED}.json", "w") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
