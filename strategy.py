# strategy.py
from abc import ABC, abstractmethod
from typing import List, Optional
from models import Candle
import numpy as np
from utils import CandleSeries
import config

class StrategyBase(ABC):
    def __init__(self):
        self.candles = CandleSeries()

    @abstractmethod
    def on_candle(self, candle: Candle):
        """
        Should return None or a dict like {'signal': 'buy'/'sell', 'size': float}
        """
        pass

class MovingAverageCrossStrategy(StrategyBase):
    """
    Simple SMA fast/slow crossover. Demonstrates OOP inheritance and state.
    """
    def __init__(self, ma_fast=config.MA_FAST, ma_slow=config.MA_SLOW):
        super().__init__()
        self.ma_fast = ma_fast
        self.ma_slow = ma_slow
        self.last_signal = None  # 'buy' or 'sell' or None

    def _sma(self, arr: np.ndarray, period: int) -> Optional[float]:
        if len(arr) < period:
            return None
        return float(arr[-period:].mean())

    def on_candle(self, candle: Candle):
        self.candles.append(candle)
        closes = self.candles.to_close_array()
        sma_fast = self._sma(closes, self.ma_fast)
        sma_slow = self._sma(closes, self.ma_slow)
        if sma_fast is None or sma_slow is None:
            return None

        if sma_fast > sma_slow and self.last_signal != 'buy':
            self.last_signal = 'buy'
            return {'signal': 'buy'}
        elif sma_fast < sma_slow and self.last_signal != 'sell':
            self.last_signal = 'sell'
            return {'signal': 'sell'}
        return None
