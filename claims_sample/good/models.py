"""
Data models for the Liberty Mutual claims processing system.

Using dataclasses and enums gives us:
  - Type safety and IDE auto-complete
  - Clear documentation of every field
  - Immutable IDs and status constants (no magic strings)
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum


class ClaimType(str, Enum):
    """Supported categories of insurance claims."""

    AUTO = "auto"
    HOME = "home"
    LIFE = "life"


class ClaimStatus(str, Enum):
    """Lifecycle states a claim can occupy."""

    OPEN = "open"
    APPROVED = "approved"
    DENIED = "denied"
    PENDING_REVIEW = "pending_review"


class PolicyTier(str, Enum):
    """Policy coverage tiers, from broadest to most limited."""

    PREMIUM = "premium"
    STANDARD = "standard"
    BASIC = "basic"


# ---------------------------------------------------------------------------
# Thresholds — named constants replace magic numbers throughout the codebase.
# ---------------------------------------------------------------------------

AUTO_AUTO_APPROVE_LIMIT: float = 500.00      # Auto claims at or below this are auto-approved.
AUTO_STANDARD_LIMIT: float = 5_000.00        # Auto claims above this need manual review.
HOME_AUTO_APPROVE_LIMIT: float = 1_000.00    # Home claims at or below this are auto-approved.

DEDUCTIBLE_PREMIUM_RATE: float = 0.10        # 10 % of claim amount.
DEDUCTIBLE_STANDARD_RATE: float = 0.20       # 20 % of claim amount.
DEDUCTIBLE_BASIC_RATE: float = 0.30          # 30 % of claim amount.
DEDUCTIBLE_BASIC_CAP: float = 500.00         # Maximum deductible for basic-tier policies.

RISK_YOUNG_DRIVER_THRESHOLD: int = 25        # Under this age = elevated risk.
RISK_MATURE_DRIVER_THRESHOLD: int = 40       # Under this age = moderate risk.
RISK_HIGH_CLAIMS_THRESHOLD: int = 3          # More than this many prior claims = high risk.
RISK_MODERATE_CLAIMS_THRESHOLD: int = 1      # More than this many prior claims = moderate risk.

POLICY_NUMBER_PATTERN: str = r"^LMI[0-9]{8}$"


@dataclass
class Claim:
    """A single insurance claim submitted by a policyholder."""

    claim_id: str
    policy_number: str
    claim_type: ClaimType
    amount: float
    notes: str = ""
    attachments: list[str] = field(default_factory=list)  # ✅ avoids mutable default arg bug
    status: ClaimStatus = ClaimStatus.OPEN
    submitted_at: datetime.datetime = field(default_factory=datetime.datetime.now)


@dataclass
class ClaimResult:
    """The outcome produced by processing a Claim."""

    claim: Claim
    approved: bool
    reason: str
    processed_at: datetime.datetime = field(default_factory=datetime.datetime.now)

    @property
    def status(self) -> ClaimStatus:
        return ClaimStatus.APPROVED if self.approved else ClaimStatus.DENIED


@dataclass
class PolicyHolder:
    """A Liberty Mutual customer who holds one or more policies."""

    first_name: str
    last_name: str
    date_of_birth: datetime.date
    policy_numbers: list[str] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
