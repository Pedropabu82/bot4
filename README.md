# bot4

Trading bot sample project using CCXT and XGBoost.

The codebase works with **Python 3.11** and relies on the `ta-lib` Python
package (version `0.6.3`). Make sure you install dependencies from
`requirements.txt` rather than the similarly named `TA-Lib` package which may
lead to import errors.

## Installing the TA-Lib development library

Before installing the Python packages you need the underlying TA‑Lib system
library. On Debian based systems the library can be built with the same steps
used in the CI workflow:

```bash
sudo apt-get update
sudo apt-get install -y build-essential wget
wget -q http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make
sudo make install
cd ..
```

After this one-time setup you can install the Python bindings via
`pip install -r requirements.txt` as described below.

## Setup

```bash
pip install -r requirements.txt
```
This installs all required libraries including `xgboost`, `joblib`,
`scikit-learn` and `websockets`.

Additional dependencies used by optional features include `xgboost`,
`scikit-learn`, `joblib` and `websockets`.

## Usage

Edit `config.json` with your API credentials then run. Alternatively set the
`BINANCE_API_KEY` and `BINANCE_API_SECRET` environment variables to avoid
storing keys in the file:

```bash
export BINANCE_API_KEY=your_key
export BINANCE_API_SECRET=your_secret
python main.py
```

Modes available via the `mode` key in `config.json`:

* `live` - run the strategy in real time
* `train` - update the model using logged trades
* `backtest` - replay trades to evaluate performance

### New options

* `min_ai_confidence` - probability threshold (0-1) required by the AI model to allow an entry
* `maker_offset` - fraction added/subtracted from best bid/ask when submitting post-only orders (default `0`)
* Spread and depth are automatically checked before orders to avoid poor fills
* The AI model expects the following features: `ema_short`, `ema_long`, `macd`,
  `macdsignal`, `rsi`, `adx`, `obv`, `atr`, `volume`
## Indicator optimization

Earlier versions shipped with a standalone script called
`optimize_indicators.py` to automatically tune moving averages and RSI
periods. The script was incomplete and has been removed. Adjust indicator
parameters manually in `config.json` if desired.


## Sample data

Example trade logs are stored in the `data/` directory. The repository
includes a small sample file called `data/trade_log_sample.csv`.
When running the scripts you should create `data/trade_log.csv` (you
can copy the sample file) as new entries will be appended there during
execution.

## Logging

All utilities now rely on Python's `logging` module. When running
`main.py` or any of the helper scripts like `auto_retrain.py` or
`fetch_ohlcv.py`, log messages are written to `bot.log` and also
displayed in the console.

The log file now begins with the header `timestamp,symbol,timeframe,type,entry_price,exit_price,pnl_pct,result`.
Backtests require data in this file; if it's empty, the results will also be empty.

## Disclaimer

This project is provided for educational purposes only. Trading
cryptocurrencies involves significant risk and may result in financial loss.
Use the code at your own discretion.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.