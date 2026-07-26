#!/usr/bin/env python3

"""
fetch_statistics.py

Collect team statistics for validated fixtures.

Input:
    data/fixtures_validated.json

Output:
    data/statistics.json


Features collected:

- Goals scored average
- Goals conceded average
- Home strength
- Away strength
- League position
- Elo rating
- Recent form
"""


from pathlib import Path
import json
import os
import time
import requests
from datetime import datetime, timezone



# --------------------------------------------------
# Paths
# --------------------------------------------------

FIXTURE_FILE = Path(
    "data/fixtures_validated.json"
)


OUTPUT_FILE = Path(
    "data/statistics.json"
)



# --------------------------------------------------
# API Configuration
# --------------------------------------------------

API_URL = os.getenv(
    "FOOTBALL_STATS_API",
    "https://api.example.com"
)


API_KEY = os.getenv(
    "FOOTBALL_API_KEY",
)



HEADERS = {

    "Accept": "application/json",

    "Authorization":
        f"Bearer {API_KEY}"

}



# --------------------------------------------------
# Load Fixtures
# --------------------------------------------------


def load_fixtures():

    if not FIXTURE_FILE.exists():

        raise FileNotFoundError(
            "fixtures_validated.json missing"
        )


    with open(
        FIXTURE_FILE,
        encoding="utf-8"
    ) as file:

        data=json.load(file)


    return data.get(
        "fixtures",
        []
    )



# --------------------------------------------------
# API Wrapper
# --------------------------------------------------


def api_request(endpoint):

    try:

        response=requests.get(

            f"{API_URL}/{endpoint}",

            headers=HEADERS,

            timeout=30

        )


        response.raise_for_status()


        return response.json()


    except Exception as error:


        print(
            "API error:",
            error
        )


        return {}



# --------------------------------------------------
# Team Statistics
# --------------------------------------------------


def get_team_statistics(team):


    data = api_request(

        f"teams/{team}/statistics"

    )



    return {


        "team":

            team,



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
                0
            ),



        "elo_rating":

            data.get(
                "elo_rating",
                0
            )

    }



# --------------------------------------------------
# Head To Head
# --------------------------------------------------


def get_h2h(home, away):


    data = api_request(

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



# --------------------------------------------------
# Build Statistics
# --------------------------------------------------


def build_statistics(fixtures):


    cache={}

    results=[]



    for index, fixture in enumerate(
        fixtures,
        start=1
    ):


        home = fixture["home"]

        away = fixture["away"]



        print(

            f"Collecting {index}/{len(fixtures)} "
            f"{home} vs {away}"

        )



        if home not in cache:


            cache[home] = (
                get_team_statistics(home)
            )


            time.sleep(1)



        if away not in cache:


            cache[away] = (
                get_team_statistics(away)
            )


            time.sleep(1)



        results.append({

            "fixture_id":

                fixture["id"],



            "teams":

                f"{home} vs {away}",



            "home":

                cache[home],



            "away":

                cache[away],



            "league":

                fixture.get(
                    "league"
                ),



            "kickoff":

                fixture.get(
                    "kickoff"
                ),



            "h2h":

                get_h2h(
                    home,
                    away
                )

        })


    return results



# --------------------------------------------------
# Save
# --------------------------------------------------


def save_statistics(data):


    OUTPUT_FILE.parent.mkdir(
        exist_ok=True
    )



    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:


        json.dump({

            "generated":

                datetime.now(
                    timezone.utc
                ).isoformat(),



            "matches":

                len(data),



            "statistics":

                data


        },
        file,
        indent=2
        )



# --------------------------------------------------
# Main Function
# --------------------------------------------------


def fetch_statistics():


    fixtures = load_fixtures()



    if not fixtures:

        raise RuntimeError(
            "No fixtures available"
        )



    statistics = build_statistics(
        fixtures
    )



    save_statistics(
        statistics
    )



    print(
        f"Saved statistics for {len(statistics)} matches"
    )



if __name__ == "__main__":

    fetch_statistics()
