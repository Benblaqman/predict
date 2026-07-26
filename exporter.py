#!/usr/bin/env python3
"""
exporter.py

Exports validated betting slips into
a dashboard-friendly JSON format.

Input:
    engine/data/optimized_slips.json
    engine/data/slip_validation.json

Output:
    engine/data/dashboard.json

"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


# --------------------------------------------------
# Configuration
# --------------------------------------------------

SLIPS_FILE = Path(
    "engine/data/optimized_slips.json"
)

VALIDATION_FILE = Path(
    "engine/data/slip_validation.json"
)

OUTPUT_FILE = Path(
    "engine/data/dashboard.json"
)



# --------------------------------------------------
# Load
# --------------------------------------------------


def load_json(path):

    if not path.exists():

        raise FileNotFoundError(
            f"{path} missing"
        )


    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)



# --------------------------------------------------
# Validation Check
# --------------------------------------------------


def check_validation():

    report = load_json(
        VALIDATION_FILE
    )


    if report.get(
        "status"
    ) != "PASS":

        raise RuntimeError(
            "Slip validation failed. "
            "Dashboard export cancelled."
        )



# --------------------------------------------------
# Risk Summary
# --------------------------------------------------


def risk_summary(slips):


    summary = {

        "ULTRA_SAFE": 0,

        "SAFE": 0,

        "MEDIUM": 0,

        "HIGH": 0

    }


    for slip in slips:

        risk = slip.get(
            "risk"
        )


        if risk in summary:

            summary[risk] += 1


    return summary



# --------------------------------------------------
# Best Slip
# --------------------------------------------------


def find_best_slip(slips):


    if not slips:

        return None



    return sorted(

        slips,

        key=lambda x:

        (

            x["summary"]
            .get(
                "average_confidence",
                0
            ),

            x["summary"]
            .get(
                "combined_odds",
                0
            )

        ),

        reverse=True

    )[0]



# --------------------------------------------------
# Format Slip
# --------------------------------------------------


def format_slip(
    slip,
    index
):


    return {

        "id":
            index,


        "risk":
            slip["risk"],


        "confidence":
            slip["summary"]
            .get(
                "average_confidence"
            ),


        "combined_odds":
            slip["summary"]
            .get(
                "combined_odds"
            ),


        "matches":[

            {

                "fixture_id":
                    match["fixture_id"],


                "teams":
                    match["teams"],


                "market":
                    match["market"],


                "confidence":
                    match["confidence"],


                "odds":
                    match["odds"]

            }

            for match in slip["matches"]

        ]

    }



# --------------------------------------------------
# Dashboard Builder
# --------------------------------------------------


def create_dashboard(slips):


    best = find_best_slip(
        slips
    )


    dashboard_slips = []


    for index, slip in enumerate(
        slips,
        start=1
    ):

        dashboard_slips.append(

            format_slip(
                slip,
                index
            )

        )



    return {


        "generated":

            datetime.now(
                timezone.utc
            ).isoformat(),



        "engine":

        {

            "name":
                "Football Prediction Engine",

            "version":
                "1.0"

        },



        "overview":

        {

            "total_slips":
                len(slips),


            "risk_distribution":
                risk_summary(
                    slips
                )

        },



        "featured_slip":

            format_slip(
                best,
                1
            )
            if best
            else None,



        "slips":

            dashboard_slips

    }



# --------------------------------------------------
# Save
# --------------------------------------------------


def save_dashboard(data):


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
        "Checking slip validation..."
    )


    check_validation()



    print(
        "Loading optimized slips..."
    )


    data = load_json(
        SLIPS_FILE
    )


    slips = data.get(
        "slips",
        []
    )


    if not slips:

        raise RuntimeError(
            "No slips available"
        )



    dashboard = create_dashboard(
        slips
    )


    save_dashboard(
        dashboard
    )


    print(
        "Dashboard export completed"
    )


    print(
        OUTPUT_FILE
    )



if __name__ == "__main__":

    main()
