#!/usr/bin/env python3


"""
Convert predictions into betting selections.
"""


import json
from pathlib import Path
from datetime import datetime, timezone



INPUT = Path(
    "data/predictions.json"
)


OUTPUT = Path(
    "data/probability_results.json"
)



def calculate_risk(confidence):

    if confidence >=85:
        return "ULTRA_SAFE"

    elif confidence >=75:
        return "SAFE"

    elif confidence >=65:
        return "MEDIUM"

    else:
        return "HIGH"



def calculate_probabilities():


    with open(
        INPUT,
        encoding="utf-8"
    ) as f:

        data=json.load(f)



    results=[]



    for match in data["predictions"]:


        markets = match["double_chance"]


        market=max(
            markets,
            key=markets.get
        )


        confidence = (
            markets[market]
            *
            100
        )



        results.append({

            "fixture_id":
                match["fixture_id"],


            "teams":
                match["teams"],


            "recommended":
                market,


            "confidence":
                round(
                    confidence,
                    2
                ),


            "odds":
                round(
                    100/confidence,
                    2
                ),


            "risk":
                calculate_risk(
                    confidence
                )

        })



    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump({

            "generated":
                datetime.now(
                    timezone.utc
                ).isoformat(),


            "results":
                results


        },f,indent=2)



    print(
        "Probability results created"
    )



if __name__=="__main__":

    calculate_probabilities()
