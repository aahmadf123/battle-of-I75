"""Pull CFBD games, betting lines and drives.

League baseline : every regular-season FBS game, 2014-2025
Rivalry games   : Toledo drives 2001-2013 (2014+ is in the league pull)

Raw JSON is large (about 20 MB of drives per season), so it is cached outside
the repo in $CFBD_CACHE (default ~/cfbd_cache). Only compact processed tables
are committed. Total cost: about 50 API calls, well inside the free tier.
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

from common import CFBD, cfbd_key

CACHE = Path(os.environ.get("CFBD_CACHE", Path.home() / "cfbd_cache"))
CACHE.mkdir(parents=True, exist_ok=True)
LEAGUE_SEASONS = range(2014, 2026)
RIVALRY_EARLY = range(2001, 2014)


def get(endpoint, fname, **params):
    path = CACHE / fname
    if path.exists():
        return
    for attempt in range(3):
        try:
            r = requests.get(f"{CFBD}{endpoint}", params=params,
                             headers={"Authorization": f"Bearer {cfbd_key()}"}, timeout=300)
            r.raise_for_status()
            json.loads(r.text)  # make sure it is complete JSON before saving
            path.write_text(r.text, encoding="utf-8")
            print("saved", fname, f"{len(r.text)/1e6:.1f} MB", flush=True)
            time.sleep(1)
            return
        except Exception as e:
            print("retry", fname, e, flush=True)
            time.sleep(5 * (attempt + 1))
    sys.exit(f"failed: {fname}")


if __name__ == "__main__":
    for y in LEAGUE_SEASONS:
        get("/games", f"games_{y}.json", year=y, seasonType="regular")
        get("/lines", f"lines_{y}.json", year=y, seasonType="regular")
        get("/drives", f"drives_{y}.json", year=y, seasonType="regular")
    for y in RIVALRY_EARLY:
        get("/games", f"games_tol_{y}.json", year=y, team="Toledo", seasonType="regular")
        get("/drives", f"drives_tol_{y}.json", year=y, team="Toledo", seasonType="regular")
    print("DONE")
