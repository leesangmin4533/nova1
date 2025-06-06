import time
import os
import sys

# Ensure the src package is available for imports when running this file
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agents.market_sentiment import MarketSentimentAgent
from agents.strategy_selector import StrategySelector
from agents.entry_decision import EntryDecisionAgent
from agents.position_manager import PositionManager
from agents.logger_agent import LoggerAgent
from agents.learning_agent import LearningAgent
from agents.utils import get_upbit_candles, get_upbit_orderbook
from status_server import start_status_server, update_state
from log_analyzer import load_logs, analyze_logs


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
        self.position = None
        self.last_signal = "HOLD"
        self.current_price = 0.0
        self.balance = 1_000_000.0  # KRW starting balance
        self.last_trade_time = None
        self.trade_history = []

    def loop(self):
        try:
            candle_data = get_upbit_candles(SYMBOL, 20)
            order_book = get_upbit_orderbook(SYMBOL)
        except Exception as e:
            print(f"Failed to fetch market data: {e}")
            return

        self.current_price = candle_data[-1]

        sentiment = self.sentiment_agent.update(candle_data, order_book, None)
        rsi = self.sentiment_agent.rsi
        bb_score = self.sentiment_agent.bb_score
        ts_score = self.sentiment_agent.ts_score

        self.strategy_selector.update_scores(self.learning_agent.weights)
        strategy, params, score = self.strategy_selector.select(sentiment)
        weight = params.get("weight")

        order_status = {
            "has_position": self.position is not None,
            "return_rate": 0.0,
        }
        if self.position:
            order_status["return_rate"] = (
                self.current_price - self.position["entry_price"]
            ) / self.position["entry_price"]

        result = self.entry_agent.evaluate(
            (strategy, params), candle_data, order_status, order_book
        )
        if isinstance(result, dict):
            signal = result.get("signal")
            confidence = result.get("confidence")
        else:
            signal = result
            confidence = None
        self.last_signal = signal

        if signal == "BUY" and self.position is None:
            self.position = {"entry_price": self.current_price, "quantity": 1.0, "symbol": SYMBOL}
            self.balance -= self.current_price
            ts = self.logger.log(
                "EntryDecisionAgent",
                "BUY",
                price=self.current_price,
                symbol=SYMBOL,
                return_rate=0.0,
            )
            if ts:
                self.last_trade_time = ts
        elif signal == "SELL" and self.position is not None:
            return_rate = (
                self.current_price - self.position["entry_price"]
            ) / self.position["entry_price"]
            self.balance += self.current_price * self.position["quantity"]
            ts = self.logger.log(
                "EntryDecisionAgent",
                "SELL",
                price=self.current_price,
                symbol=self.position["symbol"],
                return_rate=return_rate,
            )
            if ts:
                self.last_trade_time = ts
            self.trade_history.append({"strategy": strategy, "return": return_rate})
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
                ts = self.logger.log(
                    "PositionManager",
                    "CLOSE",
                    price=self.current_price,
                    symbol=self.position["symbol"],
                    return_rate=return_rate,
                )
                if ts:
                    self.last_trade_time = ts
                self.trade_history.append({"strategy": strategy, "return": return_rate})
                self.position = None

        position_state = None
        return_rate = None
        if self.position:
            return_rate = (
                self.current_price - self.position["entry_price"]
            ) / self.position["entry_price"]
            position_state = {
                "entry_price": self.position["entry_price"],
                "return_rate": return_rate,
            }

        logs = load_logs("log")
        stats = analyze_logs(logs)
        cumulative_return = stats.get("cumulative_return", 0.0)

        self.learning_agent.update(self.trade_history)
        update_state(
            sentiment=sentiment,
            strategy=strategy,
            selected_strategy=strategy,
            strategy_score=score,
            position=position_state,
            signal=self.last_signal,
            price=self.current_price,
            balance=self.balance,
            weight=weight,
            weights=self.learning_agent.weights,
            bid_volume=order_book.get("bid_volume"),
            ask_volume=order_book.get("ask_volume"),
            orderbook_score=confidence,
            rsi=rsi,
            bb_score=bb_score,
            ts_score=ts_score,
            return_rate=return_rate,
            cumulative_return=cumulative_return,
            last_trade_time=self.last_trade_time,
        )


if __name__ == "__main__":
    app = TradingApp()
    # Launch the Flask status server in a background daemon thread so
    # that the trading loop can run uninterrupted.
    server_thread = start_status_server()
    while True:
        app.loop()
        time.sleep(60)

