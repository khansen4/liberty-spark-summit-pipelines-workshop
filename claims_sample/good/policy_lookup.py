"""
Policy lookup utilities for Liberty Mutual.

Key improvements over the bad version
--------------------------------------
- Parameterised SQL queries prevent injection attacks.
- ``validate_policy_number`` uses a named regex constant (not an inline string).
- ``is_policy_active`` accepts a typed ``date`` — no ambiguous string formats.
- ``calculate_risk_score`` replaces the magic-number chain with named constants
  and a table-driven approach that's easy to extend.
- Dead commented-out code is removed; Git history preserves old attempts.
"""

from __future__ import annotations

import datetime
import re
import sqlite3
from pathlib import Path

from claims_sample.good.models import (
    POLICY_NUMBER_PATTERN,
    RISK_HIGH_CLAIMS_THRESHOLD,
    RISK_MATURE_DRIVER_THRESHOLD,
    RISK_MODERATE_CLAIMS_THRESHOLD,
    RISK_YOUNG_DRIVER_THRESHOLD,
    PolicyHolder,
)

# ---------------------------------------------------------------------------
# Risk scoring — weights live in one place, not scattered through if-chains.
# ---------------------------------------------------------------------------

_AGE_RISK_POINTS = {
    "young": 30,    # age < RISK_YOUNG_DRIVER_THRESHOLD
    "mature": 10,   # RISK_YOUNG_DRIVER_THRESHOLD ≤ age < RISK_MATURE_DRIVER_THRESHOLD
    "senior": 0,
}

_CLAIMS_RISK_POINTS = {
    "high": 50,     # prior_claims > RISK_HIGH_CLAIMS_THRESHOLD
    "moderate": 20, # prior_claims > RISK_MODERATE_CLAIMS_THRESHOLD
    "low": 0,
}

_LOCATION_RISK_POINTS = {
    "urban": 15,
    "suburban": 0,
    "rural": -5,
}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_policy_number(policy_number: str) -> bool:
    """
    Return True if *policy_number* matches the LMI format (``LMI`` + 8 digits).

    >>> validate_policy_number("LMI12345678")
    True
    >>> validate_policy_number("12345678")
    False
    """
    return bool(re.match(POLICY_NUMBER_PATTERN, policy_number))


# ---------------------------------------------------------------------------
# Database access
# ---------------------------------------------------------------------------


def lookup_policy(policy_number: str, db_path: Path) -> dict | None:
    """
    Fetch a policy row from the database by policy number.

    Uses a parameterised query (``?`` placeholder) to prevent SQL injection —
    unlike the string-concatenation approach in the bad version.

    Parameters
    ----------
    policy_number:
        The LMI-format policy identifier.
    db_path:
        Filesystem path to the SQLite database.

    Returns
    -------
    dict or None
        Row data as a dictionary, or ``None`` if not found.
    """
    if not validate_policy_number(policy_number):
        raise ValueError(f"Invalid policy number format: {policy_number!r}")

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM policies WHERE policy_number = ?",
            (policy_number,),   # ✅ parameterised — no injection risk
        )
        row = cursor.fetchone()

    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Policy state
# ---------------------------------------------------------------------------


def is_policy_active(expiration_date: datetime.date) -> bool:
    """
    Return True if the policy has not yet expired.

    Accepts a ``datetime.date`` — callers are responsible for parsing their
    own date strings, avoiding the ambiguous format problem in the bad version.

    >>> import datetime
    >>> is_policy_active(datetime.date(2099, 1, 1))
    True
    >>> is_policy_active(datetime.date(2000, 1, 1))
    False
    """
    return expiration_date > datetime.date.today()


# ---------------------------------------------------------------------------
# Risk scoring
# ---------------------------------------------------------------------------


def calculate_risk_score(
    age: int,
    prior_claims: int,
    location: str,
) -> int:
    """
    Compute a risk score for underwriting purposes.

    Higher scores indicate higher risk. Scoring weights are defined in
    module-level dicts so they can be adjusted without touching control flow.

    Parameters
    ----------
    age:
        Policyholder's age in years.
    prior_claims:
        Number of claims filed in the last three years.
    location:
        One of ``"urban"``, ``"suburban"``, or ``"rural"``.

    Returns
    -------
    int
        Risk score (higher = riskier).
    """
    if age < RISK_YOUNG_DRIVER_THRESHOLD:
        age_points = _AGE_RISK_POINTS["young"]
    elif age < RISK_MATURE_DRIVER_THRESHOLD:
        age_points = _AGE_RISK_POINTS["mature"]
    else:
        age_points = _AGE_RISK_POINTS["senior"]

    if prior_claims > RISK_HIGH_CLAIMS_THRESHOLD:
        claims_points = _CLAIMS_RISK_POINTS["high"]
    elif prior_claims > RISK_MODERATE_CLAIMS_THRESHOLD:
        claims_points = _CLAIMS_RISK_POINTS["moderate"]
    else:
        claims_points = _CLAIMS_RISK_POINTS["low"]

    location_points = _LOCATION_RISK_POINTS.get(location, 0)

    return age_points + claims_points + location_points
