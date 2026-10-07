# XEM8320 combined hardening: review validation

## Current draft PR and dependency status (2026-09-16)

This section supersedes the dependency and PR-status conclusions in the
historical campaign report below. Review is now coordinated through
[LiteDRAM #406](https://github.com/enjoy-digital/litedram/pull/406),
[LiteX #2618](https://github.com/enjoy-digital/litex/pull/2618), and
[LiteX-Boards #828](https://github.com/litex-hub/litex-boards/pull/828). All
three PRs remain drafts, and fresh final-source hardware acceptance is still in
progress.

The current host-test baseline uses clean official Migen
`4c2ae8dfeea37f235b52acb8166f12acaaae4f7c` without a local simulator patch,
with LiteDRAM `b0abe76892190d9c3f9cfec043fa847265e59109`, LiteX
`71834f37f8c35c18c73f9479c5a89f971fd66113`, and LiteX-Boards
`72d44f58153be7fc073db5ff59240f6191c2b58a`. The targeted LiteX
firmware/guard/retry/Wishbone-cache suite passed 151 tests plus 10 subtests.
A broader LiteDRAM discovery attempted 505 tests and recorded one failure, six
errors, and six skips in an environment missing additional CI dependencies.
Isolated reruns passed the ULX3S and both LPDDR4 cases, then exposed a real
LPDDR5 simulation compatibility regression in the new write-leveling failure
handling. A correction preserves the existing behavior for other PHYs while
retaining fail-closed handling for UltraScale component PHYs; actual LPDDR5
reruns are ongoing. The original discovery run is not reported as a pass.

The failed converted2667 transfer and narrow paired2667 window documented below
remain retained historical evidence. Later controlled EQ_LEVEL3 results and
passing retests do not erase those failures, and the historical campaigns do
not qualify the amended final sources.

## Historical combined-hardening campaign

This campaign combines the Windows hardening and Linux timing improvements.
Source commits were pushed to `local/usnative-pr-hardening` on the AEW2015
LiteDRAM, LiteX and litex-boards forks, then fetched into fresh Linux checkouts.
No PR had been opened at the time of this campaign. These results do not replace
the earlier source-pinned matrix or the current draft-PR status above.

**There are unresolved hardware failures.** Converted2667 showed intermittent
counter-pattern corruption; a fresh paired2667 build with optional DMA
calibration failed a later guard search. Passing retests do not qualify those
configurations. The 2933/3200 profiles remain explicit overclocks with negative
pulse-width slack, even when setup/hold and hardware tests pass.

## Full campaign results

Calibration and DMA columns show pass/fail counts. A campaign is FAIL if any
required step failed, even after earlier full-memory tests passed. Memory counts
combine BIOS 2 MiB tests and explicit 32 MiB CPU tests. BISC-only checks are not
counted as DDR calibration. Short names retain the artifact profile identities;
`2667` means 2666.667 MT/s and `2933` means 2933.333 MT/s.

| Round / profile | Campaign | Calibration | Memory passes | DMA | Setup / hold / pulse (ns) |
|---|---|---:|---:|---:|---|
| r1 / native2400_normal | PASS | 4 / 0 | 5 | 0 / 0 | +0.310 / +0.012 / +0.039 |
| r1 / native2400_paired256_quiet_cal | PASS | 4 / 0 | 6 | 9 / 0 | +0.157 / +0.012 / +0.039 |
| r1 / native2667_converted256_debug | FAIL | 1 / 0 | 2 | 2 / 1 | +0.105 / +0.010 / +0.000 |
| r1 / native2667_normal | PASS | 4 / 0 | 5 | 0 / 0 | +0.043 / +0.011 / +0.000 |
| r1 / native2667_paired256_debug | PASS | 6 / 0 | 8 | 11 / 0 | +0.038 / +0.015 / +0.000 |
| r1 / native2667_paired256_debug_cal | PASS | 5 / 0 | 7 | 10 / 0 | +0.014 / +0.015 / +0.000 |
| r1 / native2933_standard128 | PASS | 4 / 0 | 6 | 9 / 0 | +0.065 / +0.014 / -0.034 |
| r2 / native2933_standard128 | PASS | 4 / 0 | 6 | 9 / 0 | +0.065 / +0.019 / -0.034 |
| r2 / native3200_converted256_debug | FAIL | 1 / 1 | 3 | 9 / 0 | +0.039 / +0.010 / -0.167 |
| r2 / native3200_converted256_quiet | PASS | 4 / 0 | 6 | 9 / 0 | +0.114 / +0.014 / -0.167 |
| r4 / native2667_paired256_debug_cal | FAIL | 1 / 1 | 3 | 9 / 0 | +0.006 / +0.010 / +0.000 |
| r5 / native3200_converted256_debug_alt_retry001 | PASS | 11 / 0 | 13 | 10 / 0 | +0.000 / +0.005 / -0.167 |
| r5 / native3200_converted256_quiet | PASS | 10 / 0 | 12 | 9 / 0 | +0.018 / +0.011 / -0.167 |

## Measured full 1 GiB PRBS31 throughput

GB/s is decimal. CPU values are the observed MiB/s range. DMA phases are
sequential write/read, not simultaneous traffic. Throughput measured before a
later failure is retained and does not change that campaign's FAIL status.

| Round / profile | CPU write / read (MiB/s) | DMA write / read (GB/s) | Write / read peak |
|---|---|---:|---:|
| r1 / native2400_normal | 44.7–44.9 / 48.8–48.8 | not run / no DMA | — |
| r1 / native2400_paired256_quiet_cal | 48.6–48.8 / 52.7–52.7 | 4.281 / 4.315 | 89.19% / 89.89% |
| r1 / native2667_converted256_debug | 49.2–49.2 / 54.6–54.6 | not run / no DMA | — |
| r1 / native2667_normal | 49.2–49.2 / 54.6–54.6 | not run / no DMA | — |
| r1 / native2667_paired256_debug | 48.6–48.8 / 52.7–52.7 | 4.734 / 4.760 | 88.76% / 89.25% |
| r1 / native2667_paired256_debug_cal | 48.6–48.6 / 52.7–52.7 | 4.734 / 4.760 | 88.76% / 89.25% |
| r1 / native2933_standard128 | 54.4–54.5 / 60.5–60.5 | 2.638 / 2.660 | 44.96% / 45.33% |
| r2 / native2933_standard128 | 55.3–55.3 / 62.4–62.4 | 2.638 / 2.660 | 44.96% / 45.33% |
| r2 / native3200_converted256_debug | 56.4–56.4 / 64.4–64.4 | 2.862 / 2.884 | 44.71% / 45.05% |
| r2 / native3200_converted256_quiet | 58.7–59.1 / 66.3–66.4 | 2.862 / 2.884 | 44.71% / 45.05% |
| r4 / native2667_paired256_debug_cal | 48.6–48.6 / 52.7–52.7 | 4.717 / 4.760 | 88.44% / 89.25% |
| r5 / native3200_converted256_debug_alt_retry001 | 56.4–56.6 / 64.4–64.4 | 2.862 / 2.884 | 44.71% / 45.05% |
| r5 / native3200_converted256_quiet | 62.2–62.5 / 68.3–68.3 | 2.862 / 2.884 | 44.71% / 45.05% |

Raw x16 peak is MT/s × 2 MB/s: 2400 = 4.800 GB/s, 2666.667 = 5.333 GB/s,
2933.333 = 5.867 GB/s, and 3200 = 6.400 GB/s. A 256-bit width converter does not
increase controller issue throughput. Paired bank-group scheduling explains the
higher utilization of paired256 in these tests.

## Failures and bounded recovery

- R1 converted2667: two full-memory counter errors, engine fault count zero,
  first error offset 0x300. Reprogramming the same image passed 20 subsequent
  DMA checks. Root cause remains unresolved; retain the failing evidence.
- R4 paired2667 with optional DMA refinement: initial calibration, full-memory
  DMA and sequential CPU/DMA interoperability passed. The first reinitialization
  failed error 18: bit 11's measured DMA RX window was 22..34 taps; satisfying
  the -4-tap guard exhausted the measured window. Do not weaken that guard.
- R2 debug3200: initial tests passed, then TX error 8 on reinitialization.
  Diagnostic firmware identified lane 0's 28-tap common TX window, below the
  unchanged 32-tap minimum. R3 passed 12/13 starts; R4 two-neighbor recovery
  passed 24/25. A real RX48-to-RX52 recovery was observed, but RX44 needed a
  wider bounded candidate search.
- R5 permits RX offsets +4, +8, -4 and -8 only inside the measured RX window
  with margin. Acceptance requires two overlapping TX scans, at least 32 taps
  of intersection and center confirmation, followed by every normal deskew,
  guard and final memory check. The R5 diagnostic derivative passed 25 starts
  and 25 subsequent 64 MiB DMA checks; no retry was needed in those starts.
  This diagnostic is a verified BIOS ROM update of the R2 route, not fresh PAR.
  The final alternate debug campaign also exercised a real RX48-to-RX52 retry:
  two TX scans agreed on 56..88 taps, then all remaining calibration, memory
  and DMA checks passed.
- R1 debug/quiet3200 setup was -0.031/-0.005 ns and neither was programmed.
  Registered refresh timers closed those fabric paths in R2. R5 original debug
  setup was -0.093 ns and was not programmed. The alternate R5 placement reached
  0.000 ns reported setup with no failing endpoints, and +0.005 ns hold; this is
  effectively no setup margin. Its first programming attempt used a host-only
  symlink and loaded no test image; the corrected-path retry uses identical bits.

## Source and artifact identities

| Round | LiteDRAM | LiteX | litex-boards |
|---|---|---|---|
| r1 | `b57d03d1fb001b3305b033443579320339e92c8b` | `d57806879c1e9acc02c5a4788a534371c59683c5` | `c8d8ffd0ecd0cb357640eee8d3cfcc1f406f87b4` |
| r2 | `9a3ec8960cdb83936ad322f111d252934bba4fe7` | `d57806879c1e9acc02c5a4788a534371c59683c5` | `5116f01df5d338960c459d83a0a0c7a13d1ab1bd` |
| r4 | `9a3ec8960cdb83936ad322f111d252934bba4fe7` | `0ab6dee9e1969c5c72c4e5b8768d979f0c15f766` | `5116f01df5d338960c459d83a0a0c7a13d1ab1bd` |
| r5 | `9a3ec8960cdb83936ad322f111d252934bba4fe7` | `263d96bed561fa45d3d1d8d500df9f55418c4e1b` | `5116f01df5d338960c459d83a0a0c7a13d1ab1bd` |

Final R5 bitstream SHA256 identities (debug retry uses the alternate-placement image):

- `native3200_converted256_debug_alt_retry001`: `eb1a6af9d16af1a61708c33dfbe8224aea0bb3274e4bec4c7639417fc3a5b6ae`.
- `native3200_converted256_quiet`: `26d6bf6c2ccdd6bd829d506f80b408a8da2746b06960aa12f64c00c287d01c52`.

## Reproduction and limits

Vivado 2026.1, Python 3.12.3, GCC RISC-V 13.2.0, container image
`sha256:9886de736147deb9bb3878c92b7ea7d3028afa1fb3a86fc967d1f84284460f99`.
Fresh public-CLI builds use Explore placement/routing and AggressiveExplore
post-place/post-route optimization. Later rounds use two Vivado threads per
build; R1 used four. R5 alternate debug uses ExtraNetDelay_high placement from
the same freshly synthesized R5 checkpoint, followed by the same routing and
physical optimization directives. No clock constraints were relaxed to pass
setup/hold. The 3200 PLL VCO warning and -0.167 ns pulse violation remain;
2933 retains -0.034 ns pulse slack.

Example generation/build command, after installing the coordinated fork pins:

```sh
python -m litex_boards.targets.opalkelly_xem8320 \
    --toolchain vivado --with-usnative --ddr-rate 3200 --overclock \
    --with-dma --dma-data-width 256 --usnative-debug \
    --build --no-build-log --no-integrated-rom-auto-size \
    --vivado-max-threads 2 --vivado-place-directive ExtraNetDelay_high \
    --vivado-post-place-phys-opt-directive AggressiveExplore \
    --vivado-route-directive Explore \
    --vivado-post-route-phys-opt-directive AggressiveExplore \
    --vivado-report-level signoff --output-dir build/xem8320-3200-debug
```

This command requests the strategy; it does not guarantee an identical bitstream
or timing result. Exact commands, reports, BIOS/bitstream hashes and transcripts
are retained in the geto AMD workspace under
`experiments/combined-hardening[-r2|-r3|-r4|-r5]-20260916/`, with each directory's
`source_manifest.json`, `logs/` and `hardware/`. R1 has no `-r1` suffix.
Generated artifacts and device query caches are not committed to the forks.

The historical Linux affected suites passed 11 LiteDRAM tests plus 49 subtests,
149 LiteX tests plus 10 subtests, and 14 board tests plus 25 subtests. The initial
broader Linux run passed 157 tests plus 91 subtests with one skip. Windows cache,
firmware and board tests passed, but extended Windows simulations using the
older dependency snapshot hit 34 Migen MemoryToArray compatibility errors. R2's
separate `dependency-migen.patch` is retained with SHA256
`ddec554339f86a726fe1be773f807dc0835a1409be514cd312dba664e0998ed2`; it was not
a change in these three forks and is not required by the clean official-Migen
baseline described at the top of this document. Do not describe that historical
Windows simulation run as PASS.

Hardware coverage is one board at ambient conditions. Full campaigns include
initial calibration, BIOS/CPU memory tests, 64 MiB and full 1 GiB counter/PRBS31
DMA, read-only recheck, sequential CPU/DMA interoperability, two full retries
and reboot. Debug adds explicit BISC, denied DMA and full-training recovery.
Final R5 campaigns add six more full reinitializations. There were no physical
power cycles, thermal/voltage qualification or extended soak. Only volatile
programming was used; each case restores the earlier paired2667 image and checks
its BIOS memory test. Flash was not written.

At the end of this historical campaign, next work was to reproduce converted2667
corruption with exact failing DQ/data, improve optional DMA refinement using
repeated windows without reducing guard margins, test recovery across fresh
placements, audit ZQCS cadence independently of timer equivalence, and resolve
the Migen dependency for clean environments. The current status section records
the later clean-Migen resolution; the other retained failures and final-source
acceptance remain tracked by the draft PRs. Cold-start and thermal work remain
deferred. A review branch is not a reliability claim.
