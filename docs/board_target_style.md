# LiteX-Boards Target And Platform Style

This guide captures the conventions that make board support easy to review,
compare and keep compatible. It is intentionally conservative: existing boards
can keep their quirks, but new boards and touched boards should move toward
these patterns.

## Compatibility

- Keep target module names, platform module names, public CLI options,
  `BaseSoC` constructor arguments and platform resource names stable.
- When a better option name is introduced, keep the old spelling as an alias and
  make both names populate the same `argparse` destination.
- Prefer explicit `ValueError` or parser errors for new checks. Avoid changing
  existing error behavior in unrelated cleanup patches.
- Keep board-specific electrical, timing and programming quirks close to the
  board unless the same behavior is already repeated across several boards.
- Refactors should be small enough that `--help` output and no-compile builds
  can be compared before and after.
- When replacing a public helper, keep it as a deprecated alias using
  `litex_boards.compat` (`warn_deprecated()`): it emits a `FutureWarning`
  pointing to the replacement and is removed after
  `litex_boards.compat.DEPRECATION_RELEASE`.

## Target Layout

- Use `LiteXArgumentParser` for every target entry point.
- Keep the usual sections in this order when practical: imports, `_CRG`,
  `BaseSoC`, `main()`, parser options, SoC construction, builder, load/flash
  actions.
- Keep `BaseSoC` defaults compatible with the parser defaults.
- Put common feature arguments in a predictable order:
  `--sys-clk-freq`, board selectors such as `--revision` or `--variant`,
  Ethernet/Etherbone options, storage options, video options, then board-specific
  extras.
- Use mutually-exclusive groups for options that cannot be combined, such as
  `--with-ethernet`/`--with-etherbone` when a target does not support both
  simultaneously, or `--with-sdcard`/`--with-spi-sdcard`.
- Preserve common option meanings:
  `--eth-ip` is the local Ethernet/Etherbone IP address,
  `--remote-ip` is the TFTP/server peer address,
  `--eth-dynamic-ip` enables DHCP or dynamic assignment,
  `--with-sdcard` is native SDCard mode, and
  `--with-spi-sdcard` is SPI-mode SDCard.
- Targets of boards with Pmod connectors support `--pmod CONNECTOR=MODULE`:
  `add_pmod_args(parser)` before `parser.parse_args()` and
  `add_pmods(soc, args.pmod)` right after the `BaseSoC` construction (both from
  `litex_boards.extensions.pmod`). Prefer it over board-specific Pmod options.

## Platform Layout

- Keep IO declarations grouped by function: clocks/resets, LEDs/buttons,
  serial, memory, storage, networking, expansion connectors and board-specific
  peripherals.
- Prefer established LiteX resource names (`clk*`, `cpu_reset*`, `serial`,
  `user_led`, `user_btn`, `ddram`, `spiflash`, `sdcard`, `eth`, `pcie`) unless
  the board needs a more precise name.
- Keep connector names stable once published. Add aliases only when needed for
  compatibility.
- Declare Pmod connectors with 8 entries (index 0-3 = pins 1-4, index 4-7 =
  pins 7-10), 4 entries for single-row (6-pin) Pmods, or add such a canonical
  alias. Use the specification's signal names as keys for SYZYGY and FMC
  connectors.
- Describe hardware plugged on a connector (Pmod modules, daughterboards,
  carriers, docks, FMC/SYZYGY cards) as an Extension in
  `litex_boards/extensions/` instead of IO lists or helpers in the platform, see
  the [extensions guide](extensions.md). SoM platforms describe the module only
  and add their carrier/dock as an Extension.
- Keep `create_programmer()` signatures compatible with existing target calls.
- Put final timing, voltage and bitstream commands in `do_finalize()` unless
  they are required earlier by the platform/toolchain setup.

## Review Checklist

- `python3 -m litex_boards.targets.<board> --help` still exposes the same public
  options unless a compatibility alias was added.
- A no-compile build still works for the default configuration or the target is
  covered by a documented exclusion.
- Parser style and alignment checks pass.
- Any generated documentation or inventory files are refreshed.
- The board consistency audit stays at or below the known baseline:
  `python3 .github/scripts/audit_board_consistency.py --check`.
- Hardware behavior is unchanged unless the patch explicitly documents and tests
  the intended change.
