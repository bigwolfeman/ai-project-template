"""Verify protected-resource digests from evaluator.lock.json."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .errors import LockMismatchError, ManifestError

DIGEST_ALGO = "sha256"


def load_lock(lock_path: Path) -> dict[str, Any]:
    if not lock_path.is_file():
        raise ManifestError(
            f"missing evaluator lock: {lock_path}",
            path=str(lock_path),
            field="evaluator_lock_path",
        )
    try:
        doc = json.loads(lock_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifestError(
            f"invalid JSON in evaluator lock: {exc.msg}",
            path=str(lock_path),
        ) from exc
    if not isinstance(doc, dict):
        raise ManifestError(
            "evaluator lock root must be an object",
            path=str(lock_path),
        )
    return doc


def file_digest(path: Path, algorithm: str = DIGEST_ALGO) -> str:
    if algorithm != DIGEST_ALGO:
        raise LockMismatchError(
            f"unsupported digest algorithm {algorithm!r}",
            field="digest_algorithm",
            path=str(path),
        )
    if not path.is_file():
        raise LockMismatchError(
            "locked resource file is missing",
            field="path",
            path=str(path),
        )
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def verify_lock(
    campaign_dir: Path,
    lock: dict[str, Any] | None = None,
    *,
    lock_path: Path | None = None,
    campaign_id: str | None = None,
    when: str = "before",
) -> None:
    """Verify every resource digest in the lock against files under *campaign_dir*."""
    if lock is None:
        if lock_path is None:
            raise ManifestError("verify_lock requires lock or lock_path")
        lock = load_lock(lock_path)
    cid = campaign_id or lock.get("campaign_id")
    if isinstance(cid, str) and lock.get("campaign_id") not in (None, cid):
        raise LockMismatchError(
            f"lock campaign_id {lock.get('campaign_id')!r} != {cid!r}",
            campaign_id=cid,
            field="campaign_id",
        )
    resources = lock.get("resources")
    if not isinstance(resources, list) or not resources:
        raise LockMismatchError(
            "evaluator lock has no resources",
            campaign_id=cid if isinstance(cid, str) else None,
            field="resources",
        )
    mismatches: list[str] = []
    for idx, item in enumerate(resources):
        if not isinstance(item, dict):
            raise LockMismatchError(
                f"resources[{idx}] must be an object",
                campaign_id=cid if isinstance(cid, str) else None,
                field=f"resources[{idx}]",
            )
        rel = item.get("path")
        expected = item.get("digest")
        algo = item.get("digest_algorithm", DIGEST_ALGO)
        if not isinstance(rel, str) or not isinstance(expected, str):
            raise LockMismatchError(
                f"resources[{idx}] missing path or digest",
                campaign_id=cid if isinstance(cid, str) else None,
                field=f"resources[{idx}]",
            )
        target = (campaign_dir / rel).resolve()
        try:
            campaign_root = campaign_dir.resolve()
            target.relative_to(campaign_root)
        except ValueError as exc:
            raise LockMismatchError(
                f"locked path escapes campaign dir: {rel}",
                campaign_id=cid if isinstance(cid, str) else None,
                path=rel,
            ) from exc
        actual = file_digest(target, str(algo))
        if actual != expected:
            mismatches.append(f"{rel}: expected {expected}, got {actual} ({when})")
    if mismatches:
        raise LockMismatchError(
            "protected-resource digest mismatch; aborting. " + "; ".join(mismatches),
            campaign_id=cid if isinstance(cid, str) else None,
            field="resources",
        )
