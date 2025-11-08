# yahoo_data_provider.py
import time
import threading
import yfinance as yf
from models import Candle
from typing import Callable, Optional
import config

class YahooForexDataProvider:
    """
    Pulls latest forex prices from Yahoo Finance every BAR_SECONDS interval
    and emits Candle objects.
    """

    def __init__(self, yahoo_symbol=config.SYMBOL, interval_seconds=config.BAR_SECONDS):
        self.symbol = yahoo_symbol
        self.interval = interval_seconds
        self._cb: Optional[Callable[[Candle], None]] = None
        self._running = False
        self._thread = None

        # initial price fetch
        self._last_price = None

    def register_callback(self, cb):
        self._cb = cb

    def _get_latest_price(self):
        data = yf.download(self.symbol, period="1d", interval="1m")
        if data.empty:
            return None
        
        last_row = data.iloc[-1]
        return Candle(
            timestamp=time.time(),
            open=float(last_row["Open"]),
            high=float(last_row["High"]),
            low=float(last_row["Low"]),
            close=float(last_row["Close"]),
            volume=float(last_row.get("Volume", 0))
        )

    def _run(self):
        while self._running:
            candle = self._get_latest_price()
            if candle and self._cb:
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
