# Trading Agent Demo

This repository provides a minimal example of a multi-agent trading framework with
a simple PyQt5 dashboard. The agents demonstrate the following roles:

- **MarketSentimentAgent**: classifies market sentiment.
- **StrategySelector**: chooses a trading strategy based on sentiment.
- **EntryDecisionAgent**: decides whether to buy, sell, or hold.
- **PositionManager**: evaluates open positions for exit conditions.
- **LoggerAgent**: records agent activity to JSON files.
- **VisualizerAgent**: displays the current state in a window.
- **LearningAgent**: placeholder for future strategy learning.

## Requirements

- Python 3.8+
- PyQt5

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard (a Flask status server will start on port 5000):

```bash
python main.py
```

You can view the current trading status by visiting `http://localhost:5000/status`.
