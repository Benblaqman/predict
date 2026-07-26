#!/usr/bin/env python3
"""
Optimizer.py

Creates optimized betting slips.

Input:
    engine/data/probability_results.json

Output:
    engine/data/optimized_slips.json

"""

from __future__ import annotations

import json
import random
from pathlib import Path
from datetime import datetime, timezone


# --------------------------------------------------
# Configuration
# --------------------------------------------------

INPUT_FILE = Path(
    "engine/data/probability_results.json"
)

OUTPUT_FILE = Path(
    "engine/data/optimized_slips.json"
)


TOTAL_SLIPS = 10

MATCHES_PER_SLIP = 5



# --------------------------------------------------
# Load data
# --------------------------------------------------


def load_matches():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"{INPUT_FILE} not found"
        )


    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)


    return data.get(
        "results",
        []
    )



# --------------------------------------------------
# Risk classification
# --------------------------------------------------


def risk_group(match):

    confidence = match.get(
        "confidence",
        0
    )


    market = match.get(
        "recommended"
    )


    if (
        confidence >= 85
        and market in ["1X", "X2"]
    ):

        return "ULTRA_SAFE"


    if confidence >= 80:

        return "SAFE"


    if confidence >= 72:

        return "MEDIUM"


    return "HIGH"



# --------------------------------------------------
# Ranking
# --------------------------------------------------


def rank_matches(matches):

    for match in matches:

        match["risk"] = risk_group(
            match
        )


        # optimizer score

        confidence = match.get(
            "confidence",
            0
        )


        odds = match.get(
            "odds",
            1
        )


        value_score = (
            confidence
            *
            float(odds)
        )


        match["score"] = round(
            value_score,
            2
        )


    return sorted(
        matches,
        key=lambda x:
        x["score"],
        reverse=True
    )



# --------------------------------------------------
# Create risk pools
# --------------------------------------------------


def build_pools(matches):


    pools = {

        "ULTRA_SAFE": [],

        "SAFE": [],

        "MEDIUM": [],

        "HIGH": []

    }


    for match in matches:

        pools[
            match["risk"]
        ].append(
            match
        )


    return pools



# --------------------------------------------------
# Select matches
# --------------------------------------------------


def select_matches(
    pool
):


    if len(pool) < MATCHES_PER_SLIP:

        return None


    return random.sample(
        pool,
        MATCHES_PER_SLIP
    )



# --------------------------------------------------
# Build slip
# --------------------------------------------------


def create_slip(
    matches,
    risk
):


    combined_odds = 1

    total_confidence = 0


    selections = []


    for match in matches:


        combined_odds *= float(
            match.get(
                "odds",
                1
            )
        )


        total_confidence += (
            match.get(
                "confidence",
                0
            )
        )


        selections.append(

            {

                "fixture_id":
                    match["fixture_id"],


                "teams":
                    match["teams"],


                "market":
                    match["recommended"],


                "confidence":
                    match["confidence"],


                "odds":
                    match["odds"]

            }

        )


    return {

        "risk":
            risk,


        "matches":
            selections,


        "summary":

        {

            "average_confidence":
                round(
                    total_confidence /
                    MATCHES_PER_SLIP,
                    2
                ),


            "combined_odds":
                round(
                    combined_odds,
                    2
                )

        }

    }



# --------------------------------------------------
# Generate slips
# --------------------------------------------------


def generate_slips(matches):


    pools = build_pools(
        matches
    )


    strategy = [

        "ULTRA_SAFE",

        "ULTRA_SAFE",

        "SAFE",

        "SAFE",

        "SAFE",

        "MEDIUM",

        "MEDIUM",

        "MEDIUM",

        "HIGH",

        "HIGH"

    ]


    slips = []


    used_combinations = set()



    for risk in strategy:


        available = pools[risk]


        chosen = select_matches(
            available
        )


        # fallback if pool is small

        if chosen is None:

            chosen = select_matches(
                matches
            )


        if chosen is None:

            continue



        fixture_ids = tuple(
            sorted(

                m["fixture_id"]

                for m in chosen

            )
        )


        # prevent duplicate slips

        if fixture_ids in used_combinations:

            continue


        used_combinations.add(
            fixture_ids
        )


        slip = create_slip(
            chosen,
            risk
        )


        slips.append(
            slip
        )


        if len(slips) == TOTAL_SLIPS:

            break



    return slips



# --------------------------------------------------
# Save
# --------------------------------------------------


def save_slips(slips):


    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    data = {

        "generated":

            datetime.now(
                timezone.utc
            ).isoformat(),


        "total_slips":

            len(slips),


        "slips":

            slips

    }


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:


        json.dump(

            data,

            file,

            indent=2,

            ensure_ascii=False

        )



# --------------------------------------------------
# Main
# --------------------------------------------------


def main():


    print(
        "Loading probability results..."
    )


    matches = load_matches()


    if len(matches) < 5:

        raise RuntimeError(
            "Not enough matches for optimization"
        )


    print(
        f"Loaded {len(matches)} matches"
    )


    ranked = rank_matches(
        matches
    )


    slips = generate_slips(
        ranked
    )


    if len(slips) < TOTAL_SLIPS:

        print(
            "Warning: fewer than 10 slips generated"
        )


    save_slips(
        slips
    )


    print(
        f"Generated {len(slips)} betting slips"
    )


    print(
        OUTPUT_FILE
    )



if __name__ == "__main__":

    main()
