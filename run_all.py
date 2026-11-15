"""Rebuild everything from scratch: python run_all.py"""
import runpy
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC))

STEPS = [
    "pull_series.py",      # official series pages + CFBD matchup
    "resolve_series.py",   # reconcile, log discrepancies
    "pull_boxscores.py",   # toss + weather lines from official box scores
    "pull_cfbd.py",        # CFBD games, lines, drives (cached)
    "build_games.py",      # per-game features
    "code_coin_toss.py",   # coded toss table + CFBD cross-check
    "analyze.py",          # every statistic -> results.json
    "charts.py",           # figures
]

for step in STEPS:
    print(f"\n=== {step} ===")
    runpy.run_path(str(SRC / step), run_name="__main__")
