# bot4

Trading bot sample project using CCXT and XGBoost.

The codebase works with **Python 3.11** and relies on the `ta-lib` Python
package (version `0.6.3`). Make sure you install dependencies from
`requirements.txt` rather than the similarly named `TA-Lib` package which may
lead to import errors.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

Edit `config.json` with your API credentials then run:

```bash
python main.py
```

The keys can also be provided via the environment variables
`BINANCE_API_KEY` and `BINANCE_API_SECRET` which override values in
`config.json`.

Modes available via the `mode` key in `config.json`:

* `live` - run the strategy in real time
* `train` - update the model using logged trades
* `backtest` - replay trades to evaluate performance

### New options

* `min_ai_confidence` - probability threshold (0-1) required by the AI model to allow an entry
* Spread and depth are automatically checked before orders to avoid poor fills

## Sample data

Example trade logs are stored in the `data/` directory. The scripts
expect `data/trade_log.csv` to exist and will append new entries to it.

## Optional scripts

Several helper scripts are available for data collection and model
management:

* `auto_retrain.py` - automatically retrains `model_xgb.pkl` using the
  trade log. Run `python auto_retrain.py` after accumulating new trade
  data.
* `train_model.py` - performs cross validation on the trade log and saves
  a new model. Usage: `python train_model.py`.
* `fetch_ohlcv.py` - downloads recent OHLCV candles for popular pairs and
  saves them under `data/`. Execute `python fetch_ohlcv.py`.
* `websocket_client.py` - example real-time feed that falls back to REST
  when the WebSocket disconnects. Run `python websocket_client.py` to see
  the stream in action.
