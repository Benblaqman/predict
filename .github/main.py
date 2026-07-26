#!/usr/bin/env python3

"""
Football Prediction Engine Controller
"""


from fetch_matches import fetch_matches
from validate_matches import validate_matches
from fetch_statistics import fetch_statistics
from predict_matches import predict_matches
from probability_matches import calculate_probabilities
from Optimizer import optimize_slips
from validate_slips import validate_slips
from exporter import export_dashboard



def run_engine():

    print("\n⚽ FOOTBALL PREDICTION ENGINE\n")

    print("1. Fetching fixtures")
    fetch_matches()


    print("2. Validating matches")
    validate_matches()


    print("3. Fetching statistics")
    fetch_statistics()


    print("4. Generating predictions")
    predict_matches()


    print("5. Calculating probabilities")
    calculate_probabilities()


    print("6. Optimizing betting slips")
    optimize_slips()


    print("7. Validating slips")
    validate_slips()


    print("8. Exporting dashboard")
    export_dashboard()


    print("\n✅ ENGINE COMPLETED SUCCESSFULLY")



if __name__ == "__main__":
    run_engine()
