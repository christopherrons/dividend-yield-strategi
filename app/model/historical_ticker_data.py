import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pandas import DataFrame
from sklearn.linear_model import LinearRegression
from yfinance import Ticker


class HistoricalTickerData:

    def __init__(self, ticker: Ticker, start_date: str, end_date: str):
        self.ticker: Ticker = ticker
        self.start_date: str = start_date
        self.end_date: str = end_date
        self._historical_data: DataFrame = None
        self._closing_prices: DataFrame = None
        self._weekly_prices: DataFrame = None
        self._annual_dividends: DataFrame = None
        self._annual_high_prices: DataFrame = None
        self._annual_low_prices: DataFrame = None
        self._annual_high_price_yields: DataFrame = None
        self._annual_low_price_yields: DataFrame = None
        self._overvalue_yield: float = None
        self._undervalue_yield: float = None
        self._overvalue_prices: DataFrame = None
        self._undervalue_prices: DataFrame = None
        self._get_trend_by_year: DataFrame = None

    @property
    def historical_data(self) -> DataFrame:
        if self._historical_data is None:
            self._historical_data = self.ticker.history(start=self.start_date,
                                                        end=self.end_date,
                                                        actions=True,
                                                        auto_adjust=True)
        return self._historical_data

    @property
    def closing_prices(self) -> DataFrame:
        if self._closing_prices is None:
            self._closing_prices = self.historical_data[['Close']]
        return self._closing_prices

    @property
    def weekly_prices(self) -> DataFrame:
        if self._weekly_prices is None:
            self._weekly_prices = self.closing_prices.resample('W').mean()
        return self._weekly_prices

    @property
    def annual_dividends(self) -> DataFrame:
        if self._annual_dividends is None:
            self._annual_dividends = self.historical_data.loc[
                self.historical_data['Dividends'] != 0,
                ['Dividends'],
            ].resample('AS').sum()  # TODO: Modify to ensure only dividends from 2002 and later are used (due to API instability)!
        return self._annual_dividends

    @property
    def annual_high_prices(self) -> DataFrame:
        if self._annual_high_prices is None:
            self._annual_high_prices = self.closing_prices.groupby(
                self.closing_prices.index.year
            )['Close'].agg(Date='idxmax', Close='max').set_index('Date')
        return self._annual_high_prices

    @property
    def annual_low_prices(self) -> DataFrame:
        if self._annual_low_prices is None:
            self._annual_low_prices = self.closing_prices.groupby(
                self.closing_prices.index.year
            )['Close'].agg(Date='idxmin', Close='min').set_index('Date')
        return self._annual_low_prices

    @property
    def annual_high_price_yields(self) -> DataFrame:
        if self._annual_high_price_yields is None:
            index = self.annual_high_prices[
                self.annual_high_prices.index.year.isin(self.annual_dividends.index.year)
            ].index
            self._annual_high_price_yields = pd.DataFrame(
                np.divide(self.annual_dividends['Dividends'].values, self.annual_high_prices.loc[index, 'Close'].values),
                index=index,
                columns=['High Price Yields'],
            )
        return self._annual_high_price_yields

    @property
    def annual_low_price_yields(self) -> DataFrame:
        if self._annual_low_price_yields is None:
            index = self.annual_low_prices[
                self.annual_low_prices.index.year.isin(self.annual_dividends.index.year)
            ].index
            self._annual_low_price_yields = pd.DataFrame(
                np.divide(self.annual_dividends['Dividends'].values, self.annual_low_prices.loc[index, 'Close'].values),
                index=index,
                columns=['Low Price Yields'],
            )
        return self._annual_low_price_yields

    @property
    def overvalue_yield(self) -> float:
        if self._overvalue_yield is None:
            self._overvalue_yield = list(0.01 * round(
                100 * self.annual_high_price_yields[
                    self.annual_high_price_yields < self.annual_high_price_yields.quantile(0.25)
                    ].mean(),
                1,
            ))[0]  # TODO: Modify to ensure extremes of the whole timeseries are used!
        return self._overvalue_yield

    @property
    def undervalue_yield(self) -> float:
        if self._undervalue_yield is None:
            self._undervalue_yield = list(0.01 * round(
                100 * self.annual_low_price_yields[
                    self.annual_low_price_yields > self.annual_low_price_yields.quantile(0.75)
                    ].mean(),
                1,
            ))[0]  # TODO: Modify to ensure extremes of the whole timeseries are used!
        return self._undervalue_yield

    @property
    def overvalue_prices(self) -> DataFrame:
        if self._overvalue_prices is None:
            self._overvalue_prices = pd.DataFrame(
                self.annual_dividends['Dividends'] / self.overvalue_yield,
            ).rename(columns={'Dividends': 'Overvalue Prices'})
        return self._overvalue_prices

    @property
    def undervalue_prices(self) -> DataFrame:
        if self._undervalue_prices is None:
            self._undervalue_prices = pd.DataFrame(
                self.annual_dividends['Dividends'] / self.undervalue_yield,
            ).rename(columns={'Dividends': 'Undervalue Prices'})
        return self._undervalue_prices

    @property
    def annual_trend_using_weekly_prices(self) -> DataFrame:
        if self._get_trend_by_year is None:
            years = []
            slope_values = []
            for year in self.weekly_prices.index.year.unique():
                weekly_price_per_year = self.weekly_prices[self.weekly_prices.index.year == year]
                time = mdates.date2num(weekly_price_per_year.index).reshape(-1, 1)
                model: LinearRegression = LinearRegression().fit(time, weekly_price_per_year.to_numpy())
                slope = model.coef_
                years.append(year)
                slope_values.append(slope)
            data = {'slope': slope_values, 'is_positive_trend': [value > 0 for value in slope_values]}
            self._get_trend_by_year = pd.DataFrame(data, index=years)
        return self._get_trend_by_year
