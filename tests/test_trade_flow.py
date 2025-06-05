import asyncio
import builtins
import pandas as pd
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

pytest_plugins = ("pytest_asyncio",)

from live_strategy import LiveMAStrategy


class DummyExchange:
    def __init__(self):
        self.orders = []
        self.canceled = []
        self.position_amt = 0
        self.order_id = 1

    async def fetch_order_book(self, symbol, limit=5):
        return {"bids": [[100, 1]], "asks": [[101, 1]]}

    async def fetch_open_orders(self, symbol):
        return [o for o in self.orders if o["status"] == "open"]

    async def create_limit_order(self, symbol, side, qty, price, params=None):
        oid = str(self.order_id)
        self.order_id += 1
        self.position_amt = qty if side == "buy" else -qty
        order = {"id": oid, "status": "closed", "price": price, "type": "LIMIT"}
        self.orders.append(order)
        return order

    async def fetch_order(self, oid, symbol):
        for o in self.orders:
            if o["id"] == oid:
                return {"status": o["status"], "price": o.get("price"), "avgPrice": o.get("price"), "id": oid}
        return {"status": "closed", "id": oid, "price": 0}

    async def create_order(self, symbol, type, side, qty, price=None, params=None):
        oid = str(self.order_id)
        self.order_id += 1
        order = {"id": oid, "type": type, "side": side, "status": "open", "params": params}
        if type == "MARKET":
            order["status"] = "closed"
            order["price"] = price or 101
            self.position_amt = 0
        else:
            order["price"] = params.get("stopPrice") if params else price
        self.orders.append(order)
        return order

    async def cancel_order(self, oid, symbol):
        self.canceled.append(oid)
        for o in self.orders:
            if o["id"] == oid:
                o["status"] = "canceled"
        return {"status": "canceled", "id": oid}

    async def fapiPrivateV2GetPositionRisk(self, params):
        amt = self.position_amt
        entry = 100 if amt else 0
        return [{"positionAmt": amt, "entryPrice": entry, "unRealizedProfit": 0}]

    async def fetch_balance(self):
        return {"USDT": {"free": 1000}}


class DummyClient:
    def __init__(self, exchange):
        self.exchange = exchange

    async def fetch_candles(self, *args, **kwargs):
        return pd.DataFrame()

    async def get_balance(self):
        return await self.exchange.fetch_balance()

    async def close(self):
        pass


async def dummy_sleep(*args, **kwargs):
    return None


@pytest.mark.asyncio
async def test_take_profit_cancels_sl_and_logs_exit(tmp_path, monkeypatch):
    exch = DummyExchange()
    client = DummyClient(exch)
    config = {
        "indicators": {"BTCUSDT": {}},
        "tp": {"BTCUSDT": 0.04},
        "sl": {"BTCUSDT": 0.025},
        "signal_priority": True,
    }
    strat = LiveMAStrategy(client, config)

    log_path = tmp_path / "trade_log.csv"
    real_open = builtins.open

    def open_patch(path, mode="r", *args, **kwargs):
        if path == "data/trade_log.csv":
            return real_open(log_path, mode, *args, **kwargs)
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(asyncio, "sleep", dummy_sleep)
    monkeypatch.setattr(builtins, "open", open_patch)

    await strat.open_position("BTCUSDT", "long", 100, 0.01, "1m")

    sl_orders = [o for o in exch.orders if o["type"] == "STOP_MARKET" and o["status"] == "open"]
    assert sl_orders, "SL order not created"
    sl_id = sl_orders[0]["id"]

    await strat.close_position("BTCUSDT")

    assert sl_id in exch.canceled, "SL order was not canceled"

    lines = log_path.read_text().strip().splitlines()
    assert any(
        line.split(",")[3] == "EXIT" for line in lines
    ), "Exit trade not logged"
