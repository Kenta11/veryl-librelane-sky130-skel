# veryl-librelane-sky130-skel

A [git-skel](https://github.com/dalance/git-skel) skeleton for taking
[Veryl](https://veryl-lang.org/) RTL through the
[LibreLane](https://github.com/librelane/librelane) ASIC flow (sky130) and
comparing **area / power / timing** across designs.

It ships the flow plumbing you don't want to rewrite per project — a
design-auto-discovering `Makefile`, a metrics collector (`scripts/compare.py`),
LibreLane config defaults, and a Veryl CI workflow — plus a small worked example:
four 32-bit adders (ripple / carry-select / Kogge-Stone / behavioral) with
embedded `#[test]` benches that check each against a golden model using Veryl's
built-in native simulator (no external HDL simulator required).

## Use it

```bash
# in a new or existing project
git skel init https://github.com/<owner>/veryl-librelane-sky130-skel
make check     # functional check via `veryl test` (native simulator)
make flow      # run LibreLane on every design (needs LibreLane + sky130)
make compare   # area/power/timing table
```

Pull later skeleton improvements with `git skel update`.

## What's inside

| Path | Role | Kind |
|------|------|------|
| `Makefile` | `sv` / `check` / `flow` / `compare`, auto-discovers designs | infra |
| `scripts/compare.py` | reads each run's `metrics.json` → comparison table | infra |
| `.github/workflows/veryl.yml` | `veryl fmt --check` / `check` / `test` / `build` | infra |
| `docs/FLOW.md` | end-user flow guide (propagates to projects) | infra |
| `Veryl.toml` | project config — **rename & `.gitskelignore` in your project** | seed |
| `src/*.veryl` | example adders + embedded `#[test]` benches — replace with your RTL | seed |
| `librelane/<design>/config.json` | per-design sky130 config | seed |

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
