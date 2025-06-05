import pandas as pd
import talib


def extract_features(df: pd.DataFrame, symbol: str, config: dict) -> pd.DataFrame:
    """Compute model features from OHLCV dataframe using config periods."""
    ind_cfg = config.get('indicators', {}).get(symbol, {})
    ema_short_p = ind_cfg.get('ema_short', 9)
    ema_long_p = ind_cfg.get('ema_long', 21)
    rsi_p = ind_cfg.get('rsi', 14)
    macd_fast = ind_cfg.get('macd_fast', 12)
    macd_slow = ind_cfg.get('macd_slow', 26)
    macd_signal = ind_cfg.get('macd_signal', 9)

    features = pd.DataFrame()
    features['ema_short'] = talib.EMA(df['close'], timeperiod=ema_short_p)
    features['ema_long'] = talib.EMA(df['close'], timeperiod=ema_long_p)
    macd, macdsignal, _ = talib.MACD(
        df['close'], fastperiod=macd_fast, slowperiod=macd_slow, signalperiod=macd_signal
    )
    features['macd'] = macd
    features['macdsignal'] = macdsignal
    features['rsi'] = talib.RSI(df['close'], timeperiod=rsi_p)
    features['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
    features['obv'] = talib.OBV(df['close'], df['volume'])
    features['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    features['volume'] = df['volume']
    return features.dropna().reset_index(drop=True)
