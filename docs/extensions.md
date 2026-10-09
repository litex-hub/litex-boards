# Extensions: Pmods, Daughterboards, Carriers And Docks

Hardware plugged on a connector of a board (a Pmod module, a daughterboard, the carrier/dock of a
SoM, an FMC card...) is described once, independently of the boards it plugs on, as an
**Extension**. It is then bound to the board's connector names when used:

```python
from litex_boards.extensions.pmod import PmodSDCard

platform.add_extension(PmodSDCard("pmodd"))  # Digilent MicroSD Pmod on Arty's JD.
sdcard_pads = platform.request("sdcard")
```

LiteX provides the mechanism (`litex.build.extension.Extension`); LiteX-Boards provides the
descriptions of the actual hardware in `litex_boards/extensions/`.

## Using Pmods From The Command Line

Targets of boards with Pmod connectors accept a repeatable `--pmod CONNECTOR=MODULE` argument:

```
$ python3 -m litex_boards.targets.digilent_arty --pmod pmoda=gpio --pmod pmodb=i2c --build
$ python3 -m litex_boards.targets.icebreaker --pmod PMOD1A+PMOD1B=dvi --build
```

| Module          | Hardware                                        | Added to the SoC                         |
|-----------------|-------------------------------------------------|------------------------------------------|
| `gpio`          | Raw 8-bit GPIO                                  | `GPIOTristate` core (`<connector>_gpio`) |
| `uart`          | UART, Digilent UART Pmod pinout (tx: pin 2, rx: pin 3) | Additional UART core (`<connector>_uart`) |
| `usb_uart`      | Digilent PmodUSBUART                            | Additional UART core (`<connector>_uart`) |
| `i2c`           | I2C on pins 1 (SDA) and 2 (SCL)                 | `I2CMaster` core (`<connector>_i2c`)     |
| `can`           | SN65HVD230 CAN transceiver                      | CTU-CAN-FD core (`<connector>_can`)      |
| `sdcard`        | Digilent MicroSD Pmod                           | IOs only, use with `--with-(spi-)sdcard` |
| `numato_sdcard` | Numato MicroSD module                           | IOs only, use with `--with-(spi-)sdcard` |
| `dvi`           | 1BitSquared DVI Pmod (two connectors: `a+b=dvi`)| IOs only, used by the target's video options |

IOs-only modules take precedence over the board's own resources of the same name. If the target
already requested that resource before the Pmods are plugged (ex: SD Card added in `BaseSoC`), the
Pmod would be ignored, so an error is raised instead. A wrong connector name is reported with the list
of the board's Pmod connectors, and so is a module plugged on a single-row (6-pin) Pmod while it needs
a dual-row (12-pin) one: `i2c` and `can` only use pins 1-4 and work on both.

## Available Extensions

| Module                              | Content                                                                 |
|-------------------------------------|-------------------------------------------------------------------------|
| `litex_boards.extensions.pmod`      | Pmod modules: `PmodGPIO`, `PmodUART`, `PmodUSBUART`, `PmodSDCard`, `PmodNumatoSDCard`, `PmodI2S2`, `PmodCAN`, `PmodI2C`, `PmodJTAG`, `PmodPS2`, `PmodLAN8720`, `PmodUSBHostDual`, `PmodUSBHostQuad`, `PmodUSBDevice`, `PmodLED`, `Pmod1BitSquaredBreakOff`, `PmodWS2812`, `PmodDVI`, and the `--pmod` helpers. |
| `litex_boards.extensions.syzygy`    | SYZYGY pods: `SyzygyGPIO`.                                              |
| `litex_boards.extensions.fmc`       | FMC cards: `FMCRAID` (AB09-FMCRAID SATA).                               |
| `litex_boards.extensions.qmtech`    | QMTech core-board daughterboards: `QMTechDaughterboard`, `QMTechRP2040Daughterboard`. |
| `litex_boards.extensions.enclustra` | Enclustra Mercury+ ST1 baseboard: `EnclustraST1`.                       |
| `litex_boards.extensions.sipeed`    | Sipeed SoM connectors and docks: `TangPrimer20KDock(Lite)`, `TangPrimer25KDock`, `TangMegaNeoDock`, `TangMega138KProDock`, `TangConsoleDock`. |
| `litex_boards.extensions.sdram_modules` | SDRAM modules plugged on a connector: `MiSTerSDRAM`, `SipeedSDRAM`. |
| `litex_boards.extensions.machdyne` | Machdyne FPGA modules shared by their carriers: `MachdyneML1` (Mozart ML1, Vivaldi ML1). |

## Options Common To All Extensions

```python
PmodSDCard("pmodd")                              # Positional: slots in declaration order.
PmodDVI(a="PMOD1A", b="PMOD1B")                  # Keyword: slots by name.
PmodUSBUART("pmodb", name="serial")              # Rename the resource (str, or dict {old: new}).
PmodUSBHostDual("pmoda", number=2)               # Offset resources' numbers (several identical modules).
PmodCAN("pmoda", iostandard="LVCMOS18")          # Override the IOStandard.
PmodGPIO("pmoda", misc=Misc("DRIVE=8"))          # Add constraints to all resources.
```

Extensions are added with `platform.add_extension(ext)` (use `prepend=True` to take precedence over
the board's resources of the same name) and resources are then requested as usual.

## Connector Conventions

- **Pmod**: 8 entries, index 0-3 = physical pins 1-4 (top row), index 4-7 = physical pins 7-10
  (bottom row); GND/VCC are not part of the connector. Single-row (6-pin) Pmods have 4 entries (pins
  1-4). Boards declaring a Pmod differently (physical numbering, placeholders) should also expose a
  canonical alias connector.
- **SYZYGY**: dict connector using the specification's signal names (`S0`-`S27`, `D0P`/`D0N`...,
  `P2C_CLKP`...), see `litex_boards/extensions/syzygy.py`.
- **FMC**: dict connector using the VITA 57.1/57.4 signal names (`LA00_CC_P`, `HA00_P`, `CLK0_M2C_P`,
  `DP0_C2M_P`...), see `litex_boards/extensions/fmc.py`.

Keep connector names stable once published; add aliases rather than renaming.

## Writing A Pmod Module

Describe the IOs with the slot name as connector name; they are remapped to the bound connector:

```python
from litex.build.generic_platform import Pins, Subsignal
from litex_boards.extensions.pmod import PmodExtension

class PmodFoo(PmodExtension):
    """Foo Pmod: https://..."""
    def define_io(self, platform):
        return [
            ("foo", 0,
                Subsignal("clk",  Pins("pmod:3")),
                Subsignal("data", Pins("pmod:1"), *self.pullup(platform)),
                *self.slew_fast(platform),
                *self.iostandard(platform),
            ),
        ]
```

Vendor-specific attributes come from the platform (`GenericPlatform.get_io_attr()`), so the module
works on any vendor: `self.iostandard()` (3.3V default, or the user's override), `self.pullup()`
(`PULLUP True`, `PULLMODE=UP`, `PULL_MODE=UP`...) and `self.slew_fast()`. Add the module to the
`pmods` registry (or `multi_pmods` for modules using several Pmods), and to the `--pmod` handling in
`add_pmods()` if it should be usable from the command line. Add a test in `test/test_pmods.py`.

## Writing A Carrier, Daughterboard Or Dock

A carrier is an Extension whose slots are the SoM/core-board connectors it plugs on. Besides its
IOs, it can expose its own connectors (Pmods, FMC...) with `define_connectors()`, on which other
Extensions can then be plugged: LiteX resolves chained connectors at build time.

```python
from litex.build.generic_platform import Pins, IOStandard
from litex.build.extension import Extension

class FooCarrier(Extension):
    slots = {"J2": "J2", "J3": "J3"}  # Slot: default host connector.

    def define_io(self, platform):
        return [
            ("user_led", 0, Pins("J2:7"), IOStandard("LVCMOS33")),
        ]

    def define_connectors(self, platform):
        return [
            ("pmoda", "J2:17 J2:19 J2:21 J2:23 J2:18 J2:20 J2:22 J2:24"),
        ]

platform.add_extension(FooCarrier())
platform.add_extension(PmodSDCard("pmoda"))  # Pmod plugged on the carrier.
```

For fixed descriptions, `IOExtension(io=_io, connectors=_connectors, slots={...})` turns existing IO
lists into an Extension without subclassing.

SoM platforms describe the module only (on-module IOs and board-to-board connectors) and add their
carrier from `Platform.__init__`, keeping a `dock=`/`with_daughterboard=` argument when several
carriers exist (see the Sipeed and QMTech platforms).

## Deprecations

Public helpers replaced by Extensions are kept as deprecated aliases emitting a `FutureWarning` that
points to the replacement, using `litex_boards.compat` (`warn_deprecated()`, or
`deprecated_pmod_helpers()` for module-level Pmod helpers). Deprecated APIs are removed after the
release set in `litex_boards.compat.DEPRECATION_RELEASE`.

Board-specific Pmod arguments of targets are deprecated in favor of `--pmod` (still functional, they
emit a `FutureWarning` with `warn_deprecated_arg()`):

| Target              | Deprecated argument        | Replacement                                         |
|---------------------|----------------------------|-----------------------------------------------------|
| `digilent_arty`     | `--with-pmod-gpio`         | `--pmod pmoda=gpio` (CSRs: `pmoda_gpio` instead of `gpio`) |
| `trellisboard`      | `--with-pmod-gpio`         | `--pmod pmoda=gpio` (CSRs: `pmoda_gpio` instead of `gpio`) |
| `digilent_arty`     | `--sdcard-adapter numato`  | `--pmod pmodd=numato_sdcard` (Digilent adapter is the default) |
| `digilent_basys3`   | `--sdcard-adapter numato`  | `--pmod pmoda=numato_sdcard` (Digilent adapter is the default) |
| `digilent_arty`     | `--with-can`               | `--pmod pmodc=can` (core: `pmodc_can` instead of `can0`, bus region allocated automatically) |
| `digilent_genesys2` | `--with-can`               | `--pmod pmodc=can` (core: `pmodc_can` instead of `can0`, bus region allocated automatically) |
| `colorlight_i9plus` | `--with-pmod-uart`         | Nothing: no effect, the default `serial` is already on Ext-Board conn. P2 |
