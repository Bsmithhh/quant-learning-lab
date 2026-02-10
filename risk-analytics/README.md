# Risk Analytics

Statistical risk metrics for evaluating portfolios and trading strategies. **RiskAnalyzer** consumes a pandas Series of daily returns and computes annualized return, volatility, Sharpe ratio, maximum drawdown, and Value at Risk.

## Metrics & Formulas

### Annualized Return

Mean daily return scaled to 252 trading days:

- **Formula:** `mean(daily_returns) × 252`
- **Interpretation:** Expected return if daily mean were repeated over a year.

### Annualized Volatility

Standard deviation of returns scaled to annual risk:

- **Formula:** `std(daily_returns) × √252`
- **Interpretation:** Typical annualized dispersion of returns.

### Sharpe Ratio

Risk-adjusted return relative to a risk-free rate (default 2%):

- **Formula:** `(annualized_return - risk_free_rate) / annualized_volatility`
- **Interpretation:** Return per unit of risk. Sharpe > 1 is often considered good; > 2 very good; > 3 exceptional.

### Maximum Drawdown

Largest peak-to-trough decline over the period:

- **Method:** Cumulative returns `(1 + returns).cumprod()`, then running max; drawdown at each point is `(cumulative - running_max) / running_max`. Max drawdown is the minimum of that series.
- **Interpretation:** Worst historical loss from a peak (e.g. -0.25 = 25% drawdown).

### Value at Risk (VaR)

Historical VaR at a given confidence level (default 95%):

- **Formula:** `returns.quantile(1 - confidence)` (e.g. 0.95 → 5th percentile of daily returns).
- **Interpretation:** On 95% of days, returns were better than this threshold; 5% of days were worse.

## RiskAnalyzer API

- **`__init__(returns)`** — Takes a pandas Series of daily returns. Raises if nulls or empty.
- **`annualized_return()`** — Scalar.
- **`annualized_volatility()`** — Scalar.
- **`sharpe_ratio(risk_free_rate=0.02)`** — Scalar.
- **`max_drawdown()`** — Scalar (negative number).
- **`value_at_risk(confidence=0.95)`** — Scalar (e.g. daily return threshold).
- **`get_metrics(risk_free_rate=0.02, confidence=0.95)`** — Dict of all metrics above.

## Usage

Run from project root (or add `risk-analytics` to your Python path), then:

```python
from risk_analyzer import RiskAnalyzer

# returns: pandas Series of daily returns (e.g. from MarketDataProcessor)
risk = RiskAnalyzer(returns)

metrics = risk.get_metrics()
print(metrics)
# e.g. annualized_return, annualized_volatility, sharpe_ratio, max_drawdown, value_at_risk
```

Example with data from the data-processing pipeline:

```python
from data_processing.market_data_processor import MarketDataProcessor
from risk_analyzer import RiskAnalyzer

mdp = MarketDataProcessor("AAPL", "2023-01-01", "2024-01-01")
data = mdp.build()
returns = data["ret_1d"]

analyzer = RiskAnalyzer(returns)
print(analyzer.sharpe_ratio())
print(analyzer.get_metrics())
```
