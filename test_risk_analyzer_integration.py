#!/usr/bin/env python3
"""Integration test: RiskAnalyzer with real data from MarketDataProcessor."""

import sys
sys.path.insert(0, "risk-analytics")

from data_processing.market_data_processor import MarketDataProcessor
from risk_analyzer import RiskAnalyzer

# Get data
mdp = MarketDataProcessor("AAPL", "2023-01-01", "2024-01-01")
mdp.build()
returns = mdp.data["ret_1d"]

# Analyze risk
risk = RiskAnalyzer(returns)

print("=== Risk Analysis ===")
print(f"Annualized Return:     {risk.annualized_return():.2%}")
print(f"Annualized Volatility: {risk.annualized_volatility():.2%}")
print(f"Sharpe Ratio:          {risk.sharpe_ratio():.2f}")
print(f"Max Drawdown:          {risk.max_drawdown():.2%}")
print(f"VaR (95%):             {risk.value_at_risk():.2%}")

# Sanity: flag crazy numbers
ar = risk.annualized_return()
av = risk.annualized_volatility()
sr = risk.sharpe_ratio()
crazy = abs(ar) > 2 or av > 1 or av <= 0 or abs(sr) > 10
print("\nSanity (no crazy numbers)? " + ("PASS" if not crazy else "FAIL"))
if crazy:
    sys.exit(1)
