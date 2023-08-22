from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import bs4 as bs
import requests

class Utils:
    @staticmethod
    def get_tickers(index: str):
        if index == 'S&P500':
            resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            idx_table = 0
            idx_column = 0
        if index == 'Nasdaq-100':
            resp = requests.get('https://en.wikipedia.org/wiki/Nasdaq-100')
            idx_table = 2
            idx_column = 1

        soup = bs.BeautifulSoup(resp.text, 'lxml')
        table = soup.findAll('table', {'class': 'wikitable sortable'})[idx_table]
        tickers = []
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[idx_column].text
            tickers.append(ticker)

        return [s.replace('\n', '') for s in tickers]

    @staticmethod
    def get_date_yesterday() -> date:
        return (datetime.now() + relativedelta(days=-1)).date()

    @staticmethod
    def get_date_n_years_back(historical_years: int, reference_date: str) -> date:
        return (datetime.strptime(reference_date, '%Y-%m-%d') + relativedelta(years=-historical_years)).date()

    @staticmethod
    def get_date_first_trade(epoch: int) -> date:
        return (datetime(1970, 1, 1) + timedelta(seconds=epoch)).date()

    @staticmethod
    def get_date_string_yesterday() -> str:
        return Utils.get_date_yesterday().__str__()

    @staticmethod
    def get_date_string_n_years_back(historical_years: int, reference_date: str = None) -> str:
        return Utils.get_date_n_years_back(historical_years, reference_date).__str__()

    @staticmethod
    def get_date_string_first_trade(epoch: int) -> str:
        return Utils.get_date_first_trade(epoch).__str__()
