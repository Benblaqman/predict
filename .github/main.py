#!/usr/bin/env python3

"""
main.py

Football Prediction Engine Controller

Runs the complete pipeline:

1. Fetch fixtures
2. Validate fixtures
3. Fetch statistics
4. Predict matches
5. Calculate probabilities
6. Optimize slips
7. Validate slips
8. Export dashboard
"""


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



def run_step(script):

    print("\n============================")
    print(f"Running {script}")
    print("============================")


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
        "⚽ Football Prediction Engine Started"
    )


    for step in PIPELINE:

        run_step(step)



    print(
        "\n✅ ENGINE COMPLETED SUCCESSFULLY"
    )



if __name__ == "__main__":

    main()
