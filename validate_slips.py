#!/usr/bin/env python3

"""
validate_slips.py

Validates generated betting slips.

Input:
    data/optimized_slips.json

Output:
    data/slip_validation.json


Checks:

- Slip structure
- Duplicate fixtures
- Missing selections
- Invalid markets
- Invalid odds
- Invalid confidence
- Risk category validation
"""


from pathlib import Path
import json
from datetime import datetime, timezone



INPUT_FILE = Path(
    "data/optimized_slips.json"
)


OUTPUT_FILE = Path(
    "data/slip_validation.json"
)



VALID_RISKS = {

    "ULTRA_SAFE",

    "SAFE",

    "MEDIUM",

    "HIGH"

}



VALID_MARKETS = {

    "1X",

    "X2",

    "12"

}



MIN_SELECTIONS = 1



# --------------------------------------------------
# Load slips
# --------------------------------------------------


def load_slips():


    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "optimized_slips.json missing"
        )


    with open(
        INPUT_FILE,
        encoding="utf-8"
    ) as file:

        data=json.load(file)



    return data.get(
        "slips",
        []
    )



# --------------------------------------------------
# Validate selection
# --------------------------------------------------


def validate_selection(selection):


    errors=[]



    required=[

        "fixture_id",

        "teams",

        "recommended",

        "confidence",

        "odds"

    ]



    for field in required:


        if field not in selection:

            errors.append(

                f"Missing {field}"

            )



    if selection.get(
        "recommended"
    ) not in VALID_MARKETS:


        errors.append(
            "Invalid market"
        )



    odds = selection.get(
        "odds"
    )



    if not isinstance(
        odds,
        (int,float)
    ) or odds <= 1:


        errors.append(
            "Invalid odds"
        )



    confidence = selection.get(
        "confidence"
    )



    if not isinstance(
        confidence,
        (int,float)
    ):


        errors.append(
            "Invalid confidence"
        )


    elif confidence < 0 or confidence > 100:


        errors.append(
            "Confidence outside range"
        )



    return errors



# --------------------------------------------------
# Validate slip
# --------------------------------------------------


def validate_slip(
    slip
):


    errors=[]



    if slip.get(
        "risk"
    ) not in VALID_RISKS:


        errors.append(
            "Invalid risk category"
        )



    matches = slip.get(
        "matches",
        []
    )



    if len(matches) < MIN_SELECTIONS:


        errors.append(
            "No selections found"
        )



    fixture_ids=[]



    for selection in matches:


        errors.extend(

            validate_selection(
                selection
            )

        )


        fixture_ids.append(

            selection.get(
                "fixture_id"
            )

        )



    if len(fixture_ids) != len(set(fixture_ids)):


        errors.append(
            "Duplicate fixtures in slip"
        )



    summary = slip.get(
        "summary",
        {}
    )



    avg_confidence = summary.get(
        "average_confidence"
    )



    if avg_confidence is not None:


        if avg_confidence < 0 or avg_confidence > 100:

            errors.append(
                "Invalid average confidence"
            )



    combined_odds = summary.get(
        "combined_odds"
    )


    if combined_odds is not None:


        if combined_odds <= 1:

            errors.append(
                "Invalid combined odds"
            )



    return errors



# --------------------------------------------------
# Main validator
# --------------------------------------------------


def validate_slips():


    slips = load_slips()



    validated=[]

    valid_count=0

    invalid_count=0



    for index, slip in enumerate(
        slips,
        start=1
    ):


        errors = validate_slip(
            slip
        )



        result={


            "slip_number":

                index,


            "valid":

                len(errors) == 0,


            "errors":

                errors


        }



        validated.append(
            result
        )



        if errors:

            invalid_count += 1

        else:

            valid_count += 1



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


            "total_slips":

                len(slips),


            "valid_slips":

                valid_count,


            "invalid_slips":

                invalid_count,


            "validation":

                validated


        },
        file,
        indent=2
        )



    print(
        f"Validated {len(slips)} slips"
    )

    print(
        f"Valid: {valid_count}"
    )

    print(
        f"Invalid: {invalid_count}"
    )



    return valid_count



if __name__ == "__main__":

    validate_slips()
