import bs4 as bs
import requests

from app.blue_chip_filter import BlueChipFilter
from app.model.ticker_data import TickerData
from app.utils.utils import Utils
from app.yahoo_finance_api_client import YahooFinanceApiClient


def main():
    uninterrupted_dividends_boundary: int = 20
    ticker_data: TickerData = YahooFinanceApiClient.ticker_requests(
        symbols=get_sp_tickers(),
        start_date=Utils.get_date_string_today_n_years_back(uninterrupted_dividends_boundary),
        end_date=Utils.get_date_string_yesterday(),
    )

    blue_chip_filter: BlueChipFilter = BlueChipFilter()
    result: TickerData = blue_chip_filter.run_filter(ticker_data)
    print("Suggested Symbols:")
    for symbol, ticker_data_item in result.symbol_to_ticker_response.items():
        print(f"{symbol}")


def get_sp_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)

    return [s.replace('\n', '') for s in tickers]


if __name__ == "__main__":
    main()
