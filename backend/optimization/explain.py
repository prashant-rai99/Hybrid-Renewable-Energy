import numpy as np
import pandas as pd
import torch
import shap
from backend.optimization.energy_env import EnergyEnv
from backend.optimization.dqn_agent import QNetwork

FEATURE_NAMES = [
    "soc",
    "solar",
    "wind",
    "demand",
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
    "tariff",
]

df = pd.read_csv("data/campus_dataset_final.csv")
env = EnergyEnv(df)

q_net = QNetwork(state_dim=9, action_dim=5)
q_net.load_state_dict(torch.load("backend/optimization/dqn_model_best.pt"))
q_net.eval()


def q_values_fn(states):
    with torch.no_grad():
        return q_net(torch.FloatTensor(states)).numpy()


env.start_idx, env.t = 0, 0
env.soc = env.BATTERY_CAPACITY * 0.5
background_states = []
state = env._get_state()
done = False
while not done:
    background_states.append(state)
    action = int(np.argmax(q_values_fn(state[None, :])[0]))
    state, reward, done, info = env.step(action)
background = np.array(background_states)

explainer = shap.KernelExplainer(q_values_fn, background[:30])

# explain one specific decision
sample_idx = 20
sample_state = background[sample_idx]
q_vals = q_values_fn(sample_state[None, :])[0]
chosen_action = int(np.argmax(q_vals))

shap_values = explainer.shap_values(sample_state[None, :])

print(f"State being explained: {dict(zip(FEATURE_NAMES, sample_state.round(3)))}")
print(f"Q-values: {q_vals.round(2)} -> chosen action: {chosen_action}")
print(f"\nSHAP contributions for chosen action (action {chosen_action}):")

if isinstance(shap_values, list):
    contributions = shap_values[chosen_action][0]
else:
    contributions = shap_values[0][:, chosen_action]

for name, val in zip(FEATURE_NAMES, contributions):
    print(f"  {name}: {val:.4f}")

# aggregate feature importance across many decisions, for a clearer overall picture
print("\n--- Aggregate SHAP importance (across 30 decisions) ---")
sample_batch = background[:30]
shap_values_batch = explainer.shap_values(sample_batch)

if isinstance(shap_values_batch, list):
    chosen_actions = [int(np.argmax(q_values_fn(s[None, :])[0])) for s in sample_batch]
    all_contributions = np.array(
        [shap_values_batch[a][i] for i, a in enumerate(chosen_actions)]
    )
else:
    chosen_actions = [int(np.argmax(q_values_fn(s[None, :])[0])) for s in sample_batch]
    all_contributions = np.array(
        [shap_values_batch[i][:, a] for i, a in enumerate(chosen_actions)]
    )

mean_abs_importance = np.abs(all_contributions).mean(axis=0)
importance_ranked = sorted(zip(FEATURE_NAMES, mean_abs_importance), key=lambda x: -x[1])

print("Feature importance (mean |SHAP value|, averaged over 30 decisions):")
for name, val in importance_ranked:
    print(f"  {name}: {val:.4f}")
