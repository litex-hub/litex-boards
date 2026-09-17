# Efinix Hardware Validation

This document tracks hardware validation for the LiteX-Boards Efinix targets.
It is intentionally concise and can be executed with one or more dev kits
connected.

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
| `efinix_t20_f256_dev_kit` | Not validated | SDRAM | Validate SDRAM and SPI flash. |
| `efinix_t20_mipi_dev_kit` | Not validated | Integrated RAM | MIPI not validated. |
| `efinix_t8_f81_dev_kit` | Not validated | Integrated RAM | Verify Atmel programmer path. |
| `efinix_xyloni_dev_kit` | Not validated | Integrated RAM | Verify flash/BIOS offsets. |
| `efinix_t120_f576_dev_kit` | Not validated | LPDDR3 | Verify DDR, Ethernet RMII/RGMII, I2C. |
| `efinix_ti60_f225_dev_kit` | Not validated | HyperRAM | Verify HyperRAM, SD, Ethernet. |
| `efinix_ti375_c529_dev_kit` | Not validated | LPDDR4 | Verify DDR, Ethernet, SD/eMMC, OHCI, HDMI. |
| `efinix_tz170_j484_dev_kit` | Not validated | LPDDR4 | Verify DDR, SD, SPI flash. |

## Peripheral Checks

### Ti60

```sh
python3 -m litex_boards.targets.efinix_ti60_f225_dev_kit \
  --with-hyperram --with-spi-flash --with-sdcard --build --load
```

### Ti375

```sh
python3 -m litex_boards.targets.efinix_ti375_c529_dev_kit \
  --with-spi-flash --with-sdcard --with-ethernet --build --load
```

### T120

```sh
python3 -m litex_boards.targets.efinix_t120_f576_dev_kit \
  --with-spi-flash --with-i2c --with-ethernet --build --load
```

## Programmer Checks

- Verify `EfinixProgrammer.load_bitstream()` for every available board.
- Verify flash/bridge image selection for Titanium and Topaz devices.
- Verify Atmel programmer on T8/Xyloni-compatible boards where applicable.

## Known Open Items

- Efinix unified netlist flow remains opt-in and has known Ti375 LPDDR4/SFP limitations.
- No CI matrix is currently planned; validation is manual or handled by existing target tests.
