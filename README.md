# bot4

Trading bot sample project using CCXT and XGBoost.

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

## Sample data

Example trade logs are stored in the `data/` directory. The scripts
expect `data/trade_log.csv` to exist and will append new entries to it.
