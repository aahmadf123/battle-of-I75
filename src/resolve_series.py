"""Resolve the three-source table into one canonical row per game.

Rule: majority vote across available sources (UT, BG, CFBD).
If only two sources exist and they disagree, keep UT's value, mark the
game 'unresolved', and test that choice in a sensitivity check.
Output: data/processed/series.csv and data/processed/discrepancies.csv
"""
import pandas as pd

from common import PROC

df = pd.read_csv(PROC / "series_sources.csv")


def vote(vals):
    vals = [v for v in vals if v is not None and not (isinstance(v, float) and pd.isna(v))]
    best = max(set(vals), key=vals.count)
    return best, vals.count(best), len(vals)


out, log = [], []
for _, r in df.iterrows():
    cf_score = None if pd.isna(r.cfbd_ut_pts) else (int(r.cfbd_ut_pts), int(r.cfbd_bg_pts))
    score, n_agree, n_src = vote([(r.ut_ut_pts, r.ut_bg_pts), (r.bg_ut_pts, r.bg_bg_pts), cf_score])
    s_status = "agree" if n_agree == n_src else ("majority" if n_agree >= 2 else "unresolved")
    if s_status == "unresolved":
        score = (r.ut_ut_pts, r.ut_bg_pts)
    cf_host = None if pd.isna(r.cfbd_ut_host) else bool(r.cfbd_ut_host)
    host, h_agree, h_src = vote([bool(r.ut_ut_host), bool(r.bg_ut_host), cf_host])
    h_status = "agree" if h_agree == h_src else ("majority" if h_agree >= 2 else "unresolved")
    if h_status == "unresolved":
        host = bool(r.ut_ut_host)
    ut, bg = int(score[0]), int(score[1])
    out.append(dict(
        game_no=r.game_no, season=r.season, date_ut_page=r.ut_date, date_bg_page=r.bg_date,
        host="Toledo" if host else "Bowling Green", ut_pts=ut, bg_pts=bg,
        result="W" if ut > bg else ("L" if ut < bg else "T"), ot=r.ut_ot if isinstance(r.ut_ot, str) else "",
        score_status=s_status, site_status=h_status, flags=r["flags"] if isinstance(r["flags"], str) else ""))
    if isinstance(r["flags"], str) and r["flags"]:
        log.append(dict(season=r.season, flags=r["flags"],
                        ut_page=f"{r.ut_date} | {r.ut_loc} | {r.ut_raw_score}",
                        bg_page=f"{r.bg_date} | {r.bg_loc} | {r.bg_raw_score}",
                        cfbd="" if pd.isna(r.cfbd_date) else f"{r.cfbd_date} | UT home={r.cfbd_ut_host} | UT {r.cfbd_ut_pts:.0f}-{r.cfbd_bg_pts:.0f}",
                        resolved=f"host={'Toledo' if host else 'Bowling Green'} ({h_status}); score UT {ut}-{bg} ({s_status})"))

s = pd.DataFrame(out)
s.to_csv(PROC / "series.csv", index=False)
pd.DataFrame(log).to_csv(PROC / "discrepancies.csv", index=False)

w, l, t = (s.result == "W").sum(), (s.result == "L").sum(), (s.result == "T").sum()
print(f"Series (UT view): {w}-{l}-{t} in {len(s)} games")
print("Points UT-BG:", s.ut_pts.sum(), "-", s.bg_pts.sum())
for h in ("Toledo", "Bowling Green"):
    g = s[s.host == h]
    print(f"UT record at {h}: {(g.result=='W').sum()}-{(g.result=='L').sum()}-{(g.result=='T').sum()}")
print(pd.DataFrame(log)[["season", "resolved"]].to_string(index=False))
