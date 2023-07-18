import yfinance as yf
from loguru import logger
from yfinance import Tickers

from app.model.ticker_data import TickerData
from app.model.ticker_data_item import TickerDataItem


class YahooFinanceApiClient:

    @staticmethod
    def ticker_requests(symbols: [str], start_date: str, end_date: str) -> TickerData:
        logger.info(f"Gathering Historical Data from {start_date}-{end_date} for the following symbols: {symbols}")
        tickers: Tickers = yf.Tickers(symbols)
        return TickerData(start_date,
                          end_date,
                          dict((symbol, TickerDataItem(symbol, ticker)) for symbol, ticker in tickers.tickers.items())
                          )
