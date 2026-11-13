"""Step 3: actual points v expected points (xPts), Premier League 2026/27 so far.

xPts = 3 x P(win) + 1 x P(draw), summed over a team's matches. The reported xPts use the exact match
probabilities (each side's goal distribution worked out directly from its shots), which is what the
10,000 simulations of step 2 estimate, without the simulation noise.
Checks
  * simulated v exact xPts, per team
  * equal games per team; sum of gaps = total points - total xPts
Luck band: SD of a team's points under the model (sum of match variances, exact);
z = (Pts - xPts) / SD. With 20 teams, about one team is expected beyond |z| = 2 by chance alone.
"""
import json
import numpy as np
import pandas as pd

S = pd.read_csv("raw/shots_2627.csv"); M = pd.read_csv("raw/matches_2627.csv")
K = json.load(open("raw/sim_settings.json"))["k"]
R = pd.read_csv("raw/match_sims_2627.csv")
real = S[~S.own_goal]


def pmf(ps):
    d = np.array([1.0])
    for p in ps:
        d = np.convolve(d, [1 - p, p])
    return d


rows = []
for m in M.itertuples():
    sh = real[real.match_id == m.match_id]
    J = np.outer(pmf(sh[sh.side == "h"].xG.to_numpy() * K), pmf(sh[sh.side == "a"].xG.to_numpy() * K))
    ph, pd_ = np.tril(J, -1).sum(), np.trace(J); pa = 1 - ph - pd_
    for team, w in ((m.home, ph), (m.away, pa)):
        e = 3 * w + pd_
        rows.append(dict(team=team, ex_xpts=e, var=9 * w + pd_ - e ** 2))
E = pd.DataFrame(rows).groupby("team").agg(ex_xPts=("ex_xpts", "sum"), var=("var", "sum"))

h = R[["home", "hg", "ag", "xg_h", "xg_a", "xpts_h"]].set_axis(["team", "gf", "ga", "xg", "xga", "xpts"], axis=1)
a = R[["away", "ag", "hg", "xg_a", "xg_h", "xpts_a"]].set_axis(["team", "gf", "ga", "xg", "xga", "xpts"], axis=1)
D = pd.concat([h, a])
D["pts"] = np.select([D.gf > D.ga, D.gf == D.ga], [3, 1], 0)
T = D.groupby("team").agg(P=("pts", "size"), W=("pts", lambda x: (x == 3).sum()), D=("pts", lambda x: (x == 1).sum()),
                          L=("pts", lambda x: (x == 0).sum()), GF=("gf", "sum"), GA=("ga", "sum"), Pts=("pts", "sum"),
                          sim_xPts=("xpts", "sum"), xG=("xg", "sum"), xGA=("xga", "sum")).join(E)
T["xPts"] = T.ex_xPts
T["GD"] = T.GF - T.GA
T["diff"] = T.Pts - T.xPts
T["sd"] = np.sqrt(T["var"])
T["z"] = T["diff"] / T.sd
T = T.sort_values(["Pts", "GD", "GF"], ascending=False)
T["pos"] = range(1, len(T) + 1)
T["xpos"] = T.xPts.rank(ascending=False, method="first").astype(int)

print("CHECK 1  simulated v exact xPts, max team difference:", round((T.sim_xPts - T.ex_xPts).abs().max(), 3))
print("CHECK 2  equal games:", bool(T.P.nunique() == 1), f"({T.P.iloc[0]} each) | total Pts", int(T.Pts.sum()),
      "| total xPts", round(T.xPts.sum(), 1), "| sum of gaps", round(T["diff"].sum(), 2))
print("CHECK 3  teams beyond |z| = 2:", list(T.index[T.z.abs() > 2]), "| z mean", round(T.z.mean(), 2), "sd", round(T.z.std(), 2))
cols = ["pos", "Pts", "xPts", "diff", "sd", "z", "xpos", "GF", "xG", "GA", "xGA"]
print(T[cols].round(1).to_string())
T[["P", "W", "D", "L", "GF", "GA", "GD", "Pts", "xPts", "diff", "sd", "z", "pos", "xpos", "xG", "xGA", "sim_xPts"]].round(4) \
    .to_csv("data/xpts_2627_final.csv")
print("ok")
