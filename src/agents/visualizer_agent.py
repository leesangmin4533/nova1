class VisualizerAgent:
    """Simple wrapper that forwards state updates to ``status_server``."""

    def __init__(self, update_func=None):
        if update_func is None:
            from status_server import update_state
            update_func = update_state
        self.update_func = update_func

    def update(self, **state):
        """Forward provided state dictionary to the status server."""
        self.update_func(**state)
