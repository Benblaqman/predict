#!/usr/bin/env python3

"""
validate_matches.py

Validates collected football fixtures before analysis.

Input:
    data/fixtures.json

Outputs:
    data/fixtures_validated.json
    data/match_validation.json

Checks:

- Required fields
- Valid teams
- Future kickoff time
- Duplicate fixtures
- Correct fixture count
"""


from pathlib import Path
import json
from datetime import datetime, timezone



INPUT_FILE = Path(
    "data/fixtures.json"
)


VALID_OUTPUT = Path(
    "data/fixtures_validated.json"
)


REPORT_OUTPUT = Path(
    "data/match_validation.json"
)



MIN_MATCHES = 1
MAX_MATCHES = 20



# --------------------------------------------------
# Load fixtures
# --------------------------------------------------


def load_fixtures():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "fixtures.json not found"
        )


    with open(
        INPUT_FILE,
        encoding="utf-8"
    ) as file:

        data = json.load(file)


    return data.get(
        "fixtures",
        []
    )



# --------------------------------------------------
# Validate time
# --------------------------------------------------


def valid_kickoff(value):

    try:

        kickoff = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )


        now = datetime.now(
            timezone.utc
        )


        return kickoff > now


    except Exception:

        return False



# --------------------------------------------------
# Validate fixture
# --------------------------------------------------


def validate_fixture(match):


    required = [

        "id",
        "home",
        "away",
        "kickoff"

    ]


    for field in required:

        if not match.get(field):

            return False



    if match["home"] == match["away"]:

        return False



    if not valid_kickoff(
        match["kickoff"]
    ):

        return False



    return True



# --------------------------------------------------
# Remove duplicates
# --------------------------------------------------


def remove_duplicates(fixtures):


    unique=[]

    seen=set()



    for match in fixtures:


        key=(

            match["home"],

            match["away"],

            match["kickoff"]

        )



        if key in seen:

            continue



        seen.add(key)

        unique.append(match)



    return unique



# --------------------------------------------------
# Main validation
# --------------------------------------------------


def validate_matches():


    fixtures = load_fixtures()



    original_count=len(
        fixtures
    )



    valid=[]

    rejected=0



    for match in fixtures:


        if validate_fixture(match):

            valid.append(match)

        else:

            rejected += 1



    valid = remove_duplicates(
        valid
    )



    duplicate_removed = (
        original_count
        -
        rejected
        -
        len(valid)
    )



    status = True



    if len(valid) < MIN_MATCHES:

        status=False



    if len(valid) > MAX_MATCHES:

        valid = valid[:MAX_MATCHES]



    # Save cleaned fixtures

    VALID_OUTPUT.parent.mkdir(
        exist_ok=True
    )



    with open(
        VALID_OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:


        json.dump({

            "generated":

                datetime.now(
                    timezone.utc
                ).isoformat(),


            "count":

                len(valid),


            "fixtures":

                valid


        },
        file,
        indent=2
        )



    # Save report

    with open(
        REPORT_OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:


        json.dump({

            "validation_status":

                status,


            "original_matches":

                original_count,


            "valid_matches":

                len(valid),


            "rejected_matches":

                rejected,


            "duplicates_removed":

                duplicate_removed


        },
        file,
        indent=2
        )



    print(
        "Match validation complete"
    )

    print(
        f"Valid fixtures: {len(valid)}"
    )



    return status



if __name__=="__main__":

    validate_matches()
