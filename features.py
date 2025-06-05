import pandas as pd
import talib


def extract_features(
    df: pd.DataFrame,
    symbol: str | None = None,
    config: dict | None = None,
    bb_period: int = 20,
    bb_k: float = 2,
    stoch_k_period: int = 14,
    stoch_d_period: int = 3,
    ema_short_period: int = 9,
    ema_long_period: int = 21,
    macd_fastperiod: int = 12,
    macd_slowperiod: int = 26,
    macd_signalperiod: int = 9,
    rsi_period: int = 14,
) -> pd.DataFrame:
    """Compute model features from OHLCV dataframe."""
    if config and symbol is not None:
        ind_cfg = config.get('indicators', {}).get(symbol, {})
        ema_short_period = ind_cfg.get('ema_short', ema_short_period)
        ema_long_period = ind_cfg.get('ema_long', ema_long_period)
        macd_fastperiod = ind_cfg.get('macd_fast', macd_fastperiod)
        macd_slowperiod = ind_cfg.get('macd_slow', macd_slowperiod)
        macd_signalperiod = ind_cfg.get('macd_signal', macd_signalperiod)
        rsi_period = ind_cfg.get('rsi', rsi_period)

        bb_period = config.get('bb_period', bb_period)
        bb_k = config.get('bb_k', bb_k)
        stoch_k_period = config.get('stoch_k_period', stoch_k_period)
        stoch_d_period = config.get('stoch_d_period', stoch_d_period)

    features = pd.DataFrame()
    features['ema_short'] = talib.EMA(df['close'], timeperiod=ema_short_period)
    features['ema_long'] = talib.EMA(df['close'], timeperiod=ema_long_period)
    macd, macdsignal, _ = talib.MACD(
        df['close'],
        fastperiod=macd_fastperiod,
        slowperiod=macd_slowperiod,
        signalperiod=macd_signalperiod,
    )
    features['macd'] = macd
    features['macdsignal'] = macdsignal
    features['rsi'] = talib.RSI(df['close'], timeperiod=rsi_period)
    features['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
    features['obv'] = talib.OBV(df['close'], df['volume'])
    features['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)

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
