#!/usr/bin/env python3
"""
validate_matches.py

Validates engine/data/fixtures.json

Checks:
- File exists
- JSON is valid
- Exactly MATCH_LIMIT fixtures
- No duplicate fixtures
- Future kickoff times
- Required fields exist
- Home != Away
- Team names are not empty

Exit code:
0 = success
1 = validation failed
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

MATCH_LIMIT = int(os.getenv("MATCH_LIMIT", "20"))

FIXTURE_FILE = Path("engine/data/fixtures.json")


def fail(message: str) -> None:
    print(f"❌ VALIDATION FAILED: {message}")
    sys.exit(1)


def success(message: str) -> None:
    print(f"✅ {message}")


def parse_datetime(value: str) -> datetime:
    """
    Parse an ISO-8601 datetime string.
    """
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main():

    if not FIXTURE_FILE.exists():
        fail(f"{FIXTURE_FILE} does not exist.")

    try:
        with open(FIXTURE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        fail(f"Unable to read JSON: {e}")

    fixtures = data.get("fixtures")

    if fixtures is None:
        fail("Missing 'fixtures' key.")

    if not isinstance(fixtures, list):
        fail("'fixtures' must be a list.")

    if len(fixtures) != MATCH_LIMIT:
        fail(
            f"Expected {MATCH_LIMIT} fixtures but found {len(fixtures)}."
        )

    now = datetime.now(timezone.utc)

    seen = set()

    for index, match in enumerate(fixtures, start=1):

        required = [
            "id",
            "league",
            "kickoff",
            "home",
            "away",
        ]

        for field in required:
            if field not in match:
                fail(f"Fixture {index} missing '{field}'.")

        home = str(match["home"]).strip()
        away = str(match["away"]).strip()

        if not home:
            fail(f"Fixture {index}: empty home team.")

        if not away:
            fail(f"Fixture {index}: empty away team.")

        if home == away:
            fail(
                f"Fixture {index}: home and away teams are identical."
            )

        try:
            kickoff = parse_datetime(match["kickoff"])
        except Exception:
            fail(
                f"Fixture {index}: invalid kickoff '{match['kickoff']}'."
            )

        if kickoff <= now:
            fail(
                f"Fixture {index}: kickoff is not in the future."
            )

        key = (
            home.lower(),
            away.lower(),
            kickoff.isoformat(),
        )

        if key in seen:
            fail(
                f"Duplicate fixture detected: {home} vs {away}"
            )

        seen.add(key)

    success(f"{len(fixtures)} fixtures validated successfully.")


if __name__ == "__main__":
    main()
