"""Pull the official box score for every rivalry game 1998-2025 and extract,
verbatim, the coin-toss line and the weather line.

These text lines are the only thing taken from box scores. Every number in
the analysis comes from CFBD or the official series pages.
Output: data/processed/boxscore_text.csv
"""
import re

import pandas as pd
from bs4 import BeautifulSoup

from common import PROC, cached_get

UT = "https://utrockets.com/sports/football/stats/{y}/bowling-green/boxscore/{i}"
UTL = "http://stats.utrockets.com//stats/football/{y}/utbg{d}.htm"
BG = "https://bgsufalcons.com/sports/football/stats/{y}/toledo/boxscore/{i}"

SOURCES = {
    1998: BG.format(y=1998, i=9470), 1999: BG.format(y=1999, i=904),
    2000: BG.format(y=2000, i=915), 2001: BG.format(y=2001, i=926),
    2002: BG.format(y=2002, i=939), 2003: BG.format(y=2003, i=951),
    2004: BG.format(y=2004, i=964), 2005: BG.format(y=2005, i=976),
    2006: BG.format(y=2006, i=989), 2007: BG.format(y=2007, i=1002),
    2008: UTL.format(y=2008, d="1128"), 2009: UTL.format(y=2009, d="1127"),
    2010: UTL.format(y=2010, d="1117"), 2011: UTL.format(y=2011, d="1015"),
    2012: UTL.format(y=2012, d="0915"), 2013: UTL.format(y=2013, d="1026"),
    2014: UTL.format(y=2014, d="1119"), 2015: UTL.format(y=2015, d="1117"),
    2016: UT.format(y=2016, i=15895), 2017: UT.format(y=2017, i=16392),
    2018: BG.format(y=2018, i=8864), 2019: UT.format(y=2019, i=17467),
    2020: UT.format(y=2020, i=18951), 2021: BG.format(y=2021, i=11167),
    2022: UT.format(y=2022, i=21566), 2023: UT.format(y=2023, i=22590),
    2024: UT.format(y=2024, i=23239), 2025: UT.format(y=2025, i=23738),
}

TOSS = re.compile(r"[^\n]{0,80}\b(toss|coin)\b[^\n]{0,160}", re.I)


def page_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style"]):
        t.decompose()
    txt = soup.get_text("\n")
    return re.sub(r"[ \t\xa0]+", " ", txt)


def weather(txt: str) -> dict:
    """Return temperature / wind / sky exactly as the box score prints them."""
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    out = {}
    for i, l in enumerate(lines):
        for key, lab in (("temp", "Temperature"), ("wind", "Wind"), ("sky", "Weather")):
            if key in out:
                continue
            m = re.search(lab + r":\s*(.*?)(?=\s*(?:•|Temperature:|Wind:|Weather:|$))", l)
            if not m or not l.startswith(("Temperature", "Wind", "Weather")):
                continue
            val = m.group(1).strip() or (lines[i + 1] if i + 1 < len(lines) else "")
            if val and not val.endswith(":"):
                out[key] = val
    return out


def main():
    rows = []
    for y, url in SOURCES.items():
        try:
            txt = page_text(cached_get(url, f"box/{y}.html"))
        except Exception as e:  # keep going, record the failure
            rows.append(dict(season=y, url=url, toss_text="", error=str(e)[:120]))
            continue
        toss = []
        for m in TOSS.finditer(txt):
            line = m.group(0).strip()
            if line and line not in toss and "tossed" not in line.lower():
                toss.append(line)
        wx = weather(txt)
        rows.append(dict(season=y, url=url, toss_text=" || ".join(toss[:3]),
                         wx_temp=wx.get("temp", ""), wx_wind=wx.get("wind", ""),
                         wx_sky=wx.get("sky", ""), error=""))
    out = pd.DataFrame(rows)
    out.to_csv(PROC / "boxscore_text.csv", index=False)
    pd.set_option("display.max_colwidth", 90)
    print(out[["season", "wx_temp", "wx_wind", "wx_sky", "error"]].to_string(index=False))


if __name__ == "__main__":
    main()
