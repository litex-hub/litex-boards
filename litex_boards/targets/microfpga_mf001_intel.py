#!/usr/bin/env python3

# This file is Copyright (c) 2019 Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import argparse

from migen import *

from litex_boards.platforms import mf001_intel

from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *

from onchip_osc import *
from mfio import *

from atlantic import *


from litex.build.tools import write_to_file

# CRG ----------------------------------------------------------------------------------------------
class _CRG(Module):
    def __init__(self, platform):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_por = ClockDomain(reset_less=True)

        # kick off onchip oscillator
        self.submodules.osc = osc = onchip_osc(device=platform.device)

        # # #

        self.cd_sys.clk.attr.add("keep")
        self.cd_por.clk.attr.add("keep")

        # power on rst
        rst_n = Signal()
        self.sync.por += rst_n.eq(1)
        self.comb += [
            self.cd_por.clk.eq(osc.clkout),
            self.cd_sys.clk.eq(osc.clkout),
            self.cd_sys.rst.eq(~rst_n)
        ]

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    mem_map = {
        "rom":      0x00000000,
        "sram":     0x10000000,
        "main_ram": 0xc0000000,
        "mfio":     0x20000000,
        "csr" :     0xf0000000
    }
    #mem_map.update(SoCCore.mem_map)

    def __init__(self, sys_clk_freq=int(82e6), platform_id=0, **kwargs):
        assert sys_clk_freq == int(82e6)

        platform = mf_max10_001.Platform(platform_id)

# FIXME does not work
#        self.platform.add_period_constraint("sys_clk", 1e9/116.5e6)

        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq,
            ident="MicroFPGA,MAX10,001,{},{}".format(platform.rom_size, platform.ram_size),
            integrated_rom_size      = platform.rom_size * 1024,
            integrated_main_ram_size = platform.ram_size * 1024,
            with_uart=False, 
#            uart_name="jtag_atlantic",
            **kwargs)

        self.submodules.crg = _CRG(platform)

        mfio_pads = platform.request("mfio")
        # we can exclue any number of I/O pins to be included
        self.submodules.mfio = mfioBasic(mfio_pads, exclude=None)
        self.add_wb_slave(mem_decoder(self.mem_map["mfio"]), self.mfio.bus)
        self.add_memory_region("mfio", self.mem_map["mfio"], 4*4*1024)


        # Add some constants for the software
        # TODO exluded pins should be removed from count
        self.add_constant("MFIO_PINS_COUNT", len(mfio_pads))
        self.add_constant("MFIO_TYPE", "Basic")


        if not self.with_uart:
            self.submodules.uart = UART_atlantic(platform)
            self.add_csr("uart", allow_user_defined=True)
            self.add_interrupt("uart", allow_user_defined=True)



#        self.counter = counter = Signal(32)
#        self.sync += counter.eq(counter + 1)
      
#        led0 = platform.request("mfio", 0)
#        self.comb += led0.eq(counter[23])



# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX MicroFPGA SoC on Intel MAX10")
    builder_args(parser)
    soc_core_args(parser)

    parser.add_argument("--platform-id", default=0,
                        help="platform #id number to build for")

    args = parser.parse_args()

    cls = BaseSoC
    soc = cls(platform_id=int(args.platform_id), **soc_core_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build()

    print("---")
    print(builder.output_dir)

    write_to_file(builder.output_dir + "\\README.md", soc.platform.docs)









if __name__ == "__main__":
    main()
