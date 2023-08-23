from app.model.ticker_data import TickerData
from app.model.ticker_data_item import TickerDataItem
from app.utils.utils import Utils
from loguru import logger
from pandas import DatetimeIndex, PeriodIndex, Series
from typing import Dict
import pandas as pd


class BlueChipFilter:

    def __init__(self,
        sp_quality_ranking: str = 'A',
        min_nr_of_shares: int = 5000000,
        min_nr_of_institutional_investors: int = 80,
        min_nr_of_uninterrupted_dividends: int = 25,
        min_nr_of_dividend_increases: int = 5,
    ):
        self.sp_quality_ranking = sp_quality_ranking
        self.min_nr_of_shares = min_nr_of_shares
        self.min_nr_of_institutional_investors = min_nr_of_institutional_investors
        self.min_nr_of_uninterrupted_dividends = min_nr_of_uninterrupted_dividends
        self.min_nr_of_dividend_increases = min_nr_of_dividend_increases

    def run_filter(self, ticker_data: TickerData) -> TickerData:
        accepted_tickers: Dict[str, TickerDataItem] = dict()
        for symbol, ticker_data_item in ticker_data.symbol_to_ticker_response.items():
            try:
                if self.is_applicable_symbol(ticker_data_item):
                    accepted_tickers[symbol] = ticker_data_item
            except:
                logger.warning(f"Could not evaluate symbol: {symbol}")

        return TickerData(ticker_data.indices, accepted_tickers)

    def is_applicable_symbol(self, ticker_item: TickerDataItem) -> bool:
        return self.is_dividend_stock(ticker_item) and \
            self.has_sp_quality_ranking(ticker_item) and \
            self.has_minimum_nr_of_outstanding_shares(ticker_item) and \
            self.has_minimum_nr_of_institutional_investors(ticker_item) and \
            self.is_uninterrupted_dividends(ticker_item) and \
            self.is_dividends_increasing_n_times(ticker_item) and \
            self.is_earnings_increasing_n_times(ticker_item)

    def is_dividend_stock(self, ticker_item: TickerDataItem) -> bool:
        dividends: Series = ticker_item.get_dividends()
        if len(dividends) < 1 or dividends.empty:
            logger.info(f"Filter symbol {ticker_item.symbol} - No dividends available.")
            return False
        return True

    def has_sp_quality_ranking(self, ticker_item: TickerDataItem) -> bool:
        # FIXME
        return True

    def has_minimum_nr_of_outstanding_shares(self, ticker_item: TickerDataItem) -> bool:
        nr_of_shares: int = ticker_item.get_nr_of_shares()
        if nr_of_shares < self.min_nr_of_shares:
            logger.info(f"Filter symbol {ticker_item.symbol} - Number of shares to low: {nr_of_shares}.")
            return False
        return True

    def has_minimum_nr_of_institutional_investors(self, ticker_item: TickerDataItem) -> bool:
        nr_of_institutional_investors: int = ticker_item.get_nr_of_institutional_holders()
        float_held_by_institutional_investors: float = ticker_item.get_float_held_by_institutional_investors()
        if any([
            nr_of_institutional_investors < self.min_nr_of_institutional_investors,
            float_held_by_institutional_investors < 0.5,
        ]):
            logger.info(f"Filter symbol {ticker_item.symbol} - Number of institutional investors to low: {nr_of_institutional_investors}.")
            return False
        return True

    def is_uninterrupted_dividends(self, ticker_item: TickerDataItem) -> bool:
        dividend_dates: DatetimeIndex = ticker_item.get_dividend_dates()
        quarters: PeriodIndex = pd.date_range(
            start=Utils.get_date_string_n_years_back(self.min_nr_of_uninterrupted_dividends, ticker_item.end_date),
            end=ticker_item.end_date,
            freq='Q',
            tz=ticker_item.ticker.history_metadata['exchangeTimezoneName'],
        ).tz_convert(None).to_period('Q').drop_duplicates() # Only verify elapsed quarters!
        quarters = quarters[quarters.year != 2019] # Exclude 2019 due to Covid pandemic!
        missing_quarters = quarters.difference(dividend_dates.tz_convert(None).to_period('Q'))
        if not missing_quarters.empty:
            logger.info(f"Filter symbol {ticker_item.symbol} - Missing dividend quarters: {', '.join([f'{i.year}Q{i.quarter}' for i in missing_quarters])}.")
            return False
        return True

    def is_dividends_increasing_n_times(self, ticker_item: TickerDataItem) -> bool:
        dividends: Series = ticker_item.get_dividends()
        dividends_filtered = dividends.loc[
            Utils.get_date_string_n_years_back(12, ticker_item.end_date):ticker_item.end_date
        ]
        dividend_increases = dividends_filtered.diff()[dividends_filtered.diff() > 0].dropna()
        dividend_decreases = dividends_filtered.diff()[dividends_filtered.diff() < 0].dropna()
        if any([dividend_increases.size < self.min_nr_of_dividend_increases, dividend_decreases.size > 0]):
            logger.info(f"Filter symbol {ticker_item.symbol} - Number of dividend increases is too low: {dividend_increases.size}.")
            return False
        return True

    def is_earnings_increasing_n_times(self, ticker_item: TickerDataItem) -> bool:
        # FIXME
        return True
