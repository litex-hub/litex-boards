#!/usr/bin/env python3

import sys
import textwrap

# Very basic bitstream to SVF converter, tested with the ULX3S WiFi interface

flash_page_size = 256
erase_block_size = 64*1024


def bitreverse(x):
    y = 0
    for i in range(8):
        if (x >> (7 - i)) & 1 == 1:
            y |= (1 << i)
    return y

with open(sys.argv[1], 'rb') as bitf:
    bs = bitf.read()
    # Autodetect IDCODE from bitstream
    idcode_cmd = bytes([0xE2, 0x00, 0x00, 0x00])
    idcode = None
    for i in range(len(bs) - 4):
        if bs[i:i+4] == idcode_cmd:
            idcode = bs[i+4] << 24
            idcode |= bs[i+5] << 16
            idcode |= bs[i+6] << 8
            idcode |= bs[i+7]
            break
    if idcode is None:
        print("Failed to find IDCODE in bitstream, check bitstream is valid")
        sys.exit(1)
    bitf.seek(0)

    address = 0
    last_page = -1

    with open(sys.argv[2], 'w') as svf:
        print("""
STATE RESET;
HDR	0;
HIR	0;
TDR	0;
TIR	0;
ENDDR	DRPAUSE;
ENDIR	IRPAUSE;
STATE	IDLE;
        """, file=svf)
        print("""
SIR	8	TDI  (E0);
SDR	32	TDI  (00000000)
        TDO  ({:08X})
        MASK (FFFFFFFF);
        """.format(idcode), file=svf)
        print("""
SIR	8	TDI  (1C);
SDR	510	TDI  (3FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
             FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF);

// Enter Programming mode
SIR	8	TDI  (C6);
SDR	8	TDI  (00);
RUNTEST	IDLE	2 TCK	1.00E-02 SEC;

// Erase
SIR	8	TDI  (0E);
SDR	8	TDI  (01);
RUNTEST IDLE 2 TCK 2.0E-1 SEC;

// Read STATUS
SIR	8	TDI  (3C);
SDR	32	TDI  (00000000)
        TDO  (00000000)
        MASK (0000B000);

// Exit Programming mode
SIR	8	TDI  (26);
RUNTEST	IDLE	2 TCK	1.00E-02 SEC;

// BYPASS
SIR 8 TDI (FF);
STATE IDLE;
RUNTEST 32 TCK;
RUNTEST 2.00E-2 SEC;

// Enter SPI mode

SIR 8 TDI (3A);
SDR 16 TDI (68FE);
STATE IDLE;
RUNTEST 32 TCK;
RUNTEST 2.00E-2 SEC;

// SPI IO
SDR 8 TDI (D5);

RUNTEST 2.00E-0 SEC;

// CONFIRM FLASH ID
SDR 32   TDI  (000000F9)
         TDO  (68FFFFFF)
         MASK (FF000000);

SDR 8    TDI(60);
SDR 16   TDI(0080);
RUNTEST 1.00E-0 SEC;


        """, file=svf)
        while True:
            if((address // 0x10000) != last_page):
                last_page = (address // 0x10000)
                print("""SDR	8	TDI  (60);
                """, file=svf)
                address_flipped = [bitreverse(x) for x in [0xd8,int(address // 0x10000),0x00,0x00]]
                hex_address= ["{:02X}".format(x) for x in reversed(address_flipped)]
                print("\n".join(textwrap.wrap("SDR {} TDI ({});".format(8*len(hex_address), "".join(hex_address)), 100)), file=svf)
                print("""RUNTEST	3.00 SEC;
                """, file=svf)

            chunk = bitf.read(flash_page_size)
            if not chunk:
                break
            # Convert chunk to bit-reversed hex
            br_chunk = [bitreverse(x) for x in bytes([0x02, int(address / 0x10000 % 0x100),int(address / 0x100 % 0x100),int(address % 0x100)]) + chunk]
            address += len(chunk)
            hex_chunk = ["{:02X}".format(x) for x in reversed(br_chunk)]
            print("""
SDR	8	TDI  (60);
                """, file=svf)
            print("\n".join(textwrap.wrap("SDR {} TDI ({});".format(8*len(br_chunk), "".join(hex_chunk)), 100)), file=svf)
            print("""
RUNTEST	2.50E-2 SEC;
                """, file=svf)

        print("""
// BYPASS
SIR 8 TDI (FF);

//REFRESH
SIR 8 TDI(79);
SDR 24 TDI(000000);

STATE IDLE;
RUNTEST 32 TCK;
RUNTEST 2.00E-2 SEC;
STATE RESET;
        """, file=svf)
