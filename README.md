
           __   _ __      _  __    ___                   __
          / /  (_) /____ | |/_/___/ _ )___  ___ ________/ /__
         / /__/ / __/ -_)>  </___/ _  / _ \/ _ `/ __/ _  (_-<
        /____/_/\__/\__/_/|_|   /____/\___/\_,_/_/  \_,_/___/

                       LiteX boards files

              Copyright 2012-2020 / LiteX-Hub community

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

**A question or want to get in touch? Our IRC channel is [#litex at freenode.net](https://webchat.freenode.net/?channels=litex)**

> **Note:** All boards with >= 32MB of memory and enough logic can be considered as Linux Capable.


[> Open-hardware boards
-----------------------

Fully open-hardware boards, the ECP5 and iCE40 ones are even usable with the open-source FPGA toolchains!

| Name         | FPGA Family         | FPGA device   | Sys-Clk  | TTY  |       RAM           |    PCIe   |    Ethernet    |    Flash    | SDCard |
|--------------|---------------------|---------------|----------|------|---------------------|-----------|----------------|-------------|--------|
| ECPIX-5      | Lattice ECP5        | LFE5UM5G-85F  |  75MHz   | FTDI |  16-bit 512MB DDR3  |      No   |   1Gbps RGMII  |  16MB QSPI  |   Yes* |
| Fomu         | Lattice iCE40       | iCE40-UP5K    |  12MHz   | USB  |     128KB SPRAM     |      No   |         No     |  16MB QSPI  |   No   |
| HADBadge     | Lattice ECP5        | LFE5U-45F     |  48MHz   | IOs  |   8-bit  32MB SDR   |      No   |         No     |  16MB QSPI  |   No   |
| iCEBreaker   | Lattice iCE40       | iCE40-UP5K    |  24MHz   | FTDI |     128KB SPRAM     |      No   |         No     |  16MB QSPI  |   No   |
| LogicBone    | Lattice ECP5        | LFE5U-45F     |  75MHz   | FTDI |   16-bit 1GB DDR3   |      No   |   1Gbps RGMII  |  16MB QSPI  |   Yes  |
| MarbleMini   | Xilinx Artix7       | XC7A100T      |  100MHz  | FTDI |   16-bit 1GB DDR3   |      No   |   1Gbps RGMII  |  16MB QSPI  |   No   |
| MiniSpartan6 | Xilinx Spartan6     | XC6SLX25      |  80MHz   | FTDI |  16-bit  32MB SDR   |      No   |         No     |   8MB QSPI  |   Yes  |
| NeTV2        | Xilinx Artix7       | XC7A35T       | 100MHz   | IOs  |  32-bit 512MB DDR3  |  Gen2 X4  | 100Mbps RMII   |  16MB QSPI  |   Yes  |
| OrangeCrab   | Lattice ECP5        | LFE5U-25F     |  48MHz   | USB  |  16-bit 128MB SDR   |      No   |         No     |   4MB QSPI  |   Yes  |
| Pipistrello  | Xilinx Spartan6     | XC6SLX45      |  83MHz   | FTDI |  16-bit  64MB LPDDR |      No   |         No     |  16MB QSPI  |   Yes* |
| ULX3S        | Lattice ECP5        | LFE5U-45F     |  50MHz   | FTDI |  16-bit  32MB SDR   |      No   |         No     |   4MB QSPI  |   Yes  |
| TrellisBoard | Lattice ECP5        | LFE5UM5G-85F  |  75MHz   | FTDI |  32-bit   1GB DDR3  |  Gen2 X1* |   1Gbps RGMII* |  16MB QSPI  |   Yes  |
| TinyFPGA     | Lattice iCE40       | iCE40-LP8K    |  16MHz   | IOs  |         No          |      No   |         No     |  16MB QSPI  |   No   |

* Present on the board but not yet supported or validated with LiteX.

[> Accelerator boards
---------------------

PCIe accelerators boards that you could use to accelerate your applications, LiteX provides you the essential cores for it: LitePCIe and LiteDRAM along with the LiteX infrastructure to create a design and easily control it/debug it.

| Name           | FPGA Family         | FPGA device   | Sys-Clk  | TTY  |       DRAM            |    PCIe       |    Flash    |
|----------------|---------------------|---------------|----------|------|-----------------------|---------------|-------------|
| AcornCLE215+   | Xilinx Artix7       | XC7A200T      | 125MHz   | PCIe | 16-bit 1GB DDR3       |  Gen2 X4      |  16MB QSPI  |
| ForestKitten33 | Xilinx Ultrascale+  | XCVU33P       | 125MHz   | PCIe | 2 x 1024-bit 4GB HBM2*|  Gen3 X16**   |     ?       |
| BCU1525        | Xilinx Ultrascale+  | XCVU9P        | 125MHz   | PCIe | 4 x 64-bit DDR4 DIMM* |  Gen3 X16**   |     ?       |
| AlveoU250      | Xilinx Ultrascale+  | XCU250        | 125MHz   | PCIe | 4 x 64-bit DDR4 DIMM* |  Gen2 X16**   |     ?       |

* Present on the board but not yet supported or validated with LiteX.
** Currently limited to PCIe Gen2 X4 by LitePCIe.

[> Repurposed hardware
----------------------

Repurposed FPGA hardware that has been "documented" by enthusiasts :), allows you to discover FPGAs for very cheap (starting at 15$)!

| Name         | FPGA Family         | FPGA device   | Sys-Clk  | TTY  |       DRAM         |       Ethernet     |    Flash    |
|--------------|---------------------|---------------|----------|------|--------------------|--------------------|-------------|
| Colorlight5A | Lattice ECP5        | LFE5U-25F     |   60MHz  | IOs  | 32-bit 8MB SDR     | 2x 1Gbps RGMII     |   4MB QSPI  |
| Linsn RV901  | Xilinx Spartan6     | XC6SLX16      |   75MHz  | IOs  | 32-bit 8MB SDR     | 2x 1Gbps RGMII     |   4MB QSPI  |
| PanoLogic G2 | Xilinx Spartan6     | XC6SLX100-150 |   50MHz  | IOs  | 32-bit 128MB DDR2  | 1Gbps GMII         |  16MB QSPI  |
| Camlink-4K   | Lattice ECP5        | LFE5U-25F     |   81MHz  | IOs  | 16-bit 128MB DDR3  |        No          |   ?MB QSPI  |

The Colorlight5A is a very nice board to start with, cheap, powerful, easy to use with the open-source toolchain, you can find a specific LiteX project [here](https://github.com/enjoy-digital/colorlite)

* Present on the board but not yet supported or validated with LiteX.

[> Development boards
---------------------

| Name         | FPGA Family         | FPGA device   | Sys-Clk | TTY  |       RAM          |    PCIe   |    Ethernet    |    Flash    | SDCard |
|--------------|---------------------|---------------|---------|------|--------------------|-----------|----------------|-------------|--------|
| AC701        | Xilinx Artix7       | XC7A200T      | 100MHz  | FTDI | 64-bit ?MB DDR3    |  Gen2 X4  | 1Gbps RGMII    |  16MB QSPI  |   Yes* |
| Aller        | Xilinx Artix7       | XC7A200T      | 100MHz  | PCIe | 16-bit 256MB DDR3  |  Gen2 X4  |       No       | 128MB QSPI  |   No   |
| Arty(A7)     | Xilinx Artix7       | XC7A35T       | 100MHz  | FTDI | 16-bit 256MB DDR3  |     No    | 100Mbps MII    |  16MB QSPI  |   No   |
| ArtyS7       | Xilinx Spartan7     | XC7S50        | 100MHz  | FTDI | 16-bit 256MB DDR3  |     No    |       No       |  16MB QSPI  |   No   |
| Avalanche    | Microsemi PolarFire | MPF300TS      | 100MHz  | IOs  | 16-bit 256MB DDR3  |     No    |   1Gbps RGMII* |   8MB QSPI* |   No   |
| C10LPRefKit  | Intel Cyclone10     | 10CL055       |  50MHz  | FTDI | 16-bit  32MB SDR   |     No    |  100Mbps MII   |  16MB QSPI  |   No   |
| De0Nano      | Intel Cyclone4      | EP4CE22F      |  50MHz  | FTDI | 16-bit  32MB SDR   |     No    |       No       |      No     |   No   |
| De10Lite     | Intel MAX10         | 10M50DA       |  50MHz  | IOs  | 16-bit  64MB SDR   |     No    |       No       |      No     |   No   |
| De10Nano     | Intel Cyclone5      | 5CSEBA6       |  50MHz  | IOs  | 16-bit  32MB SDR   |     No    |       No       |      No     |   Yes  |
| De1SoC       | Intel Cyclone5      | 5CSEMA5       |  50MHz  | IOs  | 16-bit  64MB SDR   |     No    |       ?        |      ?      |   ?    |
| De2-115      | Intel Cyclone4      | EP4CE115      |  50MHz  | IOs  | 16-bit 128MB SDR   |     No    | 1Gbps GMII*    |  8MB QSPI   |   Yes* |
| ECP5-EVN     | Lattice ECP5        | LFE5UM5G-85F  |  50MHz  | FTDI |        No          |     No    |       ?        |      ?      |   ?    |
| Genesys2     | Xilinx Kintex7      | XC7K325T      | 125MHz  | FTDI | 32-bit   1GB DDR3  |     No    | 1Gbps RGMII*   |  32MB QSPI* |   Yes  |
| KC705        | Xilinx Kintex7      | XC7K325T      | 125MHz  | FTDI | 64-bit   1GB DDR3  | Gen2 X8** |   1Gbps GMII   |  32MB QSPI* |   Yes  |
| KCU105       | Xilinx KintexU      | XCKU40        | 125MHz  | FTDI | 64-bit   1GB DDR4  | Gen3 X8** | 1Gbps-BASE-X   |  64MB QSPI* |   Yes  |
| KX2          | Xilinx Kintex7      | XC7K160T      | 125MHz  | FTDI | 64-bit   1GB DDR3  |     No    |       No       |  64MB QSPI* |   No   |
| MachXO3      | Lattice MachXO3     | LCMXO3L-6900C | 125MHz  |  ?   |         ?          |     No    |       No       |      ?      |   No   |
| Mercury XU5  | Xilinx ZynqU+       | XCZU2EG       | 125MHz  | FTDI | 16-bit 512MB DDR4  |     No    |       No       |  64MB QSPI* |   No   |
| Mimas A7     | Xilinx Artix7       | XC7A50T       | 100MHz  | FTDI | 16-bit 256MB DDR3  |     No    | 1Gbps RGMII    |  16MB QSPI  |   No   |
| Nereid       | Xilinx Kintex7      | XC7K160T      | 100MHz  | PCIe | 64-bit   4GB DDR3  |  Gen2 X4  |       No       |  16MB QSPI  |   No   |
| Nexys4DDR    | Xilinx Artix7       | XC7A100T      | 100MHz  | FTDI | 16-bit 128MB DDR2  |     No    | 100Mbps RMII   |  16MB QSPI* |   Yes  |
| Nexys Video  | Xilinx Artix7       | XC7A200T      | 100MHz  | FTDI | 16-bit 512MB DDR3  |     No    |   1Gbps RMII*  |  32MB QSPI* |   Yes  |
| SP605        | Xilinx Spartan6     | XC6SLX45T     | 100MHz  | FTDI | 16-bit 128MB DDR3* |  Gen1 X1* |   1Gbps GMII   |   8MB QSPI* |   Yes* |
| Tagus        | Xilinx Artix7       | XC7A200T      | 100MHz  | PCIe | 16-bit 256MB DDR3  |  Gen2 X1  |  1Gbps-BASE-X* |  16MB QSPI* |   No   |
| VC707        | Xilinx Virex7       | XC7VX485T     | 125MHz  | FTDI | 64-bit   1GB DDR3  |  Gen3 X8* |   1Gbps GMII   |  16MB QSPI* |   Yes* |
| VCU118       | Xilinx VirtexU+     | XCVU9P        | 125MHz  | FTDI | 2 x 64-bit 4GB DDR4|  Gen3 X16*|  1Gbps SGMII   |  16MB QSPI* |   Yes* |
| Versa ECP5   | Lattice ECP5        | LFE5UM5G-45F  |  75MHz  | FTDI | 16-bit 128MB DDR3  |  Gen1 X1* | 1Gbps RGMII    |  16MB QSPI* |   No   |
| ZCU104       | Xilinx ZynqU+       | XCZU7EV       | 125MHz  | FTDI | 64-bit   1GB DDR4  |     No    | 1Gbps RGMII*   |  64MB QSPI* |   Yes* |
| Zybo Z7      | Xilinx ZynqU+       | XC7Z010       | 125MHz  | FTDI | 64-bit   1GB DDR4  |     No    | 1Gbps RGMII*   |  64MB QSPI* |   Yes* |

* Present on the board but not yet supported or validated with LiteX.
** Currently limited to PCIe Gen2 X4 by LitePCIe.
