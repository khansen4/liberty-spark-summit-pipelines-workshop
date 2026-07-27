"""
Tests for policy lookup utilities.

Demonstrates
------------
- Testing pure functions (no I/O) with straightforward assertions.
- Using ``datetime.date`` objects so tests are not coupled to string formats.
- Parametrize for validation boundary cases.
"""

from __future__ import annotations

import datetime

import pytest

from claims_sample.good.policy_lookup import (
    calculate_risk_score,
    is_policy_active,
    validate_policy_number,
)


# ---------------------------------------------------------------------------
# validate_policy_number
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "policy_number, expected",
    [
        ("LMI12345678", True),   # valid
        ("LMI00000000", True),   # all zeros — still valid format
        ("LMI1234567",  False),  # only 7 digits
        ("LMI123456789",False),  # 9 digits
        ("lmi12345678",  False), # lowercase prefix
        ("XYZ12345678",  False), # wrong prefix
        ("LMI1234567A",  False), # letter in digit section
        ("",             False), # empty string
    ],
)
def test_validate_policy_number(policy_number, expected):
    assert validate_policy_number(policy_number) is expected


# ---------------------------------------------------------------------------
# is_policy_active
# ---------------------------------------------------------------------------


def test_future_expiry_is_active():
    future = datetime.date.today() + datetime.timedelta(days=365)
    assert is_policy_active(future) is True


def test_past_expiry_is_inactive():
    past = datetime.date.today() - datetime.timedelta(days=1)
    assert is_policy_active(past) is False


def test_today_expiry_is_inactive():
    """A policy that expires today is no longer active."""
    assert is_policy_active(datetime.date.today()) is False


# ---------------------------------------------------------------------------
# calculate_risk_score
# ---------------------------------------------------------------------------


class TestCalculateRiskScore:
    def test_young_urban_high_claims_is_high_risk(self):
        score = calculate_risk_score(age=22, prior_claims=5, location="urban")
        # 30 (young) + 50 (high claims) + 15 (urban) = 95
        assert score == 95

    def test_senior_rural_no_claims_is_low_risk(self):
        score = calculate_risk_score(age=55, prior_claims=0, location="rural")
        # 0 + 0 + (-5) = -5
        assert score == -5

    def test_mature_suburban_moderate_claims(self):
        score = calculate_risk_score(age=35, prior_claims=2, location="suburban")
        # 10 (mature) + 20 (moderate) + 0 (suburban) = 30
        assert score == 30

    def test_boundary_young_driver_threshold(self):
        """Age exactly at RISK_YOUNG_DRIVER_THRESHOLD falls into 'mature' bracket."""
        score_young  = calculate_risk_score(age=24, prior_claims=0, location="suburban")
        score_mature = calculate_risk_score(age=25, prior_claims=0, location="suburban")
        assert score_young > score_mature
