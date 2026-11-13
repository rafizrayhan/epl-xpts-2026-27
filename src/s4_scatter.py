"""Step 4: scatter of expected points (x) v actual points (y), Premier League 2026/27 so far (same style as 2024/25)."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

for f in fm.findSystemFonts():
    if "Inter" in f: fm.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Inter", "DejaVu Sans"]
T = pd.read_csv("data/xpts_2627_final.csv", index_col=0)
SHORT = {"Nottingham Forest": "Nott'm Forest", "Manchester City": "Man City", "Manchester United": "Man Utd", "Newcastle United": "Newcastle",
         "Tottenham Hotspur": "Spurs", "AFC Bournemouth": "Bournemouth", "Brighton & Hove Albion": "Brighton", "Leeds United": "Leeds",
         "Ipswich Town": "Ipswich", "Coventry City": "Coventry", "Hull City": "Hull"}
G = int(T.P.iloc[0])
fig, ax = plt.subplots(figsize=(10, 10))
lo, hi = 4, 30
ax.plot([lo, hi], [lo, hi], color="#555", lw=1.2, ls="--", zorder=1)
ax.text(27.6, 28.7, "Points = xPts", rotation=45, color="#555", fontsize=10, ha="center")
ax.text(5.2, 27.5, "Overperformed\n(more points than xPts)", color="#1a7f5a", fontsize=11, weight="bold", va="top")
ax.text(21.5, 5.4, "Underperformed\n(fewer points than xPts)", color="#c0392b", fontsize=11, weight="bold")
col = ["#1a7f5a" if d > 0 else "#c0392b" for d in T["diff"]]
ax.scatter(T.xPts, T.Pts, s=90, c=col, edgecolor="white", lw=1, zorder=3)
# label offsets in data units (dx, dy); a thin leader line is drawn when the label is moved far
OFF = {"Arsenal": (-5.2, 0.6), "Brighton & Hove Albion": (-5.0, 0.8), "Manchester City": (0.5, 0.6), "Liverpool": (-4.6, 0.8),
       "Chelsea": (-4.4, 0.6), "Everton": (0.5, 0.5), "AFC Bournemouth": (0.5, -0.6), "Brentford": (-4.6, 0.4),
       "Leeds United": (0.5, -0.4), "Aston Villa": (-4.6, 0.6), "Tottenham Hotspur": (0.5, 0.5), "Newcastle United": (-5.0, 0.8),
       "Hull City": (-3.2, 1.2), "Ipswich Town": (0.5, 0.0), "Fulham": (0.5, 0.0), "Nottingham Forest": (0.5, -0.2),
       "Coventry City": (-4.5, -0.8), "Manchester United": (0.2, -1.3), "Sunderland": (0.5, 0.3), "Crystal Palace": (-5.4, -0.6)}
for t, r in T.iterrows():
    dx, dy = OFF[t]
    ax.annotate(f"{SHORT.get(t, t)} ({r['diff']:+.1f})", (r.xPts, r.Pts), xytext=(r.xPts + dx, r.Pts + dy), fontsize=10, zorder=4, va="center",
                arrowprops=dict(arrowstyle="-", color="#aaa", lw=0.7, shrinkA=0, shrinkB=5) if abs(dx) > 1 or abs(dy) > 1 else None)
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect("equal")
ax.set_xlabel("Expected points (xPts)", fontsize=12); ax.set_ylabel("Actual points", fontsize=12)
ax.set_title(f"Premier League 2026/27 after {G} games: actual points v expected points\n"
             "xPts from every match simulated shot by shot (10,000 runs)", fontsize=13, loc="left")
for s in ["top", "right"]: ax.spines[s].set_visible(False)
ax.grid(color="#eee", zorder=0)
fig.text(0.01, 0.005, "Data: FotMob shot xG (Opta model, league-calibrated). Distance from the dashed line = points above or below xPts. Rafiz Rayhan",
         fontsize=8.5, color="#666")
plt.tight_layout()
plt.savefig("out/xpts_scatter_2627.png", dpi=170)
print("ok")
