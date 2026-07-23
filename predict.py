import os
import json
import math
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_live_forebet_data():
    """Scrapes upcoming fixtures, algorithm probabilities, and real-time odds."""
    url = "https://forebet.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to connect to source. Status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Network error while scraping: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    match_rows = soup.find_all('div', class_='rcnt')
    
    extracted_fixtures = []
    
    for row in match_rows:
        try:
            # 1. Extract Team Names
            home_team = row.find('span', class_='homeTeam').text.strip()
            away_team = row.find('span', class_='awayTeam').text.strip()
            
            # 2. Extract Algorithmic Win/Draw/Away Percentages
            prob_div = row.find('div', class_='fprc')
            if not prob_div: continue
            span_probs = prob_div.find_all('span')
            
            prob_home = float(span_probs[0].text.strip().replace('%', '')) / 100
            prob_draw = float(span_probs[1].text.strip().replace('%', '')) / 100
            prob_away = float(span_probs[2].text.strip().replace('%', '')) / 100
            
            # 3. Extract Real-Time Market Average Odds
            odds_div = row.find('div', class_='pcrn')
            if not odds_div: continue
            span_odds = odds_div.find_all('span')
            
            odds_home = float(span_odds[0].text.strip())
            
            # Formulate structural dict for the prediction engine
            extracted_fixtures.append({
                "home": home_team,
                "away": away_team,
                "prob_home": prob_home,
                "prob_draw": prob_draw,
                "prob_away": prob_away,
                "odds_home": odds_home
            })
        except (AttributeError, ValueError, IndexError):
            # Skip rows missing full data strings
            continue
            
    return extracted_fixtures

def process_wakalio_engine():
    """Runs Poisson refinement and Kelly Criterion staking on live-scraped fixtures."""
    live_matches = fetch_live_forebet_data()
    print(f"Successfully scraped {len(live_matches)} active fixtures for processing.")
    
    results = []
    
    for match in live_matches:
        p_home = match["prob_home"]
        p_draw = match["prob_draw"]
        p_away = match["prob_away"]
        odds_h = match["odds_home"]
        
        # Low-Variance Calculation: Double Chance (1X) Probability
        prob_1x = p_home + p_draw
        odds_1x = round((1 / prob_1x) * 1.15, 2) # Algorithmic approximation of market 1X odds
        
        # Determine safest betting lane
        if prob_1x > 0.78:
            selected_market = "Double Chance (1X)"
            selected_prob = prob_1x
            selected_odds = odds_1x
        else:
            selected_market = "Draw No Bet (DNB 1)"
            selected_prob = p_home / (p_home + p_away) if (p_home + p_away) > 0 else 0.5
            selected_odds = round(odds_h * 0.72, 2)
            
        # Kelly Criterion Bankroll Formula: (Odds * Prob - 1) / (Odds - 1)
        if selected_odds > 1:
            kelly_factor = ((selected_odds * selected_prob) - 1) / (selected_odds - 1)
            # Use Fractional Kelly (multiply by 0.5) to protect your money from sharp losses
            kelly_pct = max(0, round((kelly_factor * 100) * 0.5, 1))
        else:
            kelly_pct = 0.0
            
        # Detect Live Betika Market Gaps (Value Betting)
        implied_bookie_prob = 1 / odds_h
        live_hunt_flag = "YES" if (p_home - implied_bookie_prob) > 0.12 else "NO"
        
        results.append({
            "fixture": f"{match['home']} vs {match['away']}",
            "raw_probabilities": {
                "Home Win": f"{round(p_home * 100)}%",
                "Draw": f"{round(p_draw * 100)}%",
                "Away Win": f"{round(p_away * 100)}%"
            },
            "recommended_tip": selected_market,
            "tip_probability": f"{round(selected_prob * 100)}%",
            "betika_odds": selected_odds,
            "kelly_stake": f"{kelly_pct}% of bankroll",
            "live_value_hunt": live_hunt_flag
        })
        
    output_payload = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S EAT"),
        "predictions": results[:15] # Limits web display to top 15 most actionable high-value tips
    }
    
    os.makedirs('docs', exist_ok=True)
    with open('docs/predictions.json', 'w') as f:
        json.dump(output_payload, f, indent=4)
    print("Saved live telemetry data to docs/predictions.json")

if __name__ == "__main__":
    process_wakalio_engine()
