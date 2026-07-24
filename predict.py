import os
import json
import math
import requests
from bs4 import BeautifulSoup
from datetime import datetime


# -------------------------------------------------
# POISSON DISTRIBUTION
# -------------------------------------------------

def poisson_probability(expected, goals):
    if expected < 0 or goals < 0:
        return 0
    return (math.exp(-expected) * (expected ** goals)) / math.factorial(goals)


# -------------------------------------------------
# TEAM NAME CLEANER
# -------------------------------------------------

def normalize_team_name(name):
    name = name.lower()
    name = name.replace("fc", "")
    name = name.replace(".", "")
    name = name.replace("-", " ")
    name = " ".join(name.split())
    return name


# -------------------------------------------------
# FOREBET SCRAPER
# -------------------------------------------------

def fetch_live_match_data():

    url = "https://www.forebet.com"

    headers = {
        "User-Agent":
        "Mozilla/5.0"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

    except Exception as e:

        print("Forebet Error:", e)

        return []

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    rows = soup.find_all("div", class_="rcnt")

    fixtures = []

    for row in rows:

        try:

            home = row.find(
                "span",
                class_="homeTeam"
            )

            away = row.find(
                "span",
                class_="awayTeam"
            )

            if not home or not away:
                continue

            home = home.text.strip()
            away = away.text.strip()

            probs = row.find(
                "div",
                class_="fprc"
            )

            if not probs:
                continue

            spans = probs.find_all("span")

            if len(spans) < 3:
                continue

            p_home = float(
                spans[0].text.replace("%", "")
            ) / 100

            p_draw = float(
                spans[1].text.replace("%", "")
            ) / 100

            p_away = float(
                spans[2].text.replace("%", "")
            ) / 100

            fixtures.append({

                "home": home,

                "away": away,

                "p_home": p_home,

                "p_draw": p_draw,

                "p_away": p_away

            })

        except:

            continue

    print(f"Loaded {len(fixtures)} fixtures")

    return fixtures


# -------------------------------------------------
# ENGINE
# -------------------------------------------------

def run_engine():

    fixtures = fetch_live_match_data()

    predictions = []

    variance = {
        "ULTRA-SAFE": 0,
        "LOW": 0,
        "LOW-MEDIUM": 0,
        "MEDIUM": 0
    }

    for match in fixtures:

        home = match["home"]
        away = match["away"]

        home_xg = match["p_home"] * 2.5
        away_xg = match["p_away"] * 2.0

        home_win = 0
        draw = 0
        away_win = 0

        over15 = 0
        over25 = 0



        # ----------------------------------------
        # POISSON MATRIX
        # ----------------------------------------

        for h in range(6):

            for a in range(6):

                score_prob = (
                    poisson_probability(home_xg, h) *
                    poisson_probability(away_xg, a)
                )

                if h > a:
                    home_win += score_prob

                elif h == a:
                    draw += score_prob

                else:
                    away_win += score_prob

                if (h + a) > 1:
                    over15 += score_prob

                if (h + a) > 2:
                    over25 += score_prob


        prob1X = home_win + draw
        probX2 = away_win + draw


        recommended_tip = None
        confidence = 0
        estimated_odds = 0
        variance_level = None


        # ----------------------------------------
        # DECISION ENGINE
        # ----------------------------------------

        if prob1X >= 0.85:

            recommended_tip = "1X Double Chance"
            confidence = prob1X
            estimated_odds = round(
                1 / (confidence * 0.90),
                2
            )

            variance_level = "ULTRA-SAFE"

            variance["ULTRA-SAFE"] += 1


        elif over25 >= 0.85:

            recommended_tip = "Over 2.5 Goals"
            confidence = over25
            estimated_odds = round(
                1 / (confidence * 0.90),
                2
            )

            variance_level = "LOW"

            variance["LOW"] += 1


        elif over15 >= 0.83:

            recommended_tip = "Over 1.5 Goals"

            confidence = over15

            estimated_odds = round(
                1 / (confidence * 0.90),
                2
            )

            variance_level = "LOW-MEDIUM"

            variance["LOW-MEDIUM"] += 1


        elif probX2 >= 0.75:

            recommended_tip = "X2 Double Chance"

            confidence = probX2

            estimated_odds = round(
                1 / (confidence * 0.85),
                2
            )

            variance_level = "MEDIUM"

            variance["MEDIUM"] += 1


        else:

            continue


        # ----------------------------------------
        # KELLY CRITERION
        # ----------------------------------------

        kelly = 0

        if estimated_odds > 1:

            formula = (
                (estimated_odds * confidence) - 1
            ) / (
                estimated_odds - 1
            )

            kelly = max(
                0,
                round(formula * 50, 1)
            )


        analysis = (
            f"{recommended_tip} selected because "
            f"the Poisson model produced a "
            f"{round(confidence*100)}% confidence "
            f"with {variance_level} variance."
        )


        predictions.append({

            "fixture":
            f"{home} vs {away}",

            "recommended_tip":
            recommended_tip,

            "tip_probability":
            f"{round(confidence*100)}%",

            "estimated_odds":
            estimated_odds,

            "variance":
            variance_level,

            "analysis":
            analysis,

            "kelly_stake":
            f"{kelly}%",

            "raw_probabilities":{

                "Home":
                f"{round(home_win*100)}%",

                "Draw":
                f"{round(draw*100)}%",

                "Away":
                f"{round(away_win*100)}%",

                "Over 1.5":
                f"{round(over15*100)}%",

                "Over 2.5":
                f"{round(over25*100)}%"
            }

        })


