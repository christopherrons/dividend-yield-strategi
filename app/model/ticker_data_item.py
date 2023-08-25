from pandas import DataFrame, DatetimeIndex, Series
from yfinance import Ticker


class TickerDataItem:

    def __init__(self, symbol: str, start_date: str, end_date: str, ticker: Ticker):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.ticker = ticker
        self.historical_data = None

    def get_dividend_dates(self) -> DatetimeIndex:
        return self.ticker.dividends.index

    def get_dividends(self) -> Series:
        return self.ticker.dividends

    def get_nr_of_shares(self) -> int:
        return self.ticker.info['sharesOutstanding']

    def get_nr_of_institutional_holders(self) -> int:
        major_holders: DataFrame = self.ticker.major_holders
        return int(major_holders[major_holders[1] == "Number of Institutions Holding Shares"][0].values[0])

    def get_float_held_by_institutional_investors(self) -> float:
        major_holders: DataFrame = self.ticker.major_holders
        return 0.01*float((major_holders[major_holders[1] == "% of Float Held by Institutions"][0].values[0]).strip('%'))

    def get_basic_info(self):
        return f"Name: {self.ticker.info.get('longName')} - DY: {self.ticker.info.get('dividendYield')} - PEG: {self.ticker.info.get('pegRatio')} \
        - PB: {self.ticker.info.get('priceToBook')} - Sector: {self.ticker.info.get('sector')} - Industry: {self.ticker.info.get('industry')} \
        - Website: {self.ticker.info.get('website')}"
