#!/usr/bin/env python3
"""
probability_matches.py

Combines:
- Machine learning predictions
- Bookmaker odds probabilities

Creates final Double Chance probabilities.

Input:
    engine/data/predictions.json
    engine/data/odds.json (optional)

Output:
    engine/data/probability_results.json

"""


from __future__ import annotations

import json
import os
from pathlib import Path


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PREDICTIONS_FILE = Path(
    "engine/data/predictions.json"
)

ODDS_FILE = Path(
    "engine/data/odds.json"
)

OUTPUT_FILE = Path(
    "engine/data/probability_results.json"
)


ML_WEIGHT = float(
    os.getenv(
        "ML_WEIGHT",
        "0.40"
    )
)


ODDS_WEIGHT = float(
    os.getenv(
        "ODDS_WEIGHT",
        "0.60"
    )
)



# --------------------------------------------------
# Load files
# --------------------------------------------------


def load_json(file):

    if not file.exists():
        raise FileNotFoundError(
            f"{file} missing"
        )

    with open(
        file,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)



# --------------------------------------------------
# Odds conversion
# --------------------------------------------------


def odds_to_probability(
    odds
):

    """
    Convert decimal odds into
    implied probability.

    Example:

    1.50 odds

    =

    66.7%
    """


    if not odds:
        return None


    try:

        return round(
            1 / float(odds),
            3
        )

    except:

        return None



def get_market_odds(
    odds_data,
    fixture_id
):

    """
    Extract DC odds.

    Expected format:

    {
      fixture_id:
      {
        "1X":1.20,
        "X2":2.00,
        "12":1.30
      }
    }

    """

    if not odds_data:
        return None


    return odds_data.get(
        str(fixture_id)
    )



# --------------------------------------------------
# Probability fusion
# --------------------------------------------------


def combine_probability(
    ml_probability,
    odds_probability
):


    if odds_probability is None:

        return round(
            ml_probability,
            3
        )


    combined = (

        ml_probability
        *
        ML_WEIGHT

        +

        odds_probability
        *
        ODDS_WEIGHT

    )


    return round(
        combined,
        3
    )



# --------------------------------------------------
# Process matches
# --------------------------------------------------


def process_match(
    prediction,
    odds_data
):


    fixture_id = str(
        prediction["fixture_id"]
    )


    odds = get_market_odds(
        odds_data,
        fixture_id
    )


    final = {}


    for market, ml_value in (
        prediction["probabilities"]
        .items()
    ):


        odds_probability = None


        if odds:

            decimal_odds = odds.get(
                market
            )

            odds_probability = (
                odds_to_probability(
                    decimal_odds
                )
            )


        final[market] = combine_probability(
            ml_value,
            odds_probability
        )


    best_pick = max(
        final,
        key=final.get
    )


    confidence = round(
        final[best_pick]
        *
        100,
        2
    )


    return {


        "fixture_id":
            prediction["fixture_id"],


        "teams":
            prediction["teams"],


        "markets":
            final,


        "recommended":
            best_pick,


        "confidence":
            confidence,


        "sources":
        {

            "ml_weight":
                ML_WEIGHT,

            "odds_weight":
                ODDS_WEIGHT

        }

    }



# --------------------------------------------------
# Save
# --------------------------------------------------


def save_results(
    results
):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(

            {
                "matches":
                    len(results),

                "results":
                    results

            },

            f,

            indent=2

        )



# --------------------------------------------------
# Main
# --------------------------------------------------


def main():


    predictions = load_json(
        PREDICTIONS_FILE
    )


    odds_data = {}


    if ODDS_FILE.exists():

        odds_data = load_json(
            ODDS_FILE
        )



    results = []


    for prediction in (
        predictions["predictions"]
    ):

        result = process_match(
            prediction,
            odds_data
        )

        results.append(
            result
        )



    # Highest confidence first

    results.sort(
        key=lambda x:
        x["confidence"],
        reverse=True
    )


    save_results(
        results
    )


    print(
        f"Processed {len(results)} matches"
    )

    print(
        f"Saved {OUTPUT_FILE}"
    )



if __name__ == "__main__":

    main()
