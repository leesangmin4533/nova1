from PyQt5 import QtWidgets, QtCore
import asyncio

from agents.market_sentiment import MarketSentimentAgent
from agents.strategy_selector import StrategySelector
from agents.entry_decision import EntryDecisionAgent
from agents.position_manager import PositionManager
from agents.logger_agent import LoggerAgent
from agents.visualizer import VisualizerAgent
from agents.learning_agent import LearningAgent
from config_loader import ConfigLoader
from upbit_api import UpbitClient
from broker import UpbitBroker


class TradingApp(QtWidgets.QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.config = ConfigLoader().load()
        self.sentiment_agent = MarketSentimentAgent()
        self.strategy_selector = StrategySelector()
        self.broker = UpbitBroker()
        self.entry_agent = EntryDecisionAgent(self.broker)
        self.position_manager = PositionManager()
        self.logger = LoggerAgent()
        self.learning_agent = LearningAgent(self.config)
        self.visualizer = VisualizerAgent()
        self.visualizer.show()
        self.client = UpbitClient()
        self.timer = self.createTimer()

    def createTimer(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(lambda: asyncio.create_task(self.loop()))
        timer.start(1000)
        return timer

    async def loop(self):
        data = await asyncio.gather(
            self.client.fetch_candle(),
            self.client.fetch_orderbook(),
            self.client.fetch_trades(),
        )
        candles, orderbook, trades = data
        sentiment = self.sentiment_agent.update(candles, orderbook, 0)
        strategy, params = self.strategy_selector.select(sentiment)
        signal = self.entry_agent.evaluate((strategy, params), candles, None)
        position = "None"
        self.logger.log("EntryDecisionAgent", signal)
        self.visualizer.update_state(sentiment, strategy, position)


if __name__ == "__main__":
    import sys

    app = TradingApp(sys.argv)
    sys.exit(app.exec_())
