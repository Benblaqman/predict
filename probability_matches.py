#!/usr/bin/env python3
"""
probability_matches.py

Combines:
- ML probabilities
- bookmaker odds probabilities

Creates final betting probabilities.

Input:
    engine/data/predictions.json
    engine/data/odds.json

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
    os.getenv("ML_WEIGHT", "0.40")
)

ODDS_WEIGHT = float(
    os.getenv("ODDS_WEIGHT", "0.60")
)


# --------------------------------------------------
# Market Rules
# --------------------------------------------------

MARKET_PRIORITY = {

    "1X": 3,
    "X2": 3,
    "12": 2

}


SAFE_MARKETS = {
    "1X",
    "X2"
}



# --------------------------------------------------
# Helpers
# --------------------------------------------------


def load_json(path):

    if not path.exists():

        raise FileNotFoundError(
            path
        )


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)



def odds_probability(odds):

    try:

        return round(
            1 / float(odds),
            3
        )

    except:

        return None



def classify_risk(
    confidence,
    market
):

    if (
        confidence >= 85
        and market in SAFE_MARKETS
    ):
        return "ULTRA_SAFE"


    if confidence >= 80:
        return "SAFE"


    if confidence >= 72:
        return "MEDIUM"


    return "HIGH"



def combine(
    ml,
    odds
):

    if odds is None:

        return round(
            ml,
            3
        )


    return round(
        (
            ml * ML_WEIGHT
            +
            odds * ODDS_WEIGHT
        ),
        3
    )



# --------------------------------------------------
# Market Selection
# --------------------------------------------------


def choose_market(markets):


    ranked = sorted(

        markets.items(),

        key=lambda item:
        (
            item[1],
            MARKET_PRIORITY.get(
                item[0],
                0
            )
        ),

        reverse=True
    )


    best_market, probability = ranked[0]


    # Avoid risky 12 market
    if best_market == "12":

        safe_candidates = [

            x for x in ranked

            if x[0] in SAFE_MARKETS

        ]


        if safe_candidates:

            safe_market, safe_probability = (
                safe_candidates[0]
            )


            if (
                probability
                -
                safe_probability
                <
                0.06
            ):

                best_market = safe_market
                probability = safe_probability


    return best_market, probability



# --------------------------------------------------
# Process
# --------------------------------------------------


def process_match(
    prediction,
    odds_data
):

    fixture_id = str(
        prediction["fixture_id"]
    )


    odds_markets = odds_data.get(
        fixture_id,
        {}
    )


    final_markets = {}


    for market, ml_probability in (
        prediction["probabilities"]
        .items()
    ):


        market_odds = odds_markets.get(
            market
        )


        final_markets[market] = combine(

            ml_probability,

            odds_probability(
                market_odds
            )

        )



    selected_market, confidence = choose_market(
        final_markets
    )


    confidence_percent = round(
        confidence * 100,
        2
    )


    odds = None


    if odds_markets.get(
        selected_market
    ):

        odds = float(
            odds_markets[selected_market]
        )


    else:

        odds = round(
            1 / confidence,
            2
        )



    return {

        "fixture_id":
            prediction["fixture_id"],


        "teams":
            prediction["teams"],


        "markets":
            final_markets,


        "recommended":
            selected_market,


        "confidence":
            confidence_percent,


        "odds":
            odds,


        "risk":
            classify_risk(
                confidence_percent,
                selected_market
            )

    }



# --------------------------------------------------
# Main
# --------------------------------------------------


def main():

    predictions = load_json(
        PREDICTIONS_FILE
    )


    odds = {}


    if ODDS_FILE.exists():

        odds = load_json(
            ODDS_FILE
        )


    results = []


    for match in predictions["predictions"]:

        results.append(

            process_match(
                match,
                odds
            )

        )


    results.sort(

        key=lambda x:
        x["confidence"],

        reverse=True

    )


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:


        json.dump(

            {
                "matches":
                    len(results),

                "results":
                    results

            },

            file,

            indent=2

        )


    print(
        f"Created {len(results)} probabilities"
    )



if __name__ == "__main__":

    main()
