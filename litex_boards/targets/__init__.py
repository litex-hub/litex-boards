import os
import sys
import glob
import importlib

# Boards Vendors.

vendors = [
    "1bitsquared",
    "colorlight",
    "digilent",
    "enclustra",
    "gsd",
    "hackaday"
    "kosagi",
    "lattice",
    "lambdaconcept",
    "linsn",
    "numato",
    "qmtech",
    "radiona",
    "rhsresearchllc",
    "saanlima",
    "scarabhardware",
    "siglent",
    "sqrl",
    "terasic",
    "trenz",
    "xilinx",
]

# Get all targets.
targets_dir = os.path.dirname(os.path.realpath(__file__))
targets     = glob.glob(f"{targets_dir}/*.py")

# For each target:
for target in targets:
    target = os.path.basename(target)
    target = target.replace(".py", "")
    # Verify if a Vendor prefix is present in target name, if so create the short import to
    # allow the target to be imported with the full name or short name ex:
    # from litex_boards.targets import digilent_arty or
    # from litex_boards.targets import arty
    if target.split("_")[0] in vendors:
        short_target = target[len(target.split("_")[0])+1:]
        t = importlib.import_module(f"litex_boards.targets.{target}")
        vars()[short_target] = t
        sys.modules[f"litex_boards.targets.{short_target}"] = t
