"""Training utilities for building the XGBoost model from trade logs."""

import pandas as pd
import numpy as np
import xgboost as xgb
import talib
import joblib
import logging
from sklearn.model_selection import StratifiedKFold, cross_val_score
from features import extract_features

logger = logging.getLogger(__name__)




def train_model(log_path='data/trade_log.csv', model_output='model_xgb.pkl'):
    try:
        trades = pd.read_csv(log_path)
        trades = trades.dropna()
        trades = trades[trades['type'] == 'ENTRY']

        X_list = []
        y_list = []

        for _, row in trades.iterrows():
            try:
                df = pd.DataFrame({
                    'open': [row['open']],
                    'high': [row['high']],
                    'low': [row['low']],
                    'close': [row['close']],
                    'volume': [row['volume']]
                })
                df = pd.concat([df] * 150, ignore_index=True)  # Simular série temporal
                feats = extract_features(df)
                if feats.empty:
                    continue
                X_list.append(feats.iloc[-1])
                y_list.append(1 if row['result'].lower() == 'win' else 0)
            except Exception as e:
                logger.warning(f"Erro ao processar linha: {e}")

        if not X_list:
            logger.error("Nenhum dado válido para treinar.")
            return

        X = pd.DataFrame(X_list)
        y = np.array(y_list)

        model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')

        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        roc_scores = cross_val_score(model, X, y, cv=cv, scoring='roc_auc')
        acc_scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')

        logger.info("--- Validação Cruzada ---")
        logger.info(f"ROC AUC: {roc_scores.mean():.4f} (+/- {roc_scores.std():.4f})")
        logger.info(f"Accuracy: {acc_scores.mean():.4f} (+/- {acc_scores.std():.4f})")

        model.fit(X, y)
        joblib.dump(model, model_output)
        logger.info(f"Modelo treinado e salvo em: {model_output}")

    except Exception as e:
        logger.error(f"Erro ao treinar modelo: {e}")


if __name__ == '__main__':
    train_model()
