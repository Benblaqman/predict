#!/usr/bin/env python3

"""
predict_matches.py

Creates match probabilities from team statistics.

Input:
    data/statistics.json

Output:
    data/predictions.json


Produces:

- Home win probability
- Draw probability
- Away win probability
- Double chance markets
- Recommended market
- Confidence score

"""


from pathlib import Path
import json
from datetime import datetime, timezone



INPUT_FILE = Path(
    "data/statistics.json"
)


OUTPUT_FILE = Path(
    "data/predictions.json"
)



# --------------------------------------------------
# Helpers
# --------------------------------------------------


def safe(value):

    if value is None:
        return 0

    if isinstance(value, (int, float)):
        return value

    return 0



def normalize_probabilities(
    home,
    away
):

    total = home + away


    if total > 0.90:

        factor = 0.90 / total

        home *= factor

        away *= factor



    draw = 1 - home - away



    if draw < 0:

        draw = 0



    return (

        round(home, 3),

        round(draw, 3),

        round(away, 3)

    )



# --------------------------------------------------
# Prediction Model
# --------------------------------------------------


def calculate_prediction(match):


    home = match["home"]

    away = match["away"]



    home_attack = safe(
        home.get(
            "goals_scored_avg"
        )
    )


    away_attack = safe(
        away.get(
            "goals_scored_avg"
        )
    )



    home_defence = safe(
        home.get(
            "goals_conceded_avg"
        )
    )


    away_defence = safe(
        away.get(
            "goals_conceded_avg"
        )
    )



    elo_difference = (

        safe(
            home.get(
                "elo_rating"
            )
        )

        -

        safe(
            away.get(
                "elo_rating"
            )
        )

    )



    home_strength = safe(
        home.get(
            "home_strength"
        )
    )


    away_strength = safe(
        away.get(
            "away_strength"
        )
    )



    home_score = (

        home_attack * 35

        -

        home_defence * 15

        +

        elo_difference / 20

        +

        home_strength

    )



    away_score = (

        away_attack * 35

        -

        away_defence * 15

        -

        elo_difference / 20

        +

        away_strength

    )



    difference = (
        home_score - away_score
    )



    home_probability = (

        0.50

        +

        difference / 100

    )



    home_probability = max(

        0.15,

        min(
            home_probability,
            0.80
        )

    )



    away_probability = (

        0.50

        -

        difference / 100

    )



    away_probability = max(

        0.10,

        min(
            away_probability,
            0.70
        )

    )



    home_probability, draw_probability, away_probability = normalize_probabilities(

        home_probability,

        away_probability

    )



    return {


        "home_win":

            home_probability,


        "draw":

            draw_probability,


        "away_win":

            away_probability

    }



# --------------------------------------------------
# Double Chance
# --------------------------------------------------


def create_double_chance(prob):


    return {


        "1X":

            round(

                prob["home_win"]

                +

                prob["draw"],

                3

            ),



        "X2":

            round(

                prob["away_win"]

                +

                prob["draw"],

                3

            ),



        "12":

            round(

                prob["home_win"]

                +

                prob["away_win"],

                3

            )

    }



# --------------------------------------------------
# Prediction Runner
# --------------------------------------------------


def predict_matches():


    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "statistics.json missing"
        )



    with open(
        INPUT_FILE,
        encoding="utf-8"
    ) as file:

        data = json.load(file)



    predictions = []



    for match in data.get(
        "statistics",
        []
    ):



        probabilities = calculate_prediction(
            match
        )



        double_chance = create_double_chance(
            probabilities
        )



        recommended = max(

            double_chance,

            key=double_chance.get

        )



        confidence = round(

            double_chance[recommended]
            * 100,

            2

        )



        predictions.append({


            "fixture_id":

                match.get(
                    "fixture_id"
                ),



            "teams":

                match.get(
                    "teams"
                ),



            "league":

                match.get(
                    "league"
                ),



            "kickoff":

                match.get(
                    "kickoff"
                ),



            "probabilities":

                probabilities,



            "double_chance":

                double_chance,



            "recommended_market":

                recommended,



            "confidence":

                confidence

        })



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

                "generated":

                    datetime.now(
                        timezone.utc
                    ).isoformat(),


                "matches":

                    len(predictions),


                "predictions":

                    predictions

            },

            file,

            indent=2,

            ensure_ascii=False

        )



    print(
        f"Generated {len(predictions)} predictions"
    )



if __name__ == "__main__":

    predict_matches()
