#!/usr/bin/env python3

"""
predict_matches.py

Creates match probabilities from statistics.

Input:
data/statistics.json

Output:
data/predictions.json


Produces:

- Home win probability
- Draw probability
- Away win probability
- Double chance probabilities

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

    if isinstance(value,(int,float)):
        return value

    return 0



# --------------------------------------------------
# Prediction Model
# --------------------------------------------------


def calculate_prediction(match):


    home = match["home"]

    away = match["away"]



    # Attack strength

    home_attack = safe(
        home["goals_scored_avg"]
    )


    away_attack = safe(
        away["goals_scored_avg"]
    )



    # Defensive strength

    home_defence = safe(
        home["goals_conceded_avg"]
    )


    away_defence = safe(
        away["goals_conceded_avg"]
    )



    # Elo difference

    elo_difference = (

        safe(
            home["elo_rating"]
        )

        -

        safe(
            away["elo_rating"]
        )

    )



    # Home advantage

    home_advantage = safe(
        home["home_strength"]
    )


    away_strength = safe(
        away["away_strength"]
    )



    # -------------------------------
    # Weighted model
    # -------------------------------


    home_score = (

        home_attack * 35

        -

        home_defence * 15

        +

        elo_difference / 20

        +

        home_advantage

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



    # limits

    home_probability = max(
        0.15,
        min(
            home_probability,
            0.80
        )
    )



    away_probability = (
        1
        -
        home_probability
        -
        0.25
    )



    away_probability=max(
        0.10,
        away_probability
    )



    draw_probability = (
        1
        -
        home_probability
        -
        away_probability
    )



    return {


        "home_win":
            round(
                home_probability,
                3
            ),


        "draw":
            round(
                draw_probability,
                3
            ),


        "away_win":
            round(
                away_probability,
                3
            )

    }



# --------------------------------------------------
# Double Chance
# --------------------------------------------------


def double_chance(prob):


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
# Main Prediction
# --------------------------------------------------


def predict_matches():


    with open(
        INPUT_FILE,
        encoding="utf-8"
    ) as file:


        data=json.load(file)



    predictions=[]



    for match in data["statistics"]:



        probability = calculate_prediction(
            match
        )



        dc = double_chance(
            probability
        )



        predictions.append({


            "fixture_id":

                match["fixture_id"],



            "teams":

                match["teams"],



            "probabilities":

                probability,



            "double_chance":

                dc

        })



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

                len(predictions),


            "predictions":

                predictions


        },
        file,
        indent=2
        )



    print(
        f"Generated {len(predictions)} predictions"
    )



if __name__=="__main__":

    predict_matches()
