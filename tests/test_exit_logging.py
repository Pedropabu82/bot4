import asyncio
import pytest
import os, sys, types, types as modtypes
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.modules.setdefault('xgboost', types.SimpleNamespace())
dummy_sk = modtypes.ModuleType('sklearn')
dummy_utils = modtypes.ModuleType('sklearn.utils')
dummy_cw = modtypes.ModuleType('sklearn.utils.class_weight')
dummy_cw.compute_class_weight = lambda *a, **k: None
dummy_utils.class_weight = dummy_cw
sys.modules.setdefault('sklearn', dummy_sk)
sys.modules.setdefault('sklearn.utils', dummy_utils)
sys.modules.setdefault('sklearn.utils.class_weight', dummy_cw)

from live_strategy import LiveMAStrategy

class DummyExchange:
    def __init__(self):
        self.canceled = []
    async def fetch_order(self, order_id, symbol):
        if order_id == 'sl123':
            return {'id': order_id, 'status': 'FILLED', 'avgPrice': '99'}
        return {'id': order_id, 'status': 'open'}
    async def fapiPrivateV2GetPositionRisk(self, params):
        return [{'positionAmt': '0'}]
    async def fetch_open_orders(self, symbol):
        return []
    async def cancel_order(self, order_id, symbol):
        self.canceled.append(order_id)

class DummyClient:
    def __init__(self):
        self.exchange = DummyExchange()
    async def get_balance(self):
        return {'USDT': {'free': 1000}}

@pytest.mark.asyncio
async def test_stop_order_exit(tmp_path, monkeypatch):
    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    log_file = data_dir / 'trade_log.csv'
    log_file.write_text('timestamp,symbol,timeframe,type,entry_price,exit_price,pnl_pct,result\n')
    monkeypatch.chdir(tmp_path)

    config = {'indicators': {'BTCUSDT': {}}, 'tp': {'BTCUSDT': 0.04}, 'sl': {'BTCUSDT': 0.02}}
    strat = LiveMAStrategy(DummyClient(), config)
    strat.position_side['BTCUSDT'] = 'long'
    strat.entry_price['BTCUSDT'] = 100.0
    strat.quantity['BTCUSDT'] = 1.0
    strat.entry_tf['BTCUSDT'] = '1h'
    strat.sl_order_id['BTCUSDT'] = 'sl123'
    strat.tp_order_id['BTCUSDT'] = 'tp123'

    await strat.sync_position('BTCUSDT')

    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 2
    assert lines[-1].split(',')[3] == 'EXIT'
    assert 'tp123' in strat.client.exchange.canceled
