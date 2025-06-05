import pandas as pd
import numpy as np


def EMA(series, timeperiod=30):
    return series.ewm(span=timeperiod, adjust=False).mean()


def MACD(series, fastperiod=12, slowperiod=26, signalperiod=9):
    ema_fast = EMA(series, fastperiod)
    ema_slow = EMA(series, slowperiod)
    macd = ema_fast - ema_slow
    signal = EMA(macd, signalperiod)
    hist = macd - signal
    return macd, signal, hist


def RSI(series, timeperiod=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.rolling(timeperiod).mean()
    ma_down = down.rolling(timeperiod).mean()
    rs = ma_up / ma_down
    rsi = 100 - (100 / (1 + rs))
    return rsi


def ADX(high, low, close, timeperiod=14):
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    plus_dm = (high - high.shift()).where((high - high.shift()) > (low.shift() - low), 0.0).clip(lower=0)
    minus_dm = (low.shift() - low).where((low.shift() - low) > (high - high.shift()), 0.0).clip(lower=0)
    atr = tr.rolling(timeperiod).mean()
    plus_di = 100 * (plus_dm.rolling(timeperiod).sum() / atr)
    minus_di = 100 * (minus_dm.rolling(timeperiod).sum() / atr)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(timeperiod).mean()
    return adx


def OBV(close, volume):
    direction = close.diff().fillna(0).apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    return (volume * direction).cumsum()


def ATR(high, low, close, timeperiod=14):
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(timeperiod).mean()
    return atr


def BBANDS(series, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0):
    ma = series.rolling(timeperiod).mean()
    std = series.rolling(timeperiod).std()
    upper = ma + nbdevup * std
    lower = ma - nbdevdn * std
    return upper, ma, lower


def STOCH(high, low, close, fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0):
    lowest_low = low.rolling(fastk_period).min()
    highest_high = high.rolling(fastk_period).max()
    fast_k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    slow_k = fast_k.rolling(slowk_period).mean()
    slow_d = slow_k.rolling(slowd_period).mean()
    return slow_k, slow_d
