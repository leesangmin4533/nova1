from PyQt5 import QtWidgets, QtCore
import random

from agents.market_sentiment import MarketSentimentAgent
from agents.strategy_selector import StrategySelector
from agents.entry_decision import EntryDecisionAgent
from agents.position_manager import PositionManager
from agents.logger_agent import LoggerAgent
from agents.visualizer import VisualizerAgent
from agents.learning_agent import LearningAgent


class TradingApp(QtWidgets.QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.sentiment_agent = MarketSentimentAgent()
        self.strategy_selector = StrategySelector()
        self.entry_agent = EntryDecisionAgent()
        self.position_manager = PositionManager()
        self.logger = LoggerAgent()
        self.learning_agent = LearningAgent()
        self.visualizer = VisualizerAgent()
        self.visualizer.show()
        self.timer = self.createTimer()
        # demo state
        self.candles = []
        self.order_book = {"bid": 100.0, "ask": 100.0}
        self.trade_strength = 0.5
        self.last_price = 100.0
        self.position = None
        self.sentiment = "NEUTRAL"
        self.strategy = ("hold", {})

    def createTimer(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.loop)
        timer.start(1000)
        return timer

    def loop(self):
        self._generate_fake_data()
        self.sentiment = self.sentiment_agent.update(
            self.candles, self.order_book, self.trade_strength
        )
        self.strategy = self.strategy_selector.select(self.sentiment)
        signal = self.entry_agent.evaluate(self.strategy, self.candles, None)

        if signal in ("BUY", "SELL") and not self.position:
            self.position = {"side": signal, "entry_price": self.last_price}
            self.logger.log("EntryDecisionAgent", signal, price=self.last_price)

        if self.position:
            close_signal = self.position_manager.update(
                self.position, self.position["entry_price"], self.last_price
            )
            if close_signal == "CLOSE":
                self.logger.log("PositionManager", "CLOSE", price=self.last_price)
                self.position = None

        pos_text = self.position["side"] if self.position else "None"
        self.visualizer.update_state(
            self.sentiment, self.strategy[0], pos_text
        )

    def _generate_fake_data(self):
        """Create example candle and order book data."""
        self.last_price += random.uniform(-1, 1)
        volume = random.uniform(80, 120)
        self.order_book["bid"] = random.uniform(50, 150)
        self.order_book["ask"] = random.uniform(50, 150)
        self.trade_strength = random.random()
        self.candles.append({"close": self.last_price, "volume": volume})
        if len(self.candles) > 200:
            self.candles.pop(0)


if __name__ == "__main__":
    import sys

    app = TradingApp(sys.argv)
    sys.exit(app.exec_())
