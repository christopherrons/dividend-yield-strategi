from app.blue_chip_filter import BlueChipFilter
from app.model.ticker_data import TickerData
from app.yahoo_finance_api_client import YahooFinanceApiClient


def main():
    ticker_data: TickerData = YahooFinanceApiClient.ticker_requests(
        exchanges=['NYSE', 'NASDAQ'],
        start_date=None,
        end_date=None,
    )

    blue_chip_filter: BlueChipFilter = BlueChipFilter()
    blue_chips: TickerData = blue_chip_filter.run_filter(ticker_data)

    print("Suggested Symbols:")
    for symbol, ticker_data_item in blue_chips.symbol_to_ticker_response.items():
        print(f"{symbol} - {ticker_data_item.get_basic_info()}")


if __name__ == '__main__':
    main()
