# broker.py
from models import Order, Position
import uuid
import time
from typing import Dict, List
import threading

class PaperBroker:
    """
    Simulated broker that immediately fills market orders at provided price.
    Maintains positions and balance.
    """
    def __init__(self, initial_balance=100000.0):
        self.balance = initial_balance
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.lock = threading.Lock()
        self.trade_history = []

    def get_equity(self):
        # simplified: equity = balance + sum unrealized pnl
        unreal = sum(p.unrealized_pnl for p in self.positions.values())
        return self.balance + unreal

    def place_market_order(self, symbol, side, size, price):
        order = Order(order_id=str(uuid.uuid4()), symbol=symbol, side=side, size=size, price=price, status="filled", created_at=time.time())
        with self.lock:
            self._apply_fill(order)
            self.orders[order.order_id] = order
        return order

    def _apply_fill(self, order):
        # simplistic: positions keyed by symbol
        pos = self.positions.get(order.symbol)
        # convert side to long/short
        side = 'long' if order.side == 'buy' else 'short'
        if pos is None:
            # create new position
            self.positions[order.symbol] = Position(symbol=order.symbol, side=side, size=order.size, entry_price=order.price)
        else:
            # for demo, we close existing opposite position or add to same side
            if pos.side == side:
                # average entry price
                new_size = pos.size + order.size
                pos.entry_price = (pos.entry_price * pos.size + order.price * order.size) / new_size
                pos.size = new_size
            else:
                # reduce or flip
                if order.size < pos.size:
                    pos.size -= order.size
                elif order.size == pos.size:
                    # close
                    del self.positions[order.symbol]
                else:
                    # flip
                    new_size = order.size - pos.size
                    pos.side = side
                    pos.size = new_size
                    pos.entry_price = order.price
        # no change to cash for FX spot simulation; to simplify, we update realized pnl only on explicit closes (not implemented)
        self.trade_history.append(order)

    def update_unrealized(self, symbol, market_price):
        pos = self.positions.get(symbol)
        if pos:
            if pos.side == 'long':
                pos.unrealized_pnl = (market_price - pos.entry_price) * pos.size
            else:
                pos.unrealized_pnl = (pos.entry_price - market_price) * pos.size

    def close_all(self):
        with self.lock:
            for symbol, pos in list(self.positions.items()):
                # simplified: realize all unrealized pnl into balance
                self.balance += pos.realized_pnl + pos.unrealized_pnl
                del self.positions[symbol]
