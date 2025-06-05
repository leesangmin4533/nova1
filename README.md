# Trading Agent Demo

This repository provides a minimal example of a multi-agent trading framework with
a simple Flask status page. The agents demonstrate the following roles:

- **MarketSentimentAgent**: classifies market sentiment.
- **StrategySelector**: chooses a trading strategy based on sentiment.
- **EntryDecisionAgent**: decides whether to buy, sell, or hold.
- **PositionManager**: evaluates open positions for exit conditions.
- **LoggerAgent**: records agent activity to JSON files.
- **StatusServer**: provides a Flask status page at /status.
- **LearningAgent**: placeholder for future strategy learning.

## Requirements

- Python 3.8+
- PyQt5
- Flask

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
python main.py
```
