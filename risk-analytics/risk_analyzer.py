import numpy as np

class RiskAnalyzer:
    def __init__(self, returns):
        if returns.isna().any():
            raise ValueError("Null returns detected.")

        if returns.empty:
            raise ValueError("Dataset is empty.")

        self.returns = returns
    
    def annualized_return(self):
        return self.returns.mean() * 252
    
    def annualized_volatility(self):
        return self.returns.std() * np.sqrt(252)

    def sharpe_ratio(self, risk_free_rate = 0.02):
        returns = self.annualized_return()
        volatility = self.annualized_volatility()
        sharpe_ratio = (returns - risk_free_rate) / volatility
        return sharpe_ratio
    def max_drawdown(self):
        cumulative_returns = (1 + self.returns).cumprod()
        running_max = cumulative_returns.cummax()
        return ((cumulative_returns - running_max) / running_max).min()

    def value_at_risk(self, confidence: float = 0.95):
        """Daily VaR: (1 - confidence) quantile of returns (e.g. 0.95 -> 5th percentile)."""
        return self.returns.quantile(1 - confidence)

    def get_metrics(self, risk_free_rate: float = 0.02, confidence: float = 0.95) -> dict:
        """
        Calculate all risk metrics and return as dict.
        """
        return {
            'annualized_return': self.annualized_return(),
            'annualized_volatility': self.annualized_volatility(),
            'sharpe_ratio': self.sharpe_ratio(risk_free_rate),
            'max_drawdown': self.max_drawdown(),
            'value_at_risk': self.value_at_risk(confidence)
        }