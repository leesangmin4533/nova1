# Trading Agent Demo

This repository provides a minimal example of a multi-agent trading framework with
a simple web dashboard built using Flask. The agents demonstrate the following roles:

- **MarketSentimentAgent**: classifies market sentiment.
- **StrategySelector**: chooses a trading strategy based on sentiment.
- **EntryDecisionAgent**: decides whether to buy, sell, or hold.
- **PositionManager**: evaluates open positions for exit conditions.
- **LoggerAgent**: records agent activity to JSON files.
- **VisualizerAgent**: stores the latest state for the web dashboard.
- **LearningAgent**: placeholder for future strategy learning.

## Requirements

- Python 3.8+

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the tests with `pytest`:

```bash
pytest -q
```

Run the dashboard (a Flask web server will start on port 5000):

```bash
python main.py
```

You can view the web dashboard at `http://localhost:5000/`.
The server also exposes a JSON status API at `http://localhost:5000/status`.

## Disclaimer / 면책 조항

**English:** This project is provided for demonstration and educational purposes only. It is not intended as financial advice or a solicitation to trade. Using this code for real trading is done at your own risk, and the authors disclaim all liability for any potential losses.

**한국어:** 본 프로젝트는 예제와 학습을 위한 용도로만 제공됩니다. 투자 권유나 재정적 조언이 아니며, 실제 거래에 사용하여 발생할 수 있는 손실에 대해 저자들은 일체의 책임을 지지 않습니다.

