#!/usr/bin/env python3
"""
predict_matches.py

Creates Double Chance probabilities from match statistics.

Input:
    engine/data/statistics.json

Output:
    engine/data/predictions.json


Markets:

1X  = Home win or Draw
X2  = Away win or Draw
12  = Either team wins


The model can later be replaced with a trained ML model.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np


# --------------------------------------------------
# Paths
# --------------------------------------------------

STATISTICS_FILE = Path(
    "engine/data/statistics.json"
)

OUTPUT_FILE = Path(
    "engine/data/predictions.json"
)

MODEL_FILE = Path(
    "engine/models/dc_model.pkl"
)


# --------------------------------------------------
# Load data
# --------------------------------------------------


def load_statistics():

    if not STATISTICS_FILE.exists():
        raise FileNotFoundError(
            "statistics.json missing"
        )


    with open(
        STATISTICS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)



# --------------------------------------------------
# ML Model
# --------------------------------------------------


def load_model():

    """
    Loads trained ML model.

    Example:
    RandomForestClassifier
    XGBoost
    LogisticRegression

    """

    if MODEL_FILE.exists():

        with open(
            MODEL_FILE,
            "rb"
        ) as file:

            return pickle.load(file)


    return None



# --------------------------------------------------
# Feature Engineering
# --------------------------------------------------


def safe_number(value):

    if value is None:
        return 0

    if isinstance(value, (int, float)):
        return value

    return 0



def create_features(match):


    home = match["home_stats"]

    away = match["away_stats"]


    features = [

        # attack
        safe_number(
            home["goals_scored_avg"]
        ),

        safe_number(
            away["goals_scored_avg"]
        ),


        # defence
        safe_number(
            home["goals_conceded_avg"]
        ),

        safe_number(
            away["goals_conceded_avg"]
        ),


        # strength
        safe_number(
            home["elo_rating"]
        ),

        safe_number(
            away["elo_rating"]
        ),


        # home/away advantage
        safe_number(
            home["home_strength"]
        ),

        safe_number(
            away["away_strength"]
        ),


        # league position
        safe_number(
            home["league_position"]
        ),

        safe_number(
            away["league_position"]
        )

    ]


    return np.array(
        features
    ).reshape(
        1, -1
    )



# --------------------------------------------------
# Baseline Prediction
# --------------------------------------------------


def baseline_prediction(match):

    """
    Temporary model.

    Used until enough historical
    results exist for training.
    """


    home = match["home_stats"]

    away = match["away_stats"]


    home_power = (

        safe_number(
            home["elo_rating"]
        )

        +

        safe_number(
            home["goals_scored_avg"]
        )
        * 100

    )


    away_power = (

        safe_number(
            away["elo_rating"]
        )

        +

        safe_number(
            away["goals_scored_avg"]
        )
        * 100

    )


    difference = (
        home_power - away_power
    )


    home_probability = (
        0.50
        +
        difference / 3000
    )


    home_probability = max(
        0.15,
        min(
            home_probability,
            0.85
        )
    )


    draw_probability = 0.25


    away_probability = (
        1
        -
        home_probability
        -
        draw_probability
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
# Convert probabilities
# --------------------------------------------------


def convert_double_chance(result):


    home = result["home_win"]

    draw = result["draw"]

    away = result["away_win"]


    return {


        "1X":

            round(
                home + draw,
                3
            ),


        "X2":

            round(
                away + draw,
                3
            ),


        "12":

            round(
                home + away,
                3
            )

    }



# --------------------------------------------------
# Prediction
# --------------------------------------------------


def predict_match(
    match,
    model
):


    if model:


        features = create_features(
            match
        )


        probabilities = (
            model
            .predict_proba(
                features
            )[0]
        )


        result = {

            "home_win":
                float(
                    probabilities[0]
                ),

            "draw":
                float(
                    probabilities[1]
                ),

            "away_win":
                float(
                    probabilities[2]
                )
        }


    else:

        result = (
            baseline_prediction(
                match
            )
        )


    dc = convert_double_chance(
        result
    )


    best_market = max(
        dc,
        key=dc.get
    )


    return {


        "fixture_id":
            match["fixture_id"],


        "teams":
        {

            "home":
                match["match"]["home"],

            "away":
                match["match"]["away"]

        },


        "probabilities":
            dc,


        "best_pick":
            best_market,


        "confidence":
            round(
                dc[best_market]
                *
                100,
                2
            )

    }



# --------------------------------------------------
# Save
# --------------------------------------------------


def save_predictions(
    predictions
):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(

            {
                "matches":
                    len(predictions),

                "predictions":
                    predictions

            },

            file,

            indent=2

        )



# --------------------------------------------------
# Main
# --------------------------------------------------


def main():


    data = load_statistics()


    model = load_model()


    predictions = []


    for match in data["statistics"]:


        prediction = predict_match(
            match,
            model
        )


        predictions.append(
            prediction
        )


    save_predictions(
        predictions
    )


    print(
        f"Generated {len(predictions)} predictions"
    )


if __name__ == "__main__":

    main()
