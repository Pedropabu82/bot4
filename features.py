import pandas as pd
import talib


def extract_features(
    df: pd.DataFrame,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
) -> pd.DataFrame:
    """Compute model features from OHLCV dataframe."""
    features = pd.DataFrame()
    features['ema_short'] = talib.EMA(df['close'], timeperiod=9)
    features['ema_long'] = talib.EMA(df['close'], timeperiod=21)
    macd, macdsignal, _ = talib.MACD(
        df['close'],
        fastperiod=macd_fast,
        slowperiod=macd_slow,
        signalperiod=macd_signal,
    )
    features['macd'] = macd
    features['macdsignal'] = macdsignal
    features['rsi'] = talib.RSI(df['close'], timeperiod=14)
    features['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
    features['obv'] = talib.OBV(df['close'], df['volume'])
    features['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    features['volume'] = df['volume']
    return features.dropna().reset_index(drop=True)
