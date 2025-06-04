# bot4

## Overview

`bot4` is an experimental cryptocurrency trading bot built with Python and
[ccxt](https://github.com/ccxt/ccxt). It supports live trading on Binance
Futures, simple backtesting and training of an XGBoost model for generating
signals.

## Installation

1. Clone the repository and navigate to the project directory.
   ```bash
   git clone <repo-url>
   cd bot4
   ```
2. Install Python dependencies.
   ```bash
   pip install -r requirements.txt
   ```
   The `ta-lib` package requires the TA-Lib library to be available on your system. On Debian/Ubuntu you can install it with `apt-get install -y libta-lib0 libta-lib-dev`.

## Configuration

Copy `config.json` and edit it with your API credentials and desired settings. At minimum, set `api_key` and `api_secret` to your Binance account keys. Never commit your real keys to version control.

Example:
```json
{
    "api_key": "YOUR_KEY",
    "api_secret": "YOUR_SECRET",
    "testnet": true,
    "mode": "live",
    "leverage": 10,
    "max_trades_per_day": 5,
    "indicators": {
        "BTCUSDT": {"ema_short": 12, "ema_long": 26, "rsi": 14}
    }
}
```

## Usage

Run the bot in live mode:
```bash
python main.py
```
To run backtests or train the strategy, set `mode` in `config.json` to `"backtest"` or `"train"` before executing `main.py`.

Additional utilities:
- `fetch_ohlcv.py` – download historical candles to the `data/` directory.
- `train_model.py` – train the XGBoost model from `trade_log.csv`.
- `auto_retrain.py` – automatically retrain based on log data.

## Scripts

- **`main.py`** – entry point that loads the config and launches the bot in live trading, backtest or training mode.
- **`live_strategy.py`** – implements the moving‑average based trading logic.
- **`backtest_engine.py`** – evaluates past trades stored in `trade_log.csv`.
- **`signal_engine.py`** – wrapper around the ML model for generating signals.
- **`websocket_client.py`** – handles real‑time price streams from Binance.
- **`exchange_client.py`** – simple async wrapper around ccxt exchange objects.
- **`fetch_ohlcv.py`** – utility to fetch and save historical OHLCV data.
- **`optimize_indicators.py`** – helper for tuning indicator parameters.

## API Credentials

Your API key and secret are required for live trading. Ensure they are kept private and never shared. If the credentials are invalid or missing, the bot will not be able to place orders.
