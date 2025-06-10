import asyncio
import logging
import os
from collections import defaultdict
from datetime import datetime

import joblib
import pandas as pd
import numpy as np

from api_client import BinanceClient
from signal_engine import SignalEngine
from features import extract_features
import talib

logger = logging.getLogger(__name__)


def calculate_indicators(df: pd.DataFrame, config: dict, symbol: str):
    ind_cfg = config.get("indicators", {}).get(symbol, {})
    ema_short = talib.EMA(df["close"], timeperiod=ind_cfg.get("ema_short", 12))
    ema_long = talib.EMA(df["close"], timeperiod=ind_cfg.get("ema_long", 26))
    macd, macdsignal, _ = talib.MACD(df["close"])
    rsi = talib.RSI(df["close"], timeperiod=ind_cfg.get("rsi", 14))
    return {
        "ema_short": float(ema_short.iloc[-1]),
        "ema_long": float(ema_long.iloc[-1]),
        "macd": float(macd.iloc[-1]),
        "macdsignal": float(macdsignal.iloc[-1]),
        "rsi": float(rsi.iloc[-1]),
    }


def calculate_score(indicators: dict):
    score = 0.0
    direction = "long" if indicators["ema_short"] > indicators["ema_long"] else "short"
    score += 1 if indicators["ema_short"] > indicators["ema_long"] else -1
    score += 0.5 if indicators["macd"] > indicators["macdsignal"] else -0.5
    if indicators["rsi"] > 70:
        score -= 0.5
    elif indicators["rsi"] < 30:
        score += 0.5
    return direction, score


class AsyncMultiMAStrategy:
    """Example multi-timeframe strategy using an optional XGBoost model."""

    def __init__(self, client: BinanceClient, config: dict):
        self.client = client
        self.config = config
        self.signal_engine = SignalEngine(config.get("model_path", "model_xgb.pkl"))
        self.model = self._load_model(config.get("model_path", "model_xgb.pkl"))
        self.symbols = config.get("symbols", [])
        self.timeframes = config.get("timeframes", [])
        self.data = defaultdict(lambda: defaultdict(pd.DataFrame))
        self.leverage = {s: config.get("leverage", 10) for s in self.symbols}
        self.trade_value = config.get("trade_value", 50)
        self.min_ai_confidence = config.get("min_ai_confidence", 0.5)
        self.model_required = config.get("model_required", True)

    def _load_model(self, path: str):
        if not os.path.isfile(path):
            logger.warning("Model file not found: %s", path)
            return None
        try:
            model = joblib.load(path)
            logger.info("Model loaded from %s", path)
            return model
        except Exception as exc:
            logger.error("Could not load model: %s", exc)
            return None

    async def async_init(self):
        for symbol in self.symbols:
            for tf in self.timeframes:
                candles = await self.client.fetch_candles(symbol, tf, limit=100)
                if candles is None:
                    continue
                candles["timestamp"] = pd.to_datetime(candles["timestamp"], unit="ms")
                self.data[symbol][tf] = candles.set_index("timestamp")

    def process_timeframe_data(self, symbol: str, timeframe: str, candle: pd.Series):
        df = self.data[symbol][timeframe]
        if df.empty or candle.name > df.index[-1]:
            df = pd.concat([df, candle.to_frame().T])
        else:
            df.loc[candle.name] = candle
        df = df[~df.index.duplicated(keep="last")].tail(100)
        self.data[symbol][timeframe] = df

    def get_signal_for_timeframe(self, symbol: str, timeframe: str):
        df = self.data[symbol][timeframe]
        if len(df) < 30:
            return None, 0.0
        indicators = calculate_indicators(df, self.config, symbol)
        direction, score = calculate_score(indicators)
        return direction, score

    def ai_accepts_trade(self, features: pd.DataFrame, direction: str) -> bool:
        if self.model is None:
            return not self.model_required
        X = features.tail(1)
        if X.isnull().any().any():
            return False
        prob = self.model.predict_proba(X)[0][1]
        logger.debug("AI probability %.2f for %s", prob, direction)
        if direction == "long":
            return prob >= self.min_ai_confidence
        if direction == "short":
            return prob <= (1 - self.min_ai_confidence)
        return False

    async def try_enter(self, symbol: str, tf: str, direction: str, candle: pd.Series):
        price = float(candle["close"])
        qty = round(self.trade_value * self.leverage[symbol] / price, 6)
        order_book = await self.client.exchange.fetch_order_book(symbol, limit=5)
        bid = float(order_book["bids"][0][0])
        ask = float(order_book["asks"][0][0])
        spread = (ask - bid) / bid
        if spread > 0.002:
            logger.warning("High spread %.2f%% for %s", spread * 100, symbol)
            return
        depth_ok = float(order_book["bids"][0][1]) > qty * 3
        if not depth_ok:
            logger.warning("Low liquidity for %s", symbol)
            return
        logger.info("Valid signal %s @ %s side %s qty %.6f", symbol, tf, direction, qty)
        await self.open_position(symbol, direction, price, qty, tf)

    async def open_position(self, symbol: str, side: str, price: float, qty: float, tf: str):
        logger.info("OPEN %s %s qty %.6f @ %.2f", side, symbol, qty, price)
        # Actual order logic would go here

    async def run(self):
        while True:
            for symbol in self.symbols:
                for tf in self.timeframes:
                    df = self.data[symbol][tf]
                    if df.empty or len(df) < 30:
                        continue
                    direction, score = self.get_signal_for_timeframe(symbol, tf)
                    if direction:
                        feats = extract_features(df.copy())
                        if not self.ai_accepts_trade(feats, direction):
                            logger.info("Signal rejected by AI: %s %s", symbol, tf)
                            continue
                        await self.try_enter(symbol, tf, direction, df.iloc[-1])
            await asyncio.sleep(15)

