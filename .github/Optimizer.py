#!/usr/bin/env python3

"""
Optimizer.py

Creates optimized betting slips.

Input:
    data/probability_results.json

Output:
    data/optimized_slips.json


Features:

- Confidence ranking
- Value ranking
- Risk balancing
- Duplicate fixture protection
- 10 optimized slips
"""


from pathlib import Path
from datetime import datetime, timezone
import json



INPUT_FILE = Path(
    "data/probability_results.json"
)


OUTPUT_FILE = Path(
    "data/optimized_slips.json"
)



TOTAL_SLIPS = 10

MATCHES_PER_SLIP = 5



RISK_ORDER = {

    "ULTRA_SAFE": 1,

    "SAFE": 2,

    "MEDIUM": 3,

    "HIGH": 4

}



# --------------------------------------------------
# Load Data
# --------------------------------------------------


def load_results():


    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "probability_results.json missing"
        )


    with open(
        INPUT_FILE,
        encoding="utf-8"
    ) as file:

        data=json.load(file)


    return data.get(
        "results",
        []
    )



# --------------------------------------------------
# Ranking
# --------------------------------------------------


def rank_matches(matches):


    return sorted(

        matches,

        key=lambda x:

        (

            RISK_ORDER.get(
                x.get("risk"),
                99
            ),

            -x.get(
                "confidence",
                0
            ),

            -x.get(
                "value",
                0
            )

        )

    )



# --------------------------------------------------
# Build Slip
# --------------------------------------------------


def create_slip(
    matches,
    risk
):


    if len(matches) < MATCHES_PER_SLIP:

        return None



    combined_odds = 1

    confidence_total = 0



    selections=[]



    used=set()



    for match in matches:


        if len(selections) >= MATCHES_PER_SLIP:

            break



        fixture_id = match.get(
            "fixture_id"
        )



        if fixture_id in used:

            continue



        used.add(
            fixture_id
        )



        combined_odds *= match.get(
            "odds",
            1
        )


        confidence_total += match.get(
            "confidence",
            0
        )



        selections.append({


            "fixture_id":

                fixture_id,


            "teams":

                match.get(
                    "teams"
                ),


            "recommended":

                match.get(
                    "recommended"
                ),


            "confidence":

                match.get(
                    "confidence"
                ),


            "odds":

                match.get(
                    "odds"
                )

        })



    if len(selections) != MATCHES_PER_SLIP:

        return None



    return {


        "risk":

            risk,



        "matches":

            selections,



        "summary":

        {


            "average_confidence":

                round(

                    confidence_total /
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
# Generate Slips
# --------------------------------------------------


def optimize(matches):


    ranked = rank_matches(
        matches
    )


    slips=[]



    risk_plan=[


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



    for risk in risk_plan:


        pool=[

            match

            for match in ranked

            if match.get(
                "risk"
            ) == risk

        ]



        slip=create_slip(

            pool,

            risk

        )



        if slip:

            slips.append(
                slip
            )



    return slips



# --------------------------------------------------
# Save
# --------------------------------------------------


def save_output(slips):


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



                "total_slips":

                    len(slips),



                "slips":

                    slips


            },

            file,

            indent=2,

            ensure_ascii=False

        )



# --------------------------------------------------
# Main
# --------------------------------------------------


def main():


    matches = load_results()



    if not matches:

        raise RuntimeError(
            "No betting selections available"
        )



    slips = optimize(
        matches
    )



    save_output(
        slips
    )



    print(
        f"Generated {len(slips)} optimized slips"
    )



if __name__ == "__main__":

    main()
