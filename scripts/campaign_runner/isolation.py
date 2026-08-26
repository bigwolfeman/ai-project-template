"""Worktree isolation helpers for campaign runs."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Callable

from campaign_schema import ROOT

from .errors import CampaignRunnerError, WorktreeError
from .worktree import (
    create_worktree,
    current_commit,
    refuse_if_dirty,
    remove_worktree,
    repo_root,
)


def prepare_isolation(campaign_dir: Path, manifest: dict[str, Any], campaign_id: str) -> None:
    policy = manifest.get("branch_worktree_policy") or {}
    if not policy.get("refuse_dirty_protected_or_mutable_paths", True):
        return
    try:
        repo = repo_root(campaign_dir)
    except CampaignRunnerError:
        return

    def _rel(paths: list[str]) -> list[str]:
        out: list[str] = []
        for p in paths:
            full = Path(p) if Path(p).is_absolute() else (campaign_dir / p)
            try:
                out.append(str(full.resolve().relative_to(repo.resolve())))
            except ValueError:
                out.append(p)
        return out

    refuse_if_dirty(
        repo,
        protected_paths=_rel(list(manifest.get("protected_paths") or [])),
        mutable_paths=_rel(list(manifest.get("mutable_paths") or [])),
        policy=policy,
        campaign_id=campaign_id,
    )


def overlay_paths(
    source: Path,
    dest: Path,
    rel_paths: list[str],
    *,
    campaign_id: str | None = None,
) -> None:
    """Copy mutable and protected paths from the campaign into a worktree.

    The campaign directory remains the authority for lock digests. The worktree
    receives a fresh overlay so the evaluator runs against candidate mutable
    files plus a sealed copy of the protected harness.
    """
    root = source.resolve()
    for rel in rel_paths:
        if not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
            raise WorktreeError(
                f"overlay path must be a relative path without '..': {rel!r}",
                campaign_id=campaign_id,
                path=rel,
            )
        src = (source / rel).resolve()
        try:
            src.relative_to(root)
        except ValueError as exc:
            raise WorktreeError(
                f"overlay path escapes campaign directory: {rel}",
                campaign_id=campaign_id,
                path=rel,
            ) from exc
        if not src.exists():
            raise WorktreeError(
                f"overlay source missing: {rel}",
                campaign_id=campaign_id,
                path=rel,
            )
        dst = dest / rel
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def resolve_work_dir(
    campaign_dir: Path, manifest: dict[str, Any], campaign_id: str, name: str
) -> tuple[Path, Callable[[], None]]:
    policy = manifest.get("branch_worktree_policy") or {}
    isolation = policy.get("isolation", "none")

    def _noop() -> None:
        return None

    if isolation != "git_worktree":
        return campaign_dir, _noop
    try:
        repo = repo_root(campaign_dir)
    except CampaignRunnerError:
        return campaign_dir, _noop
    slug = campaign_id
    artifact = manifest.get("artifact_policy") or {}
    ignored = artifact.get("ignored_root")
    if isinstance(ignored, str) and ignored.startswith("ignored/research/"):
        slug = ignored.rstrip("/").split("/")[-1]
    wt = create_worktree(repo, slug=slug, name=name, campaign_id=campaign_id)
    overlay = list(
        dict.fromkeys(
            [
                *(manifest.get("mutable_paths") or []),
                *(manifest.get("protected_paths") or []),
            ]
        )
    )
    overlay_paths(campaign_dir, wt, overlay, campaign_id=campaign_id)

    def _cleanup() -> None:
        remove_worktree(repo, wt, campaign_id=campaign_id)

    return wt, _cleanup


def baseline_candidate_id(campaign_dir: Path) -> str:
    try:
        return current_commit(repo_root(campaign_dir))
    except CampaignRunnerError:
        return "baseline-unchanged"


def artifact_root(campaign_dir: Path, manifest: dict[str, Any]) -> Path:
    artifact = manifest.get("artifact_policy") or {}
    ignored = artifact.get("ignored_root")
    if isinstance(ignored, str):
        root = ROOT / ignored if not Path(ignored).is_absolute() else Path(ignored)
        root.mkdir(parents=True, exist_ok=True)
        return root
    path = campaign_dir / "state" / "runtime"
    path.mkdir(parents=True, exist_ok=True)
    return path
