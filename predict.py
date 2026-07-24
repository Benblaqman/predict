import os
import json
import math
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys

def poisson_probability(expected, goals):
    """Hesabu ya Poisson ya nafasi ya timu kufunga idadi fulani ya mabao."""
    if expected < 0 or goals < 0:
        return 0
    return (math.exp(-expected) * (expected ** goals)) / math.factorial(goals)

def fetch_betika_odds():
    """Kukusanya odds halisi kutoka Betika API"""
    try:
        url = "https://api.betika.com/api/betika_web_next/sportpage/490?type=FIXTURES"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            events = data.get('data', {}).get('events', [])
            print(f"✅ Betika: Fetched {len(events)} events")
            return events
    except Exception as e:
        print(f"⚠️ Betika API error: {e}")
    return []

def normalize_team_name(name):
    """Normalize team names for matching (remove special chars, lowercase)"""
    return name.lower().strip().replace('fc', '').replace('  ', ' ').strip()

def find_match_on_betika(home_team, away_team, betika_events):
    """Find exact match on Betika using normalized team names"""
    home_norm = normalize_team_name(home_team)
    away_norm = normalize_team_name(away_team)
    
    for event in betika_events:
        event_name = event.get('name', '').lower()
        # Check if both teams are mentioned in the event name
        if home_norm in event_name and away_norm in event_name:
            odds = event.get('odds', {})
            return {
                "home": float(odds.get('1', None)),
                "draw": float(odds.get('X', None)),
                "away": float(odds.get('2', None)),
                "betika_match": event.get('name', 'Unknown'),
                "event_id": event.get('id', None)
            }
    
    return None  # Match not found on Betika

def fetch_live_match_data():
    """Hukusanya data halisi ya mechi zinazokuja na uwezekano wa kimsingi wa takwimu."""
    url = "https://forebet.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"⚠️ Forebet returned status {response.status_code}")
            return []
    except Exception as e:
        print(f"⚠️ Forebet fetch error: {e}")
        return []

    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        match_rows = soup.find_all('div', class_='rcnt')
        
        fixtures = []
        for row in match_rows:
            try:
                home_team_elem = row.find('span', class_='homeTeam')
                away_team_elem = row.find('span', class_='awayTeam')
                
                if not home_team_elem or not away_team_elem:
                    continue
                    
                home_team = home_team_elem.text.strip()
                away_team = away_team_elem.text.strip()
                
                # Kusoma uwezekano wa 1X2 uliopo kwenye data ya takwimu
                prob_div = row.find('div', class_='fprc')
                if not prob_div:
                    continue
                    
                span_probs = prob_div.find_all('span')
                if len(span_probs) < 3:
                    continue
                
                try:
                    p_h = float(span_probs[0].text.strip().replace('%', '')) / 100
                    p_d = float(span_probs[1].text.strip().replace('%', '')) / 100
                    p_a = float(span_probs[2].text.strip().replace('%', '')) / 100
                except (ValueError, IndexError):
                    continue
                
                # Kusoma odds za soko
                odds_div = row.find('div', class_='pcrn')
                if not odds_div:
                    continue
                    
                span_odds = odds_div.find_all('span')
                if len(span_odds) < 3:
                    continue
                
                try:
                    odds_home = float(span_odds[0].text.strip())
                    odds_draw = float(span_odds[1].text.strip())
                    odds_away = float(span_odds[2].text.strip())
                except (ValueError, IndexError):
                    continue
                
                fixtures.append({
                    "home": home_team, 
                    "away": away_team,
                    "p_h": p_h, 
                    "p_d": p_d, 
                    "p_a": p_a, 
                    "odds_home": odds_home,
                    "odds_draw": odds_draw,
                    "odds_away": odds_away
                })
            except Exception as e:
                continue
                
        print(f"✅ Forebet: Fetched {len(fixtures)} matches")
        return fixtures
    except Exception as e:
        print(f"⚠️ Parsing error: {e}")
        return []

def run_wakalio_model():
    """Utekelezaji wa Mikakati yako 5 kwenye mechi za moja kwa moja."""
    print("🚀 Starting Wakalio Mathematical Engine...")
    
    # Fetch live data
    raw_fixtures = fetch_live_match_data()
    betika_events = fetch_betika_odds()
    
    if not raw_fixtures:
        print("❌ No fixtures available from Forebet")
        sys.exit(1)
    
    if not betika_events:
        print("❌ No events available from Betika")
        sys.exit(1)
    
    processed_predictions = []
    betika_matched = 0
    variance_breakdown = {"ULTRA-SAFE": 0, "LOW": 0, "LOW-MEDIUM": 0, "MEDIUM": 0}
    
    for match in raw_fixtures:
        try:
            # CRITICAL: Only process matches that exist on Betika
            betika_match_data = find_match_on_betika(match["home"], match["away"], betika_events)
            
            if not betika_match_data:
                continue  # Skip - match not on Betika
            
            betika_matched += 1
            
            # Check if all odds are available
            if None in [betika_match_data["home"], betika_match_data["draw"], betika_match_data["away"]]:
                print(f"⚠️ Incomplete odds for {match['home']} vs {match['away']}")
                continue
            
            betika_odds = {
                "home": betika_match_data["home"],
                "draw": betika_match_data["draw"],
                "away": betika_match_data["away"]
            }
            
            # Kugeuza asilimia kuwa Expected Goals (xG) ili kutumia Poisson Matrix
            home_xg = match["p_h"] * 2.5
            away_xg = match["p_a"] * 2.0
            
            prob_home_win, prob_draw, prob_away_win = 0.0, 0.0, 0.0
            prob_over_1_5, prob_over_2_5 = 0.0, 0.0
            
            # 1. POISSON DISTRIBUTION MATRIX
            for h in range(6):
                for a in range(6):
                    p_score = poisson_probability(home_xg, h) * poisson_probability(away_xg, a)
                    if h > a:
                        prob_home_win += p_score
                    elif h == a:
                        prob_draw += p_score
                    else:
                        prob_away_win += p_score
                        
                    if (h + a) > 1:
                        prob_over_1_5 += p_score
                    if (h + a) > 2:
                        prob_over_2_5 += p_score

            # 2. LOW-VARIANCE MARKET ENGINE
            prob_1X = prob_home_win + prob_draw
            prob_X2 = prob_away_win + prob_draw
            prob_dnb = prob_home_win / (prob_home_win + prob_away_win) if (prob_home_win + prob_away_win) > 0 else 0.5
            
            # Determine market and variance level
            recommended_market = None
            final_prob = None
            est_odds = None
            variance_level = None
            
            # TIER 1: Ultra-safe (very low variance) - >85%
            if prob_1X > 0.85:
                recommended_market = "1X Double Chance"
                final_prob = prob_1X
                est_odds = round(1 / (prob_1X * 0.9), 2)
                variance_level = "ULTRA-SAFE"
                variance_breakdown["ULTRA-SAFE"] += 1
            
            # TIER 2: Safe (low variance) - Over 2.5 >85%
            elif prob_over_2_5 > 0.85:
                recommended_market = "Over 2.5 Goals"
                final_prob = prob_over_2_5
                est_odds = round(1 / (prob_over_2_5 * 0.9), 2)
                variance_level = "LOW"
                variance_breakdown["LOW"] += 1
            
            # TIER 3: Low-Medium variance - Over 1.5 >83% or Double Chance >80%
            elif prob_over_1_5 > 0.83:
                recommended_market = "Over 1.5 Goals"
                final_prob = prob_over_1_5
                est_odds = round(1 / (prob_over_1_5 * 0.9), 2)
                variance_level = "LOW-MEDIUM"
                variance_breakdown["LOW-MEDIUM"] += 1
            
            # TIER 4: Medium variance - X2 or DNB >75%
            elif prob_X2 > 0.75:
                recommended_market = "X2 Double Chance"
                final_prob = prob_X2
                est_odds = round(1 / (prob_X2 * 0.85), 2)
                variance_level = "MEDIUM"
                variance_breakdown["MEDIUM"] += 1
            
            # Skip very risky picks
            else:
                continue

            # 3. KELLY CRITERION BANKROLL MANAGEMENT
            kelly_stake_pct = 0.0
            if est_odds > 1:
                kelly_formula = ((est_odds * final_prob) - 1) / (est_odds - 1)
                kelly_stake_pct = max(0, round((kelly_formula * 100) * 0.5, 1))

            # 4. HUNT FOR VALUE ON BETIKA LIVE
            bookie_implied = 1 / betika_odds["home"]
            live_hunt = "YES" if (prob_home_win - bookie_implied) > 0.10 else "NO"

            processed_predictions.append({
                "fixture": f"{match['home']} vs {match['away']}",
                "betika_match": betika_match_data["betika_match"],
                "raw_probabilities": {
                    "Home": f"{round(prob_home_win*100)}%",
                    "Draw": f"{round(prob_draw*100)}%",
                    "Away": f"{round(prob_away_win*100)}%",
                    "Over 1.5": f"{round(prob_over_1_5*100)}%",
                    "Over 2.5": f"{round(prob_over_2_5*100)}%"
                },
                "recommended_tip": recommended_market,
                "tip_probability": f"{round(final_prob*100)}%",
                "estimated_odds": est_odds,
                "variance": variance_level,
                "betika_odds": {
                    "home": round(betika_odds["home"], 2),
                    "draw": round(betika_odds["draw"], 2),
                    "away": round(betika_odds["away"], 2)
                },
                "kelly_stake": f"{kelly_stake_pct}%",
                "live_value_hunt": live_hunt
            })
        except Exception as e:
            print(f"⚠️ Error processing match: {e}")
            continue

    # Hifadhi matokeo kwenye folda ya 'docs' kwa ajili ya Web Dashboard ya GitHub Pages
    if not processed_predictions:
        print("❌ No low-variance predictions generated!")
        print(f"   Forebet matches: {len(raw_fixtures)}")
        print(f"   Betika events: {len(betika_events)}")
        print(f"   Matched: {betika_matched}")
        sys.exit(1)
    
    output_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S EAT"),
        "total_matches": len(processed_predictions),
        "stats": {
            "forebet_matches": len(raw_fixtures),
            "betika_events": len(betika_events),
            "betika_matched": betika_matched,
            "variance_breakdown": variance_breakdown
        },
        "predictions": processed_predictions[:20]
    }
    
    os.makedirs('docs', exist_ok=True)
    with open('docs/predictions.json', 'w') as f:
        json.dump(output_data, f, indent=4)
    
    print(f"✅ Mchakato Umekamilika kwa Usahihi!")
    print(f"📊 Forebet matches: {len(raw_fixtures)}")
    print(f"📊 Betika events: {len(betika_events)}")
    print(f"📊 Matched on Betika: {betika_matched}")
    print(f"📊 Variance Breakdown:")
    print(f"   - ULTRA-SAFE (>85% 1X): {variance_breakdown['ULTRA-SAFE']}")
    print(f"   - LOW (>85% Over 2.5): {variance_breakdown['LOW']}")
    print(f"   - LOW-MEDIUM (>83% Over 1.5): {variance_breakdown['LOW-MEDIUM']}")
    print(f"   - MEDIUM (>75% X2): {variance_breakdown['MEDIUM']}")
    print(f"📊 Final predictions: {len(processed_predictions)}")
    print(f"📊 Data saved to docs/predictions.json")

if __name__ == "__main__":
    run_wakalio_model()
