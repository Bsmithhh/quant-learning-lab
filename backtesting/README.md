# Backtesting

Event-driven backtesting framework for trading strategies.

### Strategy Layer

Base Strategy class defines interface for all trading strategies.

**MovingAverageCrossover:**
- Generates BUY signal when short MA crosses above long MA
- Generates SELL signal when short MA crosses below long MA
- Configurable windows (default 20/50 days)
- Returns HOLD when insufficient data or no crossover

### Portfolio

Manages cash, positions, and trade execution.

**Features:**
- Cash tracking with validation
- Multi-ticker position management
- Buy/sell execution with sufficient funds/shares checks
- Trade history recording
- Portfolio valuation using current prices