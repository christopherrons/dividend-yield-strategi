from app.blue_chip_filter import BlueChipFilter
from app.model.ticker_data import TickerData
from app.utils.utils import Utils
from app.value_profile import ValueProfile
from app.yahoo_finance_api_client import YahooFinanceApiClient
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent

    # Get Blue Chips ticker symbols.
    if not root.joinpath(f'symbols_blue_chips_{Utils.get_date_today()}.csv').exists():
        ticker_data: TickerData = YahooFinanceApiClient.ticker_requests(
            symbols=root.joinpath('symbols_nyse_nasdaq.csv'), # Path to CSV file containing columns 'symbol' and 'ipoDate'.
            # exchanges=['NYSE', 'NASDAQ'], # Download ticker symbols of all currently listed companies at the specified exchange(s).
            start_date=None,
            end_date=None,
        )
        blue_chip_filter: BlueChipFilter = BlueChipFilter()
        blue_chips: TickerData = blue_chip_filter.run_filter(ticker_data)
        blue_chips.store_ticker_symbols(root.joinpath(f'symbols_blue_chips_{Utils.get_date_today()}.csv'))
    else:
        blue_chips: TickerData = YahooFinanceApiClient.ticker_requests(
            symbols=root.joinpath(f'symbols_blue_chips_{Utils.get_date_today()}.csv'),
        )
    blue_chips.download_price_data()

    # Generate Value Profiles.
    value_profile: ValueProfile = ValueProfile()

if __name__ == '__main__':
    main()
