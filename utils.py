# utils.py
import collections
from typing import Deque, List
from models import Candle
import numpy as np

class CandleSeries:
    def __init__(self, maxlen=5000):
        self._candles: Deque[Candle] = collections.deque(maxlen=maxlen)

    def append(self, candle: Candle):
        self._candles.append(candle)

    def to_close_array(self):
        return np.array([c.close for c in self._candles])

    def last(self, n=1):
        if len(self._candles) == 0:
            return []
        return list(self._candles)[-n:]
