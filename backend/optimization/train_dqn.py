import random
import numpy as np
import pandas as pd
import torch
from backend.optimization.energy_env import EnergyEnv
from backend.optimization.dqn_agent import DQNAgent

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

df = pd.read_csv("data/campus_dataset_final.csv")
env = EnergyEnv(df)
agent = DQNAgent(state_dim=9, action_dim=5)

EPISODES = 1500
TARGET_UPDATE_EVERY = 10
EVAL_EVERY = 50
test_starts = [0, 500, 1200, 2500, 4000]


def quick_eval():
    total_grid = 0
    for s in test_starts:
        env.start_idx, env.t = s, 0
        env.soc = env.BATTERY_CAPACITY * 0.5
        state = env._get_state()
        done = False
        while not done:
            with torch.no_grad():
                action = int(torch.argmax(agent.q_net(torch.FloatTensor(state))).item())
            state, reward, done, info = env.step(action)
            total_grid += info["grid_import"]
    return total_grid / len(test_starts)


best_grid = float("inf")

for ep in range(EPISODES):
    state = env.reset()
    total_reward = 0
    done = False
    while not done:
        action = agent.act(state)
        next_state, reward, done, info = env.step(action)
        agent.remember(state, action, reward, next_state, done)
        agent.replay()
        state = next_state if next_state is not None else state
        total_reward += reward

    if agent.epsilon > agent.epsilon_min:
        agent.epsilon *= agent.epsilon_decay

    if ep % TARGET_UPDATE_EVERY == 0:
        agent.update_target()

    if ep % EVAL_EVERY == 0:
        grid_score = quick_eval()
        if grid_score < best_grid:
            best_grid = grid_score
            torch.save(
                agent.q_net.state_dict(), "backend/optimization/dqn_model_best.pt"
            )
        print(
            f"Episode {ep}, reward={total_reward:.2f}, epsilon={agent.epsilon:.3f}, eval_grid={grid_score:.1f}, best={best_grid:.1f}"
        )

torch.save(agent.q_net.state_dict(), "backend/optimization/dqn_model.pt")
print("Training done. Final + best model saved.")
