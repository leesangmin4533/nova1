import pandas as pd


class EntryDecisionAgent:
    """Determine trade entry signals."""

    CONDITION_WEIGHTS = {
        "golden_cross": 0.5,
        "rsi": 0.5,
    }

    def __init__(self, threshold: float = 0.65):
        self.threshold = threshold

    @staticmethod
    def rsi(series, period: int = 14):
        delta = series.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ma_up = up.rolling(window=period).mean()
        ma_down = down.rolling(window=period).mean()
        rs = ma_up / ma_down
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def golden_cross(self, series, short=50, long=200):
        short_ma_prev = series.rolling(window=short).mean().iloc[-2]
        long_ma_prev = series.rolling(window=long).mean().iloc[-2]
        short_ma_curr = series.rolling(window=short).mean().iloc[-1]
        long_ma_curr = series.rolling(window=long).mean().iloc[-1]
        return short_ma_prev <= long_ma_prev and short_ma_curr > long_ma_curr

    def evaluate(self, strategy, chart_data, order_status):
        """Return BUY, SELL, or HOLD signal."""
        df = pd.DataFrame(chart_data)
        if len(df) < 200:
            return "HOLD"

        signals = {
            "golden_cross": self.golden_cross(df["close"]),
            "rsi": self.rsi(df["close"]) > 55,
        }

        confidence = sum(
            self.CONDITION_WEIGHTS[k] for k, v in signals.items() if v
        )

        if confidence >= self.threshold:
            return "BUY"
        return "HOLD"
