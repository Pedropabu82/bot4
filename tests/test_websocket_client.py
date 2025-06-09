pytest_plugins = ("pytest_asyncio",)
import asyncio
import json
import pandas as pd
import pytest

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import websocket_client

class DummyStrategy:
    def __init__(self):
        self.tf_calls = []
        self.tick_calls = []

    def process_timeframe_data(self, symbol, timeframe, df):
        self.tf_calls.append((symbol, timeframe, df))

    def process_tick(self, symbol, price):
        self.tick_calls.append((symbol, price))

class DummyWS:
    def __init__(self):
        self.messages = [
            json.dumps({
                "stream": "btcusdt@kline_1m",
                "data": {
                    "s": "BTCUSDT",
                    "k": {
                        "t": 1234567890000,
                        "o": "1",
                        "h": "1",
                        "l": "1",
                        "c": "1",
                        "v": "1",
                        "x": True
                    }
                }
            }),
            json.dumps({
                "stream": "btcusdt@ticker",
                "data": {"s": "BTCUSDT", "c": "1"}
            })
        ]
        self.index = 0

    async def recv(self):
        if self.index < len(self.messages):
            msg = self.messages[self.index]
            self.index += 1
            return msg
        raise asyncio.CancelledError

class DummyConn:
    async def __aenter__(self):
        return DummyWS()

    async def __aexit__(self, exc_type, exc, tb):
        pass

def dummy_connect(*args, **kwargs):
    return DummyConn()

class DummyExchange:
    def __init__(self):
        self.modes = []

    def set_sandbox_mode(self, mode):
        self.modes.append(mode)

    async def close(self):
        pass

created_exchange = DummyExchange()

def dummy_binance(*args, **kwargs):
    return created_exchange

def dummy_fetch(exchange, symbol, timeframe, limit=300):
    return pd.DataFrame([
        {
            "timestamp": pd.Timestamp.now(),
            "open": 1,
            "high": 1,
            "low": 1,
            "close": 1,
            "volume": 1,
        }
    ])

async def dummy_sleep(*args, **kwargs):
    return None

@pytest.mark.asyncio
@pytest.mark.parametrize("testnet", [True, False])
async def test_start_streams_modes(monkeypatch, testnet):
    global created_exchange
    created_exchange = DummyExchange()
    strategy = DummyStrategy()
    monkeypatch.setattr(websocket_client.websockets, "connect", dummy_connect)
    monkeypatch.setattr(websocket_client.ccxt, "binance", dummy_binance)
    monkeypatch.setattr(websocket_client, "fetch_historical_klines", dummy_fetch)
    monkeypatch.setattr(websocket_client.asyncio, "sleep", dummy_sleep)

    await websocket_client.start_streams(["BTCUSDT"], ["1m"], strategy, ["1m"], {"testnet": testnet})

    assert strategy.tf_calls, "timeframe data not processed"
    assert strategy.tick_calls, "tick data not processed"
    if testnet:
        assert created_exchange.modes == [True]
    else:
        assert created_exchange.modes == []
