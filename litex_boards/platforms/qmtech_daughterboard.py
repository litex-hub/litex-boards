from litex.build.generic_platform import Subsignal, Pins, IOStandard, Misc

class QMTechDaughterboard:
    """
        the QMTech daughterboard contains standard peripherals
        and can be used with a number of different FPGA core boards
        source: https://www.aliexpress.com/item/1005001829520314.html
    """

    def __init__(self, io_standard) -> None:
        """
             because the board can be used with FPGAs core boards from
             different vendors, the constructor needs the vendor specific IOStandard
        """
        self.io = [
            ("serial", 0,
                Subsignal("rx", Pins("J2:16")),
                Subsignal("tx", Pins("J2:15")),
                io_standard
            ),

            ("user_led", 0, Pins("J2:40"), io_standard),
            ("user_led", 1, Pins("J2:39"), io_standard),
            ("user_led", 2, Pins("J2:38"), io_standard),
            ("user_led", 3, Pins("J2:37"), io_standard),
            ("user_led", 4, Pins("J2:36"), io_standard),

            ("user_btn", 0, Pins("J3:7"),  io_standard),
            ("user_btn", 1, Pins("J2:44"), io_standard),
            ("user_btn", 2, Pins("J2:43"), io_standard),
            ("user_btn", 3, Pins("J2:42"), io_standard),
            ("user_btn", 4, Pins("J2:41"), io_standard),

            # GMII Ethernet
            ("eth_clocks", 0,
                Subsignal("tx",  Pins("J3:22")),
                Subsignal("gtx", Pins("J3:29")),
                Subsignal("rx",  Pins("J3:37")),
                io_standard
            ),
            ("eth", 0,
                # rst is hardwired on the board
                #Subsignal("rst_n",   Pins("-")),
                Subsignal("int_n",   Pins("J3:26")),
                Subsignal("mdio",    Pins("J3:15")),
                Subsignal("mdc",     Pins("J3:16")),
                Subsignal("rx_dv",   Pins("J3:42")),
                Subsignal("rx_er",   Pins("J3:32")),
                Subsignal("rx_data", Pins("J3:41 J3:40 J3:39 J3:38 J3:36 J3:35 J3:34 J3:33")),
                Subsignal("tx_en",   Pins("J3:28")),
                Subsignal("tx_er",   Pins("J3:17")),
                Subsignal("tx_data", Pins("J3:27 J3:25 J3:24 J3:23 J3:21 J3:20 J3:19 J3:18")),
                Subsignal("col",     Pins("J3:31")),
                Subsignal("crs",     Pins("J3:30")),
                io_standard
            ),

            # Seven Segment
            ("seven_seg_ctl", 0, Pins("J2:33"), io_standard),
            ("seven_seg_ctl", 1, Pins("J2:27"), io_standard),
            ("seven_seg_ctl", 2, Pins("J2:35"), io_standard),
            ("seven_seg", 0, Pins("J2:31 J2:26 J2:28 J2:32 J2:34 J2:29 J2:25 J2:30"), io_standard),

            # VGA
            ("vga", 0,
                Subsignal("hsync_n", Pins("J3:44")),
                Subsignal("vsync_n", Pins("J3:43")),
                Subsignal("r", Pins("J3:57 J3:56 J3:59 J3:58 J3:60")),
                Subsignal("g", Pins("J3:51 J3:50 J3:53 J3:52 J3:54 J3:55")),
                Subsignal("b", Pins("J3:46 J3:45 J3:48 J3:47 J3:49")),
                io_standard
            ),

            # PullUp resistors are on the board, so we don't need them in the FPGA
            ("sdcard", 0,
                Subsignal("data", Pins("J3:10 J3:9 J3:14 J3:13")),
                Subsignal("cmd",  Pins("J3:12")),
                Subsignal("clk",  Pins("J3:11")),
                Subsignal("cd",   Pins("J3:8")),
                io_standard,
            ),
        ]

    connectors = [
        ("pmoda", "J2:17 J2:19 J2:21 J2:23 J2:18 J2:20 J2:22 J2:24"), #J10
        ("pmodb", "J2:7  J2:9  J2:11 J2:13 J2:8  J2:10 J2:12 J2:14"), #J11
        ("J1", {
             3: "J2:60",
             4: "J2:59",
             5: "J2:58",
             6: "J2:57",
             7: "J2:56",
             8: "J2:55",
             9: "J2:54",
            10: "J2:53",
            11: "J2:52",
            12: "J2:51",
            13: "J2:50",
            14: "J2:49",
            15: "J2:48",
            16: "J2:47",
            17: "J2:46",
            18: "J2:45"
        }),
    ]