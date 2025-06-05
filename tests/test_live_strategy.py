import sys, os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from live_strategy import LiveMAStrategy

class DummyExchange:
    def __init__(self):
        self.last_params = None
        self.last_type = None

    async def create_order(self, symbol, order_type, side, amount, price=None, params=None):
        self.last_params = params
        self.last_type = order_type
        return {}

class DummyClient:
    def __init__(self):
        self.exchange = DummyExchange()

@pytest.mark.asyncio
async def test_set_sl_adds_close_position():
    config = {
        'indicators': {'BTCUSDT': {}},
        'tp': {'BTCUSDT': 0.07},
        'sl': {'BTCUSDT': 0.025},
        'leverage': 10,
    }
    strat = LiveMAStrategy(DummyClient(), config)
    strat.entry_price['BTCUSDT'] = 100
    strat.quantity['BTCUSDT'] = 1
    strat.position_side['BTCUSDT'] = 'long'

    await strat.set_sl('BTCUSDT')

    params = strat.client.exchange.last_params
    assert params['closePosition'] is True
    assert strat.client.exchange.last_type == 'STOP_MARKET'

@pytest.mark.asyncio
async def test_set_tp_adds_close_position():
    config = {
        'indicators': {'BTCUSDT': {}},
        'tp': {'BTCUSDT': 0.07},
        'sl': {'BTCUSDT': 0.025},
        'leverage': 10,
    }
    strat = LiveMAStrategy(DummyClient(), config)
    strat.entry_price['BTCUSDT'] = 100
    strat.quantity['BTCUSDT'] = 1
    strat.position_side['BTCUSDT'] = 'long'

    await strat.set_tp('BTCUSDT')

    params = strat.client.exchange.last_params
    assert params['closePosition'] is True
    assert strat.client.exchange.last_type == 'TAKE_PROFIT_MARKET'
