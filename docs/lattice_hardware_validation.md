# Lattice Hardware Validation

This document tracks hardware validation for the LiteX-Boards Lattice targets.
Use it with one or more dev kits connected.

## Common Commands

Build without synthesis:

```sh
python3 -m litex_boards.targets.<target> \
  --build --no-compile \
  --uart-name=stub \
  --cpu-type=vexriscv \
  --cpu-variant=minimal
```

Load and test:

```sh
python3 -m litex_boards.targets.<target> --load
litex_term /dev/ttyUSB0
```

BIOS checks:

```text
mem_test
mem_speed
sdram_test
```

## Target Matrix

| Target | UART/BIOS | Main RAM | Notes |
| --- | --- | --- | --- |
| `lattice_ecp5_evn` | Not validated | Integrated RAM | Validate LEDs and flash. |
| `lattice_ecp5_vip` | Not validated | SDRAM | Validate HDMI/SDRAM. |
| `lattice_ice40up5k_evn` | Not validated | SPRAM | Validate SPI flash/BIOS offset. |
| `lattice_certus_nx_versa` | Not validated | DDR3 | Validate DDR3/SPI flash. |
| `lattice_certuspro_nx_evn` | Not validated | Integrated RAM | Validate LEDs/buttons. |
| `lattice_certuspro_nx_versa` | Not validated | Integrated RAM | Validate PCIe. |
| `lattice_certuspro_nx_vvml` | Not validated | Integrated RAM | Validate LEDs/buttons. |
| `lattice_crosslink_nx_evn` | Not validated | SPRAM | Validate SPI flash. |
| `lattice_crosslink_nx_vip` | Not validated | HyperRAM | Validate HyperRAM. |
| `lattice_versa_ecp5` | Not validated | SDRAM | Validate Ethernet/SDRAM. |

## Peripheral Checks

### Certus-NX Versa

```sh
python3 -m litex_boards.targets.lattice_certus_nx_versa \
  --with-ddr3 --with-spi-flash --build --load
```

### CrossLink-NX EVN

```sh
python3 -m litex_boards.targets.lattice_crosslink_nx_evn \
  --with-spi-flash --build --load
```

### Versa ECP5

```sh
python3 -m litex_boards.targets.lattice_versa_ecp5 \
  --with-ethernet --build --load
```

## Programmer Checks

- Verify LatticeProgrammer/JTAG programming for each available board.
- Verify IceStorm programmer on iCE40 boards.
- Verify ecpdap/ecpprog where supported.

## Known Open Items

- No CI matrix is currently planned; validation is manual or covered by existing target tests.
