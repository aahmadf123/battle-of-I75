"""All headline numbers. Writes data/processed/results.json.

Nothing in the write-up is typed by hand: every figure quoted on the page
comes from this file.
"""
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from common import MANUAL, PROC

rng = np.random.default_rng(91)  # Game 91
R = {}


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


def rec(df, col="result"):
    return f"{(df[col]=='W').sum()}-{(df[col]=='L').sum()}-{(df[col]=='T').sum()}"


# ---------------- A. Series, 90 games ----------------
s = pd.read_csv(PROC / "series.csv")
s["ut_net"] = (s.result == "W").astype(int) - (s.result == "L").astype(int)
s["cum_net"] = s.ut_net.cumsum()
s.to_csv(PROC / "series.csv", index=False)
R["series"] = dict(record=rec(s), games=len(s), ut_pts=int(s.ut_pts.sum()), bg_pts=int(s.bg_pts.sum()),
                   ut_home=rec(s[s.host == "Toledo"]), ut_away=rec(s[s.host == "Bowling Green"]),
                   max_ut_lead=int(s.cum_net.max()), max_bg_lead=int(-s.cum_net.min()),
                   season_max_ut=int(s.loc[s.cum_net.idxmax(), "season"]),
                   season_max_bg=int(s.loc[s.cum_net.idxmin(), "season"]))

# home field across the whole series
dec = s[s.result != "T"]
home_won = ((dec.host == "Toledo") & (dec.result == "W")) | ((dec.host == "Bowling Green") & (dec.result == "L"))
k, n = int(home_won.sum()), len(dec)
R["series"]["home_team"] = dict(wins=k, decisions=n, pct=round(k / n, 3), ci95=wilson(k, n),
                                binom_p=round(stats.binomtest(k, n, 0.5).pvalue, 3))
# sensitivity: the one unresolved site (1924) flipped
alt = dec.copy()
alt.loc[alt.season == 1924, "host"] = "Toledo"
hw2 = ((alt.host == "Toledo") & (alt.result == "W")) | ((alt.host == "Bowling Green") & (alt.result == "L"))
R["series"]["home_team"]["if_1924_at_toledo"] = int(hw2.sum())

# streaks and runs test: is the series streakier than coin flips?
seq = dec.result.tolist()
runs = 1 + sum(a != b for a, b in zip(seq, seq[1:]))
def longest_run(x):
    best = cur = 1
    for a, b in zip(x, x[1:]):
        cur = cur + 1 if a == b else 1
        best = max(best, cur)
    return best


sims, longs = [], []
for _ in range(20000):
    p = rng.permutation(seq)
    sims.append(1 + int((p[1:] != p[:-1]).sum()))
    longs.append(longest_run(list(p)))
sims, longs = np.array(sims), np.array(longs)
longest = {"W": 0, "L": 0}
cur, ch = 0, None
for x in seq:
    cur = cur + 1 if x == ch else 1
    ch = x
    longest[x] = max(longest[x], cur)
R["series"]["streaks"] = dict(observed_runs=runs, expected_runs=round(float(sims.mean()), 1),
                              p_fewer_runs=round(float((sims <= runs).mean()), 4),
                              longest_ut=longest["W"], longest_bg=longest["L"],
                              p_any_run_ge_12=round(float((longs >= 12).mean()), 3),
                              p_any_run_ge_9=round(float((longs >= 9).mean()), 3),
                              note="Permutation test on decided games in order; ties dropped.")

# eras
def era(a, b, label):
    g = s[(s.season >= a) & (s.season <= b)]
    return dict(label=label, years=f"{a}-{b}", games=len(g), record=rec(g),
                ut_pts=int(g.ut_pts.sum()), bg_pts=int(g.bg_pts.sum()),
                avg_total=round(float((g.ut_pts + g.bg_pts).mean()), 1))
R["eras"] = [era(1919, 1979, "Before a trophy"), era(1980, 2010, "Peace Pipe trophy"),
             era(2011, 2025, "Battle of I-75 trophy")]

# ---------------- B. Rivalry coin toss ----------------
ct = pd.read_csv(MANUAL / "coin_toss.csv")
known = ct[ct.toss_winner.notna()]
recv = ct[ct.recv_2h.notna()]
R["toss"] = dict(
    games_with_toss=len(known),
    toss_winner_deferred=int((known.decision == "defer").sum()),
    took_ball=known[known.decision == "receive"][["season", "toss_winner"]].to_dict("records"),
    toss_winner_won=int((known.toss_winner == known.winner).sum()),
    ut_won_toss=int((known.toss_winner == "UT").sum()), bg_won_toss=int((known.toss_winner == "BG").sum()),
)
k = int((recv.recv_2h == recv.winner).sum()); n = len(recv)
R["toss"]["recv2h"] = dict(wins=k, games=n, pct=round(k / n, 3), ci95=wilson(k, n),
                           binom_p=round(stats.binomtest(k, n, 0.5).pvalue, 3))
hk = int((recv.host == recv.winner).sum())
R["toss"]["home_in_same_games"] = dict(wins=hk, games=n, pct=round(hk / n, 3))
# by who deferred
for team in ("UT", "BG"):
    g = known[(known.toss_winner == team) & (known.decision == "defer")]
    R["toss"][f"{team}_deferred"] = dict(games=len(g), ut_record=f"{(g.winner=='UT').sum()}-{(g.winner=='BG').sum()}",
                                         seasons=g.season.tolist())
a = known[(known.toss_winner == "UT") & (known.decision == "defer")]
b = known[(known.toss_winner == "BG") & (known.decision == "defer")]
table = [[int((a.winner == "UT").sum()), int((a.winner == "BG").sum())],
         [int((b.winner == "UT").sum()), int((b.winner == "BG").sum())]]
R["toss"]["fisher_ut_defer_vs_bg_defer"] = dict(table=table, p=round(stats.fisher_exact(table)[1], 3))
# minimum detectable effect with this sample
R["toss"]["min_detectable_effect_pp"] = round(100 * 2.80 * np.sqrt(0.25 / n), 1)

# ---------------- C. League baseline, FBS 2014-2025 ----------------
lg = pd.read_csv(PROC / "league_games.csv")
w = lg[lg.receiver_ok & lg.home_spread.notna() & (lg.home_pts != lg.away_pts)].copy()
w["r2_home"] = w.recv_2h == w.home
# spread from the 2H receiver's view (negative = favored), margin from its view
w["r2_spread"] = np.where(w.r2_home, w.home_spread, -w.home_spread)
w["r2_margin"] = np.where(w.r2_home, w.home_pts - w.away_pts, w.away_pts - w.home_pts)
w["r2_win"] = (w.r2_margin > 0).astype(int)
w["r2_beat_line"] = w.r2_margin + w.r2_spread  # >0 means beat the closing spread

nL = len(w)
kL = int(w.r2_win.sum())
X = sm.add_constant(w[["r2_spread"]])
logit = sm.Logit(w.r2_win, X).fit(disp=0)
b0, se0 = logit.params["const"], logit.bse["const"]
pp = lambda x: 100 * (1 / (1 + np.exp(-x)) - 0.5)
ols = sm.OLS(w.r2_beat_line, np.ones(nL)).fit()
boot = [w.r2_beat_line.sample(nL, replace=True, random_state=i).mean() for i in range(2000)]
R["league"] = dict(
    seasons="2014-2025", games=nL,
    balance=dict(mean_r2_spread=round(float(w.r2_spread.mean()), 2), share_r2_home=round(float(w.r2_home.mean()), 3),
                 note="If 2H receivers were systematically better teams this would be far from 0. A coin decides it, so it should be ~0."),
    raw_win_pct=round(kL / nL, 4), raw_ci95=wilson(kL, nL),
    spread_adjusted_pp=round(float(pp(b0)), 2),
    spread_adjusted_ci_pp=[round(float(pp(b0 - 1.96 * se0)), 2), round(float(pp(b0 + 1.96 * se0)), 2)],
    spread_adjusted_p=round(float(logit.pvalues["const"]), 3),
    pts_vs_spread=round(float(ols.params.iloc[0]), 2),
    pts_vs_spread_ci=[round(float(np.percentile(boot, 2.5)), 2), round(float(np.percentile(boot, 97.5)), 2)],
    pts_vs_spread_p=round(float(ols.pvalues.iloc[0]), 3),
)
# robustness: by season, and inside the points_ok subset
R["league"]["by_season"] = {int(k): round(float(v), 3) for k, v in w.groupby("season").r2_win.mean().items()}
sub = w[w.game_id.isin(lg[lg.points_ok].game_id)]
R["league"]["win_pct_points_ok_subset"] = dict(games=len(sub), pct=round(float(sub.r2_win.mean()), 4))
R["league"]["win_pct_excl_2020"] = round(float(w[w.season != 2020].r2_win.mean()), 4)

# Middle Eight (points_ok subset)
m = lg[lg.points_ok].copy()
m["m8_diff"] = m.m8_recv2h - m.m8_other
R["league"]["middle_eight"] = dict(
    games=len(m), mean_diff=round(float(m.m8_diff.mean()), 2),
    ci95=[round(float(m.m8_diff.mean() - 1.96 * m.m8_diff.std() / np.sqrt(len(m))), 2),
          round(float(m.m8_diff.mean() + 1.96 * m.m8_diff.std() / np.sqrt(len(m))), 2)],
    recv2h_scored_first_q3_drive=round(float((m.q3_first_drive_pts > 0).mean()), 3),
)
# what the league effect implies for the rivalry sample
eff = max(abs(R["league"]["raw_win_pct"] - 0.5), 0.005)
R["league"]["games_needed_80pct_power"] = int(np.ceil((1.96 + 0.84) ** 2 * 0.25 / eff ** 2))
w[["game_id", "season", "home", "away", "recv_2h", "r2_spread", "r2_margin", "r2_win", "r2_beat_line"]].to_csv(
    PROC / "league_analysis_rows.csv", index=False)

# ---------------- D. Rivalry Middle Eight (CFBD, points_ok only) ----------------
rv = pd.read_csv(PROC / "rivalry_games.csv")
rv = rv[rv.points_ok]
R["rivalry_middle_eight"] = rv[["season", "recv_2h", "m8_recv2h", "m8_other"]].to_dict("records")

(PROC / "results.json").write_text(json.dumps(R, indent=2, default=str))
print(json.dumps(R, indent=1, default=str))
