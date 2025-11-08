# data_provider.py
import time
import threading
import numpy as np
from models import Candle
from typing import Callable, List, Optional

class BaseDataProvider:
    def start(self): raise NotImplementedError
    def stop(self): raise NotImplementedError
    def register_callback(self, cb: Callable[[Candle], None]): raise NotImplementedError

class MockDataProvider(BaseDataProvider):
    """
    Generates synthetic price series (random walk) and emits Candle objects
    at configured intervals. Good for offline testing and OOP design.
    """
    def __init__(self, symbol="EURUSD", interval_seconds=1):
        self.symbol = symbol
        self.interval = interval_seconds
        self._running = False
        self._cb = None
        self._thread: Optional[threading.Thread] = None
        self._last_price = 1.1000

    def register_callback(self, cb):
        self._cb = cb

    def _run(self):
        while self._running:
            # simulate random walk for close price
            change = np.random.normal(loc=0, scale=0.0002)
            close = max(0.0001, self._last_price + change)
            high = close + abs(np.random.normal(0, 0.0001))
            low = close - abs(np.random.normal(0, 0.0001))
            open_p = self._last_price
            candle = Candle(timestamp=time.time(), open=open_p, high=high, low=low, close=close, volume=1.0)
            self._last_price = close
            if self._cb:
                self._cb(candle)
            time.sleep(self.interval)

    def start(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
