#!/usr/bin/env python3

"""
exporter.py

Creates dashboard-ready JSON.

Input:

data/optimized_slips.json
data/slip_validation.json


Output:

data/dashboard.json
"""


from pathlib import Path
from datetime import datetime, timezone
import json



SLIPS_FILE = Path(
    "data/optimized_slips.json"
)


VALIDATION_FILE = Path(
    "data/slip_validation.json"
)


OUTPUT_FILE = Path(
    "data/dashboard.json"
)



def load_json(path):

    if not path.exists():

        raise FileNotFoundError(
            f"{path} missing"
        )


    with open(
        path,
        encoding="utf-8"
    ) as file:

        return json.load(file)



def check_validation():

    report = load_json(
        VALIDATION_FILE
    )


    invalid = report.get(
        "invalid_slips",
        0
    )


    if invalid > 0:

        raise RuntimeError(
            "Invalid slips detected. "
            "Dashboard export cancelled."
        )



def risk_summary(slips):

    summary={

        "ULTRA_SAFE":0,

        "SAFE":0,

        "MEDIUM":0,

        "HIGH":0

    }


    for slip in slips:

        risk = slip.get(
            "risk"
        )


        if risk in summary:

            summary[risk]+=1


    return summary



def format_slip(
    slip,
    index
):

    return {


        "id":

            index,


        "risk":

            slip.get(
                "risk"
            ),


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

                    match.get(
                        "fixture_id"
                    ),


                "teams":

                    match.get(
                        "teams"
                    ),


                "market":

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

            }


            for match in slip.get(
                "matches",
                []
            )

        ]

    }



def find_best_slip(slips):

    if not slips:

        return None



    return max(

        slips,

        key=lambda slip:

        slip["summary"]
        .get(
            "average_confidence",
            0
        )

    )



def create_dashboard(slips):


    formatted=[]


    for index, slip in enumerate(
        slips,
        start=1
    ):

        formatted.append(

            format_slip(
                slip,
                index
            )

        )



    best=find_best_slip(
        slips
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

            formatted

    }



def export_dashboard():


    check_validation()


    data = load_json(
        SLIPS_FILE
    )


    slips=data.get(
        "slips",
        []
    )


    if not slips:

        raise RuntimeError(
            "No optimized slips found"
        )



    dashboard=create_dashboard(
        slips
    )


    OUTPUT_FILE.parent.mkdir(
        exist_ok=True
    )


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:


        json.dump(

            dashboard,

            file,

            indent=2,

            ensure_ascii=False

        )


    print(
        "Dashboard exported:"
    )

    print(
        OUTPUT_FILE
    )



if __name__=="__main__":

    export_dashboard()
