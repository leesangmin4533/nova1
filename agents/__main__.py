import asyncio

from .data.pipeline import DataStream
from .sentiment import MarketSentimentAgent, Sentiment
from .strategy import Strategy, StrategySelector
from .entry import EntryDecisionAgent, Signal
from .position import PositionManager, Position
from .logger_agent import LoggerAgent, LogRecord


async def main() -> None:
    data_queue: asyncio.Queue = asyncio.Queue()
    stream = DataStream(interval=1.0)
    sentiment_agent = MarketSentimentAgent(interval=1.0)
    strategies = {
        Sentiment.GREED: Strategy(id="trend_follow", parameters={}),
        Sentiment.EXTREME_FEAR: Strategy(id="reversal", parameters={}),
    }
    selector = StrategySelector(strategies=strategies)
    entry_agent = EntryDecisionAgent(interval=1.0)
    position_manager = PositionManager()
    logger = LoggerAgent()

    async def produce():
        async for data in stream.stream():
            await data_queue.put(data)

    async def consume():
        while True:
            strategy = selector.select(sentiment_agent.sentiment or Sentiment.NEUTRAL)
            signal = await entry_agent.run(data_queue, strategy)
            if signal in (Signal.BUY, Signal.SELL):
                position_manager.position = Position(entry_price=entry_agent.last_price, size=1)
                logger.log(
                    LogRecord(
                        timestamp=asyncio.get_event_loop().time(),
                        agent="EntryDecisionAgent",
                        action=signal,
                        price=entry_agent.last_price or 0.0,
                        confidence=1.0,
                    )
                )
            await asyncio.sleep(0.1)

    await asyncio.gather(sentiment_agent.run(data_queue), produce(), consume())


if __name__ == "__main__":
    asyncio.run(main())
