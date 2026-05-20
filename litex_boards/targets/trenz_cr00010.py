#!/usr/bin/env python3 

# This file is Copyright (c) 2019 (year 0 AG) Antti Lukats <antti.lukats@gmail.com>
# This file is Copyright (c) 2014-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

# info about the board http://trenz.org/max1000-info

import argparse

from migen import *

from litex_boards.platforms import cr00010

from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *

from litex.soc.integration.builder import *

from litedram.modules import MT48LC4M16
from litedram.phy import GENSDRPHY

#from litex.soc.cores import gpio
from litex.soc.cores.spi_flash import SpiFlash
from litex.soc.cores.hyperbus import HyperRAM

#from bbio import *

#class ClassicLed(gpio.GPIOOut):
#    def __init__(self, pads):
#        gpio.GPIOOut.__init__(self, pads)

# CRG ----------------------------------------------------------------------------------------------
class _CRG(Module):
    def __init__(self, platform):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain()
        self.clock_domains.cd_por = ClockDomain(reset_less=True)

        # # #

        self.cd_sys.clk.attr.add("keep")
        self.cd_sys_ps.clk.attr.add("keep")
        self.cd_por.clk.attr.add("keep")

        # clock input always available
        clk12 = platform.request("clk12")

        # power on rst
        rst_n = Signal()
        self.sync.por += rst_n.eq(1)
        self.comb += [
            self.cd_por.clk.eq(clk12),
            self.cd_sys.rst.eq(~rst_n),
            self.cd_sys_ps.rst.eq(~rst_n)
        ]

        clk_outs = Signal(5)

        self.comb += self.cd_sys.clk.eq(clk_outs[0]) # C0
        self.comb += self.cd_sys_ps.clk.eq(clk_outs[1]) # C1

        #
        # PLL we need 2 clocks one system one for SDRAM phase shifter
        # 
        self.specials += \
            Instance("ALTPLL",
                p_BANDWIDTH_TYPE="AUTO",
                p_CLK0_DIVIDE_BY=6,
                p_CLK0_DUTY_CYCLE=50,
                p_CLK0_MULTIPLY_BY=25,
                p_CLK0_PHASE_SHIFT="0",
                p_CLK1_DIVIDE_BY=6,
                p_CLK1_DUTY_CYCLE=50,
                p_CLK1_MULTIPLY_BY=25, 
                p_CLK1_PHASE_SHIFT="-10000",
                p_COMPENSATE_CLOCK="CLK0",
                p_INCLK0_INPUT_FREQUENCY=83000,
                p_INTENDED_DEVICE_FAMILY="MAX 10",
                p_LPM_TYPE = "altpll",
                p_OPERATION_MODE = "NORMAL",
                i_INCLK=clk12,
                o_CLK=clk_outs, # we have total max 5 Cx clocks
                i_ARESET=~rst_n,
                i_CLKENA=0x3f,
                i_EXTCLKENA=0xf,
                i_FBIN=1,
                i_PFDENA=1,
                i_PLLENA=1,
            )
        self.comb += platform.request("sdram_clock").eq(self.cd_sys_ps.clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCSDRAM):

##   csr_peripherals = (
##        "leds",
##    )
#    csr_map.update(SoCCore.csr_map, csr_peripherals)

##    mem_map = {
#        "rom":      0x00000000,
#        "sram":     0x10000000,
#        "main_ram": 0xc0000000,
##        "bbio":     0x60000000,
#        "csr" :     0xf0000000
##    }
##    mem_map.update(SoCCore.mem_map)

    def __init__(self, device, sys_clk_freq=int(50e6), **kwargs):
        assert sys_clk_freq == int(50e6)

        platform = cr00010.Platform(device)

        SoCSDRAM.__init__(self, platform, clk_freq=sys_clk_freq,
            integrated_rom_size=0x6000,
#            integrated_main_ram_size=0x1000,
            **kwargs)

        self.mem_map['hyperram'] = 0x30000000

        self.submodules.hyperram = HyperRAM(platform.request("hyperram"))
        self.add_wb_slave(mem_decoder(self.mem_map["hyperram"]), self.hyperram.bus)
        self.add_memory_region("hyperram", self.mem_map["hyperram"], 8*1024*1024)

 
        self.mem_map['spiflash'] = 0x20000000
        spiflash_pads = platform.request('spiflash', 1)
        self.add_memory_region(
            "spiflash", self.mem_map["spiflash"], 8*1024*1024)

        self.submodules.spiflash = SpiFlash(
                spiflash_pads,
                dummy=8,
                div=4,
                endianness=self.cpu.endianness)
        self.add_csr("spiflash")

        # 8 MB flash: W74M64FVSSIQ
        self.add_constant("SPIFLASH_PAGE_SIZE", 256)
        self.add_constant("SPIFLASH_SECTOR_SIZE", 4096)
        self.add_constant("FLASH_BOOT_ADDRESS", self.mem_map['spiflash'])

        # spi_flash.py supports max 16MB linear space
        self.add_wb_slave(mem_decoder(self.mem_map["spiflash"]), self.spiflash.bus)

        self.submodules.crg = _CRG(platform)
 
##        self.submodules.leds = ClassicLed(Cat(platform.request("user_led", i) for i in range(7)))
##        self.add_csr("leds", allow_user_defined=True)
##        self.submodules.leds = ClassicLed(platform.request("user_led", 0))

# 
#        self.add_csr("gpio_leds", allow_user_defined=True)
#        self.submodules.gpio_leds = gpio.GPIOOut(platform.request("gpio_leds"))

        self.counter = counter = Signal(32)
        self.sync += counter.eq(counter + 1)
 
	#
        # make user LED to blink
        #  
        led_red = platform.request("user_led", 0)
        self.comb += led_red.eq(counter[23])

        # connect POWER Control
        # enable permanent 3.3V   
        pwr = platform.request('power_control', 0)
        self.comb += [
            pwr.enable.eq (1),
            pwr.vid0.eq (0),
            pwr.vid1.eq (0),
            pwr.vid2.eq (0),
        ]


# use micron device as winbond and ISSI not available

        if not self.integrated_main_ram_size:
            self.submodules.sdrphy = GENSDRPHY(platform.request("sdram"))
            sdram_module = MT48LC4M16(self.clk_freq, "1:1")
            self.register_sdram(self.sdrphy,
                                sdram_module.geom_settings,
                                sdram_module.timing_settings)
 
# include all unused pins as generic BBIO basic IP core

##        bbio_pads = platform.request("bbio")
        # we can exclue any number of I/O pins to be included
##        self.submodules.bbio = bbioBasic(bbio_pads, exclude=None)
##        self.add_wb_slave(mem_decoder(self.mem_map["bbio"]), self.bbio.bus)
##        self.add_memory_region("bbio", self.mem_map["bbio"], 4*4*1024)

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on CR00010")
    builder_args(parser)
    parser.add_argument("--device", choices=['8', '16'], help='Cyclone device: "8" for 10M08SAU169C8G or "16" for 10M16SAU169C8G')

    soc_sdram_args(parser)
    args = parser.parse_args()

    if args.device == '16':
        device = '10M16SAU169C8G'
    else:
        device = '10M08SAU169C8G'
    soc = BaseSoC(device, **soc_sdram_argdict(args))


    builder = Builder(soc, **builder_argdict(args))
    builder.build()


if __name__ == "__main__":
    main()
