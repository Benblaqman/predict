#!/usr/bin/env python3
"""
main.py

Runs the complete football prediction pipeline.

Workflow:

fetch matches
    |
validate fixtures
    |
fetch statistics
    |
predict matches
    |
combine probabilities
    |
optimize slips
    |
validate slips
    |
export dashboard

"""


from __future__ import annotations

import subprocess
import sys



PIPELINE = [

    "fetch_matches.py",

    "validate_matches.py",

    "fetch_statistics.py",

    "predict_matches.py",

    "probability_matches.py",

    "Optimizer.py",

    "validate_slips.py",

    "exporter.py"

]



def run_script(script):

    print("\n")
    print("=" * 50)
    print(f"RUNNING {script}")
    print("=" * 50)


    result = subprocess.run(

        [
            sys.executable,
            script
        ]

    )


    if result.returncode != 0:

        raise RuntimeError(
            f"{script} failed"
        )



def main():

    print(
        "⚽ Starting Football Prediction Engine"
    )


    for script in PIPELINE:

        run_script(
            script
        )


    print("\n")
    print("=" * 50)
    print(
        "✅ PIPELINE COMPLETED SUCCESSFULLY"
    )
    print("=" * 50)



if __name__ == "__main__":

    main()
