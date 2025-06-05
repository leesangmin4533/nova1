# Trading Agent Demo

This repository provides a minimal example of a multi-agent trading framework with
a simple PyQt5 dashboard. The agents demonstrate the following roles:

- **MarketSentimentAgent**: classifies market sentiment.
- **StrategySelector**: chooses a trading strategy based on sentiment.
- **EntryDecisionAgent**: evaluates MA cross and RSI to trigger orders.
- **PositionManager**: evaluates open positions for exit conditions.
- **LoggerAgent**: records agent activity to JSON files.
- **VisualizerAgent**: displays the current state in a window.
- **LearningAgent**: adjusts strategy condition weights based on performance.
- **UpbitClient**: fetches real-time market data.
- **UpbitBroker**: example interface for order execution.

Additional utility functions are provided in `nova_strategy.py`:

- `generate_nova_strategy_json` to create a standardized JSON-like dictionary describing a strategy.
- `adjust_weights` to lower weights for conditions with high failure rates.

## Requirements

- Python 3.8+
- PyQt5
- aiohttp

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
python main.py
```

## Configuration

Default parameters for the NOVA framework are stored in `kodex_config.yaml`.
This YAML file defines refresh intervals, scoring weights, and failure
policies used by the agents. You can load it using `ConfigLoader`:

```python
from config_loader import ConfigLoader
config = ConfigLoader().load()
```
