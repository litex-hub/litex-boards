#!/usr/bin/env python3

# This file is part of LiteX-Boards.
#
# Copyright (c) 2025 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause
#
# Build/Use:
# ./ypcb_00338_1p1.py --uart-name=jtag_uart --with-pcie --build --load
# litex_term jtag --jtag-config=openocd_xc7_ft232.cfg
#
# DDR3: both 72-bit channels at full 64-bit width (ECC lane unused, or SECDED with --with-ecc) with the K7DDRPHY on HR banks
# (no ODELAYE2) and its CK phase shift (write leveling by CK phase). The BIOS calibrates both at
# boot: channel 0 (main_ram), then channel 1 (exposed through its LiteDRAM BIST, for user logic on
# its crossbar; "sdram_cal 1" re-calibrates it).

import os

from migen import *
from litex.gen import *

from litex_boards.platforms import ypcb_00338_1p1

from litex.soc.cores.clock          import *
from litex.soc.integration.soc import *
from litex.soc.integration.builder  import *
from litex.soc.cores.led            import LedChaser

from litedram.modules        import MT41K256M8
from litedram.phy.s7ddrphy   import K7DDRPHY
from litedram.common         import PHYPadsReducer

from litepcie.phy.s7pciephy import S7PCIEPHY
from litepcie.software import generate_litepcie_software

# CRG ----------------------------------------------------------------------------------------------

class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst       = Signal()
        self.cd_sys    = ClockDomain()
        self.cd_idelay = ClockDomain()

        # Clk (the board reset pin is not wired: reset from the MMCM's lock).
        clk200 = platform.request("clk200")

        # PLL.
        self.pll = pll = S7MMCM(speedgrade=-2)
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk200, 200e6)
        pll.create_clkout(self.cd_sys,    sys_clk_freq, margin=1e-4)
        pll.create_clkout(self.cd_idelay, 200e6)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin) # Ignore sys_clk to pll.clkin path created by SoC's rst.

        # IDelayCtrl.
        self.idelayctrl = S7IDELAYCTRL(self.cd_idelay)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    # MMCM of each channel's PHY in the channel's clock region (channel 0: banks 11-13, channel 1:
    # banks 16-18).
    ddram_mmcm_locs = ["MMCME2_ADV_X0Y2", "MMCME2_ADV_X0Y6"]

    def __init__(self, sys_clk_freq=400e6/3,
        ddram_channels  = 2,
        with_led_chaser = True,
        with_pcie       = False,
        with_ecc        = False,
        **kwargs):

        # Platform ---------------------------------------------------------------------------------
        platform = ypcb_00338_1p1.Platform()

        # CRG --------------------------------------------------------------------------------------
        self.crg = _CRG(platform, sys_clk_freq)

        # SoCCore ----------------------------------------------------------------------------------
        if kwargs["uart_name"] == "serial":
            if kwargs.get("uart_name", "serial") == "serial": kwargs["uart_name"] = "jtag_uart"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on YPCB-00338-1P1", **kwargs)

        # DDR3 SDRAM ------------------------------------------------------------------------------
        # One K7DDRPHY (HR banks, CK phase shift) + LiteDRAM core per channel, each with a BIST
        # (the calibration's traffic test). Each channel's sdram/ddrphy/sdram_generator/
        # sdram_checker CSRs are kept at a fixed stride, so the BIOS calibrates channel k at
        # channel 0's CSRs + k*stride.
        if not self.integrated_main_ram_size:
            assert ddram_channels in (1, 2)
            csr_groups = ["sdram", "ddrphy", "sdram_generator", "sdram_checker"]
            csr_first  = 16
            for k in range(ddram_channels):
                suffix = "" if k == 0 else str(k)
                for i, group in enumerate(csr_groups):
                    name = group.replace("sdram", "sdram" + suffix)
                    name = name.replace("ddrphy", "ddrphy" + suffix)
                    self.csr.add(name, n=csr_first + len(csr_groups)*k + i)
                # ECC: all nine byte lanes (SECDED on the ninth, LiteDRAM's DFI ECC); without, the
                # ECC lane unused.
                pads = PHYPadsReducer(platform.request("ddram", k), list(range(9 if with_ecc else 8)))
                phy  = K7DDRPHY(
                    pads                = pads,
                    memtype             = "DDR3",
                    sys_clk_freq        = sys_clk_freq,
                    with_odelay         = False, # HR banks.
                    with_ck_phase_shift = True,
                    name                = f"ddrphy{suffix}",
                    mmcm_loc            = self.ddram_mmcm_locs[k])
                phy.add_constraints(platform)
                setattr(self, f"ddrphy{suffix}", phy)
                # with_ecc only when enabled: LiteDRAM releases without DFI ECC don't know it.
                self.add_sdram(f"sdram{suffix}",
                    phy                   = phy,
                    module                = MT41K256M8(sys_clk_freq, "1:4"),
                    with_bist             = True,
                    with_soc_interconnect = (k == 0),
                    size                  = 0x40000000,
                    l2_cache_size         = kwargs.get("l2_size", 8192),
                    **({"with_ecc": True} if with_ecc else {}),
                )
            self.add_constant("SDRAM_CSR_STRIDE",  len(csr_groups)*self.csr.paging)
            self.add_constant("SDRAM_CONTROLLERS", ddram_channels)

        # PCIe -------------------------------------------------------------------------------------
        if with_pcie:
            self.pcie_phy = S7PCIEPHY(platform, platform.request("pcie_x8"),
                data_width = 128,
                bar0_size  = 0x20000)
            self.pcie_phy.update_config({"PCIe_Blk_Locn": "X0Y0"})
            self.add_pcie(phy=self.pcie_phy, ndmas=1)
            self.pcie_phy.add_gt_loc_constraints(locs=[
                "GTXE2_CHANNEL_X0Y23",
                "GTXE2_CHANNEL_X0Y22",
                "GTXE2_CHANNEL_X0Y21",
                "GTXE2_CHANNEL_X0Y20",
                "GTXE2_CHANNEL_X0Y19",
                "GTXE2_CHANNEL_X0Y18",
                "GTXE2_CHANNEL_X0Y17",
                "GTXE2_CHANNEL_X0Y16",
            ], gt_type="gtx")


        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            self.leds = LedChaser(platform.request_all("user_led"), sys_clk_freq)

# Build ------------------------------------------------------------------------------------------

def main():
    from litex.build.parser import LiteXArgumentParser
    parser = LiteXArgumentParser(platform=ypcb_00338_1p1.Platform, description="LiteX SoC on YPCB-00338-1P1.")
    parser.add_target_argument("--sys-clk-freq",   default=400e6/3, type=float, help="System clock frequency (DDR3 rate / 8).")
    parser.add_target_argument("--ddram-channels", default=2,       type=int,   help="DDR3 channels (1 or 2).")
    parser.add_target_argument("--with-pcie",      action="store_true",         help="Enable PCIe support.")
    parser.add_target_argument("--with-ecc",       action="store_true",         help="DDR3 ECC (SECDED on the ECC byte lane).")
    parser.add_target_argument("--driver",         action="store_true",         help="Generate PCIe driver.")
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq   = args.sys_clk_freq,
        ddram_channels = args.ddram_channels,
        with_pcie      = args.with_pcie,
        with_ecc       = args.with_ecc,
        **parser.soc_argdict
    )
    builder = Builder(soc, **parser.builder_argdict)
    if args.build or args.driver:
        if not args.build:
            builder.compile_software = False
            builder.compile_gateware = False
        builder.build(**parser.toolchain_argdict)

    if args.driver:
        generate_litepcie_software(soc, os.path.join(builder.output_dir, "driver"))

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

if __name__ == "__main__":
    main()
