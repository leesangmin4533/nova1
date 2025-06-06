import time

from agents.market_sentiment import MarketSentimentAgent
from agents.strategy_selector import StrategySelector
from agents.entry_decision import EntryDecisionAgent
from agents.position_manager import PositionManager
from agents.logger_agent import LoggerAgent
from agents.visualizer import VisualizerAgent
from agents.learning_agent import LearningAgent
from agents.utils import get_upbit_candles, get_upbit_orderbook
from status_server import start_status_server


SYMBOL = "KRW-BTC"


class TradingApp:
    """Main application that coordinates all agents."""

    def __init__(self):
        self.sentiment_agent = MarketSentimentAgent()
        self.strategy_selector = StrategySelector()
        self.entry_agent = EntryDecisionAgent()
        self.position_manager = PositionManager()
        self.logger = LoggerAgent()
        self.learning_agent = LearningAgent()
        self.visualizer = VisualizerAgent()
        self.position = None
        self.last_signal = "HOLD"
        self.current_price = 0.0
        self.balance = 1_000_000.0  # KRW starting balance

    def loop(self):
        try:
            candle_data = get_upbit_candles(SYMBOL, 20)
            order_book = get_upbit_orderbook(SYMBOL)
        except Exception as e:
            print(f"Failed to fetch market data: {e}")
            return

        self.current_price = candle_data[-1]

        sentiment = self.sentiment_agent.update(candle_data, order_book, None)
        self.strategy_selector.update_scores(self.learning_agent.weights)
        strategy, params = self.strategy_selector.select(sentiment)

        order_status = {
            "has_position": self.position is not None,
            "return_rate": 0.0,
        }
        if self.position:
            order_status["return_rate"] = (
                self.current_price - self.position["entry_price"]
            ) / self.position["entry_price"]

        signal = self.entry_agent.evaluate((strategy, params), candle_data, order_status)
        self.last_signal = signal

        if signal == "BUY" and self.position is None:
            self.position = {"entry_price": self.current_price, "quantity": 1.0, "symbol": SYMBOL}
            self.balance -= self.current_price
            self.logger.log(
                "EntryDecisionAgent",
                "BUY",
                price=self.current_price,
                symbol=SYMBOL,
                return_rate=0.0,
            )
        elif signal == "SELL" and self.position is not None:
            return_rate = (
                self.current_price - self.position["entry_price"]
            ) / self.position["entry_price"]
            self.balance += self.current_price * self.position["quantity"]
            self.logger.log(
                "EntryDecisionAgent",
                "SELL",
                price=self.current_price,
                symbol=self.position["symbol"],
                return_rate=return_rate,
            )
            self.position = None

        if self.position:
            decision = self.position_manager.update(
                self.position, self.position["entry_price"], self.current_price
            )
            if decision == "CLOSE":
                return_rate = (
                    self.current_price - self.position["entry_price"]
                ) / self.position["entry_price"]
                self.balance += self.current_price * self.position["quantity"]
                self.logger.log(
                    "PositionManager",
                    "CLOSE",
                    price=self.current_price,
                    symbol=self.position["symbol"],
                    return_rate=return_rate,
                )
                self.position = None

        position_state = None
        if self.position:
            return_rate = (
                self.current_price - self.position["entry_price"]
            ) / self.position["entry_price"]
            position_state = {
                "entry_price": self.position["entry_price"],
                "return_rate": return_rate,
            }

        self.visualizer.update_state(
            sentiment,
            strategy,
            position_state,
            self.last_signal,
            self.current_price,
            self.balance,
        )


if __name__ == "__main__":
    app = TradingApp()
    # Launch the Flask status server in a background daemon thread so
    # that the trading loop can run uninterrupted.
    server_thread = start_status_server(app)
    while True:
        app.loop()
        time.sleep(1)
