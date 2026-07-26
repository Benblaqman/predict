#!/usr/bin/env python3
"""
fetch_statistics.py

Loads fixtures.json and collects team statistics.

Output:
engine/data/statistics.json

Collected features:

- Recent form
- Goals scored
- Goals conceded
- Home performance
- Away performance
- League position
- H2H summary
- Team strength rating

"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests


# -------------------------------------------------------
# Configuration
# -------------------------------------------------------

FIXTURE_FILE = Path(
    "engine/data/fixtures.json"
)

OUTPUT_FILE = Path(
    "engine/data/statistics.json"
)


API_KEY = os.getenv(
    "FOOTBALL_API_KEY"
)

API_URL = os.getenv(
    "FOOTBALL_STATS_API",
    "https://api.example.com"
)


HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------


def load_fixtures():

    if not FIXTURE_FILE.exists():
        raise FileNotFoundError(
            "fixtures.json not found"
        )

    with open(
        FIXTURE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data["fixtures"]



def api_get(endpoint):

    """
    Generic API request wrapper.
    """

    response = requests.get(
        f"{API_URL}/{endpoint}",
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.json()



# -------------------------------------------------------
# Statistics Provider
# -------------------------------------------------------


class StatisticsProvider:


    def team_statistics(
        self,
        team
    ):

        """
        Get team statistics.

        Replace API mapping here.
        """

        data = api_get(
            f"teams/{team}/statistics"
        )


        return {

            "team": team,

            "form_last_5":
                data.get(
                    "form_last_5",
                    []
                ),

            "wins_last_5":
                data.get(
                    "wins_last_5",
                    0
                ),

            "draws_last_5":
                data.get(
                    "draws_last_5",
                    0
                ),

            "losses_last_5":
                data.get(
                    "losses_last_5",
                    0
                ),


            "goals_scored_avg":
                data.get(
                    "goals_scored_avg",
                    0
                ),


            "goals_conceded_avg":
                data.get(
                    "goals_conceded_avg",
                    0
                ),


            "home_strength":
                data.get(
                    "home_strength",
                    0
                ),


            "away_strength":
                data.get(
                    "away_strength",
                    0
                ),


            "league_position":
                data.get(
                    "league_position",
                    None
                ),


            "elo_rating":
                data.get(
                    "elo_rating",
                    0
                )

        }



    def head_to_head(
        self,
        home,
        away
    ):

        data = api_get(
            f"h2h/{home}/{away}"
        )


        return {

            "meetings":
                data.get(
                    "meetings",
                    0
                ),

            "home_wins":
                data.get(
                    "home_wins",
                    0
                ),

            "draws":
                data.get(
                    "draws",
                    0
                ),

            "away_wins":
                data.get(
                    "away_wins",
                    0
                )
        }



# -------------------------------------------------------
# Build Match Features
# -------------------------------------------------------


def build_statistics(
    fixtures
):

    provider = StatisticsProvider()

    results = []


    cache = {}


    for index, match in enumerate(
        fixtures,
        start=1
    ):

        home = match["home"]
        away = match["away"]


        print(
            f"Analysing {index}/20:"
            f" {home} vs {away}"
        )


        if home not in cache:

            cache[home] = (
                provider
                .team_statistics(home)
            )


            time.sleep(1)


        if away not in cache:

            cache[away] = (
                provider
                .team_statistics(away)
            )


            time.sleep(1)



        h2h = (
            provider
            .head_to_head(
                home,
                away
            )
        )


        results.append({

            "fixture_id":
                match["id"],


            "match": {

                "home": home,

                "away": away,

                "league":
                    match["league"],

                "kickoff":
                    match["kickoff"]

            },


            "home_stats":
                cache[home],


            "away_stats":
                cache[away],


            "h2h":
                h2h

        })


    return results



# -------------------------------------------------------
# Save
# -------------------------------------------------------


def save_statistics(data):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "matches":
                    len(data),

                "statistics":
                    data

            },
            file,
            indent=2,
            ensure_ascii=False
        )


# -------------------------------------------------------
# Main
# -------------------------------------------------------


def main():

    print(
        "Loading fixtures..."
    )

    fixtures = load_fixtures()


    print(
        f"Found {len(fixtures)} fixtures"
    )


    statistics = build_statistics(
        fixtures
    )


    save_statistics(
        statistics
    )


    print(
        "Statistics saved:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":

    main()
