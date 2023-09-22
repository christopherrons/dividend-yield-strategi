import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame, DatetimeIndex, Series
from sklearn.linear_model import LinearRegression
from yfinance import Ticker
import seaborn as sns

class TickerDataItem:

    def __init__(self, symbol: str, name: str, exchange: str, start_date: str, end_date: str, ticker: Ticker):
        self.symbol: str = symbol
        self.name: str = name
        self.exchange: str = exchange
        self.start_date: str = start_date
        self.end_date: str = end_date
        self.ticker: Ticker = ticker
        self._historical_data: DataFrame = None
        self._closing_prices: DataFrame = None
        self._weekly_prices: DataFrame = None
        self._get_trend_by_year: DataFrame = None

    @property
    def get_trend_by_year(self) -> DataFrame:
        if self._get_trend_by_year is None:
            years = []
            slope_values = []
            for year in self.weekly_prices.index.year.unique():
                weekly_price_per_year = self.weekly_prices[self.weekly_prices.index.year == year]

                time = mdates.date2num(weekly_price_per_year.index).reshape(-1, 1)
                model: LinearRegression = LinearRegression().fit(time, weekly_price_per_year.to_numpy())
                plt.scatter(time, weekly_price_per_year.to_numpy(), color='g')
                plt.plot(time, model.predict(time), color='k')
                plt.title(f"Year: {year}")

                slope = model.coef_

                years.append(year)
                slope_values.append(slope)
            data = {'slope': slope_values, 'is_positive_trend': [value > 0 for value in slope_values]}
            self._get_trend_by_year = pd.DataFrame(data, index=years)
            plt.show()
        return self._get_trend_by_year

    @property
    def weekly_prices(self) -> DataFrame:
        if self._weekly_prices is None:
            self._weekly_prices = self.closing_prices.resample('W').mean()
        return self._weekly_prices

    @property
    def closing_prices(self) -> DataFrame:
        if self._closing_prices is None:
            self._closing_prices = self.historical_data["Close"]
        return self._closing_prices

    @property
    def historical_data(self) -> DataFrame:
        if self._historical_data is None:
            self._historical_data = self.ticker.history(start=self.start_date,
                                                        end=self.end_date,
                                                        actions=True,
                                                        auto_adjust=True)
        return self._historical_data

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
        return 0.01 * float((major_holders[major_holders[1] == "% of Float Held by Institutions"][0].values[0]).strip('%'))

    def get_basic_info(self) -> str:
        return f"Name: {self.ticker.info.get('longName')} - DY: {self.ticker.info.get('dividendYield')} - PEG: {self.ticker.info.get('pegRatio')} \
        - PB: {self.ticker.info.get('priceToBook')} - Sector: {self.ticker.info.get('sector')} - Industry: {self.ticker.info.get('industry')} \
        - Website: {self.ticker.info.get('website')}"
