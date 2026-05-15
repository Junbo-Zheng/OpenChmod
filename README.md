# OpenChmod

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/Junbo-Zheng/OpenChmod/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Junbo-Zheng/OpenChmod/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pychmod)](https://pypi.org/project/pychmod/)
[![Python](https://img.shields.io/pypi/pyversions/pychmod)](https://pypi.org/project/pychmod/)

Recursively fix file permissions across a project tree in one command.

`pychmod` walks a directory and applies sensible defaults — `0755` for directories, `0644` for regular files, `0755` for scripts and executables — so you don't have to chain `find ... -exec chmod ...` invocations or remember which mode goes where. Scripts are detected by extension *or* by `#!` shebang, even when there is no extension at all.

## Features

- One pass, three modes: separate permissions for directories, files, and executables.
- Smart script detection: known extensions (`.sh`, `.py`, `.pl`, `.rb`, ...) plus shebang sniffing for extensionless files.
- `--dry-run` to preview changes and `--check` to fail CI when permissions drift.
- Glob-based `--include` / `--exclude` filters, repeatable.
- Optional symlink following, off by default.
- Zero runtime dependencies. Pure Python, 3.10+.

## Why not just `find -exec chmod`?

The classic recipe needs three passes and assumes you know which files are scripts:

```bash
find . -type d -exec chmod 0755 {} +
find . -type f -exec chmod 0644 {} +
find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod 0755 {} +
```

`pychmod` does the same in one walk, classifies scripts by shebang as well as extension (so an extensionless `./build` with `#!/usr/bin/env bash` gets the right mode), and adds `--dry-run` plus `--check` so you can preview changes or fail CI on drift — none of which `find` gives you for free.

## Installation

```bash
pip install pychmod
```

## Quick start

Apply defaults (`dirs=0755`, `files=0644`, `exec=0755`) to a project tree:

```bash
pychmod /path/to/project
```

Preview without writing:

```bash
pychmod /path/to/project --dry-run
```

Verify in CI — exits non-zero if anything drifts:

```bash
pychmod /path/to/project --check
```

## Usage

```text
pychmod [-h] [-p DIR] [--dirperms DIRPERMS] [-f FILEPERMS] [-x EXECPERMS]
        [-e PATTERN] [-i PATTERN] [--files-only] [-s] [-v] [-n] [--check]
        [DIR]
```

| Option | Description | Default |
|---|---|---|
| `DIR` / `-p DIR` | Directory to traverse (positional or flag). | — |
| `--dirperms` | Octal mode for directories. | `0755` |
| `-f`, `--fileperms` | Octal mode for regular files. | `0644` |
| `-x`, `--execperms` | Octal mode for scripts/executables. | `0755` |
| `-e`, `--exclude` | Glob pattern to exclude (repeatable). | — |
| `-i`, `--include` | Glob pattern to include, files only (repeatable). | — |
| `--files-only` | Skip directory permissions; only chmod files. | `false` |
| `-s`, `--symlinks` | Follow symlinks. | `false` |
| `-v`, `--verbose` | Print every entry processed. | `false` |
| `-n`, `--dry-run` | Show changes without applying them. | `false` |
| `--check` | Exit non-zero if any permissions are wrong. No changes made. | `false` |

> [!TIP]
> Files without an extension are inspected for a `#!` shebang line to decide whether they should be executable.

## Examples

Tighten down a webroot:

```bash
pychmod /var/www --dirperms 0750 --fileperms 0640 --execperms 0750
```

Skip VCS and cache directories:

```bash
pychmod /path/to/project -e .git -e __pycache__ --verbose
```

Only retouch Python and shell scripts:

```bash
pychmod /path/to/project -i "*.py" -i "*.sh"
```

Only fix C/C++ source files, leave directories untouched:

```bash
pychmod /path/to/project -i "*.c" -i "*.h" -i "*.cpp" --files-only
```

Follow symlinks (use with care):

```bash
pychmod /path/to/project --symlinks
```

## Use as a pre-commit / CI gate

Add a `--check` step to your pipeline so a stray `chmod 777` never lands on `main`:

```yaml
- name: Verify file permissions
  run: pychmod . --check -e .git
```

## Development

```bash
git clone https://github.com/Junbo-Zheng/OpenChmod.git
cd OpenChmod
pip install -e ".[dev]"
pytest
```
