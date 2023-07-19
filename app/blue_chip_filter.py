from typing import Dict

import pandas as pd
from loguru import logger
from pandas import DataFrame, DatetimeIndex, Series

from app.model.ticker_data import TickerData
from app.model.ticker_data_item import TickerDataItem
from app.utils.utils import Utils


class BlueChipFilter:

    def __init__(self,
                 min_nr_of_shares=5000000,
                 min_nr_of_institutional_investors=80,
                 min_nr_of_dividend_increases=5
                 ):
        self.min_nr_of_shares = min_nr_of_shares
        self.min_nr_of_institutional_investors = min_nr_of_institutional_investors
        self.min_nr_of_dividend_increases = min_nr_of_dividend_increases

    def run_filter(self, ticker_data: TickerData) -> TickerData:
        accepted_tickers: Dict[str, TickerDataItem] = dict()
        for symbol, ticker_data_item in ticker_data.symbol_to_ticker_response.items():
            try:
                if self.is_applicable_symbol(ticker_data.start_date, ticker_data.end_date, ticker_data_item):
                    accepted_tickers[symbol] = ticker_data_item
            except:
                logger.warning(f"Could not evaluate symbol: {symbol}")

        return TickerData(
            ticker_data.start_date,
            ticker_data.end_date,
            accepted_tickers
        )

    def is_applicable_symbol(self, start_date: str, end_date: str, ticker_item: TickerDataItem) -> bool:
        return self.is_dividend_stock(ticker_item) and \
            self.is_uninterrupted_dividends(start_date, end_date, ticker_item) and \
            self.is_dividends_increasing_n_times(ticker_item) and \
            self.has_minimum_nr_of_outstanding_shares(ticker_item) and \
            self.has_minimum_nr_of_institutional_investors(ticker_item) and \
            self.is_earnings_increasing_n_times(ticker_item)

    def is_dividend_stock(self, ticker_item: TickerDataItem) -> bool:
        dividend: Series = ticker_item.get_dividend()
        if len(dividend) < 1 or dividend.empty:
            logger.info(f"Filter symbol {ticker_item.symbol}: No Dividends available.")
            return False
        return True

    def is_uninterrupted_dividends(self, start_date: str, end_date: str, ticker_item: TickerDataItem) -> bool:
        dividend_dates: DataFrame = ticker_item.get_dividend_dates()
        missing_dates: DatetimeIndex = pd.date_range(start=start_date, end=end_date, freq="Y").year.difference(dividend_dates.year)
        if not missing_dates.empty:
            logger.info(f"Filter symbol {ticker_item.symbol}: Missing Dividend dates {missing_dates.values}.")
            return False
        return True

    def is_dividends_increasing_n_times(self, ticker_item: TickerDataItem) -> bool:
        dividend: Series = ticker_item.get_dividend()
        dividend_filtered: DataFrame = dividend.loc[Utils.get_date_string_today_n_years_back(12):Utils.get_date_string_yesterday()]
        if dividend_filtered[dividend_filtered > 0].dropna().size < self.min_nr_of_dividend_increases:
            logger.info(f"Filter symbol {ticker_item.symbol}: Missing Dividend increases.")
            return False
        return True

    def has_minimum_nr_of_outstanding_shares(self, ticker_item: TickerDataItem) -> bool:
        nr_of_shares: int = ticker_item.get_nr_of_shares()
        if nr_of_shares < self.min_nr_of_shares:
            logger.info(f"Filter symbol {ticker_item.symbol}: Number of shares to low {nr_of_shares}.")
            return False
        return True

    def has_minimum_nr_of_institutional_investors(self, ticker_item: TickerDataItem) -> bool:
        nr_of_institutional_investors: int = ticker_item.get_nr_of_institutional_holders()
        if nr_of_institutional_investors < self.min_nr_of_institutional_investors:
            logger.info(f"Filter symbol {ticker_item.symbol}: Number of institutional investors to low {nr_of_institutional_investors}.")
            return False
        return True

    def is_earnings_increasing_n_times(self, ticker_item: TickerDataItem) -> bool:
        # FIXME
        return True
