import json
import math
import os
from datetime import datetime

# 1. POSSON DISTRIBUTION MATHEMATICAL ENGINE
def poisson_probability(actual_expected, goals):
    """Calculates the probability of a team scoring a specific number of goals."""
    return (math.exp(-actual_expected) * (actual_expected ** goals)) / math.factorial(goals)

def analyze_match(match):
    home_team = match["home"]
    away_team = match["away"]
    
    # League baseline averages (Example: 1.5 goals per match home, 1.2 away)
    league_avg_home_scored = 1.5
    league_avg_away_scored = 1.2
    
    # Calculate Expected Goals (xG) based on Attack Strength & Defense Weakness
    home_xg = (match["home_attack"] * match["away_defense"]) * league_avg_home_scored
    away_xg = (match["away_attack"] * match["home_defense"]) * league_avg_away_scored
    
    # Calculate matrix for scorelines up to 5x5 goals
    prob_home_win = 0.0
    prob_draw = 0.0
    prob_away_win = 0.0
    prob_over_1_5 = 0.0
    prob_over_2_5 = 0.0
    
    for h in range(6):
        for a in range(6):
            p_score = poisson_probability(home_xg, h) * poisson_probability(away_xg, a)
            
            if h > a: prob_home_win += p_score
            elif h == a: prob_draw += p_score
            else: prob_away_win += p_score
                
            if (h + a) > 1: prob_over_1_5 += p_score
            if (h + a) > 2: prob_over_2_5 += p_score

    # 2. LOW-VARIANCE MARKET LOGIC
    # Double Chance Calculations
    prob_1X = prob_home_win + prob_draw
    prob_X2 = prob_away_win + prob_draw
    
    # Determine the safest mathematical tip based on highest probability
    if prob_1X > 0.75 and prob_home_win > prob_away_win:
        safe_market = "Double Chance (1X)"
        safe_prob = prob_1X
        bet_odds = match["odds_1X"]
    elif prob_over_1_5 > 0.80:
        safe_market = "Over 1.5 Goals"
        safe_prob = prob_over_1_5
        bet_odds = match["odds_ov15"]
    else:
        safe_market = "Draw No Bet (DNB 1)"
        safe_prob = prob_home_win / (prob_home_win + prob_away_win) if (prob_home_win + prob_away_win) > 0 else 0.5
        bet_odds = match["odds_home"] * 0.7 # Approximate DNB discount factor
        
    # 4. KELLY CRITERION BANKROLL MANAGEMENT
    # Formula: (Odds * Probability - 1) / (Odds - 1)
    if bet_odds > 1:
        kelly_stake = ((bet_odds * safe_prob) - 1) / (bet_odds - 1)
        kelly_stake_pct = max(0, round(kelly_stake * 100, 1)) # No negative stakes (fractional Kelly)
    else:
        kelly_stake_pct = 0.0

    # 5. LIVE VALUE HUNTING FLAG
    # Flag matches where pre-match value is tight, signaling a better live entry point
    implied_bookie_prob = (1 / match["odds_home"])
    is_live_target = "YES" if (prob_home_win - implied_bookie_prob) > 0.10 else "NO"

    return {
        "fixture": f"{home_team} vs {away_team}",
        "raw_probabilities": {
            "Home Win": f"{round(prob_home_win*100)}%",
            "Draw": f"{round(prob_draw*100)}%",
            "Away Win": f"{round(prob_away_win*100)}%"
        },
        "recommended_tip": safe_market,
        "tip_probability": f"{round(safe_prob*100)}%",
        "betika_odds": bet_odds,
        "kelly_stake": f"{kelly_stake_pct}% of bankroll",
        "live_value_hunt": is_live_target
    }

if __name__ == "__main__":
    # Sample Mock Data Feed (Replace with an API fetch from API-Football / Forebet scraper later)
    upcoming_betika_fixtures = [
        {
            "home": "Arsenal", "away": "Chelsea",
            "home_attack": 1.4, "home_defense": 0.8,
            "away_attack": 1.1, "away_defense": 1.3,
            "odds_home": 1.85, "odds_1X": 1.22, "odds_ov15": 1.25
        },
        {
            "home": "Real Madrid", "away": "Barcelona",
            "home_attack": 1.6, "home_defense": 1.0,
            "away_attack": 1.5, "away_defense": 1.2,
            "odds_home": 2.10, "odds_1X": 1.35, "odds_ov15": 1.18
        }
    ]
    
    results = [analyze_match(m) for m in upcoming_betika_fixtures]
    
    output_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S EAT"),
        "predictions": results
    }
    
    os.makedirs('docs', exist_ok=True)
    with open('docs/predictions.json', 'w') as f:
        json.dump(output_data, f, indent=4)
    print("Successfully compiled math models into docs/predictions.json")
