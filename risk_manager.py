# risk_manager.py
import config
from models import Order, Position

class RiskManager:
    """
    Very simple risk manager: determines position size based on equity and
    MAX_POSITION_PERCENT from config.
    """
    def __init__(self, broker):
        self.broker = broker  # broker exposes get_equity()

    def size_for_order(self, symbol: str, side: str, price: float) -> float:
        equity = self.broker.get_equity()
        max_risk = equity * config.MAX_POSITION_PERCENT
        # For forex in this simple sim we treat price as units per base; size measured in base currency units.
        size = max_risk / price
        return size
