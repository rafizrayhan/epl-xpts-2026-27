"""Step 2: simulate every match 10,000 times, shot by shot.

Each shot is a goal with probability = its xG x K, where K scales total xG to the goals actually scored
from shots (league calibration, as in the 2024/25 project). Own goals are not shots, so they are left out
of the simulation (they still count in the actual results).

Checks
  * after scaling, total xG equals goals from shots
  * the simulated average goals for each team in each match equal its scaled xG
"""
import json
import numpy as np
import pandas as pd

S = pd.read_csv("raw/shots_2627.csv"); M = pd.read_csv("raw/matches_2627.csv")
N, SEED = 10_000, 2627
rng = np.random.default_rng(SEED)
real = S[~S.own_goal]
K = (real.event == "Goal").sum() / real.xG.sum()
print(f"CHECK 1  xG {real.xG.sum():.1f} v goals from shots {(real.event == 'Goal').sum()} -> K = {K:.4f}; "
      f"scaled xG total {(real.xG * K).sum():.1f}")

rows, worst = [], 0.0
for m in M.itertuples():
    sh = real[real.match_id == m.match_id]
    ph, pa = sh[sh.side == "h"].xG.to_numpy() * K, sh[sh.side == "a"].xG.to_numpy() * K
    gh = (rng.random((N, ph.size)) < ph).sum(1); ga = (rng.random((N, pa.size)) < pa).sum(1)
    worst = max(worst, abs(gh.mean() - ph.sum()), abs(ga.mean() - pa.sum()))
    hw, d = (gh > ga).mean(), (gh == ga).mean(); aw = 1 - hw - d
    rows.append(dict(match_id=m.match_id, home=m.home, away=m.away, hg=m.hg, ag=m.ag, xg_h=ph.sum() / K, xg_a=pa.sum() / K,
                     p_h=hw, p_d=d, p_a=aw, xpts_h=3 * hw + d, xpts_a=3 * aw + d))
R = pd.DataFrame(rows)
print(f"CHECK 2  simulated mean goals v scaled xG, worst team in any match: {worst:.3f} (simulation noise)")
print(f"         simulated draws {R.p_d.sum():.1f} v real draws {(M.hg == M.ag).sum()}")
R.to_csv("raw/match_sims_2627.csv", index=False)
json.dump({"k": K, "n": N, "seed": SEED}, open("raw/sim_settings.json", "w"))
print("ok")
