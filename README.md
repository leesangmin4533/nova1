# Trading Agent Demo

This repository provides a minimal example of a multi-agent trading framework with
a simple PyQt5 dashboard. The agents demonstrate the following roles:

- **MarketSentimentAgent**: classifies market sentiment.
- **StrategySelector**: chooses a trading strategy based on sentiment.
- **EntryDecisionAgent**: decides whether to buy, sell, or hold.
- **PositionManager**: evaluates open positions for exit conditions.
- **LoggerAgent**: records agent activity to JSON files.
- **VisualizerAgent**: displays the current state in a window.
- **LearningAgent**: updates strategy weights based on trade history.

## Requirements

- Python 3.8+
- PyQt5
- numpy
- pandas
- scikit-learn
- xgboost

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
python main.py
```

The example application generates dummy market data and demonstrates how the
agents interact. Entry signals require a confidence of at least `0.65` based on
simple rule weights.
