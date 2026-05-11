# FPGA AI Accelerator Shell Preparation

This note summarizes the LiteX board shell options intended for early AI
inference experiments on SQRL FK33, SQRL XCU/VCU1525 and SQRL Acorn CLE215+.
The board targets remain generic LiteX SoCs; inference kernels should attach to
PCIe DMA streams, AXI memory ports or Ethernet/Etherbone as separate logic.

## Capability Matrix

| Board | Host link | Memory | Extra high-speed channels | Notes |
| --- | --- | --- | --- | --- |
| SQRL FK33 | PCIe x4/x8/x16 | HBM2, 32 pseudochannels | none in this target | Best fit for bandwidth-heavy kernels. |
| SQRL XCU/VCU1525 | PCIe x2/x4/x8/x16 | 4 selectable DDR4 channels | 2 QSFP cages, 4 lanes each | Best fit for PCIe plus external stream experiments. |
| SQRL Acorn CLE215+ | PCIe x4 | DDR3 | PCIe lanes can also be reused for SATA in the existing target | Smaller device; keep it as a compact PCIe/DDR3 accelerator shell. |

## Common PCIe Options

The three targets expose:

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

## FK33 HBM Options

FK33 now maps configurable HBM pseudochannels:

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
target promotes the bus and PCIe endpoint to 64-bit. When a mapping would exceed
the HBM AXI address width, local channel addressing is enabled automatically.

For AI kernels, prefer connecting performance-critical datapaths directly to
the selected HBM AXI interfaces instead of routing tensor traffic through CSR
or Wishbone accesses.

## XCU/VCU1525 DDR and QSFP Options

The DDR channel is explicit and validated:

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
build.

## Example Build Checks

```sh
python3 -m litex_boards.targets.sqrl_fk33 --with-pcie --pcie-lanes=16 --pcie-ndmas=2 --build --no-compile
python3 -m litex_boards.targets.sqrl_fk33 --with-hbm --hbm-channels=all --hbm-main-channel=0 --build --no-compile
python3 -m litex_boards.targets.sqrl_xcu1525 --ddram-channel=3 --with-pcie --pcie-lanes=16 --build --no-compile
python3 -m litex_boards.targets.sqrl_xcu1525 --with-ethernet --ethernet-port=qsfp1_sfp3 --build --no-compile
python3 -m litex_boards.targets.sqrl_acorn --variant=cle-215+ --with-pcie --pcie-ndmas=2 --build --no-compile
```

After generating a PCIe driver, the usual host smoke tests are:

```sh
litepcie_util info
litepcie_util scratch_test
litepcie_util dma_test
```
