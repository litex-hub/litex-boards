#!/usr/bin/env python3

#
# This file is part of LiteX-Boards.
#
# This file is Copyright (c) 2020 David Shah <dave@ds0.me>
# SPDX-License-Identifier: BSD-2-Clause

import re, sys

"""
This is a script to parse a Xilinx XDC file and produce a LiteX board Python file.

It has been tested on the Alveo U250 XDC file from
https://www.xilinx.com/member/forms/download/design-license.html?cid=41a21059-3945-404a-a349-35140c65291a&filename=xtp573-alveo-u250-xdc.zip

The "extras" section and name parsing rules will need modification to support other boards.
"""

extras = {
	("ddram", "dm"): [("IOStandard", "POD12_DCI")],
	("ddram", "dq"): [
		("IOStandard", "POD12_DCI"),
		("Misc", "PRE_EMPHASIS=RDRV_240"),
		("Misc", "EQUALIZATION=EQ_LEVEL2"),
	],
	("ddram", "dqs_p"): [
		("IOStandard", "DIFF_POD12"),
		("Misc", "PRE_EMPHASIS=RDRV_240"),
		("Misc", "EQUALIZATION=EQ_LEVEL2"),
	],
	("ddram", "dqs_n"): [
		("IOStandard", "DIFF_POD12"),
		("Misc", "PRE_EMPHASIS=RDRV_240"),
		("Misc", "EQUALIZATION=EQ_LEVEL2"),
	],
	("ddram", "clk_p"): [("IOStandard", "DIFF_SSTL12_DCI")],
	("ddram", "clk_n"): [("IOStandard", "DIFF_SSTL12_DCI")],
	("ddram", "reset_n"): [("IOStandard", "LVCMOS12")],
	("ddram", "*"): [("IOStandard", "SSTL12_DCI")],
	("ddram", ): [("Misc", "SLEW=FAST")],
	("clk300", "*"): [("IOStandard", "DIFF_SSTL12")],
	("cpu_reset", "*"): [("IOStandard", "LVCMOS12")],
	("ddr4_reset_gate", "*"): [("IOStandard", "LVCMOS12")],
	("gpio_msp", "*"): [("IOStandard", "LVCMOS12")],
	("user_led", "*"): [("IOStandard", "LVCMOS12")],
	("dip_sw", "*"): [("IOStandard", "LVCMOS12")],
	("set_w", "*"): [("IOStandard", "LVCMOS12")],
	("pcie_x16", "rst_n"): [("IOStandard", "LVCMOS12")],
	("serial", "*"): [("IOStandard", "LVCMOS12")],
	("qsfp28", "modskll_ls"): [("IOStandard", "LVCMOS12")],
	("qsfp28", "resetl_ls"): [("IOStandard", "LVCMOS12")],
	("qsfp28", "intl_ls"): [("IOStandard", "LVCMOS12")],
	("qsfp28", "lpmode_ls"): [("IOStandard", "LVCMOS12")],
	("qsfp28", "refclk_reset"): [("IOStandard", "LVCMOS12")],
	("qsfp28", "fs0"): [("IOStandard", "LVCMOS12")],
	("qsfp28", "fs1"): [("IOStandard", "LVCMOS12")],
	("i2c", "*"): [("IOStandard", "LVCMOS12")],
	("i2c_main_reset_n", "*"): [("IOStandard", "LVCMOS12")],
	("serial_msp", "*"): [("IOStandard", "LVCMOS12")],
	("user_si570_clock", "*"): [("IOStandard", "DIFF_SSTL12")],
}

groups = {}


ddr4_re = re.compile(r'DDR4_C(\d)_(.*)')

simple_ports = {
	"CPU_RESET_FPGA": ("cpu_reset", 0),
	"DDR4_RESET_GATE": ("ddr4_reset_gate", 0),
	"GPIO_MSP0": ("gpio_msp", 0),
	"GPIO_MSP1": ("gpio_msp", 1),
	"GPIO_MSP2": ("gpio_msp", 2),
	"GPIO_MSP3": ("gpio_msp", 3),
	"STATUS_LED0_FPGA": ("user_led", 0),
	"STATUS_LED1_FPGA": ("user_led", 1),
	"STATUS_LED2_FPGA": ("user_led", 2),
	"SW_DP0": ("dip_sw", 0),
	"SW_DP1": ("dip_sw", 1),
	"SW_DP2": ("dip_sw", 2),
	"SW_DP3": ("dip_sw", 3),
	"SW_SET1_FPGA": ("set_sw", 0),
	"I2C_MAIN_RESET_B_LS": ("i2c_main_reset_n", 0),
}

def permute_dqs(i):
	# Huh?
	if i >= 9:
		return (i - 9) * 2 + 1
	else:
		return i * 2

def parse_port(port):
	dm = ddr4_re.match(port)
	if dm:
		res = ("ddram", int(dm.group(1)))
		x = dm.group(2)
		if x.startswith("ADR"):
			i = int(x[3:])
			if i == 17:
				return None # not used on included DIMM
			if i == 16:
				s = ("ras_n", )
			elif i == 15:
				s = ("cas_n", )
			elif i == 14:
				s = ("we_n", )
			else:
				s = ("a", i)
		elif x.startswith("BA"):
			s = ("ba", int(x[2:]))
		elif x.startswith("BG"):
			s = ("bg", int(x[2:]))
		elif x.startswith("CK_T"):
			if int(x[4:]) > 0:
				return None # not used on included DIMM
			s = ("clk_p", int(x[4:]))
		elif x.startswith("CK_C"):
			if int(x[4:]) > 0:
				return None # not used on included DIMM
			s = ("clk_n", int(x[4:]))
		elif x.startswith("CKE"):
			if int(x[3:]) > 0:
				return None # not used on included DIMM
			s = ("cke", int(x[3:]))
		elif x.startswith("CS_B"):
			if int(x[4:]) > 0:
				return None # not used on included DIMM
			s = ("cs_n", int(x[4:]))
		elif x.startswith("ODT"):
			if int(x[3:]) > 0:
				return None # not used on included DIMM
			s = ("odt", int(x[3:]))
		elif x in ("ACT_B", "ALERT_B", "EVENT_B", "PAR", "RESET_N"):
			if x == "ALERT_B" or x == "PAR" or x == "EVENT_B":
				return None # not used on included DIMM
			x = x.replace("_B", "_N")
			s = (x.lower(), )
		elif x.startswith("DQS_T"):
			i = permute_dqs(int(x[5:]))
			if i >= 16:
				return None
			s = ("dqs_p", int(i))
		elif x.startswith("DQS_C"):
			i = permute_dqs(int(x[5:]))
			if i >= 16:
				return None
			s = ("dqs_n", int(i))
		elif x.startswith("DQ"):
			if int(x[2:]) >= 64:
				return None
			s = ("dq", int(x[2:]))
		else:
			assert False, port
		return (res, s)
	elif port in simple_ports:
		return (simple_ports[port], (simple_ports[port][0], ))
	elif port.startswith("SYSCLK") and "_300_" in port:
		return (("clk300", int(port[6])), (port[-1].lower(), ))
	elif port.startswith("PEX_"):
		res = ("pcie_x16", 0)
		if port[4:6] == "TX":
			s = ("tx_" + port[-1].lower(), int(port[6:port.rfind('_')]))
		elif port[4:6] == "RX":
			s = ("rx_" + port[-1].lower(), int(port[6:port.rfind('_')]))
		elif port[4:10] == "REFCLK":
			s = ("clk_" + port[-1].lower(), )
		else:
			assert False, port
		return (res, s)
	elif port == "PCIE_PERST_LS":
		return (("pcie_x16", 0), ("rst_n", ))
	elif port.startswith("USB_UART_"):
		# This is from FTDI perspective, we want FPGA perspective
		u = port[-2:].lower()
		return (("serial", 0), ("tx" if u == "rx" else "rx", ))
	elif port.startswith("MGT_SI570_CLOCK"):
		return (("mgt_si570_clock", int(port[15])), (port[-1].lower(), ))
	elif port.startswith("USER_SI570_CLOCK"):
		return (("user_si570_clock", 0), (port[-1].lower(), ))
	elif port.startswith("QSFP"):
		res = ("qsfp28", int(port[4]))
		if port[6:8] == "TX":
			s = ("tx" + port[-1].lower(), int(port[8])-1)
		elif port[6:8] == "RX":
			s = ("rx" + port[-1].lower(), int(port[8])-1)
		elif port[6:11] == "CLOCK":
			s = ("clk_" + port[-1].lower(), )
		elif port.endswith("REFCLK_RESET") or "_FS" in port:
			s = (port[6:].lower(), )
		elif port.endswith("_LS"):
			s = (port.split("_")[1].lower(), )
		else:
			assert False, port
		return (res, s)
	elif port.startswith("I2C_FPGA_"):
		return (("i2c", 0), (port.split("_")[2].lower(), ))
	elif port.endswith("_MSP"):
		return (("serial_msp", 0), (port.split("_")[1].lower()[:-1], ))
	elif port == "No" or port.startswith("VR") or port.startswith("N3") or "SYSMON" in port or port.startswith("TEST"):
		pass
	else:
		assert False, port
	return None

with open(sys.argv[1], "r") as xf:
	for line in xf:
		if "PACKAGE_PIN" not in line:
			continue
		sl = [x.strip() for x in re.split(r'\s|\[', line.strip(), )]
		sl = [x for x in sl if x != ""]
		pin = sl[sl.index("PACKAGE_PIN") + 1]
		port = sl[sl.index("get_ports") + 1]
		rs = parse_port(port)
		if rs is None:
			continue
		res, sig = rs

		if sig is None:
			groups[res] = pin
		else:
			if res not in groups:
				groups[res] = {}
		if len(sig) == 2:
			if sig[0] not in groups[res]:
				groups[res][sig[0]] = {}
			groups[res][sig[0]][sig[1]] = pin
		else:
			groups[res][sig[0]] = {0: pin}

def format_extras(items, force_newline = False, indent="            ", lcomma=","):
	extra = "{} \n{}".format(lcomma, indent) if force_newline else "{} ".format(lcomma)
	extra += (", \n{}".format(indent)).join(['{}("{}")'.format(i[0], i[1]) for i in items])
	return extra
print("_io = [")
for res, sigs in sorted(groups.items(), key=lambda x: x[0]):
	res_name = res[0]
	res_index = res[1]
	if res_name == "ddram" and res_index > 0:
		res_name = "ddram_ch{}".format(res_index + 1)
		res_index = 0
	print('    ("{}", {}, '.format(res_name, res_index), end='\n' if len(sigs) > 1 else '')
	for sig, pins in sorted(sigs.items(), key=lambda x: x[0]):
		max_idx = max(pins.keys())
		if len(pins) > 8:
			p = ""
			for j in range((len(pins) + 7) // 8):
				p += '\n            "{}"{}'.format(" ".join([pins[i] for i in range(j * 8,
					min((j + 1) * 8, max_idx+1))]), "," if j < ((len(pins) + 7) // 8 - 1) else "")
		else:
			p = '"{}"'.format(" ".join([pins[i] for i in range(max_idx+1)]))
		extra = ""
		if (res[0], sig) in extras:
			extra = format_extras(extras[res[0], sig], len(pins) > 8)
		elif (res[0], "*") in extras:
			extra = format_extras(extras[res[0], "*"], len(pins) > 8)
		if len(sigs) == 1:
			print('Pins({}){}'.format(p, extra), end='')
		else:
			print('        Subsignal("{}", Pins({}){}),'.format(sig, p, extra))
	if (res[0], ) in extras:
		print(format_extras(extras[res[0], ], False, "        ", "       "))
	print('    ),' if len(sigs) > 1 else '),')
print("]")
