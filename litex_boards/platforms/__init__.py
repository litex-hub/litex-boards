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

# Get all platforms.
platforms_dir = os.path.dirname(os.path.realpath(__file__))
platforms     = glob.glob(f"{platforms_dir}/*.py")

# For each platform:
for platform in platforms:
    platform = os.path.basename(platform)
    platform = platform.replace(".py", "")
    # Verify if a Vendor prefix is present in platform name, if so create the short import to
    # allow the platform to be imported with the full name or short name ex:
    # from litex_boards.platforms import digilent_arty or
    # from litex_boards.platforms import arty
    if platform.split("_")[0] in vendors:
        short_platform = platform[len(platform.split("_")[0])+1:]
        p = importlib.import_module(f"litex_boards.platforms.{platform}")
        vars()[short_platform] = p
        sys.modules[f"litex_boards.platforms.{short_platform}"] = p
