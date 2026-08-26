"""Scrub Cursor AppImage env before project Python. Never overwrite .env."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

from .errors import CampaignRunnerError

_APPIMAGE_MARKERS = ("appimage", "squashfs-root", "/tmp/.mount_")


def scrub_environ(base: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return a copy of *base* (or os.environ) safe for project interpreters.

    Removes APPIMAGE and APPDIR. Clears LD_LIBRARY_PATH when it looks like an
    AppImage inheritance or when APPIMAGE/APPDIR were present in the source env.
    """
    source = dict(os.environ if base is None else base)
    had_appimage = "APPIMAGE" in source or "APPDIR" in source
    env = dict(source)
    env.pop("APPIMAGE", None)
    env.pop("APPDIR", None)
    ld = env.get("LD_LIBRARY_PATH", "")
    if had_appimage or _ld_looks_like_appimage(ld):
        env.pop("LD_LIBRARY_PATH", None)
    return env


def _ld_looks_like_appimage(ld_library_path: str) -> bool:
    lowered = ld_library_path.lower()
    return any(marker in lowered for marker in _APPIMAGE_MARKERS)


def assert_env_file_untouched(campaign_dir: Path, before_mtime_ns: dict[str, int]) -> None:
    """Fail if any .env file under *campaign_dir* changed since the snapshot."""
    for rel, prior in before_mtime_ns.items():
        path = campaign_dir / rel
        if not path.is_file():
            raise CampaignRunnerError(
                f".env file disappeared during run: {rel}",
                path=str(path),
            )
        if path.stat().st_mtime_ns != prior:
            raise CampaignRunnerError(
                f"runner must never overwrite .env; mtime changed: {rel}",
                path=str(path),
            )


def snapshot_env_files(campaign_dir: Path) -> dict[str, int]:
    """Record mtimes for .env and .env.* under the campaign directory."""
    found: dict[str, int] = {}
    if not campaign_dir.is_dir():
        return found
    for path in campaign_dir.rglob(".env*"):
        if not path.is_file():
            continue
        name = path.name
        if name == ".env" or name.startswith(".env."):
            if name == ".env.example":
                continue
            rel = str(path.relative_to(campaign_dir))
            found[rel] = path.stat().st_mtime_ns
    return found
