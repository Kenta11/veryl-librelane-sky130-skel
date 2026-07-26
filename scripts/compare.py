#!/usr/bin/env python3
"""Collect area / power / timing metrics from LibreLane runs and print a
comparison table.

For each design under ``librelane/<name>/`` it locates the most recent run
(``runs/<tag>/``), reads that run's ``metrics.json`` (the aggregated metrics
LibreLane writes at the end of the flow), and extracts a handful of headline
numbers. Metric key names have drifted across LibreLane/OpenLane versions, so
each column tries a list of candidate keys and uses the first one present.

Usage:
    python3 scripts/compare.py                 # table for every design found
    python3 scripts/compare.py --csv out.csv   # also write a CSV
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIBRELANE_DIR = os.path.join(ROOT, "librelane")

# Candidate metric keys, most-preferred first. LibreLane and OpenLane 2 have
# used slightly different names over time; we probe each in order.
AREA_KEYS = [
    "design__instance__area",
    "design__core__area",
    "design__die__area",
]
DIE_AREA_KEYS = ["design__die__area", "design__die__area__um2"]
CELLS_KEYS = [
    "design__instance__count",
    "design__instance_count__setup",
    "design__instance__count__stdcell",
]
SLACK_KEYS = [
    "timing__setup__ws",
    "timing__setup__wns",
    "timing__setup__ws__corner:nom_tt_025C_1v80",
]
POWER_KEYS = [
    "power__total",
    "power__internal__total",
]


def pick(metrics: dict, keys):
    """Return (value, key) for the first present key, else (None, None)."""
    for k in keys:
        if k in metrics and metrics[k] is not None:
            return metrics[k], k
    # some versions suffix keys with a corner; match by prefix as a fallback
    for k in keys:
        for mk, mv in metrics.items():
            if mk.startswith(k) and mv is not None:
                return mv, mk
    return None, None


def latest_run(design_dir: str):
    runs = sorted(glob.glob(os.path.join(design_dir, "runs", "*")))
    runs = [r for r in runs if os.path.isdir(r)]
    return runs[-1] if runs else None


def load_metrics(run_dir: str):
    # LibreLane writes an aggregated metrics.json at the run root and/or under
    # a final/ step directory. Prefer the deepest/most complete one.
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


def fmt(v, unit="", scale=1.0, nd=3):
    if v is None:
        return "n/a"
    try:
        return f"{float(v) * scale:.{nd}f}{unit}"
    except (TypeError, ValueError):
        return str(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="also write results to this CSV file")
    args = ap.parse_args()

    if not os.path.isdir(LIBRELANE_DIR):
        sys.exit(f"no librelane/ directory at {LIBRELANE_DIR}")

    designs = sorted(
        d for d in os.listdir(LIBRELANE_DIR)
        if os.path.isdir(os.path.join(LIBRELANE_DIR, d))
    )

    rows = []
    for name in designs:
        design_dir = os.path.join(LIBRELANE_DIR, name)
        run = latest_run(design_dir)
        if run is None:
            rows.append({"design": name, "status": "no run"})
            continue
        metrics, mpath = load_metrics(run)
        if metrics is None:
            rows.append({"design": name, "status": "no metrics.json"})
            continue

        area, _ = pick(metrics, AREA_KEYS)
        cells, _ = pick(metrics, CELLS_KEYS)
        slack, _ = pick(metrics, SLACK_KEYS)
        power, _ = pick(metrics, POWER_KEYS)
        period = clock_period(design_dir)

        fmax = None
        if slack is not None and period is not None:
            try:
                min_period = float(period) - float(slack)  # ns
                if min_period > 0:
                    fmax = 1000.0 / min_period  # MHz
            except (TypeError, ValueError):
                pass

        rows.append({
            "design": name,
            "status": "ok",
            "cells": cells,
            "area_um2": area,
            "slack_ns": slack,
            "period_ns": period,
            "fmax_mhz": fmax,
            "power_w": power,
        })

    # markdown table
    hdr = ["design", "cells", "area (um^2)", "setup slack (ns)",
           "fmax (MHz)", "power (mW)"]
    print("| " + " | ".join(hdr) + " |")
    print("|" + "|".join("---" for _ in hdr) + "|")
    for r in rows:
        if r.get("status") != "ok":
            print(f"| {r['design']} | _{r.get('status')}_ |  |  |  |  |")
            continue
        print("| {d} | {c} | {a} | {s} | {f} | {p} |".format(
            d=r["design"],
            c=fmt(r["cells"], nd=0),
            a=fmt(r["area_um2"], nd=1),
            s=fmt(r["slack_ns"], nd=3),
            f=fmt(r["fmax_mhz"], nd=1),
            p=fmt(r["power_w"], scale=1e3, nd=3),  # W -> mW
        ))

    if args.csv:
        keys = ["design", "status", "cells", "area_um2", "slack_ns",
                "period_ns", "fmax_mhz", "power_w"]
        with open(args.csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k) for k in keys})
        print(f"\nwrote {args.csv}", file=sys.stderr)


if __name__ == "__main__":
    main()
