from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pandas import DataFrame
import csv
import requests

class Utils:
    @staticmethod
    def get_tickers(exchange: str):
        api_key = 'JSEKU0PHS270VWS0' # Free API key from https://www.alphavantage.co/support/#api-key (5 request per minute, 100 per day).
        url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'
        with requests.Session() as s:
            download = s.get(url)
            decoded_content = download.content.decode('utf-8')
            cr = list(csv.reader(decoded_content.splitlines(), delimiter=','))
            all_tickers = DataFrame(cr[1:], columns=cr[0])
            return all_tickers[(all_tickers['exchange'] == exchange) & (all_tickers['assetType'] == 'Stock')]

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
