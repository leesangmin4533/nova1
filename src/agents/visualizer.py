from PyQt5 import QtWidgets


class VisualizerAgent(QtWidgets.QWidget):
    """Basic window to visualize agent states."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trading Agent Dashboard")
        self.layout = QtWidgets.QVBoxLayout()
        self.sentiment_label = QtWidgets.QLabel("Sentiment: NEUTRAL")
        self.strategy_label = QtWidgets.QLabel("Strategy: None")
        self.position_label = QtWidgets.QLabel("Position: None")
        self.signal_label = QtWidgets.QLabel("Signal: HOLD")
        for widget in [
            self.sentiment_label,
            self.strategy_label,
            self.position_label,
            self.signal_label,
        ]:
            self.layout.addWidget(widget)
        self.setLayout(self.layout)

    def update_state(self, sentiment, strategy, position, signal):
        self.sentiment_label.setText(f"Sentiment: {sentiment}")
        self.strategy_label.setText(f"Strategy: {strategy}")
        if isinstance(position, dict):
            entry = position.get("entry_price")
            rr = position.get("return_rate")
            self.position_label.setText(
                f"Position: entry {entry:.2f}, return {rr:.2%}"
            )
        else:
            self.position_label.setText("Position: None")
        self.signal_label.setText(f"Signal: {signal}")
