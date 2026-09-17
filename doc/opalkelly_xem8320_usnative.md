# XEM8320 DDR4 profiles

For the combined Windows/Linux review branches, see the
[source-pinned validation results](opalkelly_xem8320_usnative_validation.md).
They include successful 3200 functional tests, remaining primitive timing
violations, and unresolved converted/optional-calibration 2667 failures.

The default target uses component-mode `USPDDRPHY` (ISERDESE3/OSERDESE3).
`--ddr-rate 1000` selects its 125 MHz system clock. `--ddr-rate 2000
--overclock` selects 250 MHz with a phase-related 1 GHz serializer clock and
an independent 500 MHz IDELAYCTRL reference. DDR4-2000 is buildable for
laboratory testing, but its known 1.600 ns ISERDESE3 minimum-period requirement
against a 1.000 ns clock produces a -0.600 ns pulse-width violation; no timing
or DRC check is waived. The 1000 MT/s component profile is the baseline
timing-qualified configuration.

```sh
python -m litex_boards.targets.opalkelly_xem8320 --toolchain vivado --ddr-rate 1000 --with-dma --dma-data-width 128 --build
python -m litex_boards.targets.opalkelly_xem8320 --toolchain vivado --ddr-rate 1000 --sdram-debug --with-dma --dma-data-width 256 --with-dma-bank-group-interleaving --build
python -m litex_boards.targets.opalkelly_xem8320 --toolchain vivado --ddr-rate 2000 --overclock --sdram-debug --with-dma --dma-data-width 256 --with-dma-bank-group-interleaving --build
```

Component DMA admission starts disabled. BIOS enables it only after calibration
and the mandatory final memory test pass; failed or repeated initialization
revokes admission. `--sdram-debug` enables component command-delay and
write-latency calibration detail. It does not report HSSIO eye windows.
The component target selects IDELAYCTRL's simulation-device spelling from the
`vivado` executable on `PATH`, which is also the implementation executable:
Vivado 2026.1 and later use `ULTRASCALE_PLUS`; older or unavailable tools use
the portable `ULTRASCALE` spelling.

# Experimental XEM8320 native DDR4

Requires coordinated experimental LiteDRAM and LiteX BIOS branches. The default
XEM8320 target continues to use USPDDRPHY. Select `--with-usnative` explicitly;
this path requires `--toolchain vivado` and queries that installation's device
connections for every build. Set the Vivado executable in PATH, or pass
`--vivado /path/to/vivado` for the query runner (implementation still uses PATH).
Generated Tcl, maps, logs and RTL stay under the build output directory.
The XEM8320 path has been exercised with Vivado 2026.1. A successful query or
implementation does not qualify a different Vivado release or board revision.
The 2933.333 and 3200 MT/s options are deliberately buildable for laboratory
hardware experiments, even if timing does not close. They are not signoff
profiles: retain and review the timing reports separately from a calibration or
memory-test pass. These rates retain the actual constraints rather than waiving
them, including the 0.375 ns `PLL_CLK0` requirement and the 2.667 ns TX-control
requirement at 3200 MT/s. At 3200 only, `--overclock` also downgrades Vivado's
known `PDRC-182` 1600 MHz PLLE4-VCO versus 1500 MHz limit to a warning so an
experimental bitstream can be generated. It does not waive any other DRC or
timing check; 2933.333 does not receive this downgrade.


The 2666.667, 2933.333 and 3200 targets select `EQ_LEVEL3` for DQ receivers; DQS remains
at `EQ_LEVEL2`. The 3200 profile additionally uses the matching LiteX firmware
change selecting operating RD2/WR3 and bootstrap TX/RX delays 72/48. Its
generated reset read phase remains 3. The 2400 profile keeps its existing
receiver settings. All normal calibration margin and memory-integrity
checks remain required; this does not waive static timing.


```sh
python -m litex_boards.targets.opalkelly_xem8320 --toolchain vivado --with-usnative --ddr-rate 2400 --build
python -m litex_boards.targets.opalkelly_xem8320 --toolchain vivado --with-usnative --ddr-rate 2666.667 --usnative-debug --with-dma --dma-data-width 256 --build
python -m litex_boards.targets.opalkelly_xem8320 --toolchain vivado --with-usnative --ddr-rate 2666.667 --usnative-debug --with-dma --dma-data-width 256 --with-dma-bank-group-interleaving --build
python -m litex_boards.targets.opalkelly_xem8320 --toolchain vivado --with-usnative --ddr-rate 2666.667 --with-dma --dma-data-width 256 --with-dma-bank-group-interleaving --usnative-dma-calibration --build
python -m litex_boards.targets.opalkelly_xem8320 --toolchain vivado --with-usnative --ddr-rate 2933.333 --overclock --with-dma --build
python -m litex_boards.targets.opalkelly_xem8320 --toolchain vivado --with-usnative --ddr-rate 3200 --overclock --usnative-debug --with-dma --dma-data-width 256 --build
```

| Option | Behavior |
|---|---|
| `--with-usnative` | Native PHY and normal BIOS calibration; defaults to 2400 MT/s. |
| `--usnative-debug` | Verbose calibration windows and optional trace hardware. |
| `--usnative-dma-calibration` | Explicit request for traffic-aware calibration, automatically enabled for native converted/paired 256-bit DMA builds; independent of debug. |
| `--sdram-debug` | Component-PHY calibration diagnostics; invalid with `--with-usnative`. |
| `--with-dma` | Performance-test DMA engine and `native_dma` BIOS command. Native 256-bit builds automatically calibrate using DMA traffic at startup; benchmark runs remain explicit commands. |
| `--dma-data-width 128\|256` | Fabric DMA port width; default 128. Requires DMA when selecting 256. |
| `--with-dma-bank-group-interleaving` | Experimental paired 256-bit DMA path. Requires DMA and `--dma-data-width 256`; works with either PHY. |
| `--ddr-rate` | Component: 1000 or 2000 MT/s. Native: 2400, 2666.667, 2933.333, or 3200 MT/s. |
| `--overclock` | Required for component 2000 and native 2933.333/3200; does not waive timing checks. |

### Clean experimental build dependencies

The USNative target requires coordinated changes in all three projects:
LiteX-Boards supplies the target and flags, LiteDRAM supplies the native PHY and
paired controller path, and LiteX supplies the BIOS calibration routine. The
rolling review branches and their public PRs are:

| Project | Rolling fork branch | Public review |
|---|---|---|
| LiteDRAM | `AEW2015/litedram:pr/usnative-ddr4` | [enjoy-digital/litedram#406](https://github.com/enjoy-digital/litedram/pull/406) |
| LiteX | `AEW2015/litex:pr/usnative-ddr4` | [enjoy-digital/litex#2618](https://github.com/enjoy-digital/litex/pull/2618) |
| LiteX-Boards | `AEW2015/litex-boards:pr/usnative-ddr4` | [litex-hub/litex-boards#828](https://github.com/litex-hub/litex-boards/pull/828) |

Those branch names move during review. The immutable baseline used for the
current host-test claims was LiteDRAM
`b0abe76892190d9c3f9cfec043fa847265e59109`, LiteX
`71834f37f8c35c18c73f9479c5a89f971fd66113`, LiteX-Boards
`72d44f58153be7fc073db5ff59240f6191c2b58a`, and official Migen
`4c2ae8dfeea37f235b52acb8166f12acaaae4f7c`. This is a historical tested
baseline, not the identity of later documentation amendments or completed
final-source hardware acceptance. Record all four actual revisions for each
new build.

Clone the rolling branches and the official Migen dependency into sibling
directories:

```sh
git clone --branch pr/usnative-ddr4 https://github.com/AEW2015/litedram.git
git clone --branch pr/usnative-ddr4 https://github.com/AEW2015/litex.git
git clone --branch pr/usnative-ddr4 https://github.com/AEW2015/litex-boards.git
git clone https://git.m-labs.hk/M-Labs/migen.git
git -C migen checkout --detach 4c2ae8dfeea37f235b52acb8166f12acaaae4f7c
```

Create and activate a virtual environment (`python -m venv .venv`, then
`.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` in
Bash). From the checkouts' parent directory, install into that environment:

```sh
python -m pip install -e ./migen -e ./litex -e ./litedram -e ./litex-boards
git -C migen rev-parse HEAD
git -C litedram rev-parse HEAD
git -C litex rev-parse HEAD
git -C litex-boards rev-parse HEAD
```

The four editable Python installs do not provision the normal LiteX build
toolchain. Install the required VexRiscv CPU data/software packages, a compatible
RISC-V compiler, Make, and Vivado separately. Select Vivado on PATH and run a
build command above with a fresh `--output-dir`. Native device queries run for
each build; no saved connection map or workstation firmware override is needed.
`--usnative-dma-calibration` does not enable DMA, debug, or a wider port implicitly.
Fresh hardware qualification of this entry point and the updated paired-write
rejection logic is still required; software/RTL generation alone is insufficient.

The physical channel remains x16 and the PHY ratio remains 1:4. In the
USNative profiles, the CPU clock is half the controller clock (150 to 200 MHz).
In the component profiles, the CPU runs at the controller/system clock (125 or
250 MHz). The initial profile uses the standard VexRiscv CPU and JTAG UART;
video is not supported with the USNative clock tree.
The 256-bit mode uses the standard width converter, not the previous local
paired-port bank-group controller. Its bandwidth must be measured separately.
`--with-dma-bank-group-interleaving` is the distinct opt-in paired-port path:
it enables controller bank-group scheduling, maps paired commands to opposite
groups, and uses two 128-bit native ports to present one ordered 256-bit DMA
endpoint. It supplies drain and sticky-error gating to the benchmark. The CPU
and all other masters use the same opt-in controller mapping, so it must be
tested as a whole-system configuration rather than treated as a width-converter
optimization.

The earlier local paired-controller experiment reported 4.725 GB/s writes and
4.760 GB/s reads at 2666.667 MT/s. It is retained only as a historical
comparison: the portable paired path has its own measured 2666.667 MT/s result
below. That result does not apply to other rates or configurations without their
own integrity, timing, and hardware evidence.

BIOS runs calibration and its normal memory checks at startup. The user-facing
`native_dma` benchmark runs only when explicitly commanded. Native 256-bit DMA
builds also use the same engine internally for automatic startup refinement
before normal benchmark admission. `native_dma` defaults to a destructive 64 MiB
scratch test starting at 0x41000000. Flushes precede DMA, and CPU execution must
remain outside that range. A fatal DMA timeout requires reconfiguration.

Report calibration and memory-test results separately. Record CPU memspeed in
MiB/s and DMA write/read in decimal GB/s, with efficiency against the x16 raw
peak. Debug windows are sampled calibration pass ranges, with potentially
search-limited endpoints; they are not complete eye scans or thermal qualification.
No new configuration is hardware-qualified merely because generation succeeds.

The paired 2666.667 MT/s configuration was tested on one XEM8320 with Vivado
2026.1 on 2026-09-16. It passed three calibration/memory checks, five DMA tests
(including full 1 GiB PRBS write/read/reread), and CPU-induced first/last-word
corruption detection followed by repair/reread. Sustained full-range DMA was
4.734 GB/s write and 4.760 GB/s read (88.76% and 89.25% of physical peak).
Final setup/hold slack was +0.002/+0.007 ns, with zero failing endpoints,
zero routing errors and no clock-period/pulse-width violations. This result
does not qualify other rates or temperature/power-cycle behavior.

This paired result is historical evidence for that earlier configuration. A
later width-converted 2666.667 MT/s debug run showed an intermittent DMA
counter failure and remains unqualified. Do not combine that run with the
historical throughput or calibration evidence above.

## Component PHY validation

The standard `USPDDRPHY` (ISERDESE3/OSERDESE3) x16, four-phase component path
was hardware-tested with the DMA admission gate enabled only after normal BIOS
initialization. Each entry below passed three initialization/controller-memory
checks and five DMA checks, including a full 1 GiB PRBS write and reread.

| Profile | DDR rate | DMA port | DMA write / read | Write / read efficiency | Setup / hold / pulse slack |
|---|---:|---:|---:|---:|---:|
| Standard global `tCCD_L=8` | 1000 MT/s | 128-bit | 0.905 / 0.918 GB/s | 45.24% / 45.90% | +0.146 / +0.017 / +0.139 ns |
| Paired bank groups | 1000 MT/s | 256-bit | 1.797 / 1.815 GB/s | 89.85% / 90.77% | +0.093 / +0.010 / +0.127 ns |
| Paired bank groups | 2000 MT/s | 256-bit | 3.569 / 3.584 GB/s | 89.23% / 89.60% | +0.083 / +0.014 / -0.600 ns |

The 1000 and 2000 MT/s paired configurations also passed CPU/DMA
interoperability: three expected corruption detections and zero unexpected
failures in each case. The 2000 MT/s profile remains an explicit experimental
profile. Its fabric setup and hold checks are positive, but its -0.600 ns
ISERDESE3 pulse-width violation means it is not fully STA-qualified.

The original component-PHY RTL is unchanged. The BIOS restores DQS increment
accounting before PHY reset to make repeated initialization coherent. After full
placement and routing, a verified ROM-only update added the hardware-timer DMA
wait; placement, routing, clocks, and constraints were retained. This result
does not qualify other rates, temperature, or power-cycle behavior.


### Controller row-hit timing

Native profiles enable LiteDRAM's `with_registered_row_hit` controller option.
It precomputes the buffered request's row match, removing that comparison from
CAS arbitration and command-buffer ready paths without enabling paired
bank-group scheduling or changing the physical x16/four-phase interface.
This requires a LiteDRAM revision providing the independent controller option.
Component profiles retain their existing settings; paired scheduling still
uses its existing registered row-hit path.

This fabric optimization does not qualify overclocked primitives. Native
2933.333/3200 MT/s and component 2000 MT/s remain experimental profiles with
separate clock-period checks. A generated bitstream is not timing or hardware
qualification; retain setup, hold, pulse-width, and DRC reports.


## DMA admission and calibration retry

Both component and native DMA builds include software admission, cleared at
reset and before full initialization. BIOS grants normal DMA only after the
final controller-path memory test. This requires matching LiteX firmware with
`CONFIG_SDRAM_DMA_SOFTWARE_ADMISSION` support. Native PHY training state and
sticky DMA/paired-port faults remain independent hardware gates. Native 256-bit
DMA builds permit bounded internal DMA during calibration automatically;
`--usnative-dma-calibration` also requests this explicitly. This behavior does
not depend on `--usnative-debug`.

In debug builds, `sdram_bisc` explicitly runs internal delay calibration while
holding DDR reset. A BISC PASS is not a DDR pass. Ordinary `sdram_init` always
retries full training, even after a previous failure or BISC diagnostic.

## Recorded Linux results before combined hardening validation

These historical results belong to the pinned Linux sources, not automatically
to a later combination with Windows hardening. Vivado 2026.1 Explore results:

| Native profile | Setup / hold / pulse slack (ns) | Hardware result |
|---|---|---|
| 2400 normal | +0.309 / +0.011 / +0.039 | Calibration and CPU memory PASS; no DMA |
| 2667 converted256 | +0.056 / +0.012 / +0.000 | Calibration, CPU memory and full 1 GiB DMA PASS |
| 2667 paired256 | +0.020 / +0.011 / +0.000 | Calibration, CPU memory and full 1 GiB DMA PASS |
| 2933 standard128 | +0.063 / +0.017 / -0.034 | Hardware PASS; primitive clock timing FAIL |
| 3200 converted256, corrected bootstrap | +0.004 / +0.011 / -0.167 | Hardware PASS; primitive clock timing FAIL; PLL VCO warning |

The timing-source commits were LiteDRAM `c6421f1401b8603622801aa64e713d61e86406bb`,
LiteX `501b2be3807b9f6c629425b26e5f3dcb38b57662`, and litex-boards
`251283dc9a08f28bbd1f74c43db8992aa6e7d286`. The 3200 correction used LiteX
`f6210ac1f38fe7c860eefdebb4332192b2c1a274` and litex-boards
`fbca5d62adde1c1fad0a6fd4c9948be319fba72b`. Its two tested bitfiles were verified
ROM/equalization updates of the existing routed checkpoint, not fresh PAR:

- Debug SHA256: `24868c9502760473dd87c1f533c34b38c5139a4e727026538fcaf5815ee216d9`.
- BIOS-quiet SHA256: `a550f6e5c83647659fcb19037b0b94ebd0590256c7248756c045cd0735fd1d6e`.

Each corrected 3200 image passed four full calibrations, six memory tests and
five DMA checks, with zero DMA errors/faults. Full 1 GiB PRBS31 throughput was
2.862/2.884 GB/s write/read on converted256. BIOS-quiet retained trace-capable
FPGA logic. Component-1000 standard and paired passed the tested baselines;
component-2000 had failing clock timing and was not hardware tested.

These are one-board ambient results, software reboots rather than cold power
cycles, and sequential write/read traffic. Negative pulse slack is not waived
by a hardware pass. New combined revisions require fresh implementation and
hardware evidence; keep bitstreams/checkpoints outside source control.


For native 2933/3200, registered refresh/ZQCS timer comparisons are enabled
independently of paired scheduling. The registered countdown preserves each
cycle of the original timer, including reload. This removes the long terminal
count decode from refresh arbitration; it does not relax refresh intervals or
static clock checks. Lower-rate and component configurations keep their settings.

## DMA performance-test calibration

Native 256-bit DMA builds automatically run traffic-aware calibration before
normal benchmark admission. CPU-only and component-PHY builds retain their
existing startup paths. Training is destructive to scratch DDR, adds startup
time, and can fail rather than accept insufficient measured margins.

The DMA engine is a performance/integrity example. Applications reusing it must
calibrate with representative traffic, maintain exclusive buffer ownership, and
perform the appropriate CPU/cache synchronization when ownership changes. A BIOS
benchmark result does not provide a general cache-coherent DMA driver. Existing
CPU/DMA interoperability tests explicitly synchronize caches at each handoff.

### Native 2667 receiver equalization

The XEM8320 native 2666.667 MT/s profile uses DQ-only `EQ_LEVEL3`, independently
of DMA and debug options. The 2933.333 and 3200 profiles use the same setting;
2400 and component-PHY profiles retain their previous settings. DQS is
not changed, and the known 3200 PLL DRC waiver remains restricted to 3200.

This change follows a controlled receiver experiment using the same placed and
routed 2667 paired design and BIOS. Changing only the sixteen DQ ports from
`EQ_LEVEL2` to `EQ_LEVEL3`, while preserving the final 0.84 V bank reference,
produced 32-34-tap DQ11 windows in the initial five successful starts. The
completed ten-start controlled campaign had a minimum DQ11 window of 28 taps,
with no guard adjustments or rescans. The original setting had produced a
six-tap intersection that correctly failed the required +/-4-tap guards. Setup,
hold and pulse-width slack stayed at +0.022, +0.012 and +0.000 ns in the
controlled derivative.

These observations motivate this XEM8320 profile setting; they do not establish
an electrical root cause or qualify another board, temperature or voltage.
Fresh builds from the final source revisions still require separate hardware
validation. The measured guard requirements remain unchanged.

### Experimental 2933 receiver equalization

A 2933.333 MT/s paired256 debug image failed its initial traffic-aware
calibration with DQ equalization at level 2. The counter/PRBS intersection
spanned six taps on DQ11 and two taps on DQ14, below the required five samples
at two-tap spacing. DQ13 had only the minimum eight-tap span.

A controlled derivative changed only the sixteen DQ ports to `EQ_LEVEL3`.
Firmware and all INIT values, cell placement, routing, clocks, DQS settings
and 0.84 V Vref were verified unchanged. It passed ten full calibrations,
ten separate CPU memory tests, seventy DMA checks, four software reboots and
ten bidirectional CPU/DMA buffer handoffs. DMA testing included full 1 GiB
counter/PRBS transfers and read-only rechecks, with zero errors or faults.
The baseline image was restored and passed its BIOS memory test afterward.

This experiment motivates extending DQ-only level 3 to the 2933.333 profile;
it does not establish temperature, voltage, power-cycle or multi-board
qualification. Setup/hold/pulse slack remained +0.103/+0.013/-0.034 ns.
The negative pulse slack remains an explicit overclock limitation, and no
artificial clock constraints or reduced calibration margins were used.
