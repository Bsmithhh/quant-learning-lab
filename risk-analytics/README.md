# Risk Analytics

Statistical risk metrics for evaluating portfolios and trading strategies.

## Metrics

### Annualized Return
Mean daily return scaled to annual performance (×252 trading days).

### Annualized Volatility  
Standard deviation of returns scaled to annual risk (×√252).

### Sharpe Ratio
Risk-adjusted return metric: (Return - Risk_Free_Rate) / Volatility
- Sharpe > 1.0 = good
- Sharpe > 2.0 = very good
- Sharpe > 3.0 = exceptional

### Maximum Drawdown
Largest peak-to-trough decline during the period.
Calculated using cumulative returns to reconstruct price path.

### Value at Risk (VaR)
Historical VaR at specified confidence level (default 95%).
Returns the return threshold - 95% of days had better performance.

## Usage

Add the `risk-analytics` directory to your Python path, then:

```python
from risk_analyzer import RiskAnalyzer

# Assuming you have a returns Series
risk = RiskAnalyzer(returns)

metrics = risk.get_metrics()
print(metrics)
```
