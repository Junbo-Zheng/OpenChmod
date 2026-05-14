# OpenChmod

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/Junbo-Zheng/OpenChmod/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Junbo-Zheng/OpenChmod/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/openchmod)](https://pypi.org/project/openchmod/)
[![Python](https://img.shields.io/pypi/pyversions/openchmod)](https://pypi.org/project/openchmod/)

Recursively chmod directories, files, and executables with sensible defaults. Automatically detects scripts by extension or shebang line and applies the correct permissions in a single pass.

## Overview

Managing file permissions across a project tree is tedious — directories need `0755`, regular files need `0644`, and scripts need `0755`. `pychmod` handles all three in one command, walking the tree recursively and applying the right mode to each entry.

> [!TIP]
> Files without an extension are inspected for a `#!` shebang line to determine if they should receive executable permissions.

## Installation

```bash
pip install openchmod
```

## Quick Start

```bash
# Apply sensible defaults to an entire project tree
pychmod /path/to/project

# Same thing using -p/--path
pychmod -p /path/to/project

# Custom permissions
pychmod /var/www --dirperms 0750 --fileperms 0640 --execperms 0750

# Exclude .git and __pycache__, show verbose output
pychmod /path/to/project -e .git -e __pycache__ --verbose

# Only process Python and shell scripts
pychmod /path/to/project -i "*.py" -i "*.sh"

# Preview changes without modifying anything
pychmod /path/to/project --dry-run

# CI mode: fail if any permissions are wrong
pychmod /path/to/project --check

# Follow symlinks
pychmod /path/to/project --symlinks
```

## CLI Reference

```
usage: pychmod [-h] [-p DIR] [--dirperms DIRPERMS] [-f FILEPERMS]
                 [-x EXECPERMS] [-s] [-v] [-e PATTERN] [-i PATTERN]
                 [-n] [--check]
                 [DIR]
```

| Flag | Description | Default |
|------|-------------|---------|
| `DIR` (positional) | Directory to traverse | — |
| `-p`, `--path` | Directory to traverse (alternative to positional) | — |
| `--dirperms` | Permissions for directories | `0755` |
| `-f`, `--fileperms` | Permissions for regular files | `0644` |
| `-x`, `--execperms` | Permissions for scripts/executables | `0755` |
| `-e`, `--exclude` | Glob pattern to exclude (repeatable) | — |
| `-i`, `--include` | Glob pattern to include (repeatable) | — |
| `-s`, `--symlinks` | Follow and process symlinks | `false` |
| `-v`, `--verbose` | Print each file being processed | `false` |
| `-n`, `--dry-run` | Show what would change without modifying anything | `false` |
| `--check` | Exit with error if any permissions are wrong (no changes) | `false` |

### Recognized Executable Extensions

`.bash` `.cgi` `.csh` `.exe` `.o` `.out` `.par` `.pl` `.py` `.pyc` `.pyo` `.rb` `.sh` `.so`

## Programmatic Usage

```python
from chmod.core import chmod_recursive

chmod_recursive(
    "/path/to/project",
    dirperms="0755",
    fileperms="0644",
    execperms="0755",
    verbose=True,
    follow_symlinks=False,
    exclude=[".git", "__pycache__", "node_modules"],
    include=None,
)

# Check mode — returns list of (path, current, expected) mismatches
mismatches = chmod_recursive("/path/to/project", check=True)
if mismatches:
    for path, current, expected in mismatches:
        print(f"{current} -> {expected}: {path}")
```

## Development

```bash
git clone https://github.com/Junbo-Zheng/OpenChmod.git
cd OpenChmod
pip install -e ".[dev]"
pytest
```

Run the formatter before committing:

```bash
black src tests
```
