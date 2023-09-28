import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import csv
import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from loguru import logger
from pandas import DataFrame


class Utils:

    @staticmethod
    def load_symbols_from_csv(symbol_file_path: Path) -> DataFrame:
        if not symbol_file_path:
            logger.error(f"File does not exist: {symbol_file_path}.")
            sys.exit()
        logger.info(f"Reading ticker symbols from the file: {symbol_file_path}.")
        return pd.read_csv(symbol_file_path, na_values=['null'], keep_default_na=False)

    @staticmethod
    def load_symbols_from_api(exchanges: [str]) -> DataFrame:
        return pd.concat([Utils.get_tickers(exchange) for exchange in exchanges]).reset_index(drop=True)

    @staticmethod
    def get_tickers(exchange: str):
        logger.info(f"Gathering ticker symbols for exchange: {exchange}")
        api_key = 'JSEKU0PHS270VWS0'  # Free API key from https://www.alphavantage.co/support/#api-key (5 request per minute, 100 per day).
        url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'
        with requests.Session() as s:
            download = s.get(url)
            decoded_content = download.content.decode('utf-8')
            cr = list(csv.reader(decoded_content.splitlines(), delimiter=','))
            all_tickers = DataFrame(cr[1:], columns=cr[0])
            return all_tickers[(all_tickers['exchange'] == exchange) & (all_tickers['assetType'] == 'Stock')]

    @staticmethod
    def get_date_today() -> date:
        return datetime.now().date()

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
    def get_date_string_today() -> str:
        return Utils.get_date_today().__str__()

    @staticmethod
    def get_date_string_yesterday() -> str:
        return Utils.get_date_yesterday().__str__()

    @staticmethod
    def get_date_string_n_years_back(historical_years: int, reference_date: str = None) -> str:
        return Utils.get_date_n_years_back(historical_years, reference_date).__str__()

    @staticmethod
    def get_date_string_first_trade(epoch: int) -> str:
        return Utils.get_date_first_trade(epoch).__str__()
