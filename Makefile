# Veryl -> SystemVerilog -> LibreLane (place & route) -> area/power/timing.
#
#   make           show area/power/timing (runs place & route first if needed)
#   make report    print area / power / timing from the latest run
#   make pnr       (re)run the full LibreLane flow (synthesis .. place & route)
#   make synth     quick area/critical-path/power estimate (veryl synth, no PDK)
#   make check     functional check of the design (veryl test, native simulator)
#   make sv        transpile the Veryl sources to SystemVerilog (target/)
#   make clean     remove generated SystemVerilog and LibreLane runs
#
# Day to day you just run `make`: it place-and-routes the design the first time,
# then prints the numbers. After changing the RTL, run `make pnr` to refresh the
# layout, then `make` (or `make report`) to see the new numbers.

VERYL     ?= veryl
# LibreLane launcher. Override for e.g. Nix: LIBRELANE="nix run github:librelane/librelane --"
LIBRELANE ?= librelane
PYTHON    ?= python3

.DEFAULT_GOAL := report

.PHONY: check synth sv pnr report clean

# Functional check via Veryl's built-in native simulator (no external HDL
# simulator required). Testbenches are the `#[test(...)]` modules under tb/.
check:
	$(VERYL) test

# Fast, self-contained estimate straight from Veryl: gate-level area, critical
# path and power, with no PDK or LibreLane. Great for quick iteration before the
# full (slower, accurate) place & route.
synth:
	$(VERYL) synth

sv:
	$(VERYL) build

# Place & route the design with LibreLane (sky130). Edit librelane/config.json
# to point DESIGN_NAME at your top module and to tune CLOCK_PERIOD etc.
pnr: sv
	$(LIBRELANE) librelane/config.json

# Print area / power / timing of the latest LibreLane run. If nothing has been
# placed & routed yet, run the flow once first. (After an RTL change, run
# `make pnr` to refresh the layout before reading the numbers again.)
report:
	@if [ -z "$(wildcard librelane/runs/*)" ]; then $(MAKE) pnr; fi
	$(PYTHON) scripts/report.py

clean:
	rm -rf target librelane/runs .build dependencies Veryl.lock *.f
