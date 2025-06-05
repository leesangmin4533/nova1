from PyQt5 import QtWidgets, QtCore
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent / "src"))

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
        # Example data for demonstration purposes only
        sample_candles = [
            {"close": p, "volume": 100 + i * 5} for i, p in enumerate(range(100, 130))
        ]
        book = {"bid_volume": 1200, "ask_volume": 1000}
        sentiment = self.sentiment_agent.update(sample_candles, book, None)
        strategy, params = self.strategy_selector.select(sentiment)
        # pass RSI into entry agent parameters for simple evaluation
        params["rsi"] = self.sentiment_agent._rsi([c["close"] for c in sample_candles])
        signal = self.entry_agent.evaluate((strategy, params), sample_candles, None)
        position = "None"
        self.logger.log("EntryDecisionAgent", signal)
        self.visualizer.update_state(sentiment, strategy, position)


if __name__ == "__main__":
    import sys

    app = TradingApp(sys.argv)
    sys.exit(app.exec_())
