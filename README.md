# Trading Agent Demo

This repository demonstrates a minimal multi-agent trading framework. The project now provides a static dashboard built with React and Tailwind CSS.

The agents include:

- **MarketSentimentAgent**: classifies market sentiment.
- **StrategySelector**: chooses a trading strategy based on sentiment.
- **EntryDecisionAgent**: decides whether to buy, sell, or hold.
- **PositionManager**: evaluates open positions for exit conditions.
- **LoggerAgent**: appends agent activity to a daily `log_YYYYMMDD.jsonl` file under `C:/Users/kanur/log`.
- **DailyLogger**: appends daily success and failure entries in `NOVA_LOGS` on your Desktop.
- **SessionLogger**: writes all actions for a single run to `NOVA_LOGS/trade_log_<timestamp>.json`.
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

## React Dashboard

The UI is implemented with **React** and **Tailwind CSS** and can be built into static files.

```bash
cd ui-react
npm install        # first time only
npm run build      # outputs files to ui-react/dist
```

Open `ui-react/dist/index.html` in your browser to view the dashboard.
The Python utilities in this repository operate independently of the UI.

## Legacy HTML UI

The script `nova_ui_update.py` writes a small `ui_data.json` file every few
seconds using live data from Upbit. When the legacy HTML file defined by
`config.UI_PATH` exists, running this script automatically opens it in your
browser and keeps the data refreshed.

## Disclaimer / 면책 조항

**English:** This project is provided for demonstration and educational purposes only. It is not intended as financial advice or a solicitation to trade. Using this code for real trading is done at your own risk, and the authors disclaim all liability for any potential losses.

**한국어:** 본 프로젝트는 예제와 학습을 위한 용도로만 제공됩니다. 투자 권유나 재정적 조언이 아니며, 실제 거래에 사용하여 발생할 수 있는 손실에 대해 저자들은 일체의 책임을 지지 않습니다.

