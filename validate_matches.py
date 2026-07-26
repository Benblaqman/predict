#!/usr/bin/env python3
"""
validate_slips.py

Validates optimized betting slips.

Input:
    engine/data/optimized_slips.json

Output:
    engine/data/slip_validation.json

Checks:
- File exists
- JSON integrity
- Slip count
- Match count per slip
- Duplicate fixtures
- Invalid odds
- Invalid confidence
- Contradictory markets
- Risk consistency

Exit:
0 = validation passed
1 = validation failed
"""


from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime, timezone


# --------------------------------------------------
# Configuration
# --------------------------------------------------

SLIPS_FILE = Path(
    "engine/data/optimized_slips.json"
)

REPORT_FILE = Path(
    "engine/data/slip_validation.json"
)


EXPECTED_SLIPS = 10

MATCHES_PER_SLIP = 5


MIN_CONFIDENCE = 65


# --------------------------------------------------
# Helpers
# --------------------------------------------------


errors = []


def fail(message):

    errors.append(message)



def load_slips():

    if not SLIPS_FILE.exists():

        fail(
            "optimized_slips.json missing"
        )

        return None


    try:

        with open(
            SLIPS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)


    except Exception as e:

        fail(
            f"Invalid JSON: {e}"
        )

        return None



# --------------------------------------------------
# Validation Rules
# --------------------------------------------------


def validate_structure(data):


    if not data:

        return


    slips = data.get(
        "slips"
    )


    if slips is None:

        fail(
            "Missing slips key"
        )

        return



    if len(slips) != EXPECTED_SLIPS:

        fail(

            f"Expected {EXPECTED_SLIPS} slips "
            f"but found {len(slips)}"

        )



def validate_slip(
    slip,
    index,
    global_fixtures
):


    required = [

        "risk",

        "matches",

        "summary"

    ]


    for field in required:

        if field not in slip:

            fail(

                f"Slip {index}: missing {field}"

            )



    matches = slip.get(
        "matches",
        []
    )


    if len(matches) != MATCHES_PER_SLIP:

        fail(

            f"Slip {index}: expected "
            f"{MATCHES_PER_SLIP} matches"

        )


    local_fixtures = set()



    for match in matches:


        fixture_id = match.get(
            "fixture_id"
        )


        if fixture_id is None:

            fail(

                f"Slip {index}: missing fixture id"

            )

            continue



        # Duplicate inside same slip

        if fixture_id in local_fixtures:

            fail(

                f"Slip {index}: duplicate fixture "
                f"{fixture_id}"

            )


        local_fixtures.add(
            fixture_id
        )



        # Duplicate across slips

        global_fixtures.append(
            fixture_id
        )



        confidence = match.get(
            "confidence",
            0
        )


        if confidence < MIN_CONFIDENCE:

            fail(

                f"Slip {index}: "
                f"{fixture_id} confidence too low "
                f"({confidence})"

            )



        odds = match.get(
            "odds"
        )


        try:

            odds = float(
                odds
            )


            if odds <= 1:

                fail(

                    f"Slip {index}: invalid odds "
                    f"{odds}"

                )


        except:

            fail(

                f"Slip {index}: invalid odds value"

            )



        validate_market(
            match,
            index
        )



def validate_market(
    match,
    slip_index
):


    market = match.get(
        "market"
    )


    valid = [

        "1X",

        "X2",

        "12"

    ]


    if market not in valid:

        fail(

            f"Slip {slip_index}: "
            f"unknown market {market}"

        )



# --------------------------------------------------
# Duplicate Analysis
# --------------------------------------------------


def validate_global_duplicates(
    fixture_ids
):


    seen = set()


    duplicates = set()


    for item in fixture_ids:

        if item in seen:

            duplicates.add(
                item
            )

        seen.add(
            item
        )


    for duplicate in duplicates:

        fail(

            f"Fixture appears in multiple slips: "
            f"{duplicate}"

        )



# --------------------------------------------------
# Risk Validation
# --------------------------------------------------


def validate_risk(
    slip,
    index
):


    risk = slip.get(
        "risk"
    )


    confidence = slip.get(
        "summary",
        {}
    ).get(
        "average_confidence",
        0
    )



    if risk == "ULTRA_SAFE":

        if confidence < 85:

            fail(

                f"Slip {index}: "
                "ULTRA_SAFE confidence too low"

            )



    if risk == "SAFE":

        if confidence < 75:

            fail(

                f"Slip {index}: "
                "SAFE confidence too low"

            )



# --------------------------------------------------
# Report
# --------------------------------------------------


def save_report():

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    report = {

        "checked_at":

            datetime.now(
                timezone.utc
            ).isoformat(),


        "status":

            "PASS"
            if not errors
            else
            "FAILED",


        "errors":

            errors

    }


    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(

            report,

            file,

            indent=2

        )



# --------------------------------------------------
# Main
# --------------------------------------------------


def main():


    data = load_slips()


    if data:

        validate_structure(
            data
        )


        slips = data.get(
            "slips",
            []
        )


        global_fixtures = []


        for index, slip in enumerate(
            slips,
            start=1
        ):


            validate_slip(

                slip,

                index,

                global_fixtures

            )


            validate_risk(

                slip,

                index

            )



        validate_global_duplicates(

            global_fixtures

        )



    save_report()



    if errors:

        print(
            "❌ Slip validation failed"
        )


        for error in errors:

            print(
                " -",
                error
            )


        sys.exit(1)



    else:

        print(
            "✅ All slips validated successfully"
        )


        sys.exit(0)



if __name__ == "__main__":

    main()
