# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Junbo Zheng

"""Core logic for recursive permission management."""

import fnmatch
import os
import sys
from pathlib import Path

EXEC_EXTENSIONS = frozenset(
    {
        ".bash",
        ".cgi",
        ".csh",
        ".exe",
        ".o",
        ".out",
        ".par",
        ".pl",
        ".py",
        ".pyc",
        ".pyo",
        ".rb",
        ".sh",
        ".so",
    }
)


def is_script(path):
    """Detect if a file is a script by checking for a shebang line."""
    try:
        with open(path, "rb") as f:
            return f.read(2) == b"#!"
    except OSError:
        return False


def should_skip(name, exclude):
    """Check if an entry should be skipped based on exclude patterns."""
    return any(fnmatch.fnmatch(name, p) for p in exclude)


def should_process(name, include):
    """Check if a file matches include patterns (empty means all)."""
    return any(fnmatch.fnmatch(name, p) for p in include)


def classify_file(path):
    """Determine if a file is an executable/script or a regular file."""
    ext = Path(path).suffix
    if ext:
        return ext in EXEC_EXTENSIONS
    return is_script(path)


def chmod_recursive(
    directory,
    dirperms="0755",
    fileperms="0644",
    execperms="0755",
    verbose=False,
    follow_symlinks=False,
    exclude=None,
    include=None,
    dry_run=False,
    check=False,
):
    """Recursively set permissions on a directory tree.

    Args:
        directory: Root directory to process.
        dirperms: Octal string for directories (e.g. "0755").
        fileperms: Octal string for regular files.
        execperms: Octal string for scripts/executables.
        verbose: Print each entry being processed.
        follow_symlinks: Follow symbolic links.
        exclude: Glob patterns to skip (dirs and files).
        include: Glob patterns to process (files only). If set, non-matching
                 files are skipped.
        dry_run: Show what would change without modifying anything.
        check: Return list of files with wrong permissions (no modifications).

    Returns:
        List of (path, current_mode, expected_mode) tuples when check=True,
        otherwise None.
    """
    exclude = exclude or []
    include = include or []

    dir_mode = int(dirperms, 8)
    file_mode = int(fileperms, 8)
    exec_mode = int(execperms, 8)
    mismatches = []

    for root, dirs, files in os.walk(directory, followlinks=follow_symlinks):
        dirs[:] = [d for d in dirs if not should_skip(d, exclude)]

        current = os.stat(root).st_mode & 0o7777
        if current != dir_mode:
            if check or dry_run:
                mismatches.append((root, oct(current), oct(dir_mode)))
                if dry_run:
                    print(f"would chmod {oct(current)} -> {oct(dir_mode)}: {root}")
            else:
                os.chmod(root, dir_mode)
                if verbose:
                    print(f"dir: {root}")
        elif verbose and not check and not dry_run:
            print(f"ok: {root}")

        for filename in files:
            if should_skip(filename, exclude):
                continue
            if include and not should_process(filename, include):
                continue

            filepath = os.path.join(root, filename)

            if os.path.islink(filepath) and not follow_symlinks:
                continue

            expected = exec_mode if classify_file(filepath) else file_mode
            current = os.stat(filepath).st_mode & 0o7777

            if current != expected:
                if check or dry_run:
                    mismatches.append((filepath, oct(current), oct(expected)))
                    if dry_run:
                        print(
                            f"would chmod {oct(current)} -> {oct(expected)}: {filepath}"
                        )
                else:
                    os.chmod(filepath, expected)
                    if verbose:
                        label = "exec" if expected == exec_mode else "file"
                        print(f"{label}: {filepath}")
            elif verbose and not check and not dry_run:
                print(f"ok: {filepath}")

    if check:
        return mismatches
    return None
