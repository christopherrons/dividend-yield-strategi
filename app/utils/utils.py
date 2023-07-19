from datetime import datetime, date

import bs4 as bs
import requests
from dateutil.relativedelta import relativedelta


class Utils:
    @staticmethod
    def get_sp_tickers():
        resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        soup = bs.BeautifulSoup(resp.text, 'lxml')
        table = soup.find('table', {'class': 'wikitable sortable'})
        tickers = []
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text
            tickers.append(ticker)

        return [s.replace('\n', '') for s in tickers]

    @staticmethod
    def get_date_yesterday() -> date:
        return (datetime.now() + relativedelta(days=-1)).date()

    @staticmethod
    def get_date_today_n_years_back(historical_years: int) -> date:
        return (datetime.now() + relativedelta(years=-historical_years)).date()

    @staticmethod
    def get_date_string_yesterday() -> str:
        return Utils.get_date_yesterday().__str__()

    @staticmethod
    def get_date_string_today_n_years_back(historical_years: int) -> str:
        return Utils.get_date_today_n_years_back(historical_years).__str__()
