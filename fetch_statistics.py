#!/usr/bin/env python3

"""
Collect team statistics.
"""


from pathlib import Path
import json
import os
import requests
import time



FIXTURE_FILE = Path(
    "data/fixtures.json"
)


OUTPUT_FILE = Path(
    "data/statistics.json"
)



API_URL = os.getenv(
    "FOOTBALL_STATS_API",
    "https://api.example.com"
)


API_KEY = os.getenv(
    "FOOTBALL_API_KEY"
)



HEADERS = {

    "Accept":"application/json",

    "Authorization":
        f"Bearer {API_KEY}"

}



def api_get(endpoint):

    response = requests.get(

        f"{API_URL}/{endpoint}",

        headers=HEADERS,

        timeout=30
    )

    response.raise_for_status()

    return response.json()



def load_fixtures():

    with open(
        FIXTURE_FILE,
        encoding="utf-8"
    ) as f:

        return json.load(f)["fixtures"]



def get_team_statistics(team):


    try:

        data = api_get(
            f"teams/{team}/statistics"
        )


    except Exception:

        data = {}



    return {


        "team":team,


        "form":

            data.get(
                "form_last_5",
                []
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



def fetch_statistics():


    fixtures = load_fixtures()


    cache={}


    results=[]



    for match in fixtures:


        home = match["home"]

        away = match["away"]



        if home not in cache:

            cache[home] = get_team_statistics(home)

            time.sleep(1)



        if away not in cache:

            cache[away] = get_team_statistics(away)

            time.sleep(1)



        results.append({

            "fixture_id":
                match["id"],


            "teams":
                f"{home} vs {away}",


            "home":
                cache[home],


            "away":
                cache[away]

        })



    OUTPUT_FILE.parent.mkdir(
        exist_ok=True
    )


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump({

            "matches":
                len(results),

            "statistics":
                results

        },f,indent=2)



    print(
        "Statistics saved"
    )



if __name__=="__main__":

    fetch_statistics()
