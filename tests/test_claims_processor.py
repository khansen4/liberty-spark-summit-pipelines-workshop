"""
Unit and integration tests for the claims processor.

Demonstrates
------------
- Unit tests  : each function tested in isolation with a clear AAA pattern
                (Arrange / Act / Assert).
- Edge cases  : zero amount, boundary values, unknown types.
- Regression  : a dedicated test for a specific bug that was once reported.
- Parametrize : pytest.mark.parametrize eliminates copy-paste test duplication.
"""

from __future__ import annotations

import pytest

from claims_sample.good.claims_processor import (
    calculate_deductible,
    get_claim_summary,
    process_claim,
)
from claims_sample.good.models import (
    AUTO_AUTO_APPROVE_LIMIT,
    AUTO_STANDARD_LIMIT,
    Claim,
    ClaimResult,
    ClaimStatus,
    ClaimType,
    PolicyTier,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def make_claim(
    amount: float,
    claim_type: ClaimType = ClaimType.AUTO,
    claim_id: str = "CLM-001",
    policy_number: str = "LMI12345678",
) -> Claim:
    """Convenience factory so tests stay short and readable."""
    return Claim(
        claim_id=claim_id,
        policy_number=policy_number,
        claim_type=claim_type,
        amount=amount,
    )


# ---------------------------------------------------------------------------
# process_claim — unit tests
# ---------------------------------------------------------------------------


class TestProcessClaim:
    def test_low_value_auto_claim_is_approved(self):
        # Arrange
        claim = make_claim(amount=200.00, claim_type=ClaimType.AUTO)
        # Act
        result = process_claim(claim)
        # Assert
        assert result.approved is True
        assert result.status == ClaimStatus.APPROVED

    def test_high_value_auto_claim_is_denied(self):
        claim = make_claim(amount=AUTO_STANDARD_LIMIT + 1, claim_type=ClaimType.AUTO)
        result = process_claim(claim)
        assert result.approved is False

    def test_mid_value_auto_claim_is_approved(self):
        """Amount between the two auto thresholds should still be approved."""
        mid = (AUTO_AUTO_APPROVE_LIMIT + AUTO_STANDARD_LIMIT) / 2
        claim = make_claim(amount=mid, claim_type=ClaimType.AUTO)
        result = process_claim(claim)
        assert result.approved is True

    def test_low_value_home_claim_is_approved(self):
        claim = make_claim(amount=500.00, claim_type=ClaimType.HOME)
        result = process_claim(claim)
        assert result.approved is True

    def test_high_value_home_claim_is_denied(self):
        claim = make_claim(amount=50_000.00, claim_type=ClaimType.HOME)
        result = process_claim(claim)
        assert result.approved is False

    def test_unsupported_claim_type_is_denied(self):
        claim = make_claim(amount=100.00, claim_type=ClaimType.LIFE)
        result = process_claim(claim)
        assert result.approved is False
        assert "Unsupported" in result.reason

    def test_zero_amount_raises_value_error(self):
        """A claim for $0 is meaningless; we expect a clear error."""
        claim = make_claim(amount=0)
        with pytest.raises(ValueError, match="positive"):
            process_claim(claim)

    def test_negative_amount_raises_value_error(self):
        claim = make_claim(amount=-100)
        with pytest.raises(ValueError):
            process_claim(claim)

    def test_result_contains_original_claim(self):
        """The result should carry a reference back to the original claim."""
        claim = make_claim(amount=300.00)
        result = process_claim(claim)
        assert result.claim is claim


# ---------------------------------------------------------------------------
# calculate_deductible — parametrized tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "amount, tier, expected",
    [
        (1000.00, PolicyTier.PREMIUM, 100.00),   # 10%
        (1000.00, PolicyTier.STANDARD, 200.00),  # 20%
        (1000.00, PolicyTier.BASIC, 300.00),     # 30%, under cap
        (2000.00, PolicyTier.BASIC, 500.00),     # 30% would be 600, capped at 500
        (0.01,    PolicyTier.PREMIUM, 0.00),     # near-zero amount
    ],
)
def test_calculate_deductible(amount, tier, expected):
    assert calculate_deductible(amount, tier) == expected


# ---------------------------------------------------------------------------
# get_claim_summary — unit + integration
# ---------------------------------------------------------------------------


class TestGetClaimSummary:
    def _make_result(self, amount: float, approved: bool) -> ClaimResult:
        claim = make_claim(amount=amount)
        return ClaimResult(claim=claim, approved=approved, reason="test")

    def test_empty_list_returns_zeros(self):
        summary = get_claim_summary([])
        assert summary == {"total_amount": 0, "approved_count": 0, "denied_count": 0}

    def test_counts_and_total_are_correct(self):
        results = [
            self._make_result(1000.00, approved=True),
            self._make_result(2000.00, approved=True),
            self._make_result(500.00, approved=False),
        ]
        summary = get_claim_summary(results)
        assert summary["total_amount"] == 3500.00
        assert summary["approved_count"] == 2
        assert summary["denied_count"] == 1


# ---------------------------------------------------------------------------
# REGRESSION TEST
# Bug: basic-tier deductible was not capped, so a $10,000 claim returned $3,000
# instead of the $500 cap. Fixed in commit abc1234. This test ensures it stays fixed.
# ---------------------------------------------------------------------------


def test_regression_basic_deductible_cap():
    """Deductible for basic tier must never exceed DEDUCTIBLE_BASIC_CAP ($500)."""
    deductible = calculate_deductible(10_000.00, PolicyTier.BASIC)
    assert deductible == 500.00, (
        "Regression: basic-tier deductible cap is broken again. "
        "See commit abc1234 for original fix."
    )
