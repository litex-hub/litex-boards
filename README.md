
                                  __   _ __      _  __    ___                   __
                                 / /  (_) /____ | |/_/___/ _ )___  ___ ________/ /__
                                / /__/ / __/ -_)>  </___/ _  / _ \/ _ `/ __/ _  (_-<
                               /____/_/\__/\__/_/|_|   /____/\___/\_,_/_/  \_,_/___/

                                              LiteX boards files

                                     Copyright 2012-2022 / LiteX-Hub community

[![](https://github.com/litex-hub/litex-boards/workflows/ci/badge.svg)](https://github.com/litex-hub/litex-boards/actions) ![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)

[> Intro
--------
<figure>
<p align="center">
<img src="https://user-images.githubusercontent.com/1450143/88511626-73792100-cfe5-11ea-8d3e-dbeea6314e15.JPG">
</p>
<figcaption>
<p align="center">
From the very tiny Fomu to large PCIe accelerator boards....
</p>
</figcaption>
</figure>

This repository contains the platforms/targets currently supported by LiteX:

- The platform provides the definition of the board: IOs, constraints, clocks, components + methods to load and flash the bitstream to it.
- The target provides a LiteX base design for the board that allows you to create a SoC (with or without a CPU) and integrate easily all the base components of your board: Ethernet, DRAM, PCIe, SPIFlash, SDCard, Leds, GPIOs, etc...

The targets can be used as a base to build more complex or custom SoCs. They are are for example directly reused by the [Linux-on-LiteX-VexRiscv](https://github.com/litex-hub/linux-on-litex-vexriscv) project that is just using a specific configuration (Linux-capable CPU, additional peripherals). Basing your design on provided targets allows to to reduce code duplication between very various projects.

First make sure to install LiteX correctly by following the [installation guide](https://github.com/enjoy-digital/litex/wiki/Installation) and have a look at the [LiteX's wiki](https://github.com/enjoy-digital/litex/wiki) for [tutorials](https://github.com/enjoy-digital/litex/wiki/Tutorials-Resources),  [examples of projects](https://github.com/enjoy-digital/litex/wiki/Projects) and more information to use/build FPGA designs with it.

Each target provides a default configuration with a CPU, ROM, SRAM, UART, DRAM (if available), Ethernet (if available), etc... that can be simply built and loaded to the FPGA with:

    $ ./target.py --build --load

You can then open a terminal on the main UART of the board and interact with the LiteX BIOS:

<p align="center"><img src="https://raw.githubusercontent.com/enjoy-digital/litex/master/doc/bios_screenshot.png"></p>

But this is just the starting point to create your own hardware! You can then:

- Change the CPU: add `--cpu-type=lm32, microwatt, serv, rocket, etc... `
- Change the Bus standard: add `--bus-standard=wishbone, axi-lite`
- Enable components: add `--with-ethernet --with-etherbone --with-sdcard etc...`
- [Load application code to the CPU](https://github.com/enjoy-digital/litex/wiki/Load-Application-Code-To-CPU) over UART/Ethernet/SDCard, etc...
- Create a bridge with your computer to easily [access the main bus of your SoC](https://github.com/enjoy-digital/litex/wiki/Use-Host-Bridge-to-control-debug-a-SoC).
- Add a Logic Analyzer to your SoC to easily [observe/debug your design](https://github.com/enjoy-digital/litex/wiki/Use-LiteScope-To-Debug-A-SoC).
- Simulate your SoC and interact with it at decent speed with [LiteX Sim](https://github.com/enjoy-digital/litex/blob/master/litex/tools/litex_sim.py)/Verilator.
- Integrate external cores/CPU to create your own design.
- etc...

Please use `./target.py --help` to see the pre-built various possibilities.

Hoping you will find this useful and enjoy it, please contribute back if you make improvements that could be useful to others or find issues!

**A question or want to get in touch? Our IRC channel is [#litex at irc.libera.chat](https://web.libera.chat/#litex)**


[> Supported boards
-------------------

LiteX-Boards currently supports > 120 boards from very various FPGA Vendors (Xilinx, Intel, Lattice, Efinix, Gowin, etc...)!
Some of these boards are fully open-hardware boards (Fomu, NeTV2, OrangeCrab, Butterstick, etc...) with FPGAs often supported by the open-source toolchains, some of them are repurposed off-the-shelf hardware (Colorlight 5A/I5/I9, SQRL Acorn CLE 215+, FK33, Siglent SDS1104X-E, Decklink Mini 4k, etc...) and we also of course support popular/regular FPGA dev boards :)


Most of the peripherals present are generally supported: DRAM, UART, Ethernet, SPI-Flash, SDCard, PCIe, SATA, etc... making LiteX-Boards' targets hopefully a good base infrastructure to create your own custom SoCs!

> **Note:** All boards with >= 32MB of memory and enough logic can be considered as Linux Capable, have a look at [LiteX-on-LiteX-Vexriscv](https://github.com/litex-hub/linux-on-litex-vexriscv) project to try Linux on your FPGA board!


<figure>
<p align="center">
<img src="https://user-images.githubusercontent.com/1450143/156153536-297e2ff8-6ff5-4ec9-a497-b6fa90e26b46.png">
</p>
<figcaption>
<p align="center">
Some of the suported boards, see yours? Give LiteX-Boards a try!
</p>
</figcaption>
</figure>

[> Boards list
---------------
    ├── 1bitsquared_icebreaker_bitsy.py
    ├── 1bitsquared_icebreaker.py
    ├── alchitry_au.py
    ├── alchitry_mojo.py
    ├── alinx_axu2cga.py
    ├── antmicro_datacenter_ddr4_test_board.py
    ├── antmicro_lpddr4_test_board.py
    ├── avalanche.py
    ├── berkeleylab_marblemini.py
    ├── berkeleylab_marble.py
    ├── camlink_4k.py
    ├── colorlight_5a_75b.py
    ├── colorlight_5a_75e.py
    ├── colorlight_i5.py
    ├── decklink_intensity_pro_4k.py
    ├── decklink_mini_4k.py
    ├── decklink_quad_hdmi_recorder.py
    ├── digilent_arty.py
    ├── digilent_arty_s7.py
    ├── digilent_arty_z7.py
    ├── digilent_atlys.py
    ├── digilent_basys3.py
    ├── digilent_cmod_a7.py
    ├── digilent_genesys2.py
    ├── digilent_nexys4ddr.py
    ├── digilent_nexys4.py
    ├── digilent_nexys_video.py
    ├── digilent_pynq_z1.py
    ├── digilent_zedboard.py
    ├── digilent_zybo_z7.py
    ├── ebaz4205.py
    ├── efinix_titanium_ti60_f225_dev_kit.py
    ├── efinix_trion_t120_bga576_dev_kit.py
    ├── efinix_trion_t20_bga256_dev_kit.py
    ├── efinix_trion_t20_mipi_dev_kit.py
    ├── efinix_xyloni_dev_kit.py
    ├── ego1.py
    ├── enclustra_mercury_kx2.py
    ├── enclustra_mercury_xu5.py
    ├── fairwaves_xtrx.py
    ├── fpc_iii.py
    ├── gsd_butterstick.py
    ├── gsd_orangecrab.py
    ├── hackaday_hadbadge.py
    ├── jungle_electronics_fireant.py
    ├── kosagi_fomu_evt.py
    ├── kosagi_fomu_hacker.py
    ├── kosagi_fomu_pvt.py
    ├── kosagi_netv2.py
    ├── krtkl_snickerdoodle.py
    ├── lambdaconcept_ecpix5.py
    ├── lattice_crosslink_nx_evn.py
    ├── lattice_crosslink_nx_vip.py
    ├── lattice_ecp5_evn.py
    ├── lattice_ecp5_vip.py
    ├── lattice_ice40up5k_evn.py
    ├── lattice_machxo3.py
    ├── lattice_versa_ecp5.py
    ├── linsn_rv901t.py
    ├── litex_acorn_baseboard.py
    ├── logicbone.py
    ├── marblemini.py
    ├── marble.py
    ├── micronova_mercury2.py
    ├── mist.py
    ├── mnt_rkx7.py
    ├── muselab_icesugar_pro.py
    ├── muselab_icesugar.py
    ├── myminieye_runber.py
    ├── numato_aller.py
    ├── numato_mimas_a7.py
    ├── numato_nereid.py
    ├── numato_tagus.py
    ├── pano_logic_g2.py
    ├── qmtech_10cl006.py
    ├── qmtech_5cefa2.py
    ├── qmtech_daughterboard.py
    ├── qmtech_ep4cex5.py
    ├── qmtech_wukong.py
    ├── qmtech_xc7a35t.py
    ├── quicklogic_quickfeather.py
    ├── qwertyembedded_beaglewire.py
    ├── radiona_ulx3s.py
    ├── rcs_arctic_tern_bmc_card.py
    ├── redpitaya.py
    ├── rz_easyfpga.py
    ├── saanlima_pipistrello.py
    ├── scarabhardware_minispartan6.py
    ├── seeedstudio_spartan_edge_accelerator.py
    ├── siglent_sds1104xe.py
    ├── sipeed_tang_nano_4k.py
    ├── sipeed_tang_nano_9k.py
    ├── sipeed_tang_nano.py
    ├── sipeed_tang_primer.py
    ├── sqrl_acorn.py
    ├── sqrl_fk33.py
    ├── sqrl_xcu1525.py
    ├── stlv7325.py
    ├── terasic_de0nano.py
    ├── terasic_de10lite.py
    ├── terasic_de10nano.py
    ├── terasic_de1soc.py
    ├── terasic_de2_115.py
    ├── terasic_deca.py
    ├── terasic_sockit.py
    ├── tinyfpga_bx.py
    ├── trellisboard.py
    ├── trenz_c10lprefkit.py
    ├── trenz_cyc1000.py
    ├── trenz_max1000.py
    ├── trenz_te0725.py
    ├── trenz_tec0117.py
    ├── tul_pynq_z2.py
    ├── xilinx_ac701.py
    ├── xilinx_alveo_u250.py
    ├── xilinx_alveo_u280.py
    ├── xilinx_kc705.py
    ├── xilinx_kcu105.py
    ├── xilinx_kv260.py
    ├── xilinx_sp605.py
    ├── xilinx_vc707.py
    ├── xilinx_vcu118.py
    ├── xilinx_zcu104.py
    ├── xilinx_zcu106.py
    ├── xilinx_zcu216.py
    └── ztex213.py
