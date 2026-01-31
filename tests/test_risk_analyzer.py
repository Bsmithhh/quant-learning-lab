"""Unit tests for RiskAnalyzer."""

import sys
import math
import pytest
import pandas as pd

sys.path.insert(0, "risk-analytics")
from risk_analyzer import RiskAnalyzer


def test_init_raises_on_nan_returns():
    """Returns with NaN should raise ValueError in __init__."""
    returns = pd.Series([0.01, 0.02, float("nan"), -0.01])
    with pytest.raises(ValueError, match="Null returns"):
        RiskAnalyzer(returns)


def test_sharpe_ratio_constant_returns():
    """Sharpe with constant daily returns: annualized return = 0.252, vol ≈ 0, Sharpe very large or inf."""
    returns = pd.Series([0.001] * 252)  # 0.1% daily
    risk = RiskAnalyzer(returns)
    expected_annual_return = 0.001 * 252  # 0.252
    assert risk.annualized_return() == pytest.approx(expected_annual_return)
    # Constant returns => vol effectively zero (pandas may return tiny float noise)
    assert risk.annualized_volatility() < 1e-10 or risk.annualized_volatility() == 0.0
    # Sharpe = (0.252 - 0.02) / vol => very large or inf when vol ≈ 0
    sr = risk.sharpe_ratio()
    assert math.isinf(sr) or sr > 100


def test_max_drawdown_declining_series():
    """Max drawdown on 10 days of -1%: cumulative goes 0.99 -> 0.99^10, drawdown ~ -8.6%."""
    returns = pd.Series([-0.01] * 10)
    risk = RiskAnalyzer(returns)
    md = risk.max_drawdown()
    # (0.99^10 - 0.99) / 0.99 ≈ -0.0865
    assert md == pytest.approx(-0.0865, abs=0.01)
    assert -0.15 < md < -0.05
