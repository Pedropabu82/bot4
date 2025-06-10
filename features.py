import pandas as pd
import ta.trend as trend
import ta.momentum as momentum
import ta.volume as volume
import ta.volatility as volatility


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
    features = pd.DataFrame(index=df.index)
    features['ema_short'] = trend.ema_indicator(df['close'], window=ema_short)
    features['ema_long'] = trend.ema_indicator(df['close'], window=ema_long)
    features['macd'] = trend.macd(df['close'], window_fast=macd_fast,
                                  window_slow=macd_slow)
    features['macdsignal'] = trend.macd_signal(
        df['close'], window_slow=macd_slow,
        window_fast=macd_fast, window_sign=macd_signal
    )
    features['rsi'] = momentum.rsi(df['close'], window=14)
    features['adx'] = trend.adx(df['high'], df['low'], df['close'], window=14)
    features['obv'] = volume.on_balance_volume(df['close'], df['volume'])
    features['atr'] = volatility.average_true_range(
        df['high'], df['low'], df['close'], window=14
    )

    features['bb_upper'] = volatility.bollinger_hband(
        df['close'], window=bb_period, window_dev=bb_k
    )
    features['bb_middle'] = volatility.bollinger_mavg(
        df['close'], window=bb_period
    )
    features['bb_lower'] = volatility.bollinger_lband(
        df['close'], window=bb_period, window_dev=bb_k
    )

    stoch = momentum.StochasticOscillator(
        df['close'], df['high'], df['low'],
        window=stoch_k_period, smooth_window=stoch_d_period
    )
    features['stoch_k'] = stoch.stoch()
    features['stoch_d'] = stoch.stoch_signal()

    typical_price = (df['high'] + df['low'] + df['close']) / 3
    cumulative_vp = (typical_price * df['volume']).cumsum()
    cumulative_volume = df['volume'].cumsum()
    features['vwap'] = cumulative_vp / cumulative_volume

    features['volume'] = df['volume']
    return features.dropna().reset_index(drop=True)
