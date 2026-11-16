import glob
import json
import sys

import numpy as np

DIR = sys.argv[1] if len(sys.argv) > 1 else "backend/optimization/heldout"
rows = [json.load(open(p)) for p in sorted(glob.glob(f"{DIR}/result_seed*.json"))]
print("dir:", DIR, "seeds:", [r["seed"] for r in rows])


def pct(b, x, i):
    return 100 * (b[i] - x[i]) / b[i]


def sd(v):
    return np.std(v, ddof=1) if len(v) > 1 else 0.0


def report(name, key):
    cost = [pct(r["baseline"], r[key], 0) for r in rows]
    grid = [pct(r["baseline"], r[key], 2) for r in rows]
    em = [pct(r["baseline"], r[key], 1) for r in rows]
    print(
        f"{name}: cost {np.mean(cost):.1f} +- {sd(cost):.1f} %, "
        f"grid {np.mean(grid):.1f} +- {sd(grid):.1f} %, "
        f"emissions {np.mean(em):.1f} +- {sd(em):.1f} %"
    )
    return cost, grid


print("baseline (hold, no battery):", [round(x, 1) for x in rows[0]["baseline"]])
print("per seed DQN (cost %, grid %):")
for r in rows:
    print(
        f"  seed {r['seed']}: {pct(r['baseline'], r['dqn'], 0):.1f}, {pct(r['baseline'], r['dqn'], 2):.1f}"
    )
d_cost, d_grid = report("DQN", "dqn")
r_cost, r_grid = report("Rule-based", "rule_based")
print(
    "DQN mean absolute values (cost, emissions, grid):",
    np.mean([r["dqn"] for r in rows], axis=0).round(1).tolist(),
)
print(
    "Rule mean absolute values (cost, emissions, grid):",
    np.mean([r["rule_based"] for r in rows], axis=0).round(1).tolist(),
)
wins = sum(1 for g, rg in zip(d_grid, r_grid) if g > rg)
print(f"DQN beats rule-based on grid in {wins}/{len(rows)} seeds")
wins = sum(1 for c, rc in zip(d_cost, r_cost) if c > rc)
print(f"DQN beats rule-based on cost in {wins}/{len(rows)} seeds")
print(f"cost gap DQN - rule (mean): {np.mean(d_cost) - np.mean(r_cost):.2f} points")
