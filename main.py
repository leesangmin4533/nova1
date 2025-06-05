from PyQt5 import QtWidgets, QtCore

from agents.market_sentiment import MarketSentimentAgent
from agents.strategy_selector import StrategySelector
from agents.entry_decision import EntryDecisionAgent
from agents.position_manager import PositionManager
from agents.logger_agent import LoggerAgent
from agents.visualizer import VisualizerAgent
from agents.learning_agent import LearningAgent
from agents.utils import get_upbit_candles


SYMBOL = "KRW-BTC"


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
        self.position = None
        self.last_signal = "HOLD"

    def createTimer(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.loop)
        timer.start(1000)
        return timer

    def loop(self):
        try:
            candle_data = get_upbit_candles(SYMBOL, 20)
        except Exception as e:
            print(f"Failed to fetch candles: {e}")
            return

        current_price = candle_data[-1]

        sentiment = self.sentiment_agent.update(candle_data, None, None)
        strategy, params = self.strategy_selector.select(sentiment)

        order_status = {
            "has_position": self.position is not None,
            "return_rate": 0.0,
        }
        if self.position:
            order_status["return_rate"] = (
                current_price - self.position["entry_price"]
            ) / self.position["entry_price"]

        signal = self.entry_agent.evaluate((strategy, params), candle_data, order_status)
        self.last_signal = signal

        if signal == "BUY" and self.position is None:
            self.position = {"entry_price": current_price, "quantity": 1.0, "symbol": SYMBOL}
            self.logger.log(
                "EntryDecisionAgent",
                "BUY",
                price=current_price,
                symbol=SYMBOL,
                return_rate=0.0,
            )
        elif signal == "SELL" and self.position is not None:
            return_rate = (
                current_price - self.position["entry_price"]
            ) / self.position["entry_price"]
            self.logger.log(
                "EntryDecisionAgent",
                "SELL",
                price=current_price,
                symbol=self.position["symbol"],
                return_rate=return_rate,
            )
            self.position = None

        if self.position:
            decision = self.position_manager.update(
                self.position, self.position["entry_price"], current_price
            )
            return_rate = (
                current_price - self.position["entry_price"]
            ) / self.position["entry_price"]
            if decision == "CLOSE":
                self.logger.log(
                    "PositionManager",
                    "CLOSE",
                    price=current_price,
                    symbol=self.position["symbol"],
                    return_rate=return_rate,
                )
                self.position = None

        position_state = None
        if self.position:
            return_rate = (
                current_price - self.position["entry_price"]
            ) / self.position["entry_price"]
            position_state = {
                "entry_price": self.position["entry_price"],
                "return_rate": return_rate,
            }

        self.visualizer.update_state(sentiment, strategy, position_state, self.last_signal)


if __name__ == "__main__":
    import sys

    app = TradingApp(sys.argv)
    sys.exit(app.exec_())
