# FPGA AI Accelerator Shell Preparation

This note summarizes the LiteX board shell options intended for early AI
inference experiments on SQRL FK33, SQRL XCU/VCU1525, SQRL Acorn CLE215+ and
related PCIe/HBM accelerator boards.
The board targets remain generic LiteX SoCs; inference kernels should attach to
PCIe DMA streams, AXI memory ports or Ethernet/Etherbone as separate logic.

## Capability Matrix

| Board | Host link | Memory | Extra high-speed channels | Notes |
| --- | --- | --- | --- | --- |
| SQRL FK33 | PCIe x4/x8/x16 | HBM2, 32 pseudochannels | none in this target | Best fit for bandwidth-heavy kernels. |
| SQRL XCU/VCU1525 | PCIe x2/x4/x8/x16 | 4 selectable DDR4 channels | 2 QSFP cages, 4 lanes each | Best fit for PCIe plus external stream experiments. |
| SQRL Acorn CLE215+ | PCIe x4 | DDR3 | PCIe lanes can also be reused for SATA in the existing target | Smaller device; keep it as a compact PCIe/DDR3 accelerator shell. |
| Xilinx Alveo U280 | PCIe x4/x16 | DDR4 or HBM2, 32 pseudochannels | none in this target | Same configurable HBM mapping as FK33, with Alveo PCIe support. |
| Xilinx VCU128 | none in this target | DDR4 or HBM2, 32 pseudochannels | none in this target | Useful as an HBM memory/compute development board without a host PCIe shell. |
| Xilinx Alveo U200/U250 | PCIe x4/x16 | DDR4 | none in these targets | Useful for DDR4-backed PCIe accelerator shells. |
| Alibaba VU13P | PCIe x4/x8/x16 | 4 selectable DDR4 channels | 2 QSFP cages, 4 lanes each | PCIe plus QSFP streaming; QSFP port names are `qsfpX_sfpY`. |
| ADI ADRV2CRR-FMC | PCIe x4/x8 | 2 selectable DDR4 channels | RF/FMC-oriented platform resources | Useful when inference logic is close to the ADRV/RF datapath. |

## Common PCIe Options

PCIe-capable accelerator targets expose:

```sh
--with-pcie
--pcie-ndmas=<n>
--pcie-address-width=32|64
--pcie-with-dma-status
--pcie-with-dma-monitor
--driver
```

Defaults preserve the previous single-DMA behavior. Use more DMA channels when
host traffic and accelerator traffic need independent queues.

## HBM Options

FK33, Alveo U280 and VCU128 can map configurable HBM pseudochannels:

```sh
--with-hbm
--hbm-channels=0,1,2,3
--hbm-channels=0-7
--hbm-channels=all
--hbm-main-channel=<n>
--hbm-base=0x40000000
--hbm-high-base=0x100000000
--hbm-strip-origin
```

The default remains channels 0 through 3 at the existing base address. With the
default base, channels 4 and above are placed at `--hbm-high-base` to avoid the
32-bit CPU IO/CSR window. When a mapping would exceed a 32-bit SoC bus, the
target promotes the bus to 64-bit. PCIe/HBM targets also promote the PCIe DMA
address width when needed. When a mapping would exceed the HBM AXI address
width, local channel addressing is enabled automatically.
The HBM pseudochannel parser and SoC bus mapping helper live with LiteX's
`USPHBM2` core; board targets only select channels, bases and board-specific
XCI sources.

For AI kernels, prefer connecting performance-critical datapaths directly to
the selected HBM AXI interfaces instead of routing tensor traffic through CSR
or Wishbone accesses.

## DDR and QSFP Options

The DDR channel is explicit and validated on multi-DDR targets:

```sh
--ddram-channel=0
--ddram-channel=1
--ddram-channel=2
--ddram-channel=3
```

QSFP lanes can be used for LiteEth Ethernet or Etherbone:

```sh
--with-ethernet --ethernet-port=qsfp0_sfp0
--with-etherbone --etherbone-port=qsfp0_sfp1
--ethernet-ip=192.168.1.50
--eth-dynamic-ip
```

Valid ports are `qsfp0_sfp0` through `qsfp1_sfp3`. Existing SATA support uses
`qsfp0_sfp0`, so that lane cannot be used for Ethernet/Etherbone in the same
SQRL XCU/VCU1525 build. Alibaba VU13P uses the same QSFP port naming.

## Example Build Checks

```sh
python3 -m litex_boards.targets.sqrl_fk33 --with-pcie --pcie-lanes=16 --pcie-ndmas=2 --build --no-compile
python3 -m litex_boards.targets.sqrl_fk33 --with-hbm --hbm-channels=all --hbm-main-channel=0 --build --no-compile
python3 -m litex_boards.targets.sqrl_xcu1525 --ddram-channel=3 --with-pcie --pcie-lanes=16 --build --no-compile
python3 -m litex_boards.targets.sqrl_xcu1525 --with-ethernet --ethernet-port=qsfp1_sfp3 --build --no-compile
python3 -m litex_boards.targets.sqrl_acorn --variant=cle-215+ --with-pcie --pcie-ndmas=2 --build --no-compile
python3 -m litex_boards.targets.xilinx_alveo_u280 --with-hbm --hbm-channels=all --hbm-main-channel=0 --build --no-compile
python3 -m litex_boards.targets.xilinx_alveo_u200 --with-pcie --pcie-lanes=16 --pcie-ndmas=2 --build --no-compile
python3 -m litex_boards.targets.xilinx_alveo_u250 --with-pcie --pcie-lanes=16 --pcie-ndmas=2 --build --no-compile
python3 -m litex_boards.targets.alibaba_vu13p --with-pcie --pcie-lanes=16 --pcie-ndmas=2 --build --no-compile
python3 -m litex_boards.targets.adi_adrv2crr_fmc --ddram-channel=1 --with-pcie --pcie-lanes=8 --pcie-ndmas=2 --build --no-compile
```

After generating a PCIe driver, the usual host smoke tests are:

```sh
litepcie_util info
litepcie_util scratch_test
litepcie_util dma_test
```
