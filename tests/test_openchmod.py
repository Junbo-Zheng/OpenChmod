# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Junbo Zheng

import os
import stat

import pytest

import chmod as openchmod
from chmod.core import chmod_recursive, classify_file
from chmod.cli import main


def get_mode(path):
    return stat.S_IMODE(os.stat(path).st_mode)


def test_version():
    assert openchmod.__version__ == "0.0.2"


class TestClassifyFile:
    def test_script_extension(self, tmp_path):
        f = tmp_path / "run.sh"
        f.write_text("echo hi")
        assert classify_file(str(f)) is True

    def test_regular_extension(self, tmp_path):
        f = tmp_path / "main.c"
        f.write_text("int main() {}")
        assert classify_file(str(f)) is False

    def test_no_extension_with_shebang(self, tmp_path):
        f = tmp_path / "myscript"
        f.write_text("#!/bin/bash\necho hi")
        assert classify_file(str(f)) is True

    def test_no_extension_without_shebang(self, tmp_path):
        f = tmp_path / "data"
        f.write_text("just data")
        assert classify_file(str(f)) is False


class TestChmodRecursive:
    def test_basic(self, tmp_path):
        subdir = tmp_path / "sub"
        subdir.mkdir()
        regular = subdir / "file.txt"
        regular.write_text("hello")
        script = tmp_path / "run.sh"
        script.write_text("#!/bin/bash")

        chmod_recursive(str(tmp_path))

        assert get_mode(str(tmp_path)) == 0o755
        assert get_mode(str(subdir)) == 0o755
        assert get_mode(str(regular)) == 0o644
        assert get_mode(str(script)) == 0o755

    def test_custom_perms(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")

        chmod_recursive(str(tmp_path), dirperms="0750", fileperms="0640")

        assert get_mode(str(tmp_path)) == 0o750
        assert get_mode(str(f)) == 0o640

    def test_symlink_not_followed(self, tmp_path):
        external = tmp_path / "external"
        external.mkdir()
        target = external / "target.txt"
        target.write_text("content")
        os.chmod(str(target), 0o777)

        work = tmp_path / "work"
        work.mkdir()
        link = work / "link.txt"
        link.symlink_to(target)

        chmod_recursive(str(work))

        assert get_mode(str(target)) == 0o777

    def test_exclude(self, tmp_path):
        git = tmp_path / ".git"
        git.mkdir()
        f = git / "config"
        f.write_text("data")
        os.chmod(str(f), 0o777)

        chmod_recursive(str(tmp_path), exclude=[".git"])

        assert get_mode(str(f)) == 0o777

    def test_include(self, tmp_path):
        py = tmp_path / "main.py"
        py.write_text("print()")
        txt = tmp_path / "notes.txt"
        txt.write_text("notes")
        os.chmod(str(txt), 0o777)

        chmod_recursive(str(tmp_path), include=["*.py"])

        assert get_mode(str(py)) == 0o755
        assert get_mode(str(txt)) == 0o777  # untouched

    def test_dry_run(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        os.chmod(str(f), 0o777)

        chmod_recursive(str(tmp_path), dry_run=True)

        # Nothing should change
        assert get_mode(str(f)) == 0o777

    def test_check_returns_mismatches(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        os.chmod(str(f), 0o777)

        result = chmod_recursive(str(tmp_path), check=True)

        assert len(result) > 0
        paths = [r[0] for r in result]
        assert str(f) in paths

    def test_files_only_skips_dirs(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        os.chmod(str(f), 0o777)
        os.chmod(str(tmp_path), 0o777)

        chmod_recursive(str(tmp_path), files_only=True)

        assert get_mode(str(f)) == 0o644  # file fixed
        assert get_mode(str(tmp_path)) == 0o777  # dir untouched

    def test_check_returns_empty_when_correct(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        os.chmod(str(f), 0o644)
        os.chmod(str(tmp_path), 0o755)

        result = chmod_recursive(str(tmp_path), check=True)

        assert result == []


class TestCLI:
    def test_no_args(self):
        with pytest.raises(SystemExit):
            main([])

    def test_nonexistent_dir(self):
        assert main(["/nonexistent_xyz"]) == 1

    def test_successful_run(self, tmp_path):
        (tmp_path / "file.txt").write_text("x")
        assert main([str(tmp_path)]) == 0

    def test_path_flag(self, tmp_path):
        (tmp_path / "file.txt").write_text("x")
        assert main(["-p", str(tmp_path)]) == 0

    def test_invalid_perms(self, tmp_path):
        with pytest.raises(SystemExit):
            main([str(tmp_path), "--dirperms", "9999"])

    def test_dry_run(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        os.chmod(str(f), 0o777)

        assert main([str(tmp_path), "--dry-run"]) == 0
        assert get_mode(str(f)) == 0o777

    def test_check_fails(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        os.chmod(str(f), 0o777)

        assert main([str(tmp_path), "--check"]) == 1

    def test_check_passes(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        os.chmod(str(f), 0o644)
        os.chmod(str(tmp_path), 0o755)

        assert main([str(tmp_path), "--check"]) == 0

    def test_exclude_flag(self, tmp_path):
        git = tmp_path / ".git"
        git.mkdir()
        f = git / "HEAD"
        f.write_text("ref")
        os.chmod(str(f), 0o777)

        assert main([str(tmp_path), "-e", ".git"]) == 0
        assert get_mode(str(f)) == 0o777
