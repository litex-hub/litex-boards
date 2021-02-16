from migen import *
from litex.soc.interconnect import axi, csr_bus, csr

SPI = [
    ("SCLK", 1, DIR_M_TO_S),
    ("DIN", 1, DIR_M_TO_S),
    ("nSYNC", 1, DIR_M_TO_S)
]

MUX = [
    ("nE", 1, DIR_M_TO_S),
    ("S", 3, DIR_M_TO_S),
]

class OffsetDac(Module, csr.AutoCSR):
    def __init__(self, offsetdac_pads, offsetmux_pads):
        self._status = csr.CSRStatus(32, name='status', reset=0x0ffdac)
        self.spi = Record(SPI)
        self.mux = Record(MUX)

        self.comb += self.spi.connect(offsetdac_pads)
        self.comb += self.mux.connect(offsetmux_pads)

        self._control = csr.CSRStorage(32, name='control') # DAC PD control
        self._clkdiv = csr.CSRStorage(32, name='clkdiv', reset=326) # roughly matches original timing
        self._enable = csr.CSRStorage(32, name='enable', reset=1)

        self._v0 = csr.CSRStorage(32, name='v0', reset = 0x8000) # unused
        self._v1 = csr.CSRStorage(32, name='v1', reset = 0x8000) # unused
        self._v2 = csr.CSRStorage(32, name='v2', reset = 0x8000) # unused
        self._v3 = csr.CSRStorage(32, name='v3', reset = 0x8000) # unused
        self._v4 = csr.CSRStorage(32, name='v4', reset = 0x8000) # CH1 offset
        self._v5 = csr.CSRStorage(32, name='v5', reset = 0x8000) # CH2 offset
        self._v6 = csr.CSRStorage(32, name='v6', reset = 0x8000) # CH3 offset
        self._v7 = csr.CSRStorage(32, name='v7', reset = 0x8000) # CH4 offset

        # data is transferred on falling edge of SCLK while nSYNC=0
        # data is MSB-first
        # on 24th bit, data is updated.
        # | 6 bits | 2 bits  | 16 bits |
        # | XXXXXX | PD1,PD0 | data    |
        # PD: 0 - normal
        #     1 - 1k to GND
        #     2 - 100k to GND
        #     3 - Hi-Z

        # MUX sequence:
        # A single DAC is used and connected to a 74HC4051 (8-channel
        # analog multiplexer/demultiplexer)
        # The DAC output is connected to the MUX "Z" pin
        # Z is connnected to the output selected by S if
        # /E is low, otherwise left unconnected.

        # TIMING:
        # /E high pulse is ~8.1us
        # SPI clock rate: 250kHz
        # repetition rate: 9.8kHz => 1/25.5 of SPI clock rate
        #
        # So DAC SPI clock is constantly running, /E is deactivated
        # during the DAC transition for 2 cycles

        # wavedrom file:
        """{signal: [
    ["DAC",
     {name: 'SCLK',  wave: 'n............................'},
     {name: 'DIN',   wave: '2.0xxxxxx2.3...............0x', data: ["Value-1", "PD", "Value"]},
     {name: 'nSYNC', wave: '0.10.......................10'},
     {name: 'OUT',   wave: 'z.1........................z.'},
    ],

    ["MUX",
     {name: 'nE',    wave: '01.0......................1.0'},
     {name: 'S',     wave: '2.2........................3.', data: ["S-2", "S-1", "S"]},
    ],
]}
        """


        # CLK divider

        clkdiv = Signal(16)
        self.sync += [
            If(clkdiv == self._clkdiv.storage[:16],
                clkdiv.eq(0)
            ).Else(
                clkdiv.eq(clkdiv + 1),
            )
        ]

        clk = Signal()

        clk_falling = Signal()

        self.sync += [
            clk_falling.eq(0),
            If(clkdiv == 0,
                clk.eq(~clk),
                clk_falling.eq(~clk)
            ),
        ]

        # FSM

        self.submodules.fsm = FSM(reset_state='start')

        dac_data = Array([self._v0.storage, self._v1.storage, self._v2.storage, self._v3.storage,
                          self._v4.storage, self._v5.storage, self._v6.storage, self._v7.storage])

        current_bit = Signal(max=24)
        current_channel = Signal(max=8)

        pd = Signal(2)
        pd.eq(self._control.storage[:2])

        current_dac_word = Signal(24)
        self.comb += [
            current_dac_word[0:16].eq(dac_data[current_channel][:16]),
            current_dac_word[16:18].eq(pd),
            current_dac_word[18:24].eq(0)
        ]

        self.fsm.act('start',
            If(clk_falling,
                NextValue(current_bit, 0),
                NextValue(self.mux.nE, 1),
                NextValue(self.spi.nSYNC, 1),
                NextValue(self.spi.DIN, 0),
                If(self._enable.storage[0],
                    NextState('transfer'),
                ).Else(
                    NextValue(current_channel, 0),
                ),
            )
        )

        self.fsm.act('transfer',
            If(clk_falling,
                NextValue(self.spi.nSYNC, 0),
                NextValue(self.mux.nE, 0),
                NextValue(self.spi.DIN, Array(current_dac_word)[23 - current_bit]),
                If(current_bit == 23,
                    NextValue(self.mux.nE, 1),
                    NextState('start'),
                    NextValue(self.mux.S, current_channel),
                    NextValue(current_channel, current_channel + 1)
                ).Else(NextValue(current_bit, current_bit + 1))
            )
        )

        # output SPI CLK (if enabled)
        self.sync += self.spi.SCLK.eq(clk & self._enable.storage[0])


from litex.gen.fhdl import verilog
from litex.gen.sim import run_simulation

if __name__ == '__main__':
    def testbench_offsetdac(dut):
        for _ in range(25 * 8 * 1000):
            yield

    print("Running simulation...")
    t = OffsetDac()
    run_simulation(t, testbench_offsetdac(t), vcd_name='offsetdac.vcd')
