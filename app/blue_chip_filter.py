from typing import Dict

import pandas as pd
from loguru import logger
from pandas import DatetimeIndex, PeriodIndex, Series
from requests.exceptions import HTTPError
import time


from app.model.ticker_data import TickerData
from app.model.ticker_data_item import TickerDataItem
from app.utils.utils import Utils



class BlueChipFilter:

    """
    WHAT IS A BLUE CHIP STOCK?
    
    These are the six criteria:
        1. The dividend has increased five times in the past 5 years
        2. S&P quality ranks the stock in the A category
        3. There are at least 5 mln shares outstanding
        4. There are at least 80 institutional investors
        5. The company has at least 25 years uninterruped dividends
        6. Earning have improvided in at least seven of the last 12 years
    
    
    
    
    
    """    


    def __init__(
            self,
            sp_quality_ranking: str = 'A',
            min_nr_of_shares: int = 5000000,
            min_nr_of_institutional_investors: int = 80,
            min_nr_of_uninterrupted_dividends: int = 25,
            min_nr_of_dividend_increases: int = 5,
            min_nr_of_earning_increases: int = 7,
            allowed_missing_dividend_quarters:int = 4,
            opt_check_dividend_decrease:bool = False,
            DEBUG:bool = True
    ):
        self.sp_quality_ranking = sp_quality_ranking
        self.min_nr_of_shares = min_nr_of_shares
        self.min_nr_of_institutional_investors = min_nr_of_institutional_investors
        self.min_nr_of_uninterrupted_dividends = min_nr_of_uninterrupted_dividends
        self.min_nr_of_dividend_increases = min_nr_of_dividend_increases
        self.min_nr_of_earning_increases = min_nr_of_earning_increases
        self.allowed_missing_dividend_quarters = allowed_missing_dividend_quarters
        self.opt_check_dividend_decrease = opt_check_dividend_decrease
        self.DEBUG = DEBUG

    def run_filter(self, ticker_data: TickerData,n_sleep = 400, sleep_min =5 ) -> TickerData:
        accepted_tickers: Dict[str, TickerDataItem] = dict()
        all_items = ticker_data.symbol_to_ticker_response.items()
        litems = str(len(all_items)); i=0
        for symbol, ticker_data_item in all_items:
            i+=1
            # option to pause between requests to prevent overload after x requests. 
            if i % n_sleep == 0:
                time.sleep(sleep_min*60)
            
            name = ticker_data_item.name
            logger.info(f"\n\n{i} / {litems}  Processing symbol: {symbol} - {name}")
            
            # check filters using while loop due to server rate limits.
            while True:
                try:
                    if self.is_applicable_symbol(ticker_data_item):
                        accepted_tickers[symbol] = ticker_data_item
                        logger.info(f'   -{symbol} successfully passed the set filters')
                        
                    break
                        
                except HTTPError as e:
                    if e.response.status_code == 429:  # Rate limit exceeded
                        logger.warning(f"   -Rate limit exceeded for symbol: {symbol}. Error: {e}")
                        time.sleep(300) # rest 5 minutes.
                    else:
                        logger.warning(f"   -HTTP error occurred for symbol: {symbol}. Error: {e}")
                        break
                
                except Exception as e:
                    logger.warning(f"   -Could not evaluate symbol: {symbol} with error: {e}")
                    break


        return TickerData(accepted_tickers)

    def is_applicable_symbol(self, ticker_item: TickerDataItem) -> bool:
        assert ticker_item.ticker.info['regularMarketOpen']
        return self.is_dividend_stock(ticker_item) and \
            self.has_sp_quality_ranking(ticker_item) and \
            self.has_minimum_nr_of_outstanding_shares(ticker_item) and \
            self.has_minimum_nr_of_institutional_investors(ticker_item) and \
            self.is_uninterrupted_dividends(ticker_item) and \
            self.is_dividends_increasing_n_times(ticker_item) and \
            self.is_earnings_increasing_n_times(ticker_item)

    def is_dividend_stock(self, ticker_item: TickerDataItem) -> bool:
        if not len(ticker_item.ticker.dividends) > 0:
            logger.info(f"   -Filter symbol: {ticker_item.symbol} - No dividends available.")
            return False
        if self.DEBUG:
            logger.info(f"   -Filter symbol: {ticker_item.symbol} - dividends are available.")
        return True

    def has_sp_quality_ranking(self, ticker_item: TickerDataItem) -> bool:
        # FIXME!
        return True

    def has_minimum_nr_of_outstanding_shares(self, ticker_item: TickerDataItem) -> bool:
        nr_of_shares: int = ticker_item.get_nr_of_shares()
        if nr_of_shares < self.min_nr_of_shares:
            logger.info(f"   -Filter symbol: {ticker_item.symbol} - Number of shares to low: {nr_of_shares}.")
            return False
        if self.DEBUG:
            logger.info(f"   -Filter symbol: {ticker_item.symbol} - Number of shares sufficient: {nr_of_shares}.")
        ticker_item.nr_of_shares = nr_of_shares
        return True

    def has_minimum_nr_of_institutional_investors(self, ticker_item: TickerDataItem) -> bool:
        nr_of_institutional_investors: int = ticker_item.get_nr_of_institutional_holders()
        float_held_by_institutional_investors: float = ticker_item.get_float_held_by_institutional_investors()
        if any([
            nr_of_institutional_investors < self.min_nr_of_institutional_investors,
            float_held_by_institutional_investors < 0.5,
        ]):
            logger.info(
                f"   -Filter symbol: {ticker_item.symbol} - Number of or float held by institutional investors to low: \nnr of major investors = {nr_of_institutional_investors}\nfloat held = {float_held_by_institutional_investors}")
            return False
        if self.DEBUG:
            logger.info(
                f"   -Filter symbol: {ticker_item.symbol} - Number of or float held by institutional investors sufficient: \nnr of major investors = {nr_of_institutional_investors}\nfloat held = {float_held_by_institutional_investors}")
        ticker_item.nr_of_institutional_investors = nr_of_institutional_investors
        
        return True

    def is_uninterrupted_dividends(self, ticker_item: TickerDataItem) -> bool:
        dividend_dates: DatetimeIndex = ticker_item.get_dividend_dates()
        quarters: PeriodIndex = pd.date_range(
            start=Utils.get_date_string_n_years_back(self.min_nr_of_uninterrupted_dividends, ticker_item.end_date),
            end=ticker_item.end_date,
            freq='QE',
            tz=ticker_item.ticker.history_metadata['exchangeTimezoneName'],
        ).tz_convert(None).to_period('Q').drop_duplicates()  # Only verify elapsed quarters!
        quarters = quarters[quarters.year != 2020]  # Exclude 2020 due to Covid pandemic!
        missing_quarters = quarters.difference(dividend_dates.tz_convert(None).to_period('Q'))
        
        if not missing_quarters.empty:
            n_missing_quarters = len(missing_quarters)
            if n_missing_quarters >= self.allowed_missing_dividend_quarters:
                logger.info(
                    f"   -Filter symbol: {ticker_item.symbol} - Missing dividend quarters (Failed): n = {n_missing_quarters}\n{', '.join([f'{i.year}Q{i.quarter}' for i in missing_quarters])}.")
                return False
            else:
                logger.info(
                    f"   -Filter symbol: {ticker_item.symbol} - Missing dividend quarters (Allowed): n = {n_missing_quarters}\n{', '.join([f'{i.year}Q{i.quarter}' for i in missing_quarters])}.")
                return True
        if self.DEBUG:
            logger.info(
                f"   -Filter symbol: {ticker_item.symbol} -  uninterruped dividends.")
        return True

    def is_dividends_increasing_n_times(self, ticker_item: TickerDataItem) -> bool:
        dividends: Series = ticker_item.get_dividends()
        dividends_filtered = dividends.loc[
                             Utils.get_date_string_n_years_back(12, ticker_item.end_date):ticker_item.end_date
                             ]
        dividend_increases = dividends_filtered.diff()[dividends_filtered.diff() > 0].dropna()
        dividend_decreases = dividends_filtered.diff()[dividends_filtered.diff() < 0].dropna()
        # if any([dividend_increases.size < self.min_nr_of_dividend_increases, dividend_decreases.size > 0]):
        #     logger.info(f"   -Filter symbol: {ticker_item.symbol} - Number of dividend increases is too low: {dividend_increases.size}.")
        #     return False
        if dividend_increases.size < self.min_nr_of_dividend_increases:
                logger.info(f"   -Filter symbol: {ticker_item.symbol} - Number of dividend increases is too low: {dividend_increases.size}.")
                return False
        if all([dividend_decreases.size > 0, self.opt_check_dividend_decrease]):
                logger.info(f"   -Filter symbol: {ticker_item.symbol} - Number of dividend is decreased at least once: {dividend_decreases.size}.")
                return False
        
        
        return True

    def is_earnings_increasing_n_times(self, ticker_item: TickerDataItem) -> bool:
        # FIXME!
        return True
