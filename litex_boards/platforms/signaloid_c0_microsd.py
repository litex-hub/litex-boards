# Copyright (c) 2024, Signaloid.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from litex.build.generic_platform import IOStandard, Misc, Pins, Subsignal
from litex.build.lattice import LatticeiCE40Platform

_io = [
    # Default Clk
    ("clk12", 0, Pins("B3"), IOStandard("LVCMOS33")),
    # Leds
    ("led_red", 0, Pins("B5"), IOStandard("LVCMOS33")),
    ("led_green", 0, Pins("A5"), IOStandard("LVCMOS33")),
    # SPIFlash
    (
        "spiflash",
        0,
        Subsignal("cs_n", Pins("C1"), IOStandard("LVCMOS18")),
        Subsignal("clk", Pins("D1"), IOStandard("LVCMOS18")),
        Subsignal("mosi", Pins("F1"), IOStandard("LVCMOS18")),
        Subsignal("miso", Pins("E1"), IOStandard("LVCMOS18")),
    ),
    # UART
    (
        "serial",
        0,
        Subsignal("rx", Pins("B3"), IOStandard("LVCMOS33")),
        Subsignal("tx", Pins("A4"), IOStandard("LVCMOS33"), Misc("PULLUP")),
    ),
]


_connectors = [
    ("SD_DAT0", "A1"),
    ("SD_DAT1", "A2"),
    ("SD_DAT2", "E5"),
    ("SD_DAT3", "F5"),
    ("SD_CMD", "A4"),
    ("SD_CLK", "B3"),
    ("LED_GREEN", "A5"),
    ("LED_RED", "B5"),
    ("CONFIG_MOSI", "F1"),
    ("CONFIG_MISO", "E1"),
    ("CONFIG_SCLK", "D1"),
    ("CONFIG_CS_N", "C1"),
    ("CONFIG_DONE", "D3"),
]


class Platform(LatticeiCE40Platform):
    default_clk_name = "clk12"
    default_clk_period = 1e9 / 12e6

    def __init__(self, toolchain="icestorm"):
        LatticeiCE40Platform.__init__(
            self, "ice40-up5k-uwg30", _io, _connectors, toolchain=toolchain
        )
