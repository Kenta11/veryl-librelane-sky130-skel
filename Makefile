# Veryl -> SystemVerilog -> LibreLane flow.
#
#   make check     functional check of the RTL (veryl test, native simulator)
#   make sv        transpile the Veryl sources to SystemVerilog (sv/)
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

# every librelane/<name>/config.json -> <name>
DESIGNS := $(notdir $(patsubst %/,%,$(dir $(wildcard librelane/*/config.json))))

.PHONY: all check sv flow compare clean list $(addprefix flow-,$(DESIGNS))

all: sv flow compare

# Functional check via Veryl's built-in native simulator (no external HDL
# simulator required). Tests are the `#[test(...)]` modules in src/*.veryl.
check:
	$(VERYL) test

sv:
	$(VERYL) build

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
