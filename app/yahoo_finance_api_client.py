from app.model.ticker_data import TickerData
from app.model.ticker_data_item import TickerDataItem
from app.utils.utils import Utils
from loguru import logger
from yfinance import Tickers
import yfinance as yf


class YahooFinanceApiClient:

    @staticmethod
    def ticker_requests(indices: list, start_date: str = None, end_date: str = None) -> TickerData:
        logger.info(f"Gathering historical data for the following markets: {', '.join(indices)}")
        symbols = sum([Utils.get_tickers(index)[:10] for index in indices], [])
        tickers: Tickers = yf.Tickers(list(dict.fromkeys(symbols))) # Duplicates are removed!
        return TickerData(
            indices,
            dict((symbol, TickerDataItem(
                symbol,
                start_date if start_date else Utils.get_date_string_first_trade(ticker.info['firstTradeDateEpochUtc']),
                end_date if end_date else Utils.get_date_string_yesterday(),
                ticker,
            )) for symbol, ticker in tickers.tickers.items()),
        )
