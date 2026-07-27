# veryl-librelane-sky130-skel

A [git-skel](https://github.com/dalance/git-skel) skeleton for taking a
[Veryl](https://veryl-lang.org/) design through the
[LibreLane](https://github.com/librelane/librelane) flow (sky130) — synthesis,
place & route — and reading its **area / power / timing**.

It ships the flow plumbing you don't want to rewrite per project — a `Makefile`,
a metrics reporter (`scripts/report.py`), a LibreLane config with sensible
defaults, and a Veryl CI workflow — plus a tiny example design (a registered
32-bit adder) with a `tb/` testbench that runs on Veryl's built-in native
simulator (no external HDL simulator required).

One skeleton = one design. To compare multiple designs, start a separate project
from this skeleton for each and compare their reports.

## Use it

```bash
# in a new or existing project
git skel init https://github.com/<owner>/veryl-librelane-sky130-skel
make           # area / power / timing (place & routes first if needed)
```

Day to day that's the one command you need: `make` reads the numbers, running
place & route the first time. After changing the RTL, run `make pnr` to refresh
the layout, then `make` again. Other targets:

```bash
make synth     # quick area/critical-path/power estimate (`veryl synth`, no PDK)
make check     # functional check via `veryl test` (native simulator)
make pnr       # (re)run synthesis + place & route with LibreLane (needs sky130)
```

`make synth` is a fast, self-contained estimate straight from Veryl — no PDK or
LibreLane needed — handy while iterating. `make` / `make pnr` give the accurate
post-layout numbers.

Replace `src/` with your design, point `DESIGN_NAME` in `librelane/config.json`
at your top module, and re-run. Pull later skeleton improvements with
`git skel update`.

## What's inside

| Path | Role | Kind |
|------|------|------|
| `Makefile` | `report` (default) / `pnr` / `synth` / `check` / `sv` | infra |
| `scripts/report.py` | reads the run's `metrics.json` → area/power/timing summary | infra |
| `.github/workflows/veryl.yml` | `veryl fmt --check` / `check` / `test` / `build` | infra |
| `docs/FLOW.md` | end-user flow guide (propagates to projects) | infra |
| `Veryl.toml` | project config — **rename & `.gitskelignore` in your project** | seed |
| `src/*.veryl` | your design (one top module, may span several files) | seed |
| `tb/*.veryl` | testbenches (`#[test]` modules, native simulator) | seed |
| `librelane/config.json` | LibreLane / sky130 config for the design | seed |

**infra** = maintained by the skeleton, safe to receive on `git skel update`.
**seed** = starting content you own after `init`; add to your project's
`.gitskelignore` so updates don't overwrite your work.

See [`docs/FLOW.md`](docs/FLOW.md) for the full workflow.

## License

Licensed under either of

 * Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
 * MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.

### Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in the work by you, as defined in the Apache-2.0 license, shall be
dual licensed as above, without any additional terms or conditions.
