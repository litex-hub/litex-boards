# AGENTS.md: LiteX-Boards

Platforms (pins, clocks, toolchain) and targets (the SoC built on them) for 250+ boards, used by
LiteX and its cores.

Read the LiteX agent page first: https://github.com/enjoy-digital/litex/wiki/LiteX-for-AI-Agents (framework map, conventions, how to
verify a change, contribute back). Index of the whole wiki for agents: https://github.com/enjoy-digital/litex/wiki/llms.txt.

## Where things are

- `litex_boards/platforms/<vendor>_<board>.py`: IOs, connectors, default clock, programmer.
- `litex_boards/targets/<vendor>_<board>.py`: CRG and `BaseSoC` with the board's options (`--help`).
- `litex_boards/extensions/` (Pmods, FMC, SYZYGY...), `litex_boards/prog/`.
- `test/`: parser style/alignment, target defaults/options/forwarding, board guardrails.

## Verify a change

```sh
python3 -m pytest -q test/test_parser_style.py test/test_parser_alignment.py test/test_targets_parser_api.py test/test_board_guardrails.py
python3 .github/scripts/sync_readme_boards_list.py --check        # README board list (new boards)
python3 -m litex_boards.targets.<board> --build --no-compile        # elaborate the target
```

A new board: copy the closest existing platform/target pair and follow its parser layout (the
tests check it); add it to the README list. Say which options ran on hardware.

## Rules

- Style: https://github.com/enjoy-digital/litex/blob/master/doc/coding_style.md (match the
  surrounding file; `module: Description of the change.` commit titles; one change per commit).
- Never edit generated files (`build/`, `csr.h`, `csr.csv`, the Verilog): change the Python.
- One topic per pull request, from `master`, with what was tested and on which hardware; say
  that an agent wrote it and who supervised. Do not rename options or reformat unrelated code.
- Hardware: never flash a board or write its SPI flash unless the user asked; `--load` (volatile)
  is the default for experiments.

## Debug on hardware

Method: https://github.com/enjoy-digital/litex/wiki/Debug-A-SoC-On-Hardware (check the link and `--ident` first, registers before
traces, narrow LiteScope captures). `litex_mcp` gives the same loop as MCP tools (CSRs by name,
LiteScope captures, builds with parsed timing, simulation): https://github.com/enjoy-digital/litex/wiki/LiteX-for-AI-Agents#drive-a-soc-through-mcp.
