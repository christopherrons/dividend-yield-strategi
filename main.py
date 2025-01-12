import datetime
from pathlib import Path
import pandas as pd
from loguru import logger

from app.blue_chip_filter import BlueChipFilter
from app.model.ticker_data import TickerData
from app.utils.utils import Utils
from app.value_profile import ValueProfile
from app.yahoo_finance_api_client import YahooFinanceApiClient


timestamp = datetime.datetime.now()
log_file_name = f'log/app_{timestamp:%Y-%m-%d_%H-%M-%S}.log'
logger.add(log_file_name, rotation='500 MB')


def main():
    blue_chips: TickerData = get_blue_chip_ticker_symbols()
    get_value_profiles(blue_chips)




def get_blue_chip_ticker_symbols() -> TickerData:
    root_path: Path = Path(__file__).resolve().parent
    if should_create_blue_chip_csv(root_path):
        ticker_data: TickerData = YahooFinanceApiClient.ticker_requests(
            # symbols=Utils.load_symbols_from_csv(root_path.joinpath('symbols_nyse_nasdaq.csv')), # Path to CSV file containing columns 'symbol' and 'ipoDate'.
            # symbols=Utils.load_symbols_from_api(['NYSE', 'NASDAQ']), # Download ticker symbols of all currently listed companies at the specified exchange(s).
            # symbols=Utils.load_symbols_from_api(['NYSE']), # Download ticker symbols of all currently listed companies at the specified exchange(s).
            symbols = pd.DataFrame([
                    # ['KO', 'Coca Cola','NYSE',''],
                    # ['APD', 'Air Products','NYSE',''],
                    # ['MCD', 'McDonalds','',''],
                    # ['MMM', '3M','',''], 
                    # ['ABBV', 'AbbVie','',''],
                    # ['CAT', 'Caterpillar','',''],
                    # ['HD', 'Home Depot','',''],
                    # ['HSY', 'Hershey Company','',''],
                    # ['MS', 'Morgan Stanley','',''],
                    # ['KMB', 'Kimberly-Clark','',''],
                    # ['UNH', 'UnitedHealth','',''],
                    # ['WABC', 'Westamerica Bancorp','',''],
                    # ['AXP', 'American Express','',''],
                    # ['PG', 'Procter & Gamble','',''],
                    # ['K', 'Kellanova','',''],
                    # ['TXN', 'Texas instruments','',''],
                    # ['ADM', 'Archer Daniels Midland','',''],
                    # ['CMA', 'Comerica','',''],
                    # ['DIS', 'Disney','',''],
                    ['JNJ', 'Johnson & Johnson','',''],
                    
                    ], columns=['symbol', 'name','exchange','ipoDate']),  # manual dataframe
            start_date='2014-01-01', # None
            end_date='2024-12-30',
        )
        
        blue_chip_filter: BlueChipFilter = BlueChipFilter()
        blue_chips: TickerData = blue_chip_filter.run_filter(ticker_data)
        # blue_chips.store_ticker_symbols(root_path.joinpath('result', f'symbols_blue_chips_{Utils.get_date_today()}.csv'))
        return blue_chips
    else:
        return YahooFinanceApiClient.ticker_requests(
            symbols=Utils.load_symbols_from_csv(root_path.joinpath('result', f'symbols_blue_chips_{Utils.get_date_today()}.csv')),
        )


def get_value_profiles(blue_chips: TickerData):
    root_path: Path = Path(__file__).resolve().parent
    ValueProfile.visualize_profiles(blue_chips, root_path.joinpath('result'))


def should_create_blue_chip_csv(root_path: Path) -> bool:
    return not root_path.joinpath('result', f'symbols_blue_chips_{Utils.get_date_today()}.csv').exists()


if __name__ == '__main__':
    main()
