"""Nova trading UI skeleton following the NOVA UI guidelines."""

import random
import tkinter as tk
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import requests


@dataclass
class MarketData:
    symbol: str
    price: float
    timestamp: float


class DataProvider:
    """Fetches market data from the Upbit exchange."""

    BASE_URL = "https://api.upbit.com/v1/ticker"

    def get_latest(self, symbol: str) -> MarketData:
        """Return the latest market data for ``symbol`` from Upbit."""
        market = f"KRW-{symbol.upper()}"
        response = requests.get(self.BASE_URL, params={"markets": market}, timeout=5)
        response.raise_for_status()
        ticker = response.json()[0]
        return MarketData(
            symbol=market,
            price=ticker["trade_price"],
            timestamp=ticker["timestamp"] / 1000.0,
        )


class NovaStatusApp(tk.Tk):
    """Simple UI showing market status and strategy signal."""

    BG_COLOR = "#0f1117"
    FG_COLOR = "#ffffff"
    ACCENT_COLOR = "#3ec9f3"

    def __init__(self, symbol: str):
        super().__init__()
        self.symbol = symbol
        self.data_provider = DataProvider()
        self.title("Nova Status")
        self.configure(bg=self.BG_COLOR)

        # Price label at the top
        self.price_label = tk.Label(self, fg=self.FG_COLOR, bg=self.BG_COLOR, font=("Arial", 14))
        self.price_label.pack(pady=5)

        # Psychological state label
        self.state_label = tk.Label(self, fg=self.FG_COLOR, bg=self.BG_COLOR, font=("Arial", 12))
        self.state_label.pack(pady=5)

        # Canvas for simple bar graph
        self.canvas = tk.Canvas(self, width=300, height=50, bg=self.BG_COLOR, highlightthickness=0)
        self.canvas.pack(pady=5)

        # Strategy label
        self.strategy_label = tk.Label(self, fg=self.FG_COLOR, bg=self.BG_COLOR, font=("Arial", 12))
        self.strategy_label.pack(pady=5)

        self.after(0, self.update_status)  # start updating immediately

    def fetch_psychology(self) -> List[Tuple[str, int, str]]:
        """Return random psychology data as (label, percent, color)."""
        return [
            ("공포", random.randint(0, 30), "#e74c3c"),
            ("회의", random.randint(0, 30), "#8e44ad"),
            ("탐색", random.randint(0, 30), "#2980b9"),
            ("탐욕", random.randint(0, 30), "#27ae60"),
            ("과열", random.randint(0, 30), "#f1c40f"),
        ]

    def update_status(self) -> None:
        """Fetch market and psychology data, then refresh UI."""
        try:
            data = self.data_provider.get_latest(self.symbol)
            self.price_label.config(text=f"{data.symbol} 가격: {data.price}")
        except Exception:
            # network error fallback
            self.price_label.config(text=f"{self.symbol} 가격: N/A")

        psy_data = self.fetch_psychology()
        # Choose the dominant psychology stage
        stage, _, color = max(psy_data, key=lambda x: x[1])
        self.state_label.config(text=f"현재 심리: {stage}", fg=color)

        # Draw simple bar graph
        self.canvas.delete("all")  # clear previous bars
        total = sum(p[1] for p in psy_data)
        if total == 0:
            total = 1
        x = 0
        width = 300
        for _, percent, c in psy_data:
            w = width * percent / total
            self.canvas.create_rectangle(x, 0, x + w, 50, fill=c, width=0)
            x += w

        self.strategy_label.config(text="전략: 단순 매매")
        self.after(3000, self.update_status)


if __name__ == "__main__":
    app = NovaStatusApp("BTC")
    app.mainloop()
