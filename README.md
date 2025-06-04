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

## Logging

All utilities now rely on Python's `logging` module. When running
`main.py` or any of the helper scripts like `auto_retrain.py` or
`fetch_ohlcv.py`, log messages are written to `bot.log` and also
displayed in the console.
