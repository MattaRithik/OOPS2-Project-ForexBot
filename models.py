# models.py
from dataclasses import dataclass, field
from typing import Optional
import time
import uuid

@dataclass
class Candle:
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

@dataclass
class Order:
    order_id: str
    symbol: str
    side: str            # 'buy' or 'sell'
    size: float          # units (e.g., number of lots or base currency)
    price: Optional[float] = None  # limit price (None = market)
    status: str = "new"  # 'new', 'filled', 'cancelled'
    created_at: float = field(default_factory=time.time)

@dataclass
class Position:
    symbol: str
    side: str            # 'long' or 'short'
    size: float
    entry_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
