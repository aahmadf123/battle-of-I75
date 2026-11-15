"""Turn raw CFBD games + lines + drives into one row per game.

Definitions (stated up front so readers can argue with them):
  1H receiver   offense on the first drive of the game
  2H receiver   offense on the first drive of the 3rd quarter
  Middle Eight  points scored on drives that END between 4:00 left in Q2
                and 11:00 left in Q3 (the last 4:00 of the half plus the first
                4:00 after halftime). A drive's points are booked at its end.
  Spread        median closing spread across all books CFBD lists (home view)
  receiver_ok   first Q1 and first Q3 drives start at 14:00 or later and
                were run by different teams (used for win analysis)
  points_ok     receiver_ok AND drive-level points add up to the official
                final score for both teams (used for Middle Eight analysis)

Outputs: data/processed/league_games.csv, data/processed/rivalry_games.csv
"""
import json
import os
from pathlib import Path
from statistics import median

import pandas as pd

from common import PROC

CACHE = Path(os.environ.get("CFBD_CACHE", Path.home() / "cfbd_cache"))


def secs(t):
    return t["minutes"] * 60 + t["seconds"]


def in_middle_eight(period, clock_s):
    return (period == 2 and clock_s <= 240) or (period == 3 and clock_s >= 660)


def game_features(g, drives, spread=None, total=None):
    home, away = g["homeTeam"], g["awayTeam"]
    ds = sorted(drives, key=lambda d: (d["startPeriod"], -secs(d["startTime"]), d["driveNumber"] or 0))
    if not ds:
        return None
    pts = {home: 0, away: 0}
    m8 = {home: 0, away: 0}
    for d in ds:
        off, de = d["offense"], d["defense"]
        if off not in pts or de not in pts:
            return None
        po = (d["endOffenseScore"] or 0) - (d["startOffenseScore"] or 0)
        pd_ = (d["endDefenseScore"] or 0) - (d["startDefenseScore"] or 0)
        pts[off] += po
        pts[de] += pd_
        if in_middle_eight(d["endPeriod"], secs(d["endTime"])):
            m8[off] += po
            m8[de] += pd_
    q1 = [d for d in ds if d["startPeriod"] == 1]
    q3 = [d for d in ds if d["startPeriod"] == 3]
    if not q1 or not q3:
        return None
    r1, r2 = q1[0]["offense"], q3[0]["offense"]
    hl, al = g.get("homeLineScores") or [], g.get("awayLineScores") or []
    receiver_ok = (secs(q1[0]["startTime"]) >= 840 and secs(q3[0]["startTime"]) >= 840 and r1 != r2)
    points_ok = (receiver_ok and pts[home] == g["homePoints"] and pts[away] == g["awayPoints"]
                 and len(hl) >= 4 and len(al) >= 4)
    other = away if r2 == home else home
    return dict(
        game_id=g["id"], season=g["season"], week=g["week"], date=g["startDate"][:10],
        home=home, away=away, neutral=g["neutralSite"], conf_game=g["conferenceGame"],
        home_pts=g["homePoints"], away_pts=g["awayPoints"],
        home_1h=sum(hl[:2]) if hl else None, away_1h=sum(al[:2]) if al else None,
        home_spread=spread, total_line=total,
        recv_1h=r1, recv_2h=r2, same_receiver=(r1 == r2),
        q3_first_drive_result=q3[0]["driveResult"], q3_first_drive_pts=(q3[0]["endOffenseScore"] or 0) - (q3[0]["startOffenseScore"] or 0),
        m8_recv2h=m8[r2], m8_other=m8[other],
        home_elo=g.get("homePregameElo"), away_elo=g.get("awayPregameElo"),
        receiver_ok=receiver_ok, points_ok=points_ok,
    )


def consensus(lines):
    sp = [l["spread"] for l in lines if l.get("spread") is not None]
    ou = [l["overUnder"] for l in lines if l.get("overUnder") is not None]
    return (median(sp) if sp else None, median(ou) if ou else None)


def load(fname):
    return json.loads((CACHE / fname).read_text(encoding="utf-8"))


def build_league():
    rows = []
    for y in range(2014, 2026):
        games = {g["id"]: g for g in load(f"games_{y}.json")
                 if g["completed"] and g["homeClassification"] == "fbs" and g["awayClassification"] == "fbs"}
        lines = {l["id"]: consensus(l["lines"]) for l in load(f"lines_{y}.json")}
        by_game = {}
        for d in load(f"drives_{y}.json"):
            by_game.setdefault(d["gameId"], []).append(d)
        for gid, g in games.items():
            sp, ou = lines.get(gid, (None, None))
            f = game_features(g, by_game.get(gid, []), sp, ou)
            if f:
                rows.append(f)
    df = pd.DataFrame(rows)
    df.to_csv(PROC / "league_games.csv", index=False)
    return df


def build_rivalry():
    rows = []
    for y in range(2001, 2026):
        gf = f"games_tol_{y}.json" if y < 2014 else f"games_{y}.json"
        dfname = f"drives_tol_{y}.json" if y < 2014 else f"drives_{y}.json"
        games = [g for g in load(gf) if {"Toledo", "Bowling Green"} == {g["homeTeam"], g["awayTeam"]}]
        drives = [d for d in load(dfname) if d["gameId"] in {g["id"] for g in games}]
        for g in games:
            f = game_features(g, drives)
            if f:
                rows.append(f)
    df = pd.DataFrame(rows)
    df.to_csv(PROC / "rivalry_games.csv", index=False)
    return df


if __name__ == "__main__":
    lg = build_league()
    print("league games:", len(lg), "| receiver_ok:", int(lg.receiver_ok.sum()),
          "| receiver_ok with spread:", int((lg.receiver_ok & lg.home_spread.notna()).sum()),
          "| points_ok:", int(lg.points_ok.sum()))
    rv = build_rivalry()
    print(rv[["season", "home", "home_pts", "away_pts", "recv_1h", "recv_2h", "m8_recv2h", "m8_other", "receiver_ok", "points_ok"]].to_string(index=False))
