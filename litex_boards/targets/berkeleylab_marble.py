#!/usr/bin/env python3
'''
---------------------
 LiteX SoC on Marble
---------------------
with support for SO-DIMM DDR3, ethernet and UART.
To synthesize, add --build, to configure the FPGA over jtag, add --load.

-----------------
 Example configs
-----------------
with ethernet and DDR3, default IP: 192.168.1.50/24
  ./marble.py --with-ethernet --with-bist --spd-dump VR7PU286458FBAMJT.txt

lightweight config
  ./marble.py --integrated-main-ram-size 16384 --cpu-type serv

etherbone: access wishbone over ethernet
  ./marble.py --with-etherbone --csr-csv build/csr.csv

make sure reset is not asserted (RTS signal), set PC IP to 192.168.1.100/24,
then test and benchmark the etherbone link:
  cd build
  litex/liteeth/bench/test_etherbone.py --udp --ident --access --sram --speed
'''

from migen import *

from litex_boards.platforms import berkeleylab_marble

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.bitbang import I2CMaster

from litedram.modules import MT8JTF12864, parse_spd_hexdump, SDRAMModule
from litedram.phy import s7ddrphy

from liteeth.phy.s7rgmii import LiteEthPHYRGMII

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq, resets=[]):
        self.rst = Signal()
        self.clock_domains.cd_sys    = ClockDomain()
        self.clock_domains.cd_sys4x  = ClockDomain()
        self.clock_domains.cd_sys4x_dqs = ClockDomain()
        self.clock_domains.cd_idelay = ClockDomain()

        # # #

        self.submodules.pll = pll = S7MMCM(speedgrade=-2)

        resets.append(self.rst)
        self.comb += pll.reset.eq(reduce(or_, resets))
        pll.register_clkin(platform.request("clk125"), 125e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_sys4x, 4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_idelay, 200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(125e6),
        with_ethernet   = False,
        with_etherbone  = False,
        with_rts_reset  = False,
        with_led_chaser = True,
        spd_dump        = None,
        **kwargs
    ):
        platform = berkeleylab_marble.Platform()

        # CRG, resettable over USB serial RTS signal -----------------------------------------------
        resets = []
        if with_rts_reset:
            ser_pads = platform.lookup_request('serial')
            resets.append(ser_pads.rts)
        self.submodules.crg = _CRG(platform, sys_clk_freq, resets)

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on Berkeley-Lab Marble", **kwargs)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.K7DDRPHY(
                platform.request("ddram"),
                memtype      = "DDR3",
                nphases      = 4,
                sys_clk_freq = sys_clk_freq
            )

            if spd_dump is not None:
                ram_spd = parse_spd_hexdump(spd_dump)
                ram_module = SDRAMModule.from_spd_data(ram_spd, sys_clk_freq)
                print('DDR3: loaded config from', spd_dump)
            else:
                ram_module = MT8JTF12864(sys_clk_freq, "1:4")  # KC705 chip, 1 GB
                print('DDR3: No spd data specified, falling back to MT8JTF12864')

            self.add_sdram("sdram",
                phy    = self.ddrphy,
                module = ram_module,
                # size=0x40000000,  # Limit its size to 1 GB
                l2_cache_size = kwargs.get("l2_size", 8192),
                with_bist     = kwargs.get("with_bist", False)
            )

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet or with_etherbone:
            self.submodules.ethphy = LiteEthPHYRGMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"),
                tx_delay   = 0
            )

        if with_ethernet:
            self.add_ethernet(
                phy            = self.ethphy,
                dynamic_ip     = True,
                software_debug = False
            )

        if with_etherbone:
            self.add_etherbone(phy=self.ethphy, buffer_depth=255)

        # System I2C (behing multiplexer) ----------------------------------------------------------
        i2c_pads = platform.request('i2c_fpga')
        self.submodules.i2c = I2CMaster(i2c_pads)

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.submodules.leds = LedChaser(
                pads         = platform.request_all("user_led"),
                sys_clk_freq = sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on BerkeleyLab Marble")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",          action="store_true", help="Build design.")
    target_group.add_argument("--load",           action="store_true", help="Load bitstream.")
    target_group.add_argument("--sys-clk-freq",   default=125e6,       help="System clock frequency.")
    target_group.add_argument("--with-ethernet",  action="store_true", help="Enable Ethernet support.")
    target_group.add_argument("--with-etherbone", action="store_true", help="Enable Etherbone support.")
    target_group.add_argument("--with-rts-reset", action="store_true", help="Connect UART RTS line to sys_clk reset.")
    target_group.add_argument("--with-bist",      action="store_true", help="Add DDR3 BIST Generator/Checker.")
    target_group.add_argument("--spd-dump",       type=str,            help="DDR3 configuration file, dumped using the `spdread` command in LiteX BIOS.")
    builder_args(parser)
    soc_core_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq  = int(float(args.sys_clk_freq)),
        with_ethernet = args.with_ethernet,
        with_etherbone = args.with_etherbone,
        with_bist = args.with_bist,
        spd_dump = args.spd_dump,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    if args.build:
        builder.build()

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
