# Battle of I-75: coin tosses, the Middle Eight, and a 43-43-4 tie

Code and data behind the field note at **ahmadfx.xyz/field-notes/battle-of-i75**.

Toledo and Bowling Green have played 90 times since 1919. The series is 43-43-4.
This repo asks one question with real data: **does winning the coin toss and
deferring actually help you win?**

## Short answer

| Question | Answer | Evidence |
|---|---|---|
| Does receiving the 2nd-half kickoff win games? | No measurable effect | 8,310 FBS games, 2014-2025: 50.3% win rate, spread-adjusted effect -0.15 pts of win probability (95% CI -1.45 to +1.16) |
| Does it win the Middle Eight? | Yes, by about a point | +0.93 points per game (95% CI +0.75 to +1.11), 5,545 games |
| What happened in the rivalry? | 2nd-half receiver went 16-11 | 27 games, 1998-2025. p = 0.44. Too few games to tell. |
| How often does the toss winner defer? | 22 of 26 | Official box scores, every rivalry game with a public toss line |

## What is in here

```
data/
  manual/coin_toss.csv          every rivalry coin toss, verbatim line + source URL
  processed/series.csv          all 90 games, reconciled across 3 sources
  processed/discrepancies.csv   every place the sources disagree, and how it was resolved
  processed/boxscore_text.csv   toss + weather lines pulled from official box scores
  processed/league_games.csv    one row per FBS game, 2014-2025 (from CFBD)
  processed/rivalry_games.csv   one row per rivalry game, 2001-2025 (from CFBD)
  processed/results.json        every number quoted in the field note
src/
  common.py           paths, cached downloads, CFBD key handling
  pull_series.py      official UT + BGSU series pages and CFBD matchup
  resolve_series.py   majority-vote reconciliation, logs disagreements
  pull_boxscores.py   official box scores, extracts toss + weather lines
  pull_cfbd.py        CFBD games, closing lines, drives (about 50 API calls)
  build_games.py      per-game features: receivers, Middle Eight, spread
  code_coin_toss.py   hand-coded toss table, cross-checked against CFBD
  analyze.py          all statistics -> results.json
  charts.py           figures/*.png
figures/              the four charts used in the field note
METHODOLOGY.md        definitions, sources, checks, limitations
```

## Run it yourself

You need Python 3.10+ and a free CollegeFootballData.com API key.

```
pip install -r requirements.txt
set CFBD_API_KEY=your_key_here        (Windows)
export CFBD_API_KEY=your_key_here     (Mac/Linux)
python run_all.py
```

The first run downloads about 200 MB of CFBD drive data into `~/cfbd_cache`
(outside the repo) and uses roughly 50 of the 1,000 free monthly API calls.
Later runs read from the cache.

## Sources

- [CollegeFootballData.com](https://collegefootballdata.com) API: games, closing lines, drives
- [Toledo Athletics series history vs. Bowling Green](https://utrockets.com/sports/football/opponent-history/bowling-green/12)
- [BGSU Athletics series history vs. Toledo](https://bgsufalcons.com/sports/football/opponent-history/university-of-toledo/14)
- Official box scores from utrockets.com, stats.utrockets.com and bgsufalcons.com (one URL per game in `coin_toss.csv`)

## License

Code: MIT. Data comes from the sources above and stays under their terms.
