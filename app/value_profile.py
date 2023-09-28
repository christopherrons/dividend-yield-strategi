from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from loguru import logger

from app.model.ticker_data import TickerData
from app.utils.utils import Utils


class ValueProfile:

    @staticmethod
    def visualize_profiles(blue_chips: TickerData, dst: Path):
        for symbol, ticker_data_item in blue_chips.symbol_to_ticker_response.items():
            logger.info(f'Creating the value profile for symbol: {symbol}')
            fig, axes = plt.subplots(3, 1, figsize=[13.333, 7.5])
            fig.add_subplot(111, frameon=False)
            fig.suptitle(f'Symbol: {symbol}', fontsize=10, fontweight='bold')
            plt.tick_params(labelcolor='none', top=False, bottom=False, left=False, right=False)

            axes[0].set_yscale('log')
            axes = np.append(axes, axes[2].twinx())
            axes[2].set_yscale('log')
            axes[3].invert_yaxis()

            index = pd.date_range(
                start=max(ticker_data_item.closing_prices.index.min(), ticker_data_item.annual_dividends.index.min()),
                end=min(ticker_data_item.closing_prices.index.max(), ticker_data_item.annual_dividends.index.max()),
                freq='D',
            )
            closing_prices = ticker_data_item.closing_prices.reindex(index)
            annual_high_price_yields = ticker_data_item.annual_high_price_yields.reindex(index).interpolate().reindex(index)
            annual_low_price_yields = ticker_data_item.annual_low_price_yields.reindex(index).interpolate().reindex(index)
            annual_dividends = ticker_data_item.annual_dividends.reindex(index).fillna(method='ffill')
            selected_high_price_yields = ticker_data_item.annual_high_price_yields[
                ticker_data_item.annual_high_price_yields < ticker_data_item.annual_high_price_yields.quantile(0.25)].dropna()
            selected_low_price_yields = ticker_data_item.annual_low_price_yields[
                ticker_data_item.annual_low_price_yields > ticker_data_item.annual_low_price_yields.quantile(0.75)].dropna()
            overvalue_yield = 100 * ticker_data_item.overvalue_yield
            undervalue_yield = 100 * ticker_data_item.undervalue_yield
            overvalue_prices = ticker_data_item.overvalue_prices.reindex(index).fillna(method='ffill')
            undervalue_prices = ticker_data_item.undervalue_prices.reindex(index).fillna(method='ffill')

            l1, = axes[0].plot(index, closing_prices, color='k', lw=0.5, label='Closing Prices')
            l2, = axes[0].plot(index, overvalue_prices, color='royalblue', label=f'Overvalue Yield - {overvalue_yield:.2f}%')
            l3, = axes[0].plot(index, undervalue_prices, color='orange', label=f'Undervalue Yield - {undervalue_yield:.2f}%')
            l4, = axes[1].plot(index, annual_dividends, color='k', lw=0.5, label='Annual Dividends')
            l5, = axes[2].plot(index, closing_prices, color='k', lw=0.5, label='Closing Prices')
            l6, = axes[3].plot(index, annual_high_price_yields, color='royalblue', zorder=1, label='Highest Price Yields')
            l7 = axes[3].scatter(index, selected_high_price_yields.reindex(index), color='r', edgecolors='royalblue', zorder=2,
                                 label='Selected Highest Price Yields')
            l8, = axes[3].plot(index, annual_low_price_yields, color='orange', zorder=1, label='Lowest Price Yields')
            l9 = axes[3].scatter(index, selected_low_price_yields.reindex(index), color='r', edgecolors='orange', zorder=2,
                                 label='Selected Lowest Price Yields')

            for date, high_price_yield in selected_high_price_yields.iterrows():
                axes[2].axvline(date, color='grey', lw=0.5)

            for date, low_price_yield in selected_low_price_yields.iterrows():
                axes[2].axvline(date, color='grey', lw=0.5)

            axes[0].set_ylabel('Daily Closing Prices [USD]')
            axes[1].set_ylabel('Annual Dividends [USD]')
            axes[2].set_ylabel('Daily Closing Prices [USD]')
            axes[3].set_ylabel('Dividend Yield [-]')

            axes[0].legend(handles=[l1, l2, l3], loc='lower center', bbox_to_anchor=(0.5, -0.35), ncols=3, fontsize=8, frameon=False)
            axes[1].legend(handles=[l4], loc='lower center', bbox_to_anchor=(0.5, -0.35), fontsize=8, ncols=1, frameon=False)
            axes[2].legend(handles=[l5, l6, l8, l7, l9], loc='lower center', bbox_to_anchor=(0.5, -0.35), ncols=5, fontsize=8, frameon=False)

            plt.tight_layout()
            fig.align_ylabels()
            plt.savefig(dst.joinpath(f'{symbol}_value_profile_{Utils.get_date_today()}.svg'))
            plt.close()
