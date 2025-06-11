import time
import os
import sys
from datetime import datetime

# Ensure the src package is available for imports when running this file
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agents.market_sentiment import MarketSentimentAgent
from agents.strategy_selector import StrategySelector
from agents.entry_decision import EntryDecisionAgent
from agents.position_manager import (
    PositionManager,
    can_enter_trade,
    INITIAL_CAPITAL,
    entry_block_reason,
)
from agents.risk_manager import RiskManager
from agents.emotion_axis import EmotionAxis
from agents.logger_agent import LoggerAgent
from agents.learning_agent import LearningAgent
from agents.missed_hold_tracker import track_failed_hold
from agents.human_compare import HumanCompareAgent
from agents.utils import get_upbit_candles, get_upbit_orderbook
from status_server import start_status_server, update_state
import json
from pathlib import Path
from log_analyzer import load_logs, analyze_logs
from version import STRATEGY_VERSION

import webbrowser
import subprocess
import psutil
from config import UI_PATH
from nova_core import save_decision

# Launch local React UI if built without reopening if already open
ui_file = Path(__file__).resolve().parent / "ui-react" / "dist" / "index.html"
ui_url = ui_file.as_uri()


def is_ui_already_open() -> bool:
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = " ".join(proc.info.get("cmdline") or [])
            if str(ui_file) in cmdline:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


if ui_file.exists() and not is_ui_already_open():
    webbrowser.open(ui_url)
else:
    print("[✔] UI 이미 실행 중이거나 파일 없음 → 생략됨")

# Automatically open the legacy HTML UI if available
if os.path.exists(UI_PATH):
    subprocess.Popen(["start", str(UI_PATH)], shell=True)


SYMBOL = "KRW-BTC"


class TradingApp:
    """Main application that coordinates all agents."""

    def __init__(self):
        self.sentiment_agent = MarketSentimentAgent()
        self.strategy_selector = StrategySelector()
        self.entry_agent = EntryDecisionAgent()
        self.position_manager = PositionManager()
        self.risk = RiskManager(max_risk_pct=0.1)
        self.emotion_axis = EmotionAxis()
        self.logger = LoggerAgent()
        self.learning_agent = LearningAgent()
        self.human_compare = HumanCompareAgent()
        self.positions = []
        self.last_signal = "HOLD"
        self.current_price = 0.0
        self.balance = float(INITIAL_CAPITAL)
        self.last_trade_time = None
        self.trade_history = []

    def loop(self):
        try:
            candle_data = get_upbit_candles(SYMBOL, 20)
            order_book = get_upbit_orderbook(SYMBOL)
        except Exception as e:
            print(f"시장 데이터를 가져오지 못했습니다: {e}")
            return

        self.current_price = candle_data[-1]

        # recent volatility for risk management
        if len(candle_data) >= 20:
            mean20 = sum(candle_data[-20:]) / 20
            var20 = sum((c - mean20) ** 2 for c in candle_data[-20:]) / 20
            volatility = (var20 ** 0.5) / mean20 if mean20 else 0.0
        else:
            volatility = 0.0

        sentiment = self.sentiment_agent.update(candle_data, order_book, None)
        rsi = self.sentiment_agent.rsi
        bb_score = self.sentiment_agent.bb_score
        ts_score = self.sentiment_agent.ts_score
        emotion_index = self.sentiment_agent.applied_emotion_index
        classified_emotion = self.sentiment_agent.classified_emotion

        self.strategy_selector.update_scores(self.learning_agent.weights)
        self.strategy_selector.update_market_phase(rsi, bb_score)
        strategy, params, score = self.strategy_selector.select(sentiment)
        weight = params.get("weight")

        order_status = {
            "has_position": len(self.positions) > 0,
            "return_rate": 0.0,
        }
        if self.positions:
            first = self.positions[0]
            order_status["return_rate"] = (
                self.current_price - first["entry_price"]
            ) / first["entry_price"]

        result = self.entry_agent.evaluate(
            (strategy, params),
            candle_data,
            order_status,
            order_book,
            logger=self.logger,
            symbol=SYMBOL,
            emotion_index=self.sentiment_agent.applied_emotion_index,
        )
        if isinstance(result, dict):
            signal = result.get("signal")
            confidence = result.get("confidence")
        else:
            signal = result
            confidence = None
        score_percent = self.entry_agent.last_score_percent
        self.last_signal = signal
        decision_info = {
            "timestamp": datetime.now().isoformat(),
            "confidence": score_percent,
            "action": signal,
        }
        if signal == "HOLD":
            track_failed_hold(decision_info, self.current_price, SYMBOL)

        # update weights based on signal quality
        self.learning_agent.adjust_from_signal(strategy, score_percent, confidence)

        reason = None
        if signal == "BUY":
            reason = entry_block_reason(len(self.positions) > 0, confidence, score_percent)
            if self.emotion_axis.in_cooldown() or self.emotion_axis.should_pause_for_greed(rsi):
                reason = reason or "COOLDOWN"

        human_action = self.human_compare.predict(rsi)
        score_vs_human = self.human_compare.score_vs_human(signal, human_action)
        self.logger.log_judgment(
            action=signal,
            reason=reason,
            indicators={"rsi": rsi, "bb_score": bb_score, "ts_score": ts_score},
            market_emotion=sentiment,
            human_likely_action=human_action,
            score_vs_human=score_vs_human,
            strategy_version=STRATEGY_VERSION,
            conflict_analysis=self.entry_agent.last_conflict,
        )

        decision_data = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "action": signal,
            "reason": reason,
            "human_likely_action": human_action,
            "score_vs_human": score_vs_human,
            "classified_emotion": classified_emotion,
            "market_emotion_index": emotion_index,
        }
        update_state(decision=decision_data)
        save_decision(
            signal,
            reason,
            human_action,
            score_vs_human,
            classified_emotion=classified_emotion,
            market_emotion_index=emotion_index,
        )

        allow_entry, entry_reason = self.entry_agent.decide_entry(signal, reason, score_percent)

        if allow_entry and can_enter_trade(self.positions):
            order_amount = self.risk.calculate_order_amount(
                self.balance, volatility
            )
            if order_amount > 0:
                qty = order_amount / self.current_price
                self.balance -= order_amount
                self.positions.append({"entry_price": self.current_price, "quantity": qty, "symbol": SYMBOL})
            self.position_manager.record_trade("BUY")
            self.emotion_axis.record_result(True)
            ts = self.logger.log(
                "EntryDecisionAgent",
                "BUY",
                price=self.current_price,
                symbol=SYMBOL,
                return_rate=0.0,
            )
            if ts:
                self.last_trade_time = ts
            self.logger.log_event({
                "type": "entry_approved",
                "symbol": SYMBOL,
                "confidence": confidence,
                "score_percent": score_percent,
                "reason": entry_reason,
            })
        elif signal == "SELL" and self.positions:
            self.emotion_axis.record_result(True)
            pos = self.positions.pop(0)
            return_rate = (
                self.current_price - pos["entry_price"]
            ) / pos["entry_price"]
            self.balance += self.current_price * pos["quantity"]
            self.position_manager.record_trade("SELL")
            ts = self.logger.log(
                "EntryDecisionAgent",
                "SELL",
                price=self.current_price,
                symbol=pos["symbol"],
                return_rate=return_rate,
            )
            if ts:
                self.last_trade_time = ts
            self.trade_history.append({"strategy": strategy, "return": return_rate})
            self.learning_agent.record_trade(strategy, return_rate)
        else:
            if signal == "BUY":
                self.emotion_axis.record_result(False)
            if signal == "HOLD":
                self.emotion_axis.record_result(False)
            if signal == "BUY":
                self.logger.log_event({
                    "type": "entry_denied",
                    "symbol": SYMBOL,
                    "reason": entry_reason,
                    "confidence": confidence,
                    "score_percent": score_percent,
                })

        to_remove = []
        for pos in list(self.positions):
            if self.risk.check_stop_loss(pos["entry_price"], self.current_price):
                return_rate = (
                    self.current_price - pos["entry_price"]
                ) / pos["entry_price"]
                self.balance += self.current_price * pos["quantity"]
                self.positions.remove(pos)
                self.logger.log_success(
                    "RiskManager",
                    "STOP_LOSS",
                    price=self.current_price,
                    strategy=strategy,
                    return_rate=return_rate,
                )
                continue

            decision = self.position_manager.update(
                pos, pos["entry_price"], self.current_price
            )
            if decision == "CLOSE":
                return_rate = (
                    self.current_price - pos["entry_price"]
                ) / pos["entry_price"]
                self.balance += self.current_price * pos["quantity"]
                self.position_manager.record_trade("SELL")
                ts = self.logger.log(
                    "PositionManager",
                    "CLOSE",
                    price=self.current_price,
                    symbol=pos["symbol"],
                    return_rate=return_rate,
                )
                if ts:
                    self.last_trade_time = ts
                self.trade_history.append({"strategy": strategy, "return": return_rate})
                self.learning_agent.record_trade(strategy, return_rate)
                to_remove.append(pos)
        for pos in to_remove:
            if pos in self.positions:
                self.positions.remove(pos)

        position_state = None
        return_rate = None
        if self.positions:
            pos = self.positions[0]
            return_rate = (
                self.current_price - pos["entry_price"]
            ) / pos["entry_price"]
            position_state = {
                "entry_price": pos["entry_price"],
                "return_rate": return_rate,
            }

        logs = load_logs("log")
        stats = analyze_logs(logs)
        cumulative_return = stats.get("cumulative_return", 0.0)

        self.learning_agent.update()
        bids = [[b["price"], b["volume"]] for b in order_book.get("bids", []) if b.get("volume")]
        asks = [[a["price"], a["volume"]] for a in order_book.get("asks", []) if a.get("volume")]

        update_state(
            sentiment=sentiment,
            classified_emotion=classified_emotion,
            emotion_index=emotion_index,
            strategy=strategy,
            selected_strategy=strategy,
            strategy_mode=self.strategy_selector.strategy_mode,
            strategy_score=score,
            position=position_state,
            signal=self.last_signal,
            price=self.current_price,
            balance=self.balance,
            weight=weight,
            weights=self.learning_agent.weights,
            bid_volume=order_book.get("bid_volume"),
            ask_volume=order_book.get("ask_volume"),
            bids=bids,
            asks=asks,
            positions=self.positions,
            orderbook_score=confidence,
            rsi=rsi,
            bb_score=bb_score,
            ts_score=ts_score,
            cooldown=self.emotion_axis.in_cooldown(),
            nearest_failed=self.entry_agent.nearest_failed,
            return_rate=return_rate,
            cumulative_return=cumulative_return,
            last_trade_time=self.last_trade_time,
            buy_count=self.position_manager.total_buys,
            sell_count=self.position_manager.total_sells,
        )


if __name__ == "__main__":
    app = TradingApp()
    # Launch the Flask status server in a background daemon thread so
    # that the trading loop can run uninterrupted.
    start_status_server(position_manager=app.position_manager, logger_agent=app.logger)
    symbol = SYMBOL
    while True:
        orderbook = get_upbit_orderbook(symbol)
        update_state(
            bids=[[b["price"], b["volume"]] for b in orderbook.get("bids", []) if b.get("volume")],
            asks=[[a["price"], a["volume"]] for a in orderbook.get("asks", []) if a.get("volume")],
            bid_volume=orderbook.get("bid_volume"),
            ask_volume=orderbook.get("ask_volume"),
            classified_emotion=app.sentiment_agent.classified_emotion,
            emotion_index=app.sentiment_agent.applied_emotion_index,
            buy_count=app.position_manager.total_buys,
            sell_count=app.position_manager.total_sells,
            nearest_failed=app.entry_agent.nearest_failed,
            cooldown=app.emotion_axis.in_cooldown(),
            strategy_mode=app.strategy_selector.strategy_mode,
        )
        app.loop()
        time.sleep(2)

