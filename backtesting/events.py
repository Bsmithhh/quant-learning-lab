# Event types passed through the backtester's event queue.
# Flow: MarketEvent -> SignalEvent -> OrderEvent -> FillEvent
from dataclasses import dataclass
import pandas as pd


@dataclass
class MarketEvent:
    """A new bar is available for this date."""
    date: pd.Timestamp


@dataclass
class SignalEvent:
    """Strategy wants to BUY or SELL, decided on this date's close."""
    date: pd.Timestamp
    ticker: str
    action: str
    quantity: int


@dataclass
class OrderEvent:
    """Portfolio has approved a signal and sent it to execution."""
    date: pd.Timestamp
    ticker: str
    action: str
    quantity: int


@dataclass
class FillEvent:
    """Order executed at fill_price (slippage included) plus commission."""
    date: pd.Timestamp
    ticker: str
    action: str
    quantity: int
    fill_price: float
    commission: float
