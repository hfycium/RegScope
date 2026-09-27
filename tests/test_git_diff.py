from pathlib import Path
import subprocess

import pytest

from regscope.git_diff import changed_files, changed_head_lines, resolve_revision


def git(project: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=project,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


@pytest.fixture
def git_project(tmp_path: Path) -> Path:
    git(tmp_path, "init")
    git(tmp_path, "config", "user.email", "regscope@example.test")
    git(tmp_path, "config", "user.name", "RegScope Test")
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "service.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")
    git(tmp_path, "add", "app/service.py")
    git(tmp_path, "commit", "-m", "base")
    return tmp_path


def test_resolve_and_parse_changed_head_lines(git_project: Path):
    base = git(git_project, "rev-parse", "HEAD")
    source = git_project / "app" / "service.py"
    source.write_text("def alpha():\n    return 2\n\ndef beta():\n    return 3\n", encoding="utf-8")
    git(git_project, "add", "app/service.py")
    git(git_project, "commit", "-m", "change functions")
    head = git(git_project, "rev-parse", "HEAD")

    assert resolve_revision(git_project, "HEAD") == head
    assert changed_files(git_project, base, head) == ["app/service.py"]
    assert changed_head_lines(git_project, base, head) == {"app/service.py": [2, 3, 4, 5]}


def test_changed_files_keeps_deleted_file_but_head_lines_omits_it(git_project: Path):
    base = git(git_project, "rev-parse", "HEAD")
    (git_project / "app" / "service.py").unlink()
    git(git_project, "add", "-A")
    git(git_project, "commit", "-m", "delete source")

    assert changed_files(git_project, base, "HEAD") == ["app/service.py"]
    assert changed_head_lines(git_project, base, "HEAD") == {}


def test_invalid_revision_has_clear_error(git_project: Path):
    with pytest.raises(ValueError, match="Could not run Git"):
        resolve_revision(git_project, "not-a-revision")
