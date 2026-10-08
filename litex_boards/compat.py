#
# This file is part of LiteX-Boards.
#
# SPDX-License-Identifier: BSD-2-Clause

import warnings

# Deprecated Pmod Helpers --------------------------------------------------------------------------

def deprecated_pmod_helpers(module, helpers):
    """Return a module __getattr__ (PEP 562) providing deprecated Pmod helpers.

    helpers: {name: (replacement, value)}. Accessing (or importing) module.name emits a FutureWarning
    (visible by default) pointing to the litex_boards.extensions.pmod replacement and returns value.
    """
    def __getattr__(name):
        if name in helpers:
            replacement, value = helpers[name]
            warnings.warn(f"{module}.{name} is deprecated and will be removed, use litex_boards.extensions.pmod "
                f"instead: {replacement}.", FutureWarning, stacklevel=2)
            return value
        raise AttributeError(f"module {module!r} has no attribute {name!r}")
    return __getattr__
