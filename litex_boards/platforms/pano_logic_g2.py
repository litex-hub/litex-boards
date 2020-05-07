# Support for the Pano Logic Zero Client G2
# More information about the board and the reverse engineering results
# can be found here https://github.com/tomverbeure/panologic-g2

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform, iMPACT

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # NET "led_red" LOC = E12 | IOSTANDARD = LVCMOS33;
    # NET "led_blue" LOC = H13 | IOSTANDARD = LVCMOS33;
    # NET "led_green" LOC = F13 | IOSTANDARD = LVCMOS33;
    ("user_led", 0, Pins("E12"), IOStandard("LVCMOS33")),
    ("user_led", 1, Pins("H13"),  IOStandard("LVCMOS33")),
    ("user_led", 2, Pins("F13"),  IOStandard("LVCMOS33")),

    # NET "pano_button" LOC = H12 | IOSTANDARD = LVCMOS33;
    ("user_sw", 0, Pins("H12"), IOStandard("LVCMOS33")),

    # NET "osc_clk" LOC = Y13 | IOSTANDARD = LVCMOS33;
    ("clk125", 0, Pins("Y13"), IOStandard("LVCMOS33")),

    # NET "GMII_RST_N" LOC = R11 | IOSTANDARD = LVCMOS33;
    ("gmii_rst_n", 0, Pins("R11"), IOStandard("LVCMOS33")),

    # NET "SYSRST_N" LOC = AB14 | IOSTANDARD = LVCMOS33;
    ("cpu_reset", 0, Pins("AB14"), IOStandard("LVCMOS33")),

    # NET "DDR2A_CK_P" LOC = H20 | IOSTANDARD = LVCMOS18;
    # NET "DDR2A_CK_N" LOC = J19 | IOSTANDARD = LVCMOS18;
    ("ddram_clock_a", 0,
        Subsignal("p", Pins("H20")),
        Subsignal("n", Pins("J19")),
        IOStandard("DIFF_SSTL18_II"), Misc("IN_TERM=NONE")
    ),

    # NET "DDR2B_CK_P" LOC = H4 | IOSTANDARD = LVCMOS18;
    # NET "DDR2B_CK_N" LOC = H3 | IOSTANDARD = LVCMOS18;
    ("ddram_clock_b", 0,
        Subsignal("p", Pins("H4")),
        Subsignal("n", Pins("H3")),
        IOStandard("DIFF_SSTL18_II"), Misc("IN_TERM=NONE")
    ),

    ("ddram_a", 0,
        # NET "DDR2A_A[12]" LOC = D22 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_A[11]" LOC = F19 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_A[10]" LOC = G19 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_A[9]" LOC = C22 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_A[8]" LOC = C20 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_A[7]" LOC = E20 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_A[6]" LOC = K19 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_A[5]" LOC = K20 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_A[4]" LOC = F20 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_A[3]" LOC = G20 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_A[2]" LOC = E22 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_A[1]" LOC = F22 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_A[0]" LOC = F21 | IOSTANDARD = LVCMOS18;
        Subsignal("a", Pins("F21 F22 E22 G20 F20 K20 K19 E20 C20 C22 G19 F19 D22"), IOStandard("SSTL18_II")),
        # NET "DDR2A_BA[2]" LOC = H18 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_BA[1]" LOC = K17 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_BA[0]" LOC = J17 | IOSTANDARD = LVCMOS18;
        Subsignal("ba", Pins("J17 K17 H18"), IOStandard("SSTL18_II")),
        # NET "DDR2A_RAS_L" LOC = H21 | IOSTANDARD = LVCMOS18;
        Subsignal("ras_n", Pins("H21"), IOStandard("SSTL18_II")),
        # NET "DDR2A_CAS_L" LOC = H22 | IOSTANDARD = LVCMOS18;
        Subsignal("cas_n", Pins("H22"), IOStandard("SSTL18_II")),
        # NET "DDR2A_WE_L" LOC = H19 | IOSTANDARD = LVCMOS18;
        Subsignal("we_n", Pins("H19"), IOStandard("SSTL18_II")),
        # NET "DDR2A_UDM" LOC = M20 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_LDM" LOC = L19 | IOSTANDARD = LVCMOS18;
        Subsignal("dm", Pins("M20 L19"), IOStandard("SSTL18_II")),
        # NET "DDR2A_D[0]" LOC = N20 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[1]" LOC = N22 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[2]" LOC = M21 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[3]" LOC = M22 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[4]" LOC = J20 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[5]" LOC = J22 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[6]" LOC = K21 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[7]" LOC = K22 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[8]" LOC = P21 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[9]" LOC = P22 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[10]" LOC = R20 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[11]" LOC = R22 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[12]" LOC = U20 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[13]" LOC = U22 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[14]" LOC = V21 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_D[15]" LOC = V22 | IOSTANDARD = LVCMOS18;
        Subsignal("dq", Pins("N20 N22 M21 M22 J20 J22 K21 K22 P21 P22 R20 R22 U20 U22 V21 V22"), IOStandard("SSTL18_II")),
        # NET "DDR2A_UDQS_P" LOC = T21 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_LDQS_P" LOC = L20 | IOSTANDARD = LVCMOS18;
        Subsignal("dqs", Pins("T21 L20"), IOStandard("DIFF_SSTL18_II")),
        # NET "DDR2A_UDQS_N" LOC = T22 | IOSTANDARD = LVCMOS18;
        # NET "DDR2A_LDQS_N" LOC = L22 | IOSTANDARD = LVCMOS18;
        Subsignal("dqs_n", Pins("T22 L22"), IOStandard("DIFF_SSTL18_II")),
        # NET "DDR2A_CKE" LOC = D21 | IOSTANDARD = LVCMOS18;
        Subsignal("cke", Pins("D21"), IOStandard("SSTL18_II")),
        # NET "DDR2A_ODT" LOC = G22 | IOSTANDARD = LVCMOS18;
        Subsignal("odt", Pins("G22"), IOStandard("SSTL18_II")),
    ),

    ("ddram_b", 0,
        # NET "DDR2B_A[12]" LOC = D1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_A[11]" LOC = C1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_A[10]" LOC = G4 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_A[9]" LOC = E1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_A[8]" LOC = E3 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_A[7]" LOC = H6 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_A[6]" LOC = J4 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_A[5]" LOC = K3 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_A[4]" LOC = F3 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_A[3]" LOC = K6 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_A[2]" LOC = H5 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_A[1]" LOC = H1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_A[0]" LOC = H2 | IOSTANDARD = LVCMOS18;
        Subsignal("a", Pins("H2 H1 H5 K6 F3 K3 J4 H6 E3 E1 G4 C1 D1"), IOStandard("SSTL18_II")),
        # NET "DDR2B_BA[2]" LOC = F1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_BA[1]" LOC = G1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_BA[0]" LOC = G3 | IOSTANDARD = LVCMOS18;
        Subsignal("ba", Pins("G3 G1 F1"), IOStandard("SSTL18_II")),
        # NET "DDR2B_RAS_L" LOC = K5 | IOSTANDARD = LVCMOS18;
        Subsignal("ras_n", Pins("K5"), IOStandard("SSTL18_II")),
        # NET "DDR2B_CAS_L" LOC = K4 | IOSTANDARD = LVCMOS18;
        Subsignal("cas_n", Pins("K4"), IOStandard("SSTL18_II")),
        # NET "DDR2B_WE_L" LOC = F2 | IOSTANDARD = LVCMOS18;
        Subsignal("we_n", Pins("F2"), IOStandard("SSTL18_II")),
        # NET "DDR2B_UDM" LOC = M3 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_LDM" LOC = L4 | IOSTANDARD = LVCMOS18;
        Subsignal("dm", Pins("M3 L4"), IOStandard("SSTL18_II")),
        # NET "DDR2B_D[15]" LOC = V1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[14]" LOC = V2 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[13]" LOC = U1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[12]" LOC = U3 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[11]" LOC = R1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[10]" LOC = R3 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[9]" LOC = P1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[8]" LOC = P2 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[7]" LOC = K1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[6]" LOC = K2 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[5]" LOC = J1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[4]" LOC = J3 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[3]" LOC = M1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[2]" LOC = M2 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[1]" LOC = N1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_D[0]" LOC = N3 | IOSTANDARD = LVCMOS18;
        Subsignal("dq", Pins("N3 N1 M2 M1 J3 J1 K2 K1 P2 P1 R3 R1 U3 U1 V2 V1"), IOStandard("SSTL18_II")),
        # NET "DDR2B_UDQS_P" LOC = T2 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_LDQS_P" LOC = L3 | IOSTANDARD = LVCMOS18;
        Subsignal("dqs", Pins("T2 L3"), IOStandard("DIFF_SSTL18_II")),
        # NET "DDR2B_UDQS_N" LOC = T1 | IOSTANDARD = LVCMOS18;
        # NET "DDR2B_LDQS_N" LOC = L1 | IOSTANDARD = LVCMOS18;
        Subsignal("dqs_n", Pins("T1 L1"), IOStandard("DIFF_SSTL18_II")),
        # NET "DDR2B_CKE" LOC = D2 | IOSTANDARD = LVCMOS18;
        Subsignal("cke", Pins("D2"), IOStandard("SSTL18_II")),
        # NET "DDR2B_ODT" LOC = J6 | IOSTANDARD = LVCMOS18;
        Subsignal("odt", Pins("J6"), IOStandard("SSTL18_II")),
    ),
    ## onBoard SPI Flash
    ("spiflash", 0,
        Subsignal("cs_n", Pins("T5"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("Y21"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("AB20"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("AA20"), IOStandard("LVCMOS33"))
    ),

]

_hdmi_serial = (
    # NET "DDC2_SCK" LOC = AA21 | IOSTANDARD = LVCMOS33; # Display data channel clock
    # NET "DDC2_SDA" LOC = AB19 | IOSTANDARD = LVCMOS33; # Display data channel data
    "serial", 0,
    Subsignal("tx", Pins("AB19"), IOStandard("LVCMOS33")),
    Subsignal("rx", Pins("AA21"), IOStandard("LVCMOS33"))
)

_dvi_serial = (
    # NET "DDC1_SCK" LOC = C14 | IOSTANDARD = LVCMOS33;
    # NET "DDC1_SDA" LOC = C17 | IOSTANDARD = LVCMOS33;
    "serial", 0,
    Subsignal("tx", Pins("C14"), IOStandard("LVCMOS33")),
    Subsignal("rx", Pins("C17"), IOStandard("LVCMOS33"))
)

# Platform -----------------------------------------------------------------------------------------

class Platform(XilinxPlatform):
    name = "pano logic g2"
    default_clk_name = "clk125"
    default_clk_period = 1e9/125e6

    # actual .bit file size rounded up to next flash erase boundary
    gateware_size = 0x420000

    # Micron M25P128
    spiflash_model = "m25p128"
    spiflash_read_dummy_bits = 8
    spiflash_clock_div = 4
    spiflash_total_size = int((128/8)*1024*1024) # 128Mbit/16Mbyte
    spiflash_page_size = 256
    spiflash_sector_size = 0x20000

    def __init__(self, programmer="impact", device="xc6slx150", uart_connection="dvi"):
        if uart_connection == 'dvi':
            _io.append(_dvi_serial)
        elif uart_connection == 'hdmi':
            _io.append(_hdmi_serial)
        else:
            raise ValueError("Unsupported uart_connection \"{}\", available \"dvi\", \"hdmi\"".format(uart_connection))

        XilinxPlatform.__init__(self, device+"-2-fgg484", _io)
        self.programmer = programmer

        self.add_platform_command("""CONFIG VCCAUX="2.5";""")

    def do_finalize(self, fragment, *args, **kwargs):
        pass

    def create_programmer(self):
        if self.programmer == "impact":
            return iMPACT()
        else:
            raise ValueError("{} programmer is not supported".format(self.programmer))
