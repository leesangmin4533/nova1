# Introduction to GitHub

<img src="https://octodex.github.com/images/Professortocat_v2.png" align="right" height="200px" />

Hey @leesangmin4533!

Mona here. I'm done preparing your exercise. Hope you enjoy! 💚

Remember, it's self-paced so feel free to take a break! ☕️

[![](https://img.shields.io/badge/Go%20to%20Exercise-%E2%86%92-1f883d?style=for-the-badge&logo=github&labelColor=197935)](https://github.com/leesangmin4533/nova1/issues/1)

---

&copy; 2025 GitHub &bull; [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) &bull; [MIT License](https://gh.io/mit)


## Trading Agent Prototype

This repository now includes a simple prototype for a multi-agent trading system.
Each agent has a clear responsibility and can be scheduled using `asyncio` or any
other event loop implementation.

### Agents

- **MarketSentimentAgent** – computes market sentiment from incoming market data.
- **StrategySelector** – chooses a trading strategy based on the current sentiment.
- **EntryDecisionAgent** – decides when to open a position.
- **PositionManager** – monitors open positions for exit conditions.
- **LoggerAgent** – stores decisions and market information in JSON files.
- **VisualizerAgent** – placeholder for UI updates.
- **LearningAgent** – updates strategy weights from past performance.

This code serves as a starting point for experimenting with agent-based trading
ideas.
