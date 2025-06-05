import pandas as pd
import talib


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute model features from OHLCV dataframe."""
    features = pd.DataFrame()
    features['ema_short'] = talib.EMA(df['close'], timeperiod=9)
    features['ema_long'] = talib.EMA(df['close'], timeperiod=21)
    macd, macdsignal, _ = talib.MACD(
        df['close'], fastperiod=12, slowperiod=26, signalperiod=9
    )
    features['macd'] = macd
    features['macdsignal'] = macdsignal
    features['rsi'] = talib.RSI(df['close'], timeperiod=14)
    features['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
    features['obv'] = talib.OBV(df['close'], df['volume'])
    features['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    features['volume'] = df['volume']
    return features.dropna().reset_index(drop=True)
