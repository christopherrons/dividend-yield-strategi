from app.blue_chip_filter import BlueChipFilter
from app.model.ticker_data import TickerData
from app.yahoo_finance_api_client import YahooFinanceApiClient
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    ticker_data: TickerData = YahooFinanceApiClient.ticker_requests(
        symbols=root.joinpath('symbols_nyse_nasdaq.csv'), # Path to CSV file containing columns 'symbol' and 'ipoDate'.
        # exchanges=['NYSE', 'NASDAQ'],
        start_date=None,
        end_date=None,
    )

    blue_chip_filter: BlueChipFilter = BlueChipFilter()
    blue_chips: TickerData = blue_chip_filter.run_filter(ticker_data)
    blue_chips.store_ticker_symbols(root)


if __name__ == '__main__':
    main()
