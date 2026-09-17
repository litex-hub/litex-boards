# Xilinx and Intel/Altera Hardware Validation

This document tracks hardware validation for the LiteX-Boards Xilinx and
Intel/Altera targets.

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
| `digilent_arty` | Not validated | DDR3 | Validate DDR3, Ethernet, SD. |
| `digilent_basys3` | Not validated | Integrated RAM | Validate buttons/switches/HDMI. |
| `digilent_nexys4` | Not validated | DDR2 | Validate DDR2, Ethernet, SD. |
| `digilent_nexys4ddr` | Not validated | DDR2 | Validate DDR2, SD. |
| `digilent_genesys2` | Not validated | DDR3 | Validate DDR3, Ethernet, HDMI. |
| `digilent_zedboard` | Not validated | DDR3 | Validate DDR3, SD, HDMI. |
| `terasic_de10lite` | Not validated | SDRAM | Validate SDRAM, switches. |
| `terasic_deca` | Not validated | DDR3 | Validate DDR3, Ethernet. |

## Peripheral Checks

### Digilent Arty

```sh
python3 -m litex_boards.targets.digilent_arty \
  --with-ethernet --with-sdcard --build --load
```

### Digilent Nexys Video

```sh
python3 -m litex_boards.targets.digilent_nexys_video \
  --with-ethernet --with-sdcard --with-video-terminal --build --load
```

### Terasic DE10-Lite

```sh
python3 -m litex_boards.targets.terasic_de10lite \
  --with-spi-flash --build --load
```

## Programmer Checks

- Verify VivadoProgrammer for Xilinx targets.
- Verify USBBlaster for Intel/Altera targets.
- Verify Adept/XC3SProg for legacy or Digilent-programmed targets.

## Known Open Items

- No CI matrix is currently planned; validation is manual or covered by existing target tests.
