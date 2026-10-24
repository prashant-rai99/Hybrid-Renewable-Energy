import glob
import json

import numpy as np

rows = [
    json.load(open(p))
    for p in sorted(glob.glob("backend/optimization/heldout/result_seed*.json"))
]
print("seeds:", [r["seed"] for r in rows])


def pct(b, x, i):
    return 100 * (b[i] - x[i]) / b[i]


def report(name, key):
    cost = [pct(r["baseline"], r[key], 0) for r in rows]
    grid = [pct(r["baseline"], r[key], 2) for r in rows]
    em = [pct(r["baseline"], r[key], 1) for r in rows]
    print(
        f"{name}: cost {np.mean(cost):.1f} +- {np.std(cost, ddof=1) if len(cost) > 1 else 0:.1f} %, "
        f"grid {np.mean(grid):.1f} +- {np.std(grid, ddof=1) if len(grid) > 1 else 0:.1f} %, "
        f"emissions {np.mean(em):.1f} +- {np.std(em, ddof=1) if len(em) > 1 else 0:.1f} %"
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
wins = sum(1 for g, rg in zip(d_grid, r_grid) if g > rg)
print(f"DQN beats rule-based on grid in {wins}/{len(rows)} seeds")
wins = sum(1 for c, rc in zip(d_cost, r_cost) if c > rc)
print(f"DQN beats rule-based on cost in {wins}/{len(rows)} seeds")
