#
# This file is part of LiteX-Boards.
#
# SPDX-License-Identifier: BSD-2-Clause

import warnings

# Deprecation --------------------------------------------------------------------------------------

# Deprecated APIs are kept up to this LiteX-Boards release and removed after it.
DEPRECATION_RELEASE = "2026.12"

def warn_deprecated(old, new, stacklevel=3):
    """Emit a FutureWarning (visible by default) for a deprecated API.

    stacklevel defaults to 3 to point to the caller of the function calling warn_deprecated.
    """
    warnings.warn(f"{old} is deprecated and will be removed after the LiteX-Boards {DEPRECATION_RELEASE} "
        f"release, use {new} instead.", FutureWarning, stacklevel=stacklevel)

def warn_deprecated_arg(arg, replacement):
    """Emit a FutureWarning for a deprecated target command line argument (still functional)."""
    warn_deprecated(f"Argument {arg}", replacement)

# Deprecated Pmod Helpers --------------------------------------------------------------------------

def deprecated_pmod_helpers(module, helpers):
    """Return a module __getattr__ (PEP 562) providing deprecated Pmod helpers.

    helpers: {name: (replacement, value)}. Accessing (or importing) module.name emits a FutureWarning
    (visible by default) pointing to the litex_boards.extensions.pmod replacement and returns value.
    """
    def __getattr__(name):
        if name in helpers:
            replacement, value = helpers[name]
            warn_deprecated(f"{module}.{name}", f"{replacement} (from litex_boards.extensions.pmod)")
            return value
        raise AttributeError(f"module {module!r} has no attribute {name!r}")
    return __getattr__
