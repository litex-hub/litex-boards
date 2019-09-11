import sys
import importlib

class Targets:
    def __getattr__(self, name):
        if name == "__path__":
            return []
        for support in ["official", "partner", "community"]:
            try:
                return importlib.import_module("litex_boards." + support + ".targets." + name)
            except:
                pass
        raise ModuleNotFoundError

sys.modules[__name__] = Targets()
