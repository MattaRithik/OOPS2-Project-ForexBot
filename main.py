# main.py
import threading
import time
from yahoo_data_provider import YahooForexDataProvider
from strategy import MovingAverageCrossStrategy
from broker import PaperBroker
from risk_manager import RiskManager
import config
from gui import ForexBotGUI
import tkinter as tk

class ForexBotApp:
    def __init__(self):
        self.broker = PaperBroker(initial_balance=config.INITIAL_BALANCE)
        self.risk = RiskManager(self.broker)
        self.strategy = MovingAverageCrossStrategy()
        self.data = YahooForexDataProvider(yahoo_symbol=config.SYMBOL, interval_seconds=config.BAR_SECONDS)
        self.data.register_callback(self.on_candle)
        self._running = False
        self._closes = []

    def on_candle(self, candle):
        
        # update broker unrealized
        self.broker.update_unrealized(config.SYMBOL, candle.close)
        # feed strategy
        sig = self.strategy.on_candle(candle)
        # bookkeeping for GUI
        self._closes.append(candle.close)
        if sig:
            if sig['signal'] == 'buy':
                price = candle.close
                size = self.risk.size_for_order(config.SYMBOL, 'buy', price)
                order = self.broker.place_market_order(config.SYMBOL, 'buy', size, price)
            elif sig['signal'] == 'sell':
                price = candle.close
                size = self.risk.size_for_order(config.SYMBOL, 'sell', price)
                order = self.broker.place_market_order(config.SYMBOL, 'sell', size, price)

    def start(self):
        if self._running: return
        self._running = True
        self.data.start()

    def stop(self):
        if not self._running: return
        self._running = False
        self.data.stop()

    def get_state(self):
        return {"closes": self._closes[-200:], "positions": {k:v for k,v in self.broker.positions.items()}}

def run_gui_app():
    app = ForexBotApp()
    root = tk.Tk()
    gui = ForexBotGUI(root, start_callback=app.start, stop_callback=app.stop, get_state_callback=app.get_state)
    try:
        root.mainloop()
    finally:
        gui.shutdown()
        app.stop()

if __name__ == "__main__":
    run_gui_app()
