import sys
sys.path.append('../..')  # Adjust path to import from root

from data_processing.market_data_processor import MarketDataProcessor
from backtesting.strategy import MovingAverageCrossover
from backtesting.backtester import Backtester
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Get clean market data
print("Fetching AAPL data...")
mdp = MarketDataProcessor("AAPL", "2023-01-01", "2024-01-01")
data = mdp.build()
# Strategy expects lowercase 'close' (use Adj Close for backtesting)
data = data.copy()
data["close"] = data["Adj Close"]
print(f"✓ Loaded {len(data)} days of data")

# Step 2: Create strategy
print("\nInitializing moving average crossover strategy...")
strategy = MovingAverageCrossover(short_window=20, long_window=50, quantity=100)
print("✓ Strategy ready")

# Step 3: Create backtester
print("\nInitializing backtester...")
bt = Backtester(
    strategy=strategy,
    data=data,
    ticker='AAPL',
    initial_cash=100000
)
print("✓ Backtester ready")

# Step 4: Run the backtest
print("\nRunning backtest...")
results = bt.run()
print(f"✓ Backtest complete - {len(results)} days processed")

# Step 5: Convert results to DataFrame for analysis
results_df = pd.DataFrame(results)
print("\n=== Backtest Results ===")
print(f"Starting Value: ${bt.initial_cash:,.2f}")
print(f"Ending Value:   ${results_df['portfolio_value'].iloc[-1]:,.2f}")
print(f"Total Return:   {((results_df['portfolio_value'].iloc[-1] / bt.initial_cash) - 1):.2%}")
print(f"\nTrades executed: {len(bt.portfolio.trades)}")
print(f"Final cash: ${results_df['current_cash'].iloc[-1]:,.2f}")
print(f"Final positions: {results_df['portfolio'].iloc[-1]}")

# Step 6: Plot equity curve
plt.figure(figsize=(12, 6))
plt.plot(results_df['date'], results_df['portfolio_value'], label='Strategy')
plt.axhline(y=bt.initial_cash, color='r', linestyle='--', label='Starting Capital')
plt.title('Portfolio Value Over Time')
plt.xlabel('Date')
plt.ylabel('Portfolio Value ($)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('backtest_equity_curve.png')
print("\n✓ Saved equity curve to backtest_equity_curve.png")

# Step 7: Show some trades
print("\n=== First 5 Trades ===")
for i, trade in enumerate(bt.portfolio.trades[:5]):
    print(f"{i+1}. {trade}")

# Step 8: Signal distribution (extract action from signal dict)
print("\n=== Signal Distribution ===")
print(results_df['signal'].apply(lambda x: x['action']).value_counts())

# Step 9: When did BUY vs SELL occur? (explains why some signals don't execute)
print("\n=== Signal dates (order matters: SELL with 0 shares is skipped) ===")
for _, row in results_df.iterrows():
    sig = row['signal']
    if sig['action'] in ('BUY', 'SELL'):
        pos = row['portfolio']
        print(f"  {row['date'].date()}: {sig['action']} (positions: {pos})")
