"""Asynchronous Binance API client wrapper using ccxt."""

import ccxt.async_support as ccxt
import pandas as pd
import logging
import asyncio
import os

logger = logging.getLogger(__name__)

class BinanceClient:
    def __init__(self, config):
        self.config = config
        api_key = os.getenv('BINANCE_API_KEY', config.get('api_key'))
        api_secret = os.getenv('BINANCE_API_SECRET', config.get('api_secret'))
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'asyncio_loop': asyncio.get_event_loop(),
            'options': {
                'defaultType': 'future',
                'adjustForTimeDifference': True,
                'recvWindow': 10000
            }
        })
        if config.get('testnet', False):
            self.exchange.set_sandbox_mode(True)
        logger.info(
            "BinanceClient initialized (testnet)" if config.get('testnet', False)
            else "BinanceClient initialized (mainnet)"
        )

    async def fetch_candles(self, symbol, timeframe, limit=300):
        try:
            data = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logger.error(f"Error fetching candles for {symbol} {timeframe}: {e}")
            return None

    async def get_balance(self):
        try:
            balance = await self.exchange.fetch_balance()
            return balance
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {'USDT': {'free': 0}}

    async def close(self):
        try:
            await self.exchange.close()
            logger.info("BinanceClient connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
