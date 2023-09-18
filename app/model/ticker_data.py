from app.model.ticker_data_item import TickerDataItem
from loguru import logger
from pathlib import Path
from typing import Dict
import pandas as pd


class TickerData:

    def __init__(self, symbol_to_ticker_response: Dict[str, TickerDataItem]):
        self.symbol_to_ticker_response = symbol_to_ticker_response

    def store_ticker_symbols(self, dst: Path) -> None:
        logger.info("Store Blue Chip ticker symbols.")
        df_tickers = pd.DataFrame(
            [[
                symbol,
                ticker_data_item.name,
                ticker_data_item.exchange,
                ticker_data_item.start_date,
            ] for idx, (symbol, ticker_data_item) in enumerate(self.symbol_to_ticker_response.items())
            ],
            columns=['symbol', 'name', 'exchange', 'ipoDate'],
        )
        df_tickers.to_csv(dst.joinpath('symbols_blue_chips.csv'), index=False)
