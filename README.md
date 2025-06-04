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


## Configuration

Edit `config.json` for exchange credentials and strategy options. Keys can also be supplied through the `BINANCE_API_KEY` and `BINANCE_API_SECRET` environment variables which override the values from `config.json`. Example:

```bash
export BINANCE_API_KEY=your_key
export BINANCE_API_SECRET=your_secret
python main.py
```

Relevant settings:

* `mode` - choose `live`, `train` or `backtest`
* `min_ai_confidence` - probability threshold (0-1) required by the model
  before placing an order
* Spread and order book depth are checked before execution to avoid poor fills

Modes available via the `mode` key in `config.json`:

* `live` - run the strategy in real time
* `train` - update the model using logged trades
* `backtest` - replay trades to evaluate performance


## Sample data

Example trade logs are stored in the `data/` directory. The scripts
expect `data/trade_log.csv` to exist and will append new entries to it.

## Optional scripts

Several helper scripts are available for data collection and model
management:

* `auto_retrain.py` - automatically retrains `model_xgb.pkl` using `data/trade_log.csv`. Run `python auto_retrain.py` after collecting new trades.
* `train_model.py` - performs cross validation on the trade log and saves a new model. Usage: `python train_model.py`.
* `fetch_ohlcv.py` - downloads recent OHLCV candles for popular pairs and stores them under `data/`. Execute `python fetch_ohlcv.py`.
* `websocket_client.py` - example real-time feed that falls back to REST when the WebSocket disconnects. Run `python websocket_client.py` to see the stream.
