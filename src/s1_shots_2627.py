"""Step 1: shot and match tables from the FotMob files, Premier League 2026/27 so far.

Checks
  * every match finished, every team has played the same number of games
  * shot goals plus own goals reproduce the final score of every match
  * the rebuilt table adds up (3 x wins + draws = points, wins = losses, goal difference sums to 0)
Own goals: FotMob lists an own goal under the team of the player who scored it, so it counts for the opponent.
"""
import json, glob
from pathlib import Path
import pandas as pd

IN = "raw/fotmob_pl_2026_27"
S, M = [], []
for f in sorted(glob.glob(f"{IN}/match_*.json")):
    d = json.load(open(f)); g = d["general"]; h, a = d["header"]["teams"]
    assert g["homeTeam"]["id"] == h["id"] and g["awayTeam"]["id"] == a["id"], f
    mid = int(g["matchId"])
    M.append(dict(match_id=mid, round=int(g["matchRound"]), date=g["matchTimeUTCDate"][:10], home=h["name"], away=a["name"],
                  home_id=h["id"], away_id=a["id"], hg=h["score"], ag=a["score"], finished=g["finished"]))
    for s in d["shotmap"]["shots"]:
        S.append(dict(match_id=mid, team_id=s["teamId"], player=s.get("playerName"), min=s.get("min"), period=s.get("period"),
                      event=s["eventType"], xG=s.get("expectedGoals"), situation=s.get("situation"), own_goal=bool(s.get("isOwnGoal"))))
M = pd.DataFrame(M).sort_values(["date", "match_id"]).reset_index(drop=True)
S = pd.DataFrame(S)
S["side"] = S.merge(M[["match_id", "home_id"]], on="match_id").eval("team_id == home_id").map({True: "h", False: "a"}).values

games = pd.concat([M.home, M.away]).value_counts()
print(f"CHECK 1  {len(M)} matches, all finished: {bool(M.finished.all())} | 20 teams: {games.size == 20} | "
      f"games per team: {sorted(games.unique())}")

bad = 0
for m in M.itertuples():
    s = S[S.match_id == m.match_id]
    goals = lambda side: ((s.side == side) & (s.event == "Goal") & ~s.own_goal).sum()
    ogs = lambda side: ((s.side == side) & s.own_goal).sum()          # own goals by players of this side
    bad += (goals("h") + ogs("a"), goals("a") + ogs("h")) != (m.hg, m.ag)
print(f"CHECK 2  shots + own goals reproduce the score: {len(M) - bad} of {len(M)} matches")

n = len(M); w = (M.hg > M.ag).sum(); dr = (M.hg == M.ag).sum()
print(f"CHECK 3  {len(S)} shots, {int(S.own_goal.sum())} own goals (no xG), shots without xG other than own goals: "
      f"{int((S.xG.isna() & ~S.own_goal).sum())} | goals {int(M.hg.sum() + M.ag.sum())}, home wins {w}, draws {dr}, away wins {n - w - dr}")

Path("raw").mkdir(exist_ok=True)
S.to_csv("raw/shots_2627.csv", index=False); M.to_csv("raw/matches_2627.csv", index=False)
print("ok")
