"""Typed failures for the campaign runner. Always fail loud."""

from __future__ import annotations


class CampaignRunnerError(Exception):
    """Base error. Subclasses name campaign, trial, or field when known."""

    def __init__(
        self,
        message: str,
        *,
        campaign_id: str | None = None,
        trial_id: str | None = None,
        field: str | None = None,
        path: str | None = None,
    ) -> None:
        parts: list[str] = []
        if campaign_id is not None:
            parts.append(f"campaign_id={campaign_id}")
        if trial_id is not None:
            parts.append(f"trial_id={trial_id}")
        if field is not None:
            parts.append(f"field={field}")
        if path is not None:
            parts.append(f"path={path}")
        prefix = f"[{', '.join(parts)}] " if parts else ""
        super().__init__(prefix + message)
        self.campaign_id = campaign_id
        self.trial_id = trial_id
        self.field = field
        self.path = path


class ManifestError(CampaignRunnerError):
    """Campaign manifest missing, invalid, or inconsistent."""


class ValidationError(CampaignRunnerError):
    """Schema or layout validation failed."""


class LockMismatchError(CampaignRunnerError):
    """Protected-resource digest does not match evaluator.lock.json."""


class DirtyWorktreeError(CampaignRunnerError):
    """Protected or mutable paths have unrecorded changes."""


class WorktreeError(CampaignRunnerError):
    """Git worktree create/remove failed."""


class ProcessError(CampaignRunnerError):
    """Subprocess failed without a timeout."""


class ProcessTimeoutError(CampaignRunnerError):
    """Subprocess exceeded its timeout; process tree was killed."""


class AdapterError(CampaignRunnerError):
    """Domain adapter failed prepare, execute, collect, or normalize."""


class ComparatorError(CampaignRunnerError):
    """Comparator could not classify a result."""


class BudgetExhaustedError(CampaignRunnerError):
    """Resource budget or stop condition blocks further trials."""


class LedgerError(CampaignRunnerError):
    """Ledger append or projection rebuild failed."""


class UsageError(CampaignRunnerError):
    """CLI usage is invalid."""
