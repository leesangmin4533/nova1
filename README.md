# Trading Agent Demo

This repository provides a minimal example of a multi-agent trading framework with
a simple PyQt5 dashboard. The agents demonstrate the following roles:
- **MarketSentimentAgent**: analyzes candles, order book, and volume to assign one of five sentiment levels.
- **StrategySelector**: chooses the best trading strategy based on current sentiment.
- **EntryDecisionAgent**: determines buy, sell, or hold signals from strategy conditions.
- **PositionManager**: monitors open positions for profit or loss exits.
- **LoggerAgent**: writes all actions to JSON files.
- **VisualizerAgent**: displays agent states with a PyQt5 window.
- **LearningAgent**: updates strategy weights from historical performance.


## Requirements

- Python 3.8+
- numpy
- PyQt5

Install dependencies:

```bash
pip install -r requirements.txt
```
Logs are written to the `log/` directory in JSON format.

Run the dashboard:

```bash
python main.py
```
