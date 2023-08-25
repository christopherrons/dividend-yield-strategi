from app.model.ticker_data import TickerData
from app.model.ticker_data_item import TickerDataItem
from app.utils.utils import Utils
from loguru import logger
from pandas import DataFrame
from yfinance import Tickers
import pandas as pd
import yfinance as yf


class YahooFinanceApiClient:

    @staticmethod
    def ticker_requests(exchanges: list, start_date: str = None, end_date: str = None) -> TickerData:
        logger.info(f"Gathering historical data for the following exchanges: {', '.join(exchanges)}")
        symbols: DataFrame = pd.concat([Utils.get_tickers(index) for index in exchanges]).reset_index(drop=True)
        tickers: Tickers = yf.Tickers(list(symbols['symbol']))
        return TickerData(
            exchanges,
            dict((symbol, TickerDataItem(
                symbol,
                start_date if start_date else list(symbols.loc[symbols['symbol'] == symbol, 'ipoDate'])[0],
                end_date if end_date else Utils.get_date_string_yesterday(),
                ticker,
            )) for symbol, ticker in tickers.tickers.items()),
        )
