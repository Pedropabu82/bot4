import importlib
import sys
import os
import types

import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# -- Create a minimal talib stub so tests can run without the binary package --
talib_stub = types.ModuleType("talib")


def ema(series, timeperiod):
    return series.ewm(span=timeperiod, adjust=False).mean()


def macd(series, fastperiod=12, slowperiod=26, signalperiod=9):
    ema_fast = ema(series, fastperiod)
    ema_slow = ema(series, slowperiod)
    macd_val = ema_fast - ema_slow
    signal = ema(macd_val, signalperiod)
    hist = macd_val - signal
    return macd_val, signal, hist


def rsi(series, timeperiod=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(timeperiod).mean()
    avg_loss = loss.rolling(timeperiod).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def noop(*args, **kwargs):
    return pd.Series(np.zeros(len(args[0])))


talib_stub.EMA = ema
talib_stub.MACD = macd
talib_stub.RSI = rsi
talib_stub.ADX = noop
talib_stub.OBV = lambda close, volume: volume.cumsum()
talib_stub.ATR = noop
talib_stub.BBANDS = lambda close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0: (
    close.rolling(timeperiod).mean() + nbdevup * close.rolling(timeperiod).std(),
    close.rolling(timeperiod).mean(),
    close.rolling(timeperiod).mean() - nbdevdn * close.rolling(timeperiod).std(),
)
talib_stub.STOCH = lambda high, low, close, fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0: (
    pd.Series(np.zeros(len(close))),
    pd.Series(np.zeros(len(close))),
)

sys.modules["talib"] = talib_stub

features = importlib.reload(importlib.import_module("features"))


def test_extract_features_custom_periods():
    df = pd.DataFrame(
        {
            "open": np.arange(1, 31),
            "high": np.arange(1, 31) + 1,
            "low": np.arange(1, 31) - 1,
            "close": np.arange(1, 31),
            "volume": np.arange(1, 31),
        }
    )

    config = {
        "bb_period": 10,
        "bb_k": 2,
        "stoch_k_period": 5,
        "stoch_d_period": 2,
        "indicators": {
            "SYMBOL": {
                "ema_short": 5,
                "ema_long": 8,
                "rsi": 6,
                "macd_fast": 4,
                "macd_slow": 7,
                "macd_signal": 3,
            }
        },
    }

    feats = features.extract_features(df, "SYMBOL", config)

    exp_ema_short = ema(df["close"], 5)
    exp_ema_long = ema(df["close"], 8)
    exp_macd, exp_signal, _ = macd(
        df["close"], fastperiod=4, slowperiod=7, signalperiod=3
    )
    exp_rsi = rsi(df["close"], 6)

    expected = (
        pd.DataFrame(
            {
                "ema_short": exp_ema_short,
                "ema_long": exp_ema_long,
                "macd": exp_macd,
                "macdsignal": exp_signal,
                "rsi": exp_rsi,
            }
        )
        .dropna()
        .reset_index(drop=True)
    )

    expected = expected.iloc[-len(feats) :].reset_index(drop=True)

    pd.testing.assert_series_equal(feats["ema_short"], expected["ema_short"])
    pd.testing.assert_series_equal(feats["ema_long"], expected["ema_long"])
    pd.testing.assert_series_equal(feats["macd"], expected["macd"])
    pd.testing.assert_series_equal(feats["macdsignal"], expected["macdsignal"])
    pd.testing.assert_series_equal(feats["rsi"], expected["rsi"])

