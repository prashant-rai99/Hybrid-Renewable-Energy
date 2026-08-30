import pandas as pd
import numpy as np
import torch
from collections import Counter
from backend.optimization.energy_env import EnergyEnv
from backend.optimization.dqn_agent import QNetwork

df = pd.read_csv("data/campus_dataset_final.csv")
env = EnergyEnv(df)

q_net = QNetwork(state_dim=9, action_dim=5)
q_net.load_state_dict(torch.load("backend/optimization/dqn_model_best.pt"))
q_net.eval()


def run_episode(start_idx, policy):
    env.start_idx = start_idx
    env.t = 0
    env.soc = env.BATTERY_CAPACITY * 0.5
    state = env._get_state()
    total_cost, total_emissions, total_grid = 0, 0, 0
    done = False
    while not done:
        action = policy(state)
        state, reward, done, info = env.step(action)
        total_cost += info["cost"]
        total_emissions += info["emissions"]
        total_grid += info["grid_import"]
    return total_cost, total_emissions, total_grid


def action_distribution(start_idx, policy):
    env.start_idx = start_idx
    env.t = 0
    env.soc = env.BATTERY_CAPACITY * 0.5
    state = env._get_state()
    actions = []
    done = False
    while not done:
        action = policy(state)
        actions.append(action)
        state, reward, done, info = env.step(action)
    return actions


def dqn_policy(state):
    with torch.no_grad():
        return int(torch.argmax(q_net(torch.FloatTensor(state))).item())


def baseline_policy(state):
    return 2  # always hold, no battery use


test_starts = [0, 500, 1200, 2500, 4000]
dqn_results = [run_episode(s, dqn_policy) for s in test_starts]
baseline_results = [run_episode(s, baseline_policy) for s in test_starts]

dqn_cost, dqn_em, dqn_grid = np.mean(dqn_results, axis=0)
base_cost, base_em, base_grid = np.mean(baseline_results, axis=0)

print(
    f"Baseline -> cost: {base_cost:.1f}, emissions: {base_em:.1f}, grid_import: {base_grid:.1f}"
)
print(
    f"DQN      -> cost: {dqn_cost:.1f}, emissions: {dqn_em:.1f}, grid_import: {dqn_grid:.1f}"
)
print(f"Cost reduction: {100*(base_cost-dqn_cost)/base_cost:.1f}%")
print(f"Grid dependence reduction: {100*(base_grid-dqn_grid)/base_grid:.1f}%")

all_actions = []
for s in test_starts:
    all_actions += action_distribution(s, dqn_policy)
print("Action distribution:", Counter(all_actions))


def avg_soc_trace(start_idx, policy):
    env.start_idx = start_idx
    env.t = 0
    env.soc = env.BATTERY_CAPACITY * 0.5
    state = env._get_state()
    socs = [env.soc]
    done = False
    while not done:
        action = policy(state)
        state, reward, done, info = env.step(action)
        socs.append(env.soc)
    return socs


socs = avg_soc_trace(0, dqn_policy)
print("SoC trace (min, max, avg):", min(socs), max(socs), sum(socs) / len(socs))
