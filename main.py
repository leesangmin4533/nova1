import threading
import time

from agents.market_sentiment import MarketSentimentAgent
from agents.strategy_selector import StrategySelector
from agents.entry_decision import EntryDecisionAgent
from agents.position_manager import PositionManager
from agents.logger_agent import LoggerAgent
from agents.learning_agent import LearningAgent
from status_server import create_app, shared_state


def run_server():
    app = create_app()
    app.run(host="0.0.0.0", port=5000, use_reloader=False)


def main():
    sentiment_agent = MarketSentimentAgent()
    strategy_selector = StrategySelector()
    entry_agent = EntryDecisionAgent()
    position_manager = PositionManager()
    logger = LoggerAgent()
    learning_agent = LearningAgent()

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    while True:
        sentiment = sentiment_agent.update(None, None, None)
        strategy, params = strategy_selector.select(sentiment)
        signal = entry_agent.evaluate((strategy, params), None, None)
        logger.log("EntryDecisionAgent", signal)

        shared_state["sentiment"] = sentiment_agent.state
        shared_state["strategy"] = (strategy, params)
        shared_state["signal"] = signal
        shared_state["positions"] = position_manager.positions
        time.sleep(1)


if __name__ == "__main__":
    main()
