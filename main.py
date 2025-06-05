from time import sleep
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from agents.market_sentiment import MarketSentimentAgent
from agents.strategy_selector import StrategySelector
from agents.entry_decision import EntryDecisionAgent
from agents.position_manager import PositionManager
from agents.logger_agent import LoggerAgent
from agents.learning_agent import LearningAgent
from agents.web_visualizer import WebVisualizerAgent


def main():
    sentiment_agent = MarketSentimentAgent()
    strategy_selector = StrategySelector()
    entry_agent = EntryDecisionAgent()
    position_manager = PositionManager()
    logger = LoggerAgent()
    learning_agent = LearningAgent()
    visualizer = WebVisualizerAgent()

    while True:
        sentiment = sentiment_agent.update(None, None, None)
        strategy, params = strategy_selector.select(sentiment)
        signal = entry_agent.evaluate((strategy, params), None, None)
        position = "None"
        logger.log("EntryDecisionAgent", signal)
        visualizer.update_state(sentiment, strategy, position)
        sleep(1)


if __name__ == "__main__":
    main()
