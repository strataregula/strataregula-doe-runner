"""
Compatibility layer for sr_doe_runner (deprecated)

This module provides backward compatibility by forwarding imports
to the new strataregula_doe_runner package.

WARNING: This import path is deprecated. Please use:
    from strataregula_doe_runner import ...
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "The 'sr_doe_runner' package name is deprecated. "
    "Please use 'strataregula_doe_runner' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Forward all imports to new package
from strataregula_doe_runner import *  # noqa
from strataregula_doe_runner import __version__, __author__, __email__