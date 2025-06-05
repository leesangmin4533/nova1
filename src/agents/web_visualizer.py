from flask import Flask, render_template_string
from threading import Thread


class WebVisualizerAgent:
    """Simple web server to visualize agent states."""

    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.sentiment = "NEUTRAL"
        self.strategy = "None"
        self.position = "None"
        self.app = Flask(__name__)
        self._setup_routes()
        self._start_server()

    def _setup_routes(self):
        @self.app.route("/")
        def index():
            html = """
            <html>
            <head>
              <title>Trading Agent Dashboard</title>
              <meta http-equiv="refresh" content="1">
              <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
              </style>
            </head>
            <body>
              <h1>Trading Agent Dashboard</h1>
              <p>Sentiment: {{ sentiment }}</p>
              <p>Strategy: {{ strategy }}</p>
              <p>Position: {{ position }}</p>
            </body>
            </html>
            """
            return render_template_string(
                html,
                sentiment=self.sentiment,
                strategy=self.strategy,
                position=self.position,
            )

    def _start_server(self):
        thread = Thread(
            target=self.app.run,
            kwargs={"host": self.host, "port": self.port, "debug": False, "use_reloader": False},
        )
        thread.daemon = True
        thread.start()

    def update_state(self, sentiment, strategy, position):
        self.sentiment = sentiment
        self.strategy = strategy
        self.position = position

