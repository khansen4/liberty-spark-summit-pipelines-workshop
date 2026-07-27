"""
Claims processing logic for Liberty Mutual.

Design notes
------------
- All threshold values live in ``models`` as named constants — no magic numbers here.
- The nested-if tree from the bad version is replaced with small, single-purpose helpers.
- Type hints on every function signature let Ruff / mypy catch mistakes statically.
- The mutable default argument bug (``attachments=[]``) is fixed in the ``Claim`` dataclass.
"""

from __future__ import annotations

from claims_sample.good.models import (
    AUTO_AUTO_APPROVE_LIMIT,
    AUTO_STANDARD_LIMIT,
    DEDUCTIBLE_BASIC_CAP,
    DEDUCTIBLE_BASIC_RATE,
    DEDUCTIBLE_PREMIUM_RATE,
    DEDUCTIBLE_STANDARD_RATE,
    HOME_AUTO_APPROVE_LIMIT,
    Claim,
    ClaimResult,
    ClaimStatus,
    ClaimType,
    PolicyTier,
)


# ---------------------------------------------------------------------------
# Internal helpers — each handles exactly one decision.
# ---------------------------------------------------------------------------


def _evaluate_auto_claim(amount: float) -> tuple[bool, str]:
    """Return (approved, reason) for an auto claim based on dollar amount."""
    if amount <= AUTO_AUTO_APPROVE_LIMIT:
        return True, "Low-value auto claim — auto-approved."
    if amount <= AUTO_STANDARD_LIMIT:
        return True, "Mid-value auto claim — approved, pending routine review."
    return False, "High-value auto claim — requires manual adjuster review."


def _evaluate_home_claim(amount: float) -> tuple[bool, str]:
    """Return (approved, reason) for a home claim based on dollar amount."""
    if amount <= HOME_AUTO_APPROVE_LIMIT:
        return True, "Low-value home claim — auto-approved."
    return False, "Home claim exceeds auto-approval threshold — adjuster required."


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def process_claim(claim: Claim) -> ClaimResult:
    """
    Evaluate a claim and return a ``ClaimResult``.

    Parameters
    ----------
    claim:
        The submitted ``Claim`` object.

    Returns
    -------
    ClaimResult
        Contains the approval decision and a human-readable reason.

    Raises
    ------
    ValueError
        If the claim amount is not positive.
    """
    if claim.amount <= 0:
        raise ValueError(f"Claim amount must be positive; got {claim.amount}.")

    evaluators = {
        ClaimType.AUTO: _evaluate_auto_claim,
        ClaimType.HOME: _evaluate_home_claim,
    }

    if claim.claim_type not in evaluators:
        return ClaimResult(claim=claim, approved=False, reason="Unsupported claim type.")

    approved, reason = evaluators[claim.claim_type](claim.amount)
    return ClaimResult(claim=claim, approved=approved, reason=reason)


def calculate_deductible(amount: float, tier: PolicyTier) -> float:
    """
    Calculate the policyholder's deductible for a given claim amount and policy tier.

    Named constants (``DEDUCTIBLE_*``) make the rates explicit and easy to update.
    """
    if tier == PolicyTier.PREMIUM:
        return round(amount * DEDUCTIBLE_PREMIUM_RATE, 2)
    if tier == PolicyTier.STANDARD:
        return round(amount * DEDUCTIBLE_STANDARD_RATE, 2)
    # Basic tier: rate applies but is capped at DEDUCTIBLE_BASIC_CAP.
    return round(min(amount * DEDUCTIBLE_BASIC_RATE, DEDUCTIBLE_BASIC_CAP), 2)


def get_claim_summary(results: list[ClaimResult]) -> dict[str, int | float]:
    """
    Aggregate a list of ``ClaimResult`` objects into a summary dictionary.

    Returns
    -------
    dict with keys: total_amount, approved_count, denied_count
    """
    return {
        "total_amount": sum(r.claim.amount for r in results),
        "approved_count": sum(1 for r in results if r.approved),
        "denied_count": sum(1 for r in results if not r.approved),
    }
