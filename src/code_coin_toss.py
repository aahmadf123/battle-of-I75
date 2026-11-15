"""Hand-coded coin-toss table, one row per game 1998-2025.

Coding rule: toss_winner and decision are read straight from the verbatim
toss line (column toss_text, copied by pull_boxscores.py). Receivers come
from the opening and 2nd-half kickoffs in the same box score, then are
cross-checked against CFBD drives. Any conflict is written in `note`.
Output: data/manual/coin_toss.csv
"""
import pandas as pd

from common import MANUAL, PROC

# season: (toss_winner, decision, recv_1h, recv_2h, note)
CODED = {
    1998: (None, None, "BG", "UT", "Toss line names 'Miami' and says BG deferred, but UT kicked off to open and BG kicked off the 2nd half. Line is a template error; toss winner unknown."),
    1999: ("UT", "defer", "BG", "UT", ""),
    2000: (None, None, None, None, "Box score has no play-by-play; toss not in public record."),
    2001: ("BG", "defer", "UT", "BG", ""),
    2002: ("BG", "defer", "UT", "BG", ""),
    2003: ("BG", "defer", "UT", "BG", ""),
    2004: ("BG", "receive", "BG", "UT", ""),
    2005: ("UT", "defer", "BG", "UT", "Went to 2OT (OT toss not used here)."),
    2006: ("BG", "defer", "UT", "BG", ""),
    2007: ("BG", "receive", "BG", "UT", "CFBD drive order lists Toledo first; box score kickoff shows BG received. Box score used."),
    2008: ("UT", "defer", "BG", "UT", ""),
    2009: ("UT", "receive", "UT", "BG", ""),
    2010: ("BG", "defer", "UT", "BG", ""),
    2011: ("BG", "defer", "UT", "BG", ""),
    2012: ("UT", "defer", "BG", "UT", ""),
    2013: ("UT", "defer", "BG", "UT", ""),
    2014: ("BG", "defer", "UT", "BG", "Line only mentions UT's goal; kickoffs and CFBD confirm UT received 1H."),
    2015: ("BG", "receive", "BG", "UT", ""),
    2016: ("UT", "defer", "BG", "UT", ""),
    2017: ("UT", "defer", "BG", "UT", ""),
    2018: ("BG", "defer", "UT", "BG", ""),
    2019: ("UT", "defer", "BG", "UT", ""),
    2020: ("UT", "defer", "BG", "UT", ""),
    2021: ("UT", "defer", "BG", "UT", ""),
    2022: ("BG", "defer", "UT", "BG", ""),
    2023: ("BG", "defer", "UT", "BG", ""),
    2024: ("BG", "defer", "UT", "BG", ""),
    2025: ("BG", "defer", "UT", "BG", ""),
}

NAME = {"UT": "Toledo", "BG": "Bowling Green"}

box = pd.read_csv(PROC / "boxscore_text.csv").set_index("season")
series = pd.read_csv(PROC / "series.csv").set_index("season")
riv = pd.read_csv(PROC / "rivalry_games.csv").set_index("season")

rows = []
for y, (w, dec, r1, r2, note) in CODED.items():
    s = series.loc[y]
    cf = riv.loc[y] if y in riv.index else None
    cf_check = ""
    if cf is not None and r2:
        cf_check = "match" if cf.recv_2h == NAME[r2] and cf.recv_1h == NAME[r1] else "MISMATCH"
    rows.append(dict(
        season=y, host="UT" if s.host == "Toledo" else "BG",
        toss_winner=w, decision=dec, recv_1h=r1, recv_2h=r2,
        ut_pts=s.ut_pts, bg_pts=s.bg_pts, winner="UT" if s.ut_pts > s.bg_pts else "BG",
        cfbd_receiver_check=cf_check,
        wx_temp=box.loc[y, "wx_temp"], wx_wind=box.loc[y, "wx_wind"], wx_sky=box.loc[y, "wx_sky"],
        toss_text=box.loc[y, "toss_text"], source_url=box.loc[y, "url"], note=note))
df = pd.DataFrame(rows)
df.to_csv(MANUAL / "coin_toss.csv", index=False)
print(df[["season", "host", "toss_winner", "decision", "recv_2h", "winner", "cfbd_receiver_check", "wx_wind"]].to_string(index=False))
