#!/usr/bin/env python3

"""
probability_matches.py

Converts model predictions into betting recommendations.

Input:
    data/predictions.json

Output:
    data/probability_results.json


Creates:

- Recommended market
- Confidence
- Estimated odds
- Risk category
- Value score

Compatible with:
    Optimizer.py
"""


from pathlib import Path
import json
from datetime import datetime, timezone



INPUT_FILE = Path(
    "data/predictions.json"
)


OUTPUT_FILE = Path(
    "data/probability_results.json"
)



# --------------------------------------------------
# Configuration
# --------------------------------------------------


MIN_CONFIDENCE = 0.55



# --------------------------------------------------
# Risk Engine
# --------------------------------------------------


def risk_level(confidence):


    if confidence >= 0.85:

        return "ULTRA_SAFE"


    elif confidence >= 0.75:

        return "SAFE"


    elif confidence >= 0.65:

        return "MEDIUM"


    else:

        return "HIGH"



# --------------------------------------------------
# Odds Calculation
# --------------------------------------------------


def calculate_odds(probability):


    if probability <= 0:

        return 0



    odds = 1 / probability



    # bookmaker margin adjustment

    odds *= 0.92



    return round(
        max(1.05, odds),
        2
    )



# --------------------------------------------------
# Value Calculation
# --------------------------------------------------


def calculate_value(
    probability,
    odds
):


    market_probability = 1 / odds



    value = (

        probability

        -

        market_probability

    )



    return round(
        value * 100,
        2
    )



# --------------------------------------------------
# Convert Prediction
# --------------------------------------------------


def process_prediction(match):


    market = match.get(
        "recommended_market"
    )


    probabilities = match.get(
        "double_chance",
        {}
    )


    probability = probabilities.get(
        market,
        0
    )



    if probability < MIN_CONFIDENCE:

        return None



    odds = calculate_odds(
        probability
    )



    confidence = round(

        probability * 100,

        2

    )



    return {


        "fixture_id":

            match.get(
                "fixture_id"
            ),



        "teams":

            match.get(
                "teams"
            ),



        "recommended":

            market,



        "confidence":

            confidence,



        "probability":

            probability,



        "odds":

            odds,



        "value":

            calculate_value(

                probability,

                odds

            ),



        "risk":

            risk_level(
                probability
            ),



        "league":

            match.get(
                "league"
            ),



        "kickoff":

            match.get(
                "kickoff"
            )

    }



# --------------------------------------------------
# Main
# --------------------------------------------------


def generate_probability_results():


    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "predictions.json missing"
        )



    with open(
        INPUT_FILE,
        encoding="utf-8"
    ) as file:


        data=json.load(file)



    results=[]



    for match in data.get(
        "predictions",
        []
    ):


        result = process_prediction(
            match
        )



        if result:

            results.append(
                result
            )



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


                "total_results":

                    len(results),


                "results":

                    results

            },

            file,

            indent=2,

            ensure_ascii=False

        )



    print(
        f"Generated {len(results)} probability results"
    )



if __name__ == "__main__":

    generate_probability_results()
