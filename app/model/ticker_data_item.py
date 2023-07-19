from pandas import DataFrame, Series
from yfinance import Ticker


class TickerDataItem:

    def __init__(self, symbol: str, ticker: Ticker):
        self.symbol = symbol
        self.ticker = ticker
        self.historical_data = None  # This can be added if required: yf.download(symbol)

    def get_dividend_dates(self) -> DataFrame:
        return self.ticker.dividends.index

    def get_dividend(self) -> Series:
        return self.ticker.dividends

    def get_nr_of_shares(self) -> int:
        return self.ticker.info["sharesOutstanding"]

    def get_nr_of_institutional_holders(self) -> int:
        major_holders: DataFrame = self.ticker.major_holders
        return int(major_holders[major_holders[1] == "Number of Institutions Holding Shares"][0].values[0])

    def get_basic_info(self):
        return f"Name: {self.ticker.info['longName']} - DY: {self.ticker.info['dividendYield']} - PEG: {self.ticker.info['pegRatio']} - PB: {self.ticker.info['priceToBook']} - Sector: {self.ticker.info['sector']} - Industry: {self.ticker.info['industry']} - Website: {self.ticker.info['website']}"
