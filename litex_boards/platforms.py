import sys
import importlib

class Platforms:
    def __getattr__(self, name):
        if name == "__path__":
            return []
        for support in ["official", "partner", "community"]:
            try:
                return importlib.import_module("litex_boards." + support + ".platforms." + name)
            except:
                pass
        raise ModuleNotFoundError

sys.modules[__name__] = Platforms()
