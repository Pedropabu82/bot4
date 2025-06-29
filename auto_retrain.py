"""Retrain the XGBoost model automatically from logged trades."""

import pandas as pd
import numpy as np
import ccxt
import joblib
import xgboost as xgb
import talib
import time
import os
import logging
import json
from sklearn.utils.class_weight import compute_class_weight
from features import extract_features

logger = logging.getLogger(__name__)

def fetch_ohlcv(symbol, timeframe, since, limit=300):
    binance = ccxt.binance({
        'enableRateLimit': True,
    })
    binance.options['defaultType'] = 'future'
    try:
        data = binance.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        logger.error(f"Erro ao buscar candles para {symbol} {timeframe}: {e}")
        return None


def train_from_log(trade_log='data/trade_log.csv', config_file='config.json'):
    if not os.path.exists(trade_log):
        logger.error(f"Arquivo {trade_log} não encontrado.")
        return

    trades = pd.read_csv(trade_log)
    trades = trades.dropna()
    trades['result'] = trades['result'].astype(str)

    if 'EXIT' not in trades['type'].unique():
        logger.warning(
            "Nenhuma linha de EXIT encontrada no log de trades. "
            "Somente entradas (ENTRY) estão presentes. O modelo precisa de ambos "
            "registros para aprender os resultados."
        )

    trades = trades[(trades['type'] == 'ENTRY') &
                    (trades['result'].str.lower().isin(['win', 'loss']))]
    if trades.empty:
        logger.error("Nenhum trade concluído encontrado no log para treino.")
        return

    with open(config_file, 'r') as f:
        cfg = json.load(f)
    bb_period = cfg.get('bb_period', 20)
    bb_k = cfg.get('bb_k', 2)
    stoch_k_period = cfg.get('stoch_k_period', 14)
    stoch_d_period = cfg.get('stoch_d_period', 3)
    indicator_cfg = cfg.get('indicators', {})
    logger.info(f"Carregando {len(trades)} trades do log.")

    if len(trades) < 10:
        logger.error("ERRO: Menos de 10 trades disponíveis. Adicione mais dados para treino.")
        return

    X, y = [], []

    for _, row in trades.iterrows():
        symbol = row['symbol']
        timeframe = row['timeframe']
        timestamp = pd.to_datetime(row['timestamp'])
        since = int((timestamp - pd.Timedelta(minutes=600)).timestamp() * 1000)

        df = fetch_ohlcv(symbol, timeframe, since)
        if df is None or df.empty:
            logger.warning(f"Dados vazios para {symbol} {timeframe}, pulando...")
            continue

        cfg = indicator_cfg.get(symbol, {})
        ema_short = cfg.get('ema_short', 9)
        ema_long = cfg.get('ema_long', 21)
        macd_fast = cfg.get('macd_fast', 12)
        macd_slow = cfg.get('macd_slow', 26)
        macd_signal = cfg.get('macd_signal', 9)
        feats = extract_features(
            df,
            bb_period=bb_period,
            bb_k=bb_k,
            stoch_k_period=stoch_k_period,
            stoch_d_period=stoch_d_period,
            ema_short=ema_short,
            ema_long=ema_long,
            macd_fast=macd_fast,
            macd_slow=macd_slow,
            macd_signal=macd_signal,
        )
        if feats.empty:
            logger.warning(f"Features vazias para {symbol} {timeframe}, pulando...")
            continue

        X.append(feats.iloc[-1])
        y.append(1 if row['result'].lower() == 'win' else 0)

        time.sleep(0.1)

    if not X:
        logger.error("Nenhum dado válido coletado para treino.")
        return

    unique_classes = set(y)
    logger.info(f"Classes encontradas no y: {unique_classes}")
    if len(unique_classes) < 2:
        logger.error("ERRO: Apenas uma classe detectada no vetor y. Adicione mais trades de tipos diferentes (win/loss).")
        return

    df_X = pd.DataFrame(X)
    # Compute class weights for balancing
    class_weights = compute_class_weight('balanced', classes=np.unique(y), y=np.array(y))
    weight_dict = {0: class_weights[0], 1: class_weights[1]}
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', scale_pos_weight=weight_dict[1]/weight_dict[0])
    model.fit(df_X, y)
    joblib.dump(model, "model_xgb.pkl")
    logger.info("Modelo treinado e salvo como model_xgb.pkl")

if __name__ == "__main__":
    train_from_log()
