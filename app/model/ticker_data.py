from __future__ import annotations
from app.model.ticker_data_item import TickerDataItem
from app.utils.utils import Utils
from loguru import logger
from pathlib import Path
from typing import Dict
import pandas as pd
import yfinance as yf


class TickerData:

    def __init__(self, symbol_to_ticker_response: Dict[str, TickerDataItem]):
        self.symbol_to_ticker_response = symbol_to_ticker_response

    def download_price_data(self) -> None:
        for symbol, ticker_data_item in self.symbol_to_ticker_response.items():
            logger.info(f"Downloading historical data for symbol: {symbol}")
            ticker_data_item.historical_data = yf.download(
                symbol,
                start=ticker_data_item.start_date,
                end=ticker_data_item.end_date,
                actions=True,
                auto_adjust=True,
                progress=False,
            )

    def store_ticker_symbols(self, dst: Path) -> None:
        logger.info("Store Blue Chip ticker symbols.")
        df_tickers = pd.DataFrame(
            [[
                symbol,
                ticker_data_item.name,
                ticker_data_item.exchange,
                Utils.get_date_first_trade(ticker_data_item.ticker.info['firstTradeDateEpochUtc']).strftime('%Y-%m-%d'),
            ] for idx, (symbol, ticker_data_item) in enumerate(self.symbol_to_ticker_response.items())
            ],
            columns=['symbol', 'name', 'exchange', 'ipoDate'],
        )
        if not df_tickers.empty:
            df_tickers.to_csv(dst, index=False)