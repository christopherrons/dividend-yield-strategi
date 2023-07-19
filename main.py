from app.blue_chip_filter import BlueChipFilter
from app.model.ticker_data import TickerData
from app.utils.utils import Utils
from app.yahoo_finance_api_client import YahooFinanceApiClient


def main():
    uninterrupted_dividends_boundary: int = 20
    ticker_data: TickerData = YahooFinanceApiClient.ticker_requests(
        symbols=Utils.get_sp_tickers(),
        start_date=Utils.get_date_string_today_n_years_back(uninterrupted_dividends_boundary),
        end_date=Utils.get_date_string_yesterday(),
    )

    blue_chip_filter: BlueChipFilter = BlueChipFilter()
    result: TickerData = blue_chip_filter.run_filter(ticker_data)
    print("Suggested Symbols:")
    for symbol, ticker_data_item in result.symbol_to_ticker_response.items():
        print(f"{symbol} - {ticker_data_item.get_basic_info()}")


if __name__ == "__main__":
    main()
