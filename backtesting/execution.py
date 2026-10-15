# Simulated broker: fills orders at the next bar's open.
from .events import OrderEvent, FillEvent


class ExecutionHandler:
    def __init__(self, commission: float = 5, slippage_pct: float = 0.001):
        self.commission = commission
        self.slippage_pct = slippage_pct
        self.pending_orders: list = []

    def submit(self, order: OrderEvent):
        """Hold the order until the next bar opens."""
        self.pending_orders.append(order)

    def fill_pending(self, date, open_price: float) -> list:
        """
        Fill every pending order at this bar's open.

        Slippage always works against us: buys pay more, sells receive less.
        """
        fills = []
        for order in self.pending_orders:
            if order.action == 'BUY':
                price = open_price * (1 + self.slippage_pct)
            else:
                price = open_price * (1 - self.slippage_pct)
            fills.append(FillEvent(date, order.ticker, order.action, order.quantity, price, self.commission))
        self.pending_orders = []
        return fills
