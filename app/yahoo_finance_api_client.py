from typing import Dict

import yfinance as yf
from pandas import DataFrame
from yfinance import Tickers, Ticker

from app.model.ticker_data import TickerData
from app.model.ticker_data_item import TickerDataItem
from app.utils.utils import Utils


class YahooFinanceApiClient:

    @staticmethod
    def ticker_requests(symbols: DataFrame, start_date: str = None, end_date: str = None) -> TickerData:
        tickers: Tickers = yf.Tickers(list(symbols['symbol']))
        symbol_to_ticker_response: Dict[str, TickerDataItem] = {
            symbol: YahooFinanceApiClient.create_ticker_data_item(symbol, ticker, symbols, start_date, end_date)
            for symbol, ticker in tickers.tickers.items()
        }
        return TickerData(symbol_to_ticker_response)

    @staticmethod
    def create_ticker_data_item(symbol: str, ticker: Ticker, symbols: DataFrame, start_date: str, end_date: str) -> TickerDataItem:
        return TickerDataItem(
            symbol,
            list(symbols.loc[symbols['symbol'] == symbol, 'name'])[0],
            list(symbols.loc[symbols['symbol'] == symbol, 'exchange'])[0],
            start_date if start_date else list(symbols.loc[symbols['symbol'] == symbol, 'ipoDate'])[0],
            end_date if end_date else Utils.get_date_string_yesterday(),
            ticker,
        )
