"""Build the 90-game series table from three independent sources.

Sources
  UT   : utrockets.com opponent-history page (Toledo SID)
  BG   : bgsufalcons.com opponent-history page (BGSU SID)
  CFBD : collegefootballdata.com /teams/matchup (1962 onward only)

Every disagreement between sources is kept and flagged, never silently fixed.
Output: data/processed/series.csv
"""
import re

import pandas as pd
from bs4 import BeautifulSoup

from common import PROC, cached_get, cfbd_json

UT_URL = "https://utrockets.com/sports/football/opponent-history/bowling-green/12"
BG_URL = "https://bgsufalcons.com/sports/football/opponent-history/university-of-toledo/14"


def parse_history(html: str, us: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "lxml")
    table = max(soup.find_all("table"), key=lambda t: len(t.find_all("tr")))
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
        if len(cells) < 4:
            continue
        date, season, loc, score = cells[:4]
        m = re.search(r"\b([WLT])\s+(\d+)-(\d+)", score)
        ot = re.search(r"\((\d*OT)\)", score)
        if not m or not season.isdigit():
            continue
        res, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        side = loc.split()[0].lower()  # home / away / neutral
        rows.append(dict(season=int(season), date=date, loc=loc, side=side,
                         res=res, us=a, them=b, ot=ot.group(1) if ot else "", raw_score=score))
    df = pd.DataFrame(rows)
    if us == "UT":
        df = df.rename(columns={"us": "ut_pts", "them": "bg_pts"})
        df["ut_host"] = df.side == "home"
    else:
        df = df.rename(columns={"us": "bg_pts", "them": "ut_pts"})
        df["ut_host"] = df.side == "away"
    return df.add_prefix(f"{us.lower()}_").rename(columns={f"{us.lower()}_season": "season"})


def main():
    ut = parse_history(cached_get(UT_URL, "ut_series.html"), "UT")
    bg = parse_history(cached_get(BG_URL, "bg_series.html"), "BG")
    m = cfbd_json("/teams/matchup", "matchup.json", team1="Toledo", team2="Bowling Green")
    cf = pd.DataFrame(m["games"])
    cf = pd.DataFrame({
        "season": cf.season,
        "cfbd_date": cf.date.str[:10],
        "cfbd_venue": cf.venue,
        "cfbd_ut_host": cf.homeTeam == "Toledo",
        "cfbd_ut_pts": cf.apply(lambda g: g.homeScore if g.homeTeam == "Toledo" else g.awayScore, axis=1),
        "cfbd_bg_pts": cf.apply(lambda g: g.awayScore if g.homeTeam == "Toledo" else g.homeScore, axis=1),
    })
    assert ut.season.is_unique and bg.season.is_unique and cf.season.is_unique
    df = ut.merge(bg, on="season", how="outer").merge(cf, on="season", how="left")
    df = df.sort_values("season").reset_index(drop=True)

    flags = []
    for _, r in df.iterrows():
        f = []
        if (r.ut_ut_pts, r.ut_bg_pts) != (r.bg_ut_pts, r.bg_bg_pts):
            f.append("score_UT_vs_BG")
        if pd.notna(r.cfbd_ut_pts) and (r.ut_ut_pts, r.ut_bg_pts) != (r.cfbd_ut_pts, r.cfbd_bg_pts):
            f.append("score_UT_vs_CFBD")
        if pd.notna(r.cfbd_ut_pts) and (r.bg_ut_pts, r.bg_bg_pts) != (r.cfbd_ut_pts, r.cfbd_bg_pts):
            f.append("score_BG_vs_CFBD")
        if r.ut_ut_host != r.bg_ut_host:
            f.append("site_UT_vs_BG")
        if pd.notna(r.cfbd_ut_host) and r.ut_ut_host != r.cfbd_ut_host:
            f.append("site_UT_vs_CFBD")
        if r.ut_date.split(",")[0] != r.bg_date.split(",")[0] or r.ut_date.split(",")[-1].strip() != r.bg_date.split(",")[-1].strip():
            f.append("date_UT_vs_BG")
        flags.append(";".join(f))
    df["flags"] = flags
    df.insert(0, "game_no", range(1, len(df) + 1))
    df.to_csv(PROC / "series_sources.csv", index=False)
    print(len(df), "games")
    print(df[df["flags"] != ""][["season", "ut_date", "bg_date", "cfbd_date", "ut_loc", "bg_loc", "cfbd_venue",
                              "ut_raw_score", "bg_raw_score", "cfbd_ut_pts", "cfbd_bg_pts", "flags"]].to_string())


if __name__ == "__main__":
    main()
