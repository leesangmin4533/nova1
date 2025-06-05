from PyQt5 import QtWidgets, QtCore
import random
from pathlib import Path

import pandas as pd
import sys

sys.path.append(str(Path(__file__).resolve().parent / "src"))

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

    def createTimer(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.loop)
        timer.start(1000)
        return timer

    def loop(self):
        # Generate dummy candle data
        if not hasattr(self, "candles"):
            self.candles = [
                {"close": 100 + random.random(), "volume": 1000 + random.randint(-10, 10)}
                for _ in range(200)
            ]
        else:
            last_price = self.candles[-1]["close"]
            new_price = last_price * (1 + random.uniform(-0.01, 0.01))
            self.candles.append({"close": new_price, "volume": 1000 + random.randint(-10, 10)})
            self.candles = self.candles[-200:]

        order_book = {"bid_volume": random.uniform(0.5, 1.5), "ask_volume": random.uniform(0.5, 1.5)}
        sentiment = self.sentiment_agent.update(self.candles, order_book, None)
        strategy, params = self.strategy_selector.select(sentiment)
        signal = self.entry_agent.evaluate((strategy, params), self.candles, None)
        position = "None"
        self.logger.log("EntryDecisionAgent", signal)
        self.visualizer.update_state(sentiment, strategy, position)


if __name__ == "__main__":
    import sys

    app = TradingApp(sys.argv)
    sys.exit(app.exec_())
