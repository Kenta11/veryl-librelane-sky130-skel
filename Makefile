# Veryl -> SystemVerilog -> LibreLane (place & route) -> area/power/timing.
#
#   make check     functional check of the design (veryl test, native simulator)
#   make sv        transpile the Veryl sources to SystemVerilog (sv/)
#   make pnr       run the full LibreLane flow (synthesis .. place & route)
#   make report    print area / power / timing from the latest run
#   make all       pnr + report
#   make clean     remove generated SV and LibreLane runs

VERYL     ?= veryl
LIBRELANE ?= librelane          # or: nix run github:librelane/librelane --
PYTHON    ?= python3

.PHONY: all check sv pnr report clean

all: pnr report

# Functional check via Veryl's built-in native simulator (no external HDL
# simulator required). Testbenches are the `#[test(...)]` modules under tb/.
check:
	$(VERYL) test

sv:
	$(VERYL) build

# Place & route the design with LibreLane (sky130). Edit librelane/config.json
# to point DESIGN_NAME at your top module and to tune CLOCK_PERIOD etc.
pnr: sv
	$(LIBRELANE) librelane/config.json

# Print area / power / timing of the latest LibreLane run.
report:
	$(PYTHON) scripts/report.py

clean:
	rm -rf sv build librelane/runs .build dependencies Veryl.lock *.f
