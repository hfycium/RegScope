from __future__ import annotations

import re
import subprocess
from pathlib import Path


_HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def resolve_revision(project_root: str | Path, revision: str) -> str:
    """Resolve a Git revision to an immutable commit ID in the target repository."""
    root = Path(project_root).resolve()
    return _run_git(root, ["rev-parse", "--verify", f"{revision}^{{commit}}"])


def changed_files(project_root: str | Path, base: str, head: str) -> list[str]:
    """Return sorted target-relative file paths changed between two revisions."""
    root = Path(project_root).resolve()
    resolved_base = resolve_revision(root, base)
    resolved_head = resolve_revision(root, head)
    output = _run_git(root, ["diff", "--name-only", "--no-ext-diff", resolved_base, resolved_head, "--"])
    return sorted(line for line in output.splitlines() if line)


def changed_head_lines(project_root: str | Path, base: str, head: str) -> dict[str, list[int]]:
    """Return changed line numbers that exist in the head revision, keyed by file."""
    root = Path(project_root).resolve()
    resolved_base = resolve_revision(root, base)
    resolved_head = resolve_revision(root, head)
    output = _run_git(root, ["diff", "--unified=0", "--no-ext-diff", resolved_base, resolved_head, "--"])

    lines_by_file: dict[str, set[int]] = {}
    current_file: str | None = None
    for line in output.splitlines():
        if line.startswith("+++ b/"):
            current_file = line.removeprefix("+++ b/")
            lines_by_file.setdefault(current_file, set())
            continue

        match = _HUNK_HEADER.match(line)
        if current_file is None or match is None:
            continue

        start = int(match.group(1))
        count = int(match.group(2) or 1)
        if count:
            lines_by_file[current_file].update(range(start, start + count))

    return {path: sorted(lines) for path, lines in sorted(lines_by_file.items()) if lines}


def _run_git(project_root: Path, arguments: list[str]) -> str:
    command = ["git", *arguments]
    result = subprocess.run(
        command,
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Git command failed"
        raise ValueError(f"Could not run Git in {project_root}: {message}")
    return result.stdout.strip()
