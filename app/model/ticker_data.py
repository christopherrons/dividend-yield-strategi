from app.model.ticker_data_item import TickerDataItem
from typing import Dict


class TickerData:

    def __init__(self, exchanges: list, symbol_to_ticker_response: Dict[str, TickerDataItem]):
        self.exchanges = exchanges
        self.symbol_to_ticker_response = symbol_to_ticker_response
