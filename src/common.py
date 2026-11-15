"""Shared helpers: paths, cached HTTP, CFBD auth."""
import json
import os
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
MANUAL = ROOT / "data" / "manual"
FIG = ROOT / "figures"
for p in (RAW, PROC, MANUAL, FIG):
    p.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (battle-of-i75 research; contact via github)"}
CFBD = "https://api.collegefootballdata.com"


def cfbd_key() -> str:
    key = os.environ.get("CFBD_API_KEY")
    if not key:
        alt = Path.home() / ".cfbd_key"
        if alt.exists():
            key = alt.read_text().strip()
    if not key:
        raise SystemExit("Set CFBD_API_KEY (free key at collegefootballdata.com).")
    return key


def cached_get(url: str, fname: str, params=None, cfbd=False, binary=False):
    """Download once, then reuse the local copy so reruns cost no API calls."""
    path = RAW / fname
    if path.exists():
        return path.read_bytes() if binary else path.read_text(encoding="utf-8")
    headers = dict(UA)
    if cfbd:
        headers["Authorization"] = f"Bearer {cfbd_key()}"
    r = requests.get(url, params=params, headers=headers, timeout=120)
    r.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    if binary:
        path.write_bytes(r.content)
        return r.content
    path.write_text(r.text, encoding="utf-8")
    time.sleep(0.5)
    return r.text


def cfbd_json(endpoint: str, fname: str, **params):
    return json.loads(cached_get(f"{CFBD}{endpoint}", fname, params=params, cfbd=True))
