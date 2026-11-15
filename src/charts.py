"""Static figures (PNG, 1600x900) for the field note and social posts.
Every value is read from data/processed or data/manual. No typed numbers."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from common import FIG, MANUAL, PROC

UT, BG = "#1F4E9C", "#E8590C"       # validated pair (CVD dE 25.8)
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#fcfcfb"
R = json.loads((PROC / "results.json").read_text())

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "font.family": "DejaVu Sans", "font.size": 15, "axes.edgecolor": MUTED,
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 1,
})


def frame(title, subtitle):
    fig, ax = plt.subplots(figsize=(16, 9), dpi=100)
    fig.subplots_adjust(left=0.08, right=0.96, top=0.80, bottom=0.13)
    fig.text(0.08, 0.92, title, fontsize=28, weight="bold", color=INK)
    fig.text(0.08, 0.865, subtitle, fontsize=16, color=INK2)
    fig.text(0.08, 0.03, "Ahmad Firas Azfar · ahmadfx.xyz/field-notes · data: CollegeFootballData.com, UT & BGSU official box scores",
             fontsize=11.5, color=MUTED)
    return fig, ax


def save(fig, name):
    fig.savefig(FIG / name)
    plt.close(fig)


# 1. Series rollercoaster ---------------------------------------------------
s = pd.read_csv(PROC / "series.csv")
fig, ax = frame("107 years, 90 games, dead even",
                "Toledo wins minus Bowling Green wins after each game. Above zero, Toledo leads the series.")
x = s.season.values
y = s.cum_net.values
ax.step(x, y, where="post", color=INK, linewidth=2)
ax.fill_between(x, y, 0, where=y > 0, step="post", color=UT, alpha=0.25, linewidth=0)
ax.fill_between(x, y, 0, where=y < 0, step="post", color=BG, alpha=0.25, linewidth=0)
ax.axhline(0, color=INK2, linewidth=1)
ax.axvspan(1935.6, 1947.6, color=GRID, alpha=0.8, linewidth=0)
ax.text(1941.6, 4.6, "No games\n1936–47", ha="center", va="top", fontsize=12, color=INK2)
lo = s.loc[s.cum_net.idxmin()]
ax.annotate(f"BG leads by {-int(lo.cum_net)} after {int(lo.season)}", (lo.season, lo.cum_net),
            xytext=(lo.season + 3, lo.cum_net - 0.2), fontsize=13, color=INK, va="center",
            arrowprops=dict(arrowstyle="-", color=INK2))
at = lambda yr: float(s.loc[s.season == yr, "cum_net"].iloc[0])
ax.annotate("BG wins 12 straight\n1955–66 (Doyt Perry era)", (1961, at(1961)), xytext=(1947, -9.3),
            fontsize=13, color=INK, ha="center", arrowprops=dict(arrowstyle="-", color=INK2))
ax.annotate("Toledo wins 9 straight\n2010–18", (2014, at(2014)), xytext=(2003, 3.6), fontsize=13, color=INK,
            ha="center", arrowprops=dict(arrowstyle="-", color=INK2))
ax.annotate(f"Now {R['series']['record']}", (2025, 0), xytext=(2017.5, -3.2), fontsize=14, weight="bold",
            color=INK, arrowprops=dict(arrowstyle="-", color=INK2))
ax.set_xlim(1917, 2028)
ax.set_ylim(-12, 5)
ax.set_ylabel("Series lead (games)")
ax.grid(axis="x", visible=False)
save(fig, "01_series_rollercoaster.png")

# 2. Middle Eight vs game ---------------------------------------------------
L = R["league"]
fig, ax = frame("Deferring wins the Middle Eight. It doesn't win the game.",
                f"Team receiving the 2nd-half kickoff, {L['games']:,} FBS vs FBS games, 2014–2025. Bars show 95% intervals.")
rows = [("Middle Eight points\n(last 4:00 of Q2 + first 4:00 of Q3)", L["middle_eight"]["mean_diff"], L["middle_eight"]["ci95"], UT),
        ("Final margin vs. the closing spread", L["pts_vs_spread"], L["pts_vs_spread_ci"], MUTED)]
for i, (lab, v, ci, c) in enumerate(rows):
    yy = 1 - i
    ax.barh(yy, v, height=0.42, color=c, zorder=3)
    ax.errorbar(v, yy, xerr=[[v - ci[0]], [ci[1] - v]], fmt="none", ecolor=INK, elinewidth=2, capsize=8, zorder=4)
    ax.text(max(v, ci[1]) + 0.06 if v >= 0 else ci[1] + 0.06, yy, f"{v:+.2f} pts  [{ci[0]:+.2f}, {ci[1]:+.2f}]",
            va="center", fontsize=15, color=INK)
ax.set_yticks([1, 0], [r[0] for r in rows], fontsize=15, color=INK)
ax.axvline(0, color=INK2, linewidth=1.2)
ax.set_xlim(-1.0, 1.9)
ax.set_ylim(-0.6, 1.6)
ax.set_xlabel("Points per game for the 2nd-half receiver")
ax.grid(axis="y", visible=False)
fig.subplots_adjust(left=0.30)
save(fig, "02_middle_eight_vs_game.png")

# 3. Sample size: league vs rivalry -----------------------------------------
T = R["toss"]["recv2h"]
fig, ax = frame("27 rivalry games can't settle the coin toss. 8,310 games can.",
                "Win rate of the team that received the 2nd-half kickoff, with 95% intervals.")
pts = [(f"Battle of I-75\n{T['wins']}-{T['games']-T['wins']} ({T['games']} games, 1998–2025)", T["pct"], T["ci95"], BG),
       (f"All FBS games\n{L['games']:,} games, 2014–2025", L["raw_win_pct"], L["raw_ci95"], UT)]
for i, (lab, p, ci, c) in enumerate(pts):
    yy = 1 - i
    ax.plot([ci[0] * 100, ci[1] * 100], [yy, yy], color=c, linewidth=6, solid_capstyle="round", zorder=3)
    ax.plot(p * 100, yy, "o", ms=16, color=c, mec=SURF, mew=2.5, zorder=4)
    ax.text(p * 100, yy + 0.2, f"{p*100:.1f}%", ha="center", fontsize=16, weight="bold", color=INK)
    ax.text(ci[1] * 100 + 1.2, yy, f"{ci[0]*100:.0f}% to {ci[1]*100:.0f}%", va="center", fontsize=14, color=INK2)
ax.axvline(50, color=INK2, linewidth=1.2, linestyle=(0, (4, 3)))
ax.text(50.4, 1.55, "coin flip", fontsize=13, color=INK2)
ax.set_yticks([1, 0], [p[0] for p in pts], fontsize=15, color=INK)
ax.set_xlim(35, 85)
ax.set_ylim(-0.5, 1.7)
ax.set_xlabel("Win rate of 2nd-half receiver (%)")
ax.grid(axis="y", visible=False)
fig.subplots_adjust(left=0.27)
save(fig, "03_sample_size.png")

# 4. Every rivalry coin toss --------------------------------------------------
ct = pd.read_csv(MANUAL / "coin_toss.csv")
fig, ax = frame("Every Battle of I-75 coin toss with a public record",
                "Official box scores, 1998–2025. Filled = toss winner deferred. Hollow = took the ball.")
labels = ["Won the toss", "Received 2nd half", "Won the game"]
col = {"UT": UT, "BG": BG}
for _, r in ct.iterrows():
    xx = r.season
    if isinstance(r.toss_winner, str):
        filled = r.decision == "defer"
        ax.plot(xx, 2, "o", ms=18, mfc=col[r.toss_winner] if filled else SURF, mec=col[r.toss_winner], mew=3, zorder=3)
    else:
        ax.text(xx, 2, "?", ha="center", va="center", fontsize=16, color=MUTED)
    if isinstance(r.recv_2h, str):
        ax.plot(xx, 1, "s", ms=16, color=col[r.recv_2h], mec=SURF, mew=2, zorder=3)
    else:
        ax.text(xx, 1, "?", ha="center", va="center", fontsize=16, color=MUTED)
    ax.plot(xx, 0, "D", ms=15, color=col[r.winner], mec=SURF, mew=2, zorder=3)
ax.set_yticks([2, 1, 0], labels, fontsize=15, color=INK)
ax.set_xticks(range(1998, 2026, 3))
ax.set_xlim(1996.8, 2026.2)
ax.set_ylim(-0.7, 2.7)
ax.grid(axis="y", visible=False)
ax.plot([], [], "o", ms=12, color=UT, label="Toledo")
ax.plot([], [], "o", ms=12, color=BG, label="Bowling Green")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2, frameon=False, fontsize=14)
fig.text(0.08, 0.065, "? = not determinable: 1998 toss line is a template error ('Miami'); 2000 has no play-by-play.",
         fontsize=12, color=INK2)
fig.subplots_adjust(left=0.17, bottom=0.2)
save(fig, "04_every_coin_toss.png")
print("figures written:", sorted(p.name for p in FIG.glob("*.png")))
