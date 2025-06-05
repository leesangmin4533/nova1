from PyQt5 import QtWidgets, QtCore

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
        # Poll Upbit data twice per second
        timer.start(500)
        return timer

    def loop(self):
        # Placeholder example data
        sentiment = self.sentiment_agent.update(None, None, None)
        strategy, params = self.strategy_selector.select(sentiment)
        signal = self.entry_agent.evaluate((strategy, params), None, None)
        position = "None"
        self.logger.log(sentiment, strategy, signal)
        self.visualizer.update_state(sentiment, strategy, position)


if __name__ == "__main__":
    import sys

    app = TradingApp(sys.argv)
    sys.exit(app.exec_())
