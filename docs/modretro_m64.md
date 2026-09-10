# ModRetro M64

The platform pinout follows ModRetro's M64 MLB schematic, part number 100-0610,
dated 2026-08-12. Official sources:

- [M64 open-source repository](https://github.com/ModRetro/oss-m64-console)
- [Hardware files and mechanical drawings](https://support.modretro.com/en_us/articles/m64-open-source-files-ByrpukdUGg)
- [Motherboard schematic](https://cdn.shopify.com/s/files/1/0829/2034/1806/files/M64_MLB_SCH.pdf?v=1786637413)
- [Motherboard assembly drawing](https://cdn.shopify.com/s/files/1/0829/2034/1806/files/M64_MLB_ASY.pdf?v=1786637413)

The FPGA is an Artix UltraScale+ XCAU15P-2FFVB676E. The target uses the independent
50MHz oscillator Y4, a 100MHz system clock, 64KiB of ROM and 128KiB of main RAM
in FPGA block RAM. The default console is JTAG UART on USER1. Hardware operation
has not yet been tested.

## Build and load

```sh
python3 -m litex_boards.targets.modretro_m64 --build
python3 -m litex_boards.targets.modretro_m64 --load
```

`--load` uses Vivado's programmer to load the FPGA through J10. The schematic
specifies a TC2050-IDC footprint and TC2050-XILINX adapter for a Xilinx Platform
Cable. J10 uses **1.8V JTAG**: pin 1 is VREF, 2 TMS, 4 TCK, 6 TDO, 8 TDI,
3/5/7/9 ground and 10 unconnected (sheet 20).

For a console, use an OpenOCD-compatible adapter with 1.8V signalling and an
OpenOCD configuration for that adapter and the XCAU15P TAP. The TAP has a 6-bit
instruction register and IDCODE 0x04ac2093, ignoring the revision nibble:

```tcl
# Add the configuration for your JTAG adapter before this block.
transport select jtag
adapter speed 10000
set _CHIPNAME xcau15p
jtag newtap $_CHIPNAME tap -irlen 6 -ignore-version -expected-id 0x04ac2093
```

```sh
litex_term jtag --jtag-config=m64.cfg
```

The target constrains JTAG to 10MHz. `--with-jtagbone` selects a crossover UART
and JTAGBone on USER1. The physical UART is available with `--uart-name=serial`:
J18 pin 4 is FPGA RX, pin 5 FPGA TX and pin 1 ground, at **3.3V**. J18 is marked
unpopulated in the schematic. This UART is separate from `serial_mcu`.

## Interfaces

| Platform resource | Connection | Schematic sheets |
| --- | --- | --- |
| `clk50`, `cpu_reset_n` | Y4 oscillator; system reset supervisor | 3, 9, 10, 30 |
| `clk_ref`, `clk_alt`, `clk_gth`, `clkgen_i2c`, `clkgen` | 8T49N241 clock generator, I2C address 0x7c | 3, 8, 10 |
| `serial`, `serial_mcu`, `spi_mcu` | Debug header and STM32 links | 9, 20, 24 |
| `psram:0..2` | U2/U17/U11, APS256XXN-OB9-BG, 32MiB each | 11, 12, 18, 19 |
| `psram:3` | U12, APS512XXN-OB9-BG, 64MiB | 11, 19 |
| `hdmi`, `hdmi_ctrl`, `hdmi_i2c`, `hdmi_ddc` | GTH bank 226 and SN75DP159 retimer, control I2C address 0x5e | 7, 8, 13 |
| `n64_controller:0..3` | Four controller data lines | 5, 9 |
| `gpio`, connector `J25` | Eight expansion pins, GPIO_BONUS_0..7, **1.8V** | 10 |

`--with-gpio` exposes J25 through GPIO CSRs; all pins start as inputs. The
programmable clock outputs require a clock-generator configuration and timing
constraints matching that configuration. Their `100_` schematic net prefix
denotes differential impedance, not a documented 100MHz frequency.

PSRAM and HDMI currently have platform resources only. The PSRAM devices use
x16 DDR data and two DQS/DM signals; a matching controller and PHY are still
needed. HDMI uses four GTH transmitters through the DP159, including the clock
lane; it requires a GTH video PHY and retimer setup.

The SD card and LEDs connect to the STM32, so they have no FPGA platform
resources. The MT25QU256 configuration flash is shared with the STM32 and holds
FPGA/MCU images (sheets 9, 17, 25). Access would require STARTUPE3 and coordination
with the MCU; this target does not use or program it. Initial operation also
depends on the MCU enabling the board's power rails.
