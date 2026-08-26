"""Git worktree isolation. Never uses destructive hard resets."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from .errors import DirtyWorktreeError, WorktreeError

_HARD_FLAG = "--hard"


def _run_git(args: list[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    if args and args[0] == "reset" and _HARD_FLAG in args:
        raise WorktreeError("destructive git reset is forbidden in the campaign runner")
    try:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=check,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError as exc:
        raise WorktreeError("git executable not found") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise WorktreeError(f"git {' '.join(args)} failed: {detail}") from exc


def repo_root(start: Path) -> Path:
    proc = _run_git(["rev-parse", "--show-toplevel"], cwd=start)
    return Path(proc.stdout.strip())


def current_commit(repo: Path) -> str:
    proc = _run_git(["rev-parse", "HEAD"], cwd=repo)
    return proc.stdout.strip()


def list_dirty_paths(repo: Path, pathspecs: list[str]) -> list[str]:
    """Return dirty paths under *pathspecs* (relative to repo)."""
    if not pathspecs:
        return []
    proc = _run_git(
        ["status", "--porcelain", "-uall", "--", *pathspecs],
        cwd=repo,
        check=True,
    )
    dirty: list[str] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        entry = line[3:] if len(line) > 3 else line
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        dirty.append(entry.strip())
    return dirty


def refuse_if_dirty(
    repo: Path,
    *,
    protected_paths: list[str],
    mutable_paths: list[str],
    policy: dict[str, Any],
    campaign_id: str | None = None,
) -> None:
    if not policy.get("refuse_dirty_protected_or_mutable_paths", True):
        return
    pathspecs = list(dict.fromkeys([*protected_paths, *mutable_paths]))
    dirty = list_dirty_paths(repo, pathspecs)
    if not dirty:
        return
    listed = ", ".join(dirty)
    raise DirtyWorktreeError(
        "protected or mutable paths have unrecorded changes: "
        f"{listed}. Commit, stash, or restore them before the runner starts. "
        "Do not discard candidate work with a destructive hard reset.",
        campaign_id=campaign_id,
        path=dirty[0],
    )


def worktree_base(repo: Path, slug: str) -> Path:
    return repo / "ignored" / "research" / slug / "worktrees"


def create_worktree(
    repo: Path,
    *,
    slug: str,
    name: str,
    commit: str | None = None,
    campaign_id: str | None = None,
) -> Path:
    """Create a disposable worktree under ignored/research/<slug>/worktrees/."""
    base = worktree_base(repo, slug)
    base.mkdir(parents=True, exist_ok=True)
    target = base / name
    if target.exists():
        raise WorktreeError(
            f"worktree path already exists: {target}",
            campaign_id=campaign_id,
            path=str(target),
        )
    ref = commit or current_commit(repo)
    # Detached worktree at an immutable commit identifier.
    _run_git(["worktree", "add", "--detach", str(target), ref], cwd=repo)
    return target


def remove_worktree(repo: Path, worktree: Path, *, campaign_id: str | None = None) -> None:
    if not worktree.exists():
        return
    _run_git(["worktree", "remove", "--force", str(worktree)], cwd=repo)
    _run_git(["worktree", "prune"], cwd=repo, check=False)
