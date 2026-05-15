# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Junbo Zheng

"""pychmod: Recursively chmod directories, files, and executables."""

from chmod.core import (
    EXEC_EXTENSIONS,
    chmod_recursive,
    classify_file,
    is_script,
)

__version__ = "0.0.2"

__all__ = [
    "EXEC_EXTENSIONS",
    "chmod_recursive",
    "classify_file",
    "is_script",
    "__version__",
]
