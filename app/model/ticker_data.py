from typing import Dict

from app.model.ticker_data_item import TickerDataItem


class TickerData:

    def __init__(self, start_date: str, end_date: str, symbol_to_ticker_response: Dict[str, TickerDataItem]):
        self.start_date = start_date
        self.end_date = end_date
        self.symbol_to_ticker_response = symbol_to_ticker_response
