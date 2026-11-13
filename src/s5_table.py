"""Step 5: the current league table with expected points, as an image (rendered with Playwright, as in step 0)."""
import asyncio
from pathlib import Path
import pandas as pd
from playwright.async_api import async_playwright
T = pd.read_csv("data/xpts_2627_final.csv").rename(columns={"Unnamed: 0": "team", "diff": "gap", "pos": "Pos", "xpos": "xPos"}).sort_values("Pos")
SHORT = {"AFC Bournemouth": "Bournemouth", "Brighton & Hove Albion": "Brighton", "Nottingham Forest": "Nott'm Forest", "Tottenham Hotspur": "Tottenham",
         "Manchester City": "Man City", "Manchester United": "Man United", "Leeds United": "Leeds", "Ipswich Town": "Ipswich", "Coventry City": "Coventry",
         "Hull City": "Hull", "Newcastle United": "Newcastle", "Crystal Palace": "Crystal Palace"}
GREEN, RED = "#1a7f5a", "#c0392b"
rows = ""
for r in T.itertuples():
    out = abs(r.z) > 2
    col = GREEN if r.gap > 0 else RED
    w = min(abs(r.gap) / 8, 1) * 70
    bar = f'<div class="bar" style="width:{w:.0f}px;background:{col};{"margin-left:auto" if r.gap < 0 else ""}"></div>'
    gapcell = (f'<td class="gb"><div class="half neg">{bar if r.gap < 0 else ""}</div><div class="half pos">{bar if r.gap > 0 else ""}</div></td>' +
               (f'<td class="num g" style="color:#6b7280">0.0</td>' if abs(r.gap) < 0.05 else f'<td class="num g" style="color:{col}">{r.gap:+.1f}</td>'))
    mv = r.Pos - r.xPos
    rows += (f'<tr class="{"zone" if r.Pos >= 18 else ""}{" out" if out else ""}"><td class="num pos">{r.Pos}</td><td class="team">{SHORT.get(r.team, r.team)}</td>'
             f'<td class="num">{r.P}</td><td class="num">{r.W}</td><td class="num">{r.D}</td><td class="num">{r.L}</td><td class="num">{("0" if r.GD == 0 else f"{r.GD:+d}")}</td>'
             f'<td class="num pts">{r.Pts}</td><td class="num x">{r.xPts:.1f}</td>{gapcell}<td class="num xp">{r.xPos}</td></tr>')
H = f"""<html><head><style>
*{{box-sizing:border-box;margin:0}} body{{width:1080px;height:1350px;background:#fcfcfb;font-family:Inter,sans-serif;color:#1f2328;padding:62px 64px}}
h1{{font-size:40px;font-weight:700;letter-spacing:-.01em;line-height:1.15}} .sub{{font-size:22px;color:#5b6370;margin-top:10px}}
table{{width:100%;border-collapse:collapse;margin-top:34px;font-size:22px}}
th{{font-size:15px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.06em;text-align:right;padding:0 8px 12px;border-bottom:2px solid #1f2328}}
th.l{{text-align:left}} th.c{{text-align:center}}
td{{padding:0 8px;height:46px;border-bottom:1px solid #e6e6e3;vertical-align:middle}}
.num{{text-align:right;font-variant-numeric:tabular-nums}} .pos{{color:#6b7280;width:46px}} .team{{font-weight:500}}
.pts{{font-weight:700}} .x{{color:#374151}} .xp{{color:#6b7280}} .g{{font-weight:700;width:76px}}
.gb{{width:150px;padding:0}} .gb div.half{{display:inline-block;width:72px;height:14px;vertical-align:middle}} .neg{{text-align:right;border-right:1.5px solid #9ca3af}}
.bar{{height:14px;border-radius:3px}} .neg .bar{{border-radius:3px 0 0 3px}} .pos .bar{{border-radius:0 3px 3px 0}}
tr.out td{{background:#eef6f2}} tr.out .team{{font-weight:700}}
tr.zone td.pos{{color:{RED}}}
.foot{{position:absolute;left:64px;right:64px;bottom:44px;font-size:15.5px;color:#5b6370;line-height:1.5}} .foot b{{color:#1f2328}}
</style></head><body>
<h1>Premier League 2026/27 after {int(T.P.iloc[0])} games:<br>actual table v expected points</h1>
<div class="sub">xPts from every match simulated shot by shot, from expected goals (xG)</div>
<table><tr><th class="l">#</th><th class="l">Team</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th><th>xPts</th><th class="c">Gap</th><th></th><th>xPos</th></tr>{rows}</table>
<div class="foot"><b>Gap</b> = actual points − xPts. <b>xPos</b> = position on expected points. Shaded: beyond 2 standard deviations of normal luck.<br>
Data: FotMob shot xG (Opta model) · {len(pd.read_csv('raw/matches_2627.csv'))} matches, {len(pd.read_csv('raw/shots_2627.csv')):,} shots · xG scaled to league scoring · own goals left out of the model<br><b>Rafiz Rayhan</b></div>
</body></html>"""
Path("out").mkdir(exist_ok=True); open("out/_table.html", "w").write(H)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        await pg.goto(Path("out/_table.html").resolve().as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(300)
        await pg.screenshot(path="out/xpts_table_2627.png"); await b.close()
    Path("out/_table.html").unlink(); print("ok")
asyncio.run(main())
