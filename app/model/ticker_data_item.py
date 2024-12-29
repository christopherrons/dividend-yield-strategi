from pandas import DataFrame, DatetimeIndex, Series
from yfinance import Ticker

from app.model.historical_ticker_data import HistoricalTickerData


class TickerDataItem:

    def __init__(self, symbol: str, name: str, exchange: str, start_date: str, end_date: str, ticker: Ticker):
        self.symbol: str = symbol
        self.name: str = name
        self.exchange: str = exchange
        self.start_date: str = start_date
        self.end_date: str = end_date
        self.ticker: Ticker = ticker
        self.historical_ticker_data: HistoricalTickerData = HistoricalTickerData(ticker, start_date, end_date)

    @property
    def historical_data(self) -> DataFrame:
        return self.historical_ticker_data.historical_data

    @property
    def closing_prices(self) -> DataFrame:
        return self.historical_ticker_data.closing_prices

    @property
    def weekly_prices(self) -> DataFrame:
        return self.historical_ticker_data.weekly_prices

    @property
    def annual_dividends(self) -> DataFrame:
        return self.historical_ticker_data.annual_dividends

    @property
    def annual_high_prices(self) -> DataFrame:
        return self.historical_ticker_data.annual_high_prices

    @property
    def annual_low_prices(self) -> DataFrame:
        return self.historical_ticker_data.annual_low_prices

    @property
    def annual_high_price_yields(self) -> DataFrame:
        return self.historical_ticker_data.annual_high_price_yields

    @property
    def annual_low_price_yields(self) -> DataFrame:
        return self.historical_ticker_data.annual_low_price_yields

    @property
    def overvalue_yield(self) -> float:
        return self.historical_ticker_data.overvalue_yield

    @property
    def undervalue_yield(self) -> float:
        return self.historical_ticker_data.undervalue_yield

    @property
    def overvalue_prices(self) -> DataFrame:
        return self.historical_ticker_data.overvalue_prices

    @property
    def undervalue_prices(self) -> DataFrame:
        return self.historical_ticker_data.undervalue_prices

    @property
    def annual_trend_using_weekly_prices(self) -> DataFrame:
        return self.historical_ticker_data.annual_trend_using_weekly_prices

    def get_dividend_dates(self) -> DatetimeIndex:
        return self.ticker.dividends.index

    def get_dividends(self) -> Series:
        return self.ticker.dividends

    def get_nr_of_shares(self) -> int:
        return self.ticker.info['sharesOutstanding']

    def get_nr_of_institutional_holders(self) -> int:
        major_holders: DataFrame = self.ticker.major_holders
        if len(major_holders) ==0:
            result = 0
        else:
            result = int(major_holders.at['institutionsCount','Value'])
            # result = int(major_holders[major_holders[1] == "Number of Institutions Holding Shares"][0].values[0]) # old line, for yfinance version 0.2.36
        return result

    def get_float_held_by_institutional_investors(self) -> float:
        major_holders: DataFrame = self.ticker.major_holders
        if len(major_holders) ==0:
            result = 0
        else:
            result = float(major_holders.at['institutionsFloatPercentHeld','Value'])
            # result = 0.01 * float((major_holders[major_holders[1] == "% of Float Held by Institutions"][0].values[0]).strip('%')) # old line, for yfinance version 0.2.36
        
        return result

    def get_basic_info(self) -> str:
        return f"Name: {self.ticker.info.get('longName')} - DY: {self.ticker.info.get('dividendYield')} - PEG: {self.ticker.info.get('pegRatio')} \
        - PB: {self.ticker.info.get('priceToBook')} - Sector: {self.ticker.info.get('sector')} - Industry: {self.ticker.info.get('industry')} \
        - Website: {self.ticker.info.get('website')}"
