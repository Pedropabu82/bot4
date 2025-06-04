# bot4

A sample trading bot project using CCXT and XGBoost, designed for automated cryptocurrency trading. Supports live trading, backtesting, and model training with AI-driven trade signals.

## Features

- Real-time trading via CCXT
- AI models using XGBoost for signal generation
- Multiple modes: live, train, backtest
- Automatic retraining and indicator optimization scripts
- Sample data and logs for testing

## Prerequisites

- Python 3.11
- TA-Lib system library

To install TA-Lib on Ubuntu:

```bash
sudo apt-get install -y build-essential libta-lib0 libta-lib0-dev
```

## Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/Pedropabu82/bot4.git
cd bot4
pip install -r requirements.txt
```

## Configuration

Edit `config.json` with your API credentials and desired settings. Keys can also be provided through the `BINANCE_API_KEY` and `BINANCE_API_SECRET` environment variables which override values in `config.json`.

Relevant settings:

- `mode` - choose `live`, `train` or `backtest`
- `min_ai_confidence` - probability threshold (0-1) required by the model before placing an order
- Exchange API keys and other strategy parameters

## Usage

Run the bot:

```bash
python main.py
```

## Modes

- `live` - Run the strategy in real time with your API keys
- `train` - Update the AI model using logged trades
- `backtest` - Replay historical trades and evaluate performance

## Helper Scripts

- `train_model.py` - Retrain the XGBoost model with new trade data. Usage: `python train_model.py`.
- `auto_retrain.py` - Automate model retraining at intervals. Usage: `python auto_retrain.py`.
- `optimize_indicators.py` - Tune technical indicators for the strategy. Usage: `python optimize_indicators.py`.
- `fetch_ohlcv.py` - Download historical price data for backtesting. Usage: `python fetch_ohlcv.py`.
- `websocket_client.py` - Example real-time feed that falls back to REST when disconnected. Usage: `python websocket_client.py`.

## Sample Data

Example trade logs are in the `data/` directory (`data/trade_log.csv`). Backtests require this file; if it's empty, the results will also be empty.

## Example Output

On successful run, expect log output in the console and new entries in `data/trade_log.csv`.

## Troubleshooting

- If you see import errors for TA-Lib, ensure the system library is installed (see prerequisites).
- Double-check API keys and permissions in `config.json`.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

## Contributing

Contributions are welcome! Please open issues or pull requests as needed.
