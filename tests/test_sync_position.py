import sys, os
import pytest
pytestmark = pytest.mark.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from live_strategy import LiveMAStrategy

class DummyExchange:
    def __init__(self):
        self.orders = [
            {'id': '1', 'type': 'STOP_MARKET', 'status': 'open'},
            {'id': '2', 'type': 'TAKE_PROFIT_MARKET', 'status': 'closed'},
        ]
        self.cancelled = []

    async def fapiPrivateV2GetPositionRisk(self, params):
        return [{'positionAmt': '0', 'entryPrice': '0', 'unRealizedProfit': '0'}]

    async def fetch_open_orders(self, symbol):
        return list(self.orders)

    async def cancel_order(self, order_id, symbol):
        self.cancelled.append(order_id)
        for o in self.orders:
            if o['id'] == order_id:
                o['status'] = 'canceled'

class DummyClient:
    def __init__(self, exchange):
        self.exchange = exchange

@pytest.mark.asyncio
async def test_sync_position_cancels_sl_tp_when_position_closed():
    exch = DummyExchange()
    client = DummyClient(exch)
    strat = LiveMAStrategy(client, {'indicators': {'BTCUSDT': {}}})
    strat.position_side['BTCUSDT'] = 'long'
    strat.entry_price['BTCUSDT'] = 100
    strat.quantity['BTCUSDT'] = 1
    strat.unrealized_pnl['BTCUSDT'] = 10

    await strat.sync_position('BTCUSDT')

    assert '1' in exch.cancelled, 'stop order not canceled'
    assert not any(o['status'] == 'open' for o in exch.orders)
    assert strat.position_side['BTCUSDT'] is None
    assert strat.entry_price['BTCUSDT'] is None
    assert strat.quantity['BTCUSDT'] is None
    assert strat.unrealized_pnl['BTCUSDT'] == 0
