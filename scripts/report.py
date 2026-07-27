#!/usr/bin/env python3
"""Print the area / power / timing of the design's latest LibreLane run.

Reads the aggregated ``metrics.json`` LibreLane writes at the end of the flow
under ``librelane/runs/<tag>/`` and prints the headline numbers. Metric key
names have drifted across LibreLane/OpenLane versions, so each field tries a
list of candidate keys and uses the first one present.

Usage:
    python3 scripts/report.py                 # human-readable summary
    python3 scripts/report.py --json          # raw picked metrics as JSON
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DESIGN_DIR = os.path.join(ROOT, "librelane")

# Candidate metric keys, most-preferred first.
AREA_KEYS = ["design__instance__area", "design__core__area", "design__die__area"]
DIE_AREA_KEYS = ["design__die__area", "design__die__area__um2"]
CELLS_KEYS = [
    "design__instance__count",
    "design__instance_count__setup",
    "design__instance__count__stdcell",
]
SLACK_KEYS = ["timing__setup__ws", "timing__setup__wns"]
HOLD_SLACK_KEYS = ["timing__hold__ws", "timing__hold__wns"]
POWER_KEYS = ["power__total", "power__internal__total"]
POWER_INT_KEYS = ["power__internal__total"]
POWER_SW_KEYS = ["power__switching__total"]
POWER_LEAK_KEYS = ["power__leakage__total"]


def pick(metrics: dict, keys):
    for k in keys:
        if k in metrics and metrics[k] is not None:
            return metrics[k]
    for k in keys:
        for mk, mv in metrics.items():
            if mk.startswith(k) and mv is not None:
                return mv
    return None


def latest_run(design_dir: str):
    runs = [r for r in glob.glob(os.path.join(design_dir, "runs", "*"))
            if os.path.isdir(r)]
    return max(runs, key=os.path.getmtime) if runs else None


def load_metrics(run_dir: str):
    candidates = [
        os.path.join(run_dir, "final", "metrics.json"),
        os.path.join(run_dir, "metrics.json"),
    ]
    candidates += sorted(glob.glob(os.path.join(run_dir, "**", "metrics.json"),
                                   recursive=True))
    for path in candidates:
        if os.path.isfile(path):
            with open(path) as fh:
                try:
                    return json.load(fh), path
                except json.JSONDecodeError:
                    continue
    return None, None


def clock_period(design_dir: str):
    cfg = os.path.join(design_dir, "config.json")
    if os.path.isfile(cfg):
        with open(cfg) as fh:
            try:
                return json.load(fh).get("CLOCK_PERIOD")
            except json.JSONDecodeError:
                return None
    return None


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true",
                    help="print the picked metrics as JSON instead of text")
    args = ap.parse_args()

    run = latest_run(DESIGN_DIR)
    if run is None:
        sys.exit("no LibreLane run found under librelane/runs/ — run `make pnr` first")
    metrics, mpath = load_metrics(run)
    if metrics is None:
        sys.exit(f"no metrics.json found under {run}")

    area = num(pick(metrics, AREA_KEYS))
    die = num(pick(metrics, DIE_AREA_KEYS))
    cells = pick(metrics, CELLS_KEYS)
    slack = num(pick(metrics, SLACK_KEYS))
    hold = num(pick(metrics, HOLD_SLACK_KEYS))
    power = num(pick(metrics, POWER_KEYS))
    p_int = num(pick(metrics, POWER_INT_KEYS))
    p_sw = num(pick(metrics, POWER_SW_KEYS))
    p_leak = num(pick(metrics, POWER_LEAK_KEYS))
    period = num(clock_period(DESIGN_DIR))

    fmax = None
    if slack is not None and period is not None and (period - slack) > 0:
        fmax = 1000.0 / (period - slack)  # MHz

    if args.json:
        print(json.dumps({
            "run": os.path.relpath(run, ROOT),
            "cell_area_um2": area, "die_area_um2": die, "cells": cells,
            "setup_slack_ns": slack, "hold_slack_ns": hold,
            "clock_period_ns": period, "fmax_mhz": fmax,
            "power_w": power, "power_internal_w": p_int,
            "power_switching_w": p_sw, "power_leakage_w": p_leak,
        }, indent=2))
        return

    def line(label, val, unit="", scale=1.0, nd=3):
        s = "n/a" if val is None else f"{val * scale:.{nd}f}{unit}"
        print(f"  {label:<22} {s}")

    print(f"design: {metrics.get('design__name', 'example_Adder')}")
    print(f"run:    {os.path.relpath(run, ROOT)}\n")

    print("Area")
    line("standard-cell area", area, " um^2", nd=1)
    line("die area", die, " um^2", nd=1)
    line("cell count", num(cells), "", nd=0)

    print("\nTiming")
    line("clock period", period, " ns", nd=3)
    line("setup slack (WNS)", slack, " ns", nd=3)
    line("hold slack", hold, " ns", nd=3)
    line("fmax (approx)", fmax, " MHz", nd=1)

    print("\nPower")
    line("total", power, " mW", scale=1e3, nd=3)
    line("internal", p_int, " mW", scale=1e3, nd=3)
    line("switching", p_sw, " mW", scale=1e3, nd=3)
    line("leakage", p_leak, " mW", scale=1e3, nd=3)


if __name__ == "__main__":
    main()
