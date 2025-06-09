import sys, os, types, types as modtypes
import warnings
import pytest
pytestmark = pytest.mark.filterwarnings("ignore")
warnings.filterwarnings("ignore")
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

import pandas as pd
import talib

from features import extract_features
from live_strategy import LiveMAStrategy


class DummyClient:
    pass


class DummySignalEngine:
    def __init__(self):
        self.calls = []

    def get_signal_for_timeframe(self, data, **kwargs):
        self.calls.append((data, kwargs))
        return {"ok": True, "confidence": 1.0}


def make_df(n=40):
    return pd.DataFrame({
        'open': range(1, n+1),
        'high': range(1, n+1),
        'low': range(1, n+1),
        'close': range(1, n+1),
        'volume': [1]*n,
    })


def test_extract_features_custom_ema():
    df = make_df()
    feats = extract_features(df, ema_short=3, ema_long=5)
    expected_short = talib.EMA(df['close'], timeperiod=3).iloc[-1]
    expected_long = talib.EMA(df['close'], timeperiod=5).iloc[-1]
    assert abs(feats.iloc[-1]['ema_short'] - expected_short) < 1e-8
    assert abs(feats.iloc[-1]['ema_long'] - expected_long) < 1e-8


def test_ai_accepts_trade_passes_config(monkeypatch):
    config = {
        'indicators': {'BTCUSDT': {'ema_short': 5, 'ema_long': 10, 'macd_fast': 8, 'macd_slow': 17, 'macd_signal': 5}},
        'bb_period': 20,
        'bb_k': 2,
        'stoch_k_period': 14,
        'stoch_d_period': 3,
        'min_ai_confidence': 0,
    }
    strat = LiveMAStrategy(DummyClient(), config)
    strat.signal_engine = DummySignalEngine()
    df = make_df()
    strat.data['BTCUSDT'] = {'1m': df}

    captured = {}

    def fake_extract(
        df,
        bb_period,
        bb_k,
        stoch_k_period,
        stoch_d_period,
        ema_short,
        ema_long,
        macd_fast,
        macd_slow,
        macd_signal,
    ):
        captured['ema_short'] = ema_short
        captured['ema_long'] = ema_long
        captured['macd_fast'] = macd_fast
        captured['macd_slow'] = macd_slow
        captured['macd_signal'] = macd_signal
        return extract_features(
            df.tail(30),
            bb_period,
            bb_k,
            stoch_k_period,
            stoch_d_period,
            ema_short,
            ema_long,
            macd_fast,
            macd_slow,
            macd_signal,
        )

    monkeypatch.setattr('live_strategy.extract_features', fake_extract)

    assert strat.ai_accepts_trade('BTCUSDT', '1m', 'long')
    assert captured['ema_short'] == 5
    assert captured['ema_long'] == 10
    assert captured['macd_fast'] == 8
    assert captured['macd_slow'] == 17
    assert captured['macd_signal'] == 5
