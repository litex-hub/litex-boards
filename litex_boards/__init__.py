import os
import sys
import glob
import importlib

# Boards Vendors.

vendors = [
    "1bitsquared",
    "alinx",
    "antmicro",
    "arduino",
    "berkeleylab",
    "colorlight",
    "decklink",
    "digilent",
    "efinix",
    "enclustra",
    "gsd",
    "fairwaves",
    "hackaday",
    "kosagi",
    "krtkl",
    "lattice",
    "lambdaconcept",
    "linsn",
    "muselab",
    "myminieye",
    "numato",
    "qmtech",
    "qwertyembedded",
    "radiona",
    "rhsresearchllc",
    "rz",
    "saanlima",
    "scarabhardware",
    "siglent",
    "sipeed",
    "seeedstudio",
    "sqrl",
    "terasic",
    "trenz",
    "tul",
    "xilinx",
]

# Get all platforms/targets.
litex_boards_dir = os.path.dirname(os.path.realpath(__file__))
platforms        = glob.glob(f"{litex_boards_dir}/platforms/*.py")
targets          = glob.glob(f"{litex_boards_dir}/targets/*.py")

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

# For each target:
for target in targets:
    target = os.path.basename(target)
    target = target.replace(".py", "")
    # Verify if a Vendor prefix is present in target name, if so create the short import to
    # allow the target to be imported with the full name or short name ex:
    # from litex_boards.targets import digilent_arty or
    # from litex_boards.targets import arty
    if target.split("_")[0] in vendors:
        try:
            short_target = target[len(target.split("_")[0])+1:]
            t = importlib.import_module(f"litex_boards.targets.{target}")
            vars()[short_target] = t
            sys.modules[f"litex_boards.targets.{short_target}"] = t
        except ModuleNotFoundError:
            # Not all dependencies for this target is satisfied. Skip.
            pass
