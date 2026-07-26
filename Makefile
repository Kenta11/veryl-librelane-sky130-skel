# Veryl -> SystemVerilog -> LibreLane flow.
#
#   make sv        transpile the Veryl sources to SystemVerilog (sv/)
#   make check     functional check of the RTL with Icarus Verilog
#   make flow      run the full LibreLane flow for every design
#   make compare   collect area/power/timing into a comparison table
#   make all       sv + flow + compare
#   make clean     remove generated SV and LibreLane runs
#
# Designs are auto-discovered from librelane/<name>/config.json, so adding a new
# design is just: drop a src/*.veryl module and a librelane/<name>/config.json.

VERYL     ?= veryl
LIBRELANE ?= librelane          # or: nix run github:librelane/librelane --
PYTHON    ?= python3
IVERILOG  ?= iverilog

# every librelane/<name>/config.json -> <name>
DESIGNS  := $(notdir $(patsubst %/,%,$(dir $(wildcard librelane/*/config.json))))
SV_FILES := $(wildcard sv/*.sv)
TB       := $(wildcard tb/*.sv)

.PHONY: all sv check flow compare clean list $(addprefix flow-,$(DESIGNS))

all: sv flow compare

sv:
	$(VERYL) build

# Functional check. Requires a testbench under tb/ (tb/tb_check.sv by default).
check: sv
	@mkdir -p build
	$(IVERILOG) -g2012 -o build/tb.vvp $(TB) sv/*.sv
	vvp build/tb.vvp

flow: $(addprefix flow-,$(DESIGNS))

flow-%:
	$(VERYL) build
	$(LIBRELANE) librelane/$*/config.json

compare:
	$(PYTHON) scripts/compare.py --csv results.csv

list:
	@echo "designs: $(DESIGNS)"

clean:
	rm -rf sv build results.csv librelane/*/runs .build dependencies Veryl.lock *.f
