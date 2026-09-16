# Gowin Hardware Validation

This document tracks the hardware validation steps for the LiteX-Boards Gowin
targets. It is intentionally small enough to be used at a desk with one or more
boards connected.

## Goals

- Verify the Gowin no-compile matrix is a reliable proxy for real builds.
- Validate basic bring-up on available boards: UART, BIOS, main RAM, and LEDs.
- Validate newly added peripheral options on the boards that expose them.
- Record programmer-specific issues so they can be fixed in LiteX or
  openFPGALoader instead of worked around locally.

## Common Commands

Build without synthesis:

```sh
python3 -m litex_boards.targets.<target> \
  --build --no-compile \
  --uart-name=stub \
  --cpu-type=vexriscv \
  --cpu-variant=minimal
```

Load and validate a built bitstream:

```sh
python3 -m litex_boards.targets.<target> --load
litex_term /dev/ttyUSB0
```

From the BIOS:

```text
mem_test
mem_speed
sdram_test
```

## Validation Matrix

| Target | Priority | UART/BIOS | Main RAM | Notes |
| --- | --- | --- | --- | --- |
| `sipeed_tang_primer_20k` | High | Not validated | Not validated | FT2232 programmer needs revalidation after openFPGALoader fix. |
| `sipeed_tang_nano_4k` | High | Not validated | HyperRAM option | Verify HyperRAM-backed framebuffer when board available. |
| `sipeed_tang_nano_9k` | High | Not validated | HyperRAM option | Verify HyperRAM-backed framebuffer and SPI SDCard. |
| `sipeed_tang_mega_60k` | Medium | Not validated | DDR3 | Audio/camera/HDMI/SPI-SD options can be smoke-tested. |
| `sipeed_tang_console` | Medium | Not validated | DDR3 | PCIe build is no-compile only until a host test is available. |
| `sipeed_tang_mega_138k` | Medium | Not validated | DDR3 | Ethernet/SD/PCIe/LCD need host-side tests. |
| `sipeed_tang_mega_138k_pro` | Medium | Not validated | DDR3 | Fan PWM, Ethernet/SFP, PCIe and HDMI out. |
| `modretro_chromatic` | Medium | Not validated | External memory | LCD, HDMI, QSPI, I2S, USB CDC-ACM, cartridge/link/IR. |
| `brisbaneSilicon_brs_100_gw1nr9` | Low | Not validated | HyperRAM | Onboard PSRAM integration. |

## Peripheral-Specific Checks

### Tang Nano 4K / 9K HyperRAM Framebuffer

```sh
python3 -m litex_boards.targets.sipeed_tang_nano_9k \
  --with-video-framebuffer --build --load
```

Verify a stable image and that the BIOS still reports the HyperRAM region.

### ModRetro Chromatic

```sh
python3 -m litex_boards.targets.modretro_chromatic \
  --with-lcd-terminal --with-hdmi-colorbars --with-qspi \
  --with-i2s-audio --with-esp32-uart --with-usb-acm \
  --build --load
```

Check each peripheral independently if resource pressure is observed.

### Tang Mega 60K

```sh
python3 -m litex_boards.targets.sipeed_tang_mega_60k \
  --with-hdmi --with-audio --with-camera --with-spi-sdcard \
  --build --load
```

Validate each option separately before combining them.

## Programmer Checks

- `openFPGALoader --cable ft2232 --ftdi-channel 0 --detect`
- `openFPGALoader -b tangprimer20k <bitstream>`
- Repeat load/detect at least twice to catch the FTDI reset issue.

## Known Open Items

- Tang Mega 60K Ethernet RGMII: RX pinout still needs to be sourced from the
  board schematic or an authoritative Sipeed pin table.
- openFPGALoader FT2232/Sipeed reset fallback should be exercised on hardware
  after the upstream/fork PR is available.
- Hardware matrix should be updated from `Not validated` to `Validated` only
  after the commands above pass on physical boards.
