#!/usr/bin/env python3
"""
fetch_matches.py

Downloads today's football fixtures from the configured fixture provider,
selects the next available 20 matches, normalizes the data,
and saves engine/data/fixtures.json.

Output:
engine/data/fixtures.json
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

# --------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------

MATCH_LIMIT = int(os.getenv("MATCH_LIMIT", 20))

API_URL = os.getenv(
    "FIXTURE_API",
    "https://api.betika.com/v1/uo/matches?page=1",
)

HEADERS = {
    "User-Agent": "BetikaPredictionEngine/1.0",
    "Accept": "application/json",
}

OUTPUT_DIR = Path("engine/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "fixtures.json"

# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------


def normalize_team(name: str) -> str:
    """Normalize common team name variants."""

    aliases = {
        "Man Utd": "Manchester United",
        "Man United": "Manchester United",
        "Spurs": "Tottenham",
        "Inter": "Inter Milan",
    }

    return aliases.get(name.strip(), name.strip())


def parse_time(value: str):
    """
    Convert ISO datetime string to datetime.

    Returns None if parsing fails.
    """

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except Exception:
        return None


# --------------------------------------------------------------------
# Provider
# --------------------------------------------------------------------


class FixtureProvider:
    def fetch(self):

        response = requests.get(
            API_URL,
            headers=HEADERS,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()


# --------------------------------------------------------------------
# Extract Fixtures
# --------------------------------------------------------------------


def extract_matches(raw):

    fixtures = []

    now = datetime.now(timezone.utc)

    # Change this mapping if your provider's JSON differs.
    for item in raw.get("data", []):

        if item.get("sport") != "football":
            continue

        kickoff = parse_time(item.get("kickoff"))

        if kickoff is None:
            continue

        if kickoff <= now:
            continue

        fixture = {
            "id": item.get("id"),
            "league": item.get("league"),
            "kickoff": kickoff.isoformat(),
            "home": normalize_team(item.get("home_team")),
            "away": normalize_team(item.get("away_team")),
        }

        fixtures.append(fixture)

    fixtures.sort(key=lambda x: x["kickoff"])

    # Remove duplicates

    unique = []

    seen = set()

    for match in fixtures:

        key = (
            match["home"],
            match["away"],
            match["kickoff"],
        )

        if key in seen:
            continue

        seen.add(key)

        unique.append(match)

    return unique[:MATCH_LIMIT]


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------


def main():

    print("Downloading fixtures...")

    provider = FixtureProvider()

    raw = provider.fetch()

    fixtures = extract_matches(raw)

    if len(fixtures) < MATCH_LIMIT:
        raise RuntimeError(
            f"Expected {MATCH_LIMIT} matches but found {len(fixtures)}"
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generated": datetime.now(
                    timezone.utc
                ).isoformat(),
                "count": len(fixtures),
                "fixtures": fixtures,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Saved {len(fixtures)} fixtures.")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
