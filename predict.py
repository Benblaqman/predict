import os
import json
import math
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def poisson_probability(expected, goals):
    """Hesabu ya Poisson ya nafasi ya timu kufunga idadi fulani ya mabao."""
    return (math.exp(-expected) * (expected ** goals)) / math.factorial(goals)

def fetch_live_match_data():
    """Hukusanya data halisi ya mechi zinazokuja na uwezekano wa kimsingi wa takwimu."""
    url = "https://forebet.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return []
    except Exception:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    match_rows = soup.find_all('div', class_='rcnt')
    
    fixtures = []
    for row in match_rows:
        try:
            home_team = row.find('span', class_='homeTeam').text.strip()
            away_team = row.find('span', class_='awayTeam').text.strip()
            
            # Kusoma uwezekano wa 1X2 uliopo kwenye data ya takwimu
            prob_div = row.find('div', class_='fprc')
            if not prob_div: continue
            span_probs = prob_div.find_all('span')
            
            p_h = float(span_probs[0].text.strip().replace('%', '')) / 100
            p_d = float(span_probs[1].text.strip().replace('%', '')) / 100
            p_a = float(span_probs[2].text.strip().replace('%', '')) / 100
            
            # Kusoma odds za soko
            odds_div = row.find('div', class_='pcrn')
            if not odds_div: continue
            span_odds = odds_div.find_all('span')
            odds_home = float(span_odds[0].text.strip())
            
            fixtures.append({
                "home": home_team, "away": away_team,
                "p_h": p_h, "p_d": p_d, "p_a": p_a, "odds_home": odds_home
            })
        except Exception:
            continue
    return fixtures

def run_wakalio_model():
    """Utekelezaji wa Mikakati yako 5 kwenye mechi za moja kwa moja."""
    raw_fixtures = fetch_live_match_data()
    processed_predictions = []
    
    for match in raw_fixtures:
        # Kugeuza asilimia kuwa Expected Goals (xG) ili kutumia Poisson Matrix
        home_xg = match["p_h"] * 2.5
        away_xg = match["p_a"] * 2.0
        
        prob_home_win, prob_draw, prob_away_win = 0.0, 0.0, 0.0
        prob_over_1_5, prob_over_2_5 = 0.0, 0.0
        
        # 1. POSSON DISTRIBUTION MATRIX
        for h in range(6):
            for a in range(6):
                p_score = poisson_probability(home_xg, h) * poisson_probability(away_xg, a)
                if h > a: prob_home_win += p_score
                elif h == a: prob_draw += p_score
                else: prob_away_win += p_score
                    
                if (h + a) > 1: prob_over_1_5 += p_score
                if (h + a) > 2: prob_over_2_5 += p_score

        # 2. LOW-VARIANCE MARKET ENGINE (Uteuzi wa soko lenye ushindi wa juu zaidi)
        prob_1X = prob_home_win + prob_draw
        prob_X2 = prob_away_win + prob_draw
        prob_dnb = prob_home_win / (prob_home_win + prob_away_win) if (prob_home_win + prob_away_win) > 0 else 0.5
        
        # Kupata soko salama kulingana na vigezo vyako
        if prob_1X > 0.80:
            recommended_market = "Double Chance (1X)"
            final_prob = prob_1X
            est_odds = round(1 / (prob_1X * 0.9), 2)
        elif prob_over_1_5 > 0.82:
            recommended_market = "Over 1.5 Goals"
            final_prob = prob_over_1_5
            est_odds = round(1 / (prob_over_1_5 * 0.9), 2)
        else:
            recommended_market = "Draw No Bet (DNB 1)"
            final_prob = prob_dnb
            est_odds = round(match["odds_home"] * 0.75, 2)

        # 4. KELLY CRITERION BANKROLL MANAGEMENT
        kelly_stake_pct = 0.0
        if est_odds > 1:
            kelly_formula = ((est_odds * final_prob) - 1) / (est_odds - 1)
            # Fractional Kelly (0.5) kuzuia upotezaji mkubwa wa mtaji
            kelly_stake_pct = max(0, round((kelly_formula * 100) * 0.5, 1))

        # 5. HUNT FOR VALUE ON BETIKA LIVE
        bookie_implied = 1 / match["odds_home"]
        live_hunt = "YES" if (prob_home_win - bookie_implied) > 0.10 else "NO"

        processed_predictions.append({
            "fixture": f"{match['home']} vs {match['away']}",
            "raw_probabilities": {
                "Home": f"{round(prob_home_win*100)}%",
                "Draw": f"{round(prob_draw*100)}%",
                "Away": f"{round(prob_away_win*100)}%",
                "Over 2.5": f"{round(prob_over_2_5*100)}%"
            },
            "recommended_tip": recommended_market,
            "tip_probability": f"{round(final_prob*100)}%",
            "estimated_odds": est_odds,
            "kelly_stake": f"{kelly_stake_pct}%",
            "live_value_hunt": live_hunt
        })

    # Hifadhi matokeo kwenye folda ya 'docs' kwa ajili ya Web Dashboard ya GitHub Pages
    output_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S EAT"),
        "predictions": processed_predictions[:20]
    }
    
    os.makedirs('docs', exist_ok=True)
    with open('docs/predictions.json', 'w') as f:
        json.dump(output_data, f, indent=4)
    print("Mchakato Umekamilika kwa Usahihi.")

if __name__ == "__main__":
    run_wakalio_model()
