# Football Prediction Engine ⚽

A Python-based football prediction and betting slip optimization engine.

The system collects football fixtures, analyses team statistics, generates probability-based predictions, combines model calculations with bookmaker odds, creates optimized betting slips, validates selections, and exports dashboard-ready data.

The engine is designed as a complete automated pipeline where raw football data is transformed into structured betting recommendations.

---

# Features

## ⚽ Fixture Collection

- Automatically fetches upcoming football fixtures from a configured football data provider.
- Selects the next available matches based on kickoff time.
- Normalizes team names to prevent duplicate or inconsistent records.
- Stores clean fixture data for analysis.

---

## ✅ Match Validation

Before analysis begins, fixtures are checked for:

- Correct number of matches available.
- Valid home and away teams.
- Future kickoff times.
- Duplicate fixture removal.
- Required data fields.

This prevents incomplete or incorrect matches from entering the prediction system.

---

## 📊 Team Statistics Analysis

The engine collects important football indicators including:

- Recent team form.
- Wins, draws, and losses.
- Goals scored averages.
- Goals conceded averages.
- Home team performance.
- Away team performance.
- League position.
- Team strength ratings.
- Head-to-head history.

These statistics become the foundation for prediction calculations.

---

## 🤖 Match Prediction Engine

The prediction module analyses each fixture using:

- Team strength comparison.
- Attack and defence performance.
- League position factors.
- Home advantage.
- Away performance.

The system produces probability estimates for:

- Home win.
- Draw.
- Away win.
- Double Chance markets:

  - 1X (Home win or Draw)
  - X2 (Away win or Draw)
  - 12 (Either team wins)

---

## 📈 Probability Fusion

The probability engine combines:

- Internal prediction model probability.
- Available bookmaker odds.

This creates a final confidence score by balancing statistical prediction and market information.

The result is:

- Recommended market.
- Confidence percentage.
- Estimated value.
- Probability ranking.

---

## 🎯 Betting Slip Optimization

The optimizer converts individual match predictions into structured betting slips.

The system:

- Ranks selections by confidence.
- Groups selections by risk level.
- Creates multiple betting combinations.
- Produces 10 separate betting slips.
- Calculates combined odds.
- Calculates average slip confidence.

Risk categories:

- ULTRA SAFE
- SAFE
- MEDIUM
- HIGH

---

## 🔍 Slip Validation

Generated betting slips are checked for:

- Duplicate fixtures.
- Missing selections.
- Invalid markets.
- Invalid odds.
- Incorrect confidence values.
- Broken slip structures.

Only validated slips are exported to the dashboard.

---

## 📤 Dashboard Export

The exporter creates a clean dashboard data file containing:

- Generated slips.
- Match selections.
- Confidence levels.
- Odds information.
- Risk categories.
- Engine information.

The dashboard reads this final output instead of processing raw prediction files.

---

# System Workflow
