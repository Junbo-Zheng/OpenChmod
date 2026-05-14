# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Junbo Zheng

"""Command-line interface for openchmod."""

import argparse
import os
import re
import sys

from chmod.core import EXEC_EXTENSIONS, chmod_recursive

PERM_RE = re.compile(r"^0[0-7]{3}$")


def valid_perm(value):
    """Argparse type validator for octal permission strings."""
    if not PERM_RE.match(value):
        raise argparse.ArgumentTypeError(
            f"'{value}' is not a valid permission (must be 4 octal digits, e.g. 0755)"
        )
    return value


def build_parser():
    parser = argparse.ArgumentParser(
        prog="pychmod",
        description="Recursively chmod directories, files, and executables.",
        epilog="Executable extensions: " + " ".join(sorted(EXEC_EXTENSIONS)),
    )
    parser.add_argument(
        "directory", nargs="?", metavar="DIR", help="Directory to traverse."
    )
    parser.add_argument(
        "-p", "--path", metavar="DIR", help="Directory to traverse (alternative)."
    )
    parser.add_argument(
        "--dirperms",
        default="0755",
        type=valid_perm,
        help="Permissions for directories (default: 0755).",
    )
    parser.add_argument(
        "-f",
        "--fileperms",
        default="0644",
        type=valid_perm,
        help="Permissions for regular files (default: 0644).",
    )
    parser.add_argument(
        "-x",
        "--execperms",
        default="0755",
        type=valid_perm,
        help="Permissions for scripts/executables (default: 0755).",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Glob pattern to exclude (repeatable).",
    )
    parser.add_argument(
        "-i",
        "--include",
        action="append",
        default=[],
        metavar="PATTERN",
        help="Glob pattern to include (repeatable, files only).",
    )
    parser.add_argument(
        "-s",
        "--symlinks",
        action="store_true",
        help="Follow and process symlinks.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print each file being processed.",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would change without modifying anything.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mode: exit with error if any permissions are wrong (no changes made).",
    )
    return parser


def main(argv=None):
    """Entry point for the openchmod CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    target = args.path or args.directory
    if not target:
        parser.error("directory is required (positional or -p/--path)")

    if not os.path.isdir(target):
        sys.stderr.write(f"Error: '{target}' is not a directory.\n")
        return 1

    print(f"chmod dirs={args.dirperms} files={args.fileperms} exec={args.execperms}")

    try:
        result = chmod_recursive(
            target,
            dirperms=args.dirperms,
            fileperms=args.fileperms,
            execperms=args.execperms,
            verbose=args.verbose,
            follow_symlinks=args.symlinks,
            exclude=args.exclude,
            include=args.include,
            dry_run=args.dry_run,
            check=args.check,
        )
    except OSError as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1

    if args.check and result:
        print(f"\n{len(result)} file(s) with incorrect permissions:")
        for path, current, expected in result:
            print(f"  {current} -> {expected}: {path}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
