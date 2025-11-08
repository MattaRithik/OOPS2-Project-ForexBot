# gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from models import Candle
import time

class ForexBotGUI:
    def __init__(self, root, start_callback, stop_callback, get_state_callback):
        self.root = root
        self.start_cb = start_callback
        self.stop_cb = stop_callback
        self.get_state = get_state_callback

        root.title("Forex Bot (Paper Trading)")

        main = ttk.Frame(root, padding="8")
        main.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Controls
        controls = ttk.Frame(main)
        controls.grid(row=0, column=0, sticky=tk.W)
        ttk.Button(controls, text="Start", command=self.start).grid(row=0, column=0, padx=4)
        ttk.Button(controls, text="Stop", command=self.stop).grid(row=0, column=1, padx=4)

        # Chart area
        self.fig = Figure(figsize=(6,3))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=main)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky=(tk.N,tk.W))

        # Log area
        self.log = scrolledtext.ScrolledText(main, width=80, height=10)
        self.log.grid(row=2, column=0, pady=6)

        # status update loop
        self._running = True
        self._update_loop()

    def start(self):
        self.start_cb()
        self._log("Started")

    def stop(self):
        self.stop_cb()
        self._log("Stopped")

    def _log(self, txt):
        ts = time.strftime("%H:%M:%S")
        self.log.insert(tk.END, f"[{ts}] {txt}\n")
        self.log.see(tk.END)

    def _update_loop(self):
        state = self.get_state()
        # draw price series
        if state:
            closes = state.get("closes", [])
            times = list(range(len(closes)))
            self.ax.clear()
            if closes:
                self.ax.plot(times, closes)
            positions = state.get("positions", {})
            for i, (sym, pos) in enumerate(positions.items()):
                self._log(f"Pos {sym}: {pos.side} size={pos.size:.2f} entry={pos.entry_price:.5f} pnl={pos.unrealized_pnl:.2f}")
        # schedule next update
        if self._running:
            self.canvas.draw()
            self.root.after(1000, self._update_loop)

    def shutdown(self):
        self._running = False
