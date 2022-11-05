from litex.build.generic_platform import *
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("C18"), IOStandard("LVCMOS33")),

    # Leds
    ("user_led", 0, Pins("T20"),  IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("U20"),  IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("W20"),  IOStandard("LVCMOS33")),

    # Serial
    ("serial", 0,
        Subsignal("tx", Pins("R19")),
        Subsignal("rx", Pins("P19")),
        IOStandard("LVCMOS33"),
    ),
    ("serial", 1,
        Subsignal("tx", Pins("U21")),
        Subsignal("rx", Pins("T21")),
        IOStandard("LVCMOS33"),
    ),

    # DDR3 SDRAM (voltage changed from 1.5V to 1.35V)
    ("ddram", 0,
        Subsignal("a", Pins(
            "M2 M5 M3 M1 L6 P1 N3 N2",
            "M6 R1 L5 N5 N4 P2 P6"),
            IOStandard("SSTL135")),
        Subsignal("ba", Pins("L3 K6 L4"), IOStandard("SSTL135")),
        Subsignal("ras_n", Pins("J4"), IOStandard("SSTL135")),
        Subsignal("cas_n", Pins("K3"), IOStandard("SSTL135")),
        Subsignal("we_n", Pins("L1"), IOStandard("SSTL135")),
        Subsignal("dm", Pins("G3 F1"), IOStandard("SSTL135")),
        Subsignal("dq", Pins(
            "G2 H4 H5 J1 K1 H3 H2 J5",
            "E3 B2 F3 D2 C2 A1 E2 B1"),
            IOStandard("SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_p", Pins("K2 E1"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("dqs_n", Pins("J2 D1"),
            IOStandard("DIFF_SSTL135"),
            Misc("IN_TERM=UNTUNED_SPLIT_40")),
        Subsignal("clk_p", Pins("P5"), IOStandard("DIFF_SSTL135")),
        Subsignal("clk_n", Pins("P4"), IOStandard("DIFF_SSTL135")),
        Subsignal("cke", Pins("J6"), IOStandard("SSTL135")),
        Subsignal("odt", Pins("K4"), IOStandard("SSTL135")),
        Subsignal("reset_n", Pins("G1"), IOStandard("SSTL135")),
        Misc("SLEW=FAST"),
    ),

    # eMMC - there are pullups on the board so we don't enable them here
    ("sdcard", 0,
        Subsignal("data", Pins("P17 W17 R18 V18")),
        Subsignal("cmd",  Pins("Y19")),
        Subsignal("clk",  Pins("Y18")),
            #Subsignal("cd",   Pins(),
        Misc("SLEW=FAST"),
        IOStandard("LVCMOS33"),
    ),
    # RGMII Ethernet
    ("eth_ref_clk", 0, Pins("H19"), IOStandard("LVCMOS33")),  # 125 MHz if enabled?
    ("eth_clocks", 0,
        Subsignal("tx", Pins("J19")),
        Subsignal("rx", Pins("K19")),
        IOStandard("LVCMOS33")
    ),
    ("eth", 0,
        Subsignal("rst_n",   Pins("N18"), IOStandard("LVCMOS33")),
        Subsignal("int_n",   Pins("N20"), IOStandard("LVCMOS33")),
        Subsignal("mdio",    Pins("M21"), IOStandard("LVCMOS33")),
        Subsignal("mdc",     Pins("N22"), IOStandard("LVCMOS33")),
        Subsignal("rx_ctl",  Pins("M22"), IOStandard("LVCMOS33")),
        Subsignal("rx_data", Pins("L20 L21 K21 K22"), IOStandard("LVCMOS33")),
        Subsignal("tx_ctl",  Pins("J22"), IOStandard("LVCMOS33")),
        Subsignal("tx_data", Pins("G20 H20 H22 J21"), IOStandard("LVCMOS33")),
    ),

    # PCIe
    ("pcie_x1", 0,
        # Subsignal("rst_n", Pins(""), IOStandard("LVCMOS33")),
        Subsignal("clk_p", Pins("F6")),
        Subsignal("clk_n", Pins("E6")),
        Subsignal("rx_p",  Pins("B8")),
        Subsignal("rx_n",  Pins("A8")),
        Subsignal("tx_p",  Pins("B4")),
        Subsignal("tx_n",  Pins("A4"))
    ),

    # USB ULPI
    ("ulpi_clock", 0, Pins("W19"), IOStandard("LVCMOS33")),
    ("ulpi", 0,
        Subsignal("data", Pins("AB18 AA18 AA19 AB20 AA20 AB21 AA21 AB22")),
        Subsignal("dir", Pins("W21")),
        Subsignal("stp", Pins("Y22")),
        Subsignal("nxt", Pins("W22")),
        Subsignal("rst", Pins("V20")),
        IOStandard("LVCMOS33"), Misc("SLEW=FAST")
    ),

    ("ulpi_clock", 1, Pins("V4"), IOStandard("LVCMOS33")),
    ("ulpi", 1,
        Subsignal("data", Pins("AB2 AA3 AB3 Y4 AA4 AB5 AA5 AB6")),
        Subsignal("dir", Pins("AB7")),
        Subsignal("stp", Pins("AA6")),
        Subsignal("nxt", Pins("AB8")),
        Subsignal("rst", Pins("AA8")),
        IOStandard("LVCMOS33"), Misc("SLEW=FAST")
    ),

]

# Platform -----------------------------------------------------------------------------------------

class Platform(Xilinx7SeriesPlatform):
    default_clk_name   = "clk100"
    default_clk_period = 1e9/100e6

    def __init__(self, device="xc7a100tfgg484-1", toolchain="vivado"):
        Xilinx7SeriesPlatform.__init__(self, device, _io, toolchain=toolchain)
        # self.toolchain.bitstream_commands = \
        #     ["set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]"]
        # self.toolchain.additional_commands = \
        #     ["write_cfgmem -force -format bin -interface spix4 -size 16 "
        #      "-loadbit \"up 0x0 {build_name}.bit\" -file {build_name}.bin"]
        self.add_platform_command("set_property INTERNAL_VREF 0.675 [get_iobanks 35]")

    def create_programmer(self):
        bscan_spi = "bscan_spi_xc7a100t.bit" if "xc7a100t" in self.device else "bscan_spi_xc7a35t.bit"
        return OpenOCD("openocd_xc7_ft2232.cfg", bscan_spi)

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(self.lookup_request("clk100", loose=True), 1e9/100e6)
