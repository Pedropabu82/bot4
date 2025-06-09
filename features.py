import pandas as pd
import talib


def extract_features(
    df: pd.DataFrame,
    bb_period: int = 20,
    bb_k: float = 2,
    stoch_k_period: int = 14,
    stoch_d_period: int = 3,
    ema_short: int = 9,
    ema_long: int = 21,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
) -> pd.DataFrame:
    """Compute model features from OHLCV dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Candle data with columns ``open``, ``high``, ``low``,
        ``close`` and ``volume``.
    ema_short : int, optional
        Period for the short exponential moving average.
    ema_long : int, optional
        Period for the long exponential moving average.
    macd_fast : int, optional
        Fast period for the MACD indicator.
    macd_slow : int, optional
        Slow period for the MACD indicator.
    macd_signal : int, optional
        Signal period for the MACD indicator.
    """
    features = pd.DataFrame()
    features['ema_short'] = talib.EMA(df['close'], timeperiod=ema_short)
    features['ema_long'] = talib.EMA(df['close'], timeperiod=ema_long)
    macd, macdsignal, _ = talib.MACD(
        df['close'],
        fastperiod=macd_fast,
        slowperiod=macd_slow,
        signalperiod=macd_signal,
    )
    features['macd'] = macd
    features['macdsignal'] = macdsignal
    features['rsi'] = talib.RSI(df['close'], timeperiod=14)
    features['adx'] = talib.ADX(
        df['high'], df['low'], df['close'], timeperiod=14
    )
    features['obv'] = talib.OBV(df['close'], df['volume'])
    features['atr'] = talib.ATR(
        df['high'], df['low'], df['close'], timeperiod=14
    )

    upper, middle, lower = talib.BBANDS(
        df['close'], timeperiod=bb_period, nbdevup=bb_k, nbdevdn=bb_k, matype=0
    )
    features['bb_upper'] = upper
    features['bb_middle'] = middle
    features['bb_lower'] = lower

    slowk, slowd = talib.STOCH(
        df['high'],
        df['low'],
        df['close'],
        fastk_period=stoch_k_period,
        slowk_period=3,
        slowk_matype=0,
        slowd_period=stoch_d_period,
        slowd_matype=0,
    )
    features['stoch_k'] = slowk
    features['stoch_d'] = slowd

    typical_price = (df['high'] + df['low'] + df['close']) / 3
    cumulative_vp = (typical_price * df['volume']).cumsum()
    cumulative_volume = df['volume'].cumsum()
    features['vwap'] = cumulative_vp / cumulative_volume

    features['volume'] = df['volume']
    return features.dropna().reset_index(drop=True)
