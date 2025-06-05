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
        for widget in [self.sentiment_label, self.strategy_label, self.position_label]:
            self.layout.addWidget(widget)
        self.setLayout(self.layout)

    def update_state(self, sentiment, strategy, position):
        self.sentiment_label.setText(f"Sentiment: {sentiment}")
        self.strategy_label.setText(f"Strategy: {strategy}")
        self.position_label.setText(f"Position: {position}")
