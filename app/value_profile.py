from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from loguru import logger

from app.model.ticker_data import TickerData
from app.utils.utils import Utils


def extrapolate_dividends(ticker_data_item):
    df = ticker_data_item.annual_dividends.copy()
    df['raw_data'] = 1
    # Calculate the average annual growth rate (AAGR)
    df['Growth'] = df['Dividends'].pct_change()  # Calculate percentage change
    predicted_dividend = df['Dividends'].iloc[-1] * (1 + df['Growth'].mean())

    new_date = df.index[-1] + pd.DateOffset(years=1)

    # Add the new row for the next year
    new_row = pd.DataFrame({"Dividends": [predicted_dividend],'raw_data':[0]}, index=[new_date])
    df = pd.concat([df, new_row])
    df = df.drop(columns=['Growth'])
    return df   

def set_to_january_first(date_index):
    return date_index.to_period('Y').to_timestamp('01-01')

class ValueProfile:
    


    @staticmethod
    def visualize_profiles(blue_chips: TickerData, dst: Path):
        for symbol, ticker_data_item in blue_chips.symbol_to_ticker_response.items():
            name = ticker_data_item.name
            
            
            # PLOT 1 -  THREE WINDOWS (DEBUG PROFILES)
            logger.info(f'Creating the value profile for symbol: {symbol}')
            fig, axes = plt.subplots(3, 1, figsize=[13.333, 7.5])
            fig.add_subplot(111, frameon=False)
            fig.suptitle(f'Symbol: {symbol}  ({name})', fontsize=10, fontweight='bold')
            plt.tick_params(labelcolor='none', top=False, bottom=False, left=False, right=False)

            axes[0].set_yscale('log')
            axes = np.append(axes, axes[2].twinx())
            axes[2].set_yscale('log')
            axes[3].invert_yaxis()

            # TODO: in the IQ trends reports the end date is not limited by the annual dividends, but extrapolated in the future. 
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
            
            
            #%%
            # PLOT 2 - SINGLE WINDOW + DETAILS
            # all_items = blue_chips.symbol_to_ticker_response
            # ticker_data_item = all_items['KO']
            
            
            
            fig = plt.figure(figsize=(13.333, 10))
            gs = fig.add_gridspec(7, 1)  # Total rows = 7 (6 for line plot, 1 for bar plot)

            # Line plot (takes 6/7 of the height)
            ax = fig.add_subplot(gs[:4, 0])
            
            
            start_idx = ticker_data_item.closing_prices.index.min()
            index = pd.date_range(
                start=start_idx-pd.DateOffset(years =1),
                end=ticker_data_item.closing_prices.index.max() + pd.DateOffset(years =1),
                freq='D',
            )
            years = index.year.unique()
            
            
            # variables
            closing_prices = ticker_data_item.closing_prices.reindex(index) # double from above
            MA200          = closing_prices['Close'].rolling(window=200, min_periods=1).mean()
            MA50           = closing_prices['Close'].rolling(window=50, min_periods=1).mean()
            overvalue_yield = 100 * ticker_data_item.overvalue_yield
            undervalue_yield = 100 * ticker_data_item.undervalue_yield
        
            df_dividends = extrapolate_dividends(ticker_data_item)
            df_dividends['overvalue_prices']  = df_dividends['Dividends'] / ticker_data_item.overvalue_yield
            df_dividends['undervalue_prices'] = df_dividends['Dividends'] / ticker_data_item.undervalue_yield
            
            overvalue_prices  = df_dividends[['overvalue_prices','raw_data']].reindex(index).ffill()
            undervalue_prices = df_dividends[['undervalue_prices','raw_data']].reindex(index).ffill()
            
            idx_historic_data = overvalue_prices['raw_data'] ==1
            idx_extra_data    = overvalue_prices['raw_data'] ==0
            
            # plotting
            l1, = ax.plot(index, closing_prices, color='k', lw=0.5, label='Closing Prices')
            l2, = ax.plot(index[idx_historic_data], overvalue_prices['overvalue_prices'].loc[overvalue_prices['raw_data']==1],    color='tomato', label=f'Overvalue Yield: {overvalue_yield:.2f}%')
            l3, = ax.plot(index[idx_historic_data], undervalue_prices['undervalue_prices'].loc[overvalue_prices['raw_data']==1],  color='forestgreen', label=f'Undervalue Yield: {undervalue_yield:.2f}%')
            # extra polated
            l4, = ax.plot(index[idx_extra_data], overvalue_prices['overvalue_prices'].loc[overvalue_prices['raw_data']==0],    color='tomato', ls = '--',  label=f'Overvalue Yield: {overvalue_yield:.2f}%')
            l5, = ax.plot(index[idx_extra_data], undervalue_prices['undervalue_prices'].loc[overvalue_prices['raw_data']==0],  color='forestgreen', ls = '--',    label=f'Undervalue Yield: {undervalue_yield:.2f}%')
            
            l6, = ax.plot(index, MA200,color='darkgrey', lw=1.5, label='200 days MA')
            l7, = ax.plot(index, MA50,color='orange', lw=1.5, label='50 days MA')
            
            legend1 = ax.legend(handles=[l1, l2, l3], loc='lower center', bbox_to_anchor=(0.5, -0.15), ncols=3, fontsize=12, frameon=False)
            legend2 = ax.legend(handles=[l6, l7], loc='lower center', bbox_to_anchor=(0.5, -0.2), ncols=2, fontsize=12, frameon=False)
               
            ax.add_artist(legend1)
            
            
            # text
            ticker_data_item.stats = ticker_data_item.ticker.get_info()
            name                      = ticker_data_item.name
            symbol                    = ticker_data_item.symbol
            nr_shares                 = ticker_data_item.stats['sharesOutstanding']
            perc_held_by_institutions = ticker_data_item.stats['heldPercentInstitutions']*100
            pb                        = ticker_data_item.stats['priceToBook']
            pe_trailing               = ticker_data_item.stats['trailingPE']
            pe_forward                = ticker_data_item.stats['forwardPE']
            beta                      = ticker_data_item.stats['beta']
            if 'debtToEquity' in ticker_data_item.stats.keys():
                debth_to_equity           = ticker_data_item.stats['debtToEquity']
            else:
                debth_to_equity       = np.nan
            roe                       = ticker_data_item.stats['returnOnEquity']*100
            if 'grossMargins' in ticker_data_item.stats.keys():
                gross_margin              = ticker_data_item.stats['grossMargins']*100
            else:
                gross_margin = np.nan  
            
            if 'profitMargins' in ticker_data_item.stats.keys():
                profit_margin             = ticker_data_item.stats['profitMargins']*100
            else:
                profit_margin  = np.nan
            

            today              = pd.Timestamp.now(tz=overvalue_prices.index.tz).normalize()
            nearest_idx        = overvalue_prices.index.get_indexer([today], method='nearest')
            nearest_overvalue  = overvalue_prices['overvalue_prices'].iloc[nearest_idx].item()
            nearest_undervalue = undervalue_prices['undervalue_prices'].iloc[nearest_idx].item() 
            current_price      = ticker_data_item.stats['currentPrice']
            current_yield      = ticker_data_item.stats['dividendYield']*100
            
            price_up_potential   = (nearest_overvalue - current_price) / current_price*100
            price_down_potential = (nearest_undervalue - current_price) / current_price*100
            
            # text stats            
            ax.text(0.02,0.9, f'Nr of shares outstanding: {nr_shares}', transform = ax.transAxes)
            ax.text(0.02,0.87, f'Inst own: {perc_held_by_institutions:.1f} %', transform = ax.transAxes)
            
            ax.text(0.02,0.8, f'Price to Book: {pb:.1f}', transform = ax.transAxes)
            ax.text(0.02,0.77,f'DebtToEquity: {debth_to_equity:.2f}', transform = ax.transAxes)
            ax.text(0.02,0.74,f'Beta: {beta:.2f}', transform = ax.transAxes)
            
            ax.text(0.02,0.67, f'PE(Trailing): {pe_trailing:.1f}', transform = ax.transAxes)
            ax.text(0.02,0.64, f'PE(Forward): {pe_forward:.1f}', transform = ax.transAxes)
            
            ax.text(0.02,0.57, f'ROAvgEquity: {roe:.1f} %', transform = ax.transAxes)                        
            ax.text(0.02,0.54, f'Gross Margin: {gross_margin:.1f} %', transform = ax.transAxes)
            ax.text(0.02,0.51, f'Net Profit Margin: {profit_margin:.1f} %', transform = ax.transAxes)
            
            # text prices
            x_left = 0.65
            y_pos  = 0.13
            x_price = x_left + 0.15
            x_yield = x_price +0.15
            
            ax.text(x_left,y_pos,'CURRENT', transform = ax.transAxes)
            ax.text(x_left,y_pos-0.05,'OVERVALUE', transform = ax.transAxes)
            ax.text(x_left,y_pos-0.1,'UNDERVALUE', transform = ax.transAxes)
            
            ax.text(x_price,y_pos+0.05,'PRICE', transform = ax.transAxes, ha = 'center')
            ax.text(x_yield,y_pos+0.05,'YIELD', transform = ax.transAxes, ha = 'center')
    
            ax.text(x_price,y_pos, f'{current_price:.1f}', transform = ax.transAxes, ha ='center' )
            ax.text(x_price,y_pos-0.05, f'{nearest_overvalue:.1f}', transform = ax.transAxes, ha ='center' )
            ax.text(x_price,y_pos-0.1, f'{nearest_undervalue:.1f}', transform = ax.transAxes, ha ='center' )

            ax.text(x_price+0.06,y_pos-0.05, f'({price_up_potential:.1f} %)', transform = ax.transAxes, ha ='center' )
            ax.text(x_price+0.06,y_pos-0.1, f'({price_down_potential:.1f} %)', transform = ax.transAxes, ha ='center' )    
            
    
            ax.text(x_yield,y_pos, f'{current_yield:.1f} %', transform = ax.transAxes, ha ='center' )
            ax.text(x_yield,y_pos-0.05, f'{overvalue_yield:.1f} %', transform = ax.transAxes, ha ='center' )
            ax.text(x_yield,y_pos-0.1, f'{undervalue_yield:.1f} %', transform = ax.transAxes, ha ='center' )
            ax.text(0.9, 1.01,today.strftime('%Y-%m-%d'), transform = ax.transAxes, ha = 'center')

            # layout
            # Set xticks and xticklabels with years
            xticks = pd.date_range(f'{years.min()}-01-01', f'{years.max()}-01-01', freq='YS')
            ax.set_xticks(xticks)
            ax.set_xticklabels(years, rotation=0)
            ax.set_xlim(start_idx-pd.DateOffset(days=2),)
            ytick_positions = np.linspace(closing_prices.min().item(), closing_prices.max().item(), num = len(xticks))
            yticks_rounded  = np.round(ytick_positions / 10) * 10
            ax.set_yticks(yticks_rounded)
            ax.tick_params(axis='both', direction='in')
            
            ax.grid(ls = '--', lw = 0.4)
            ax.set_facecolor('ghostwhite')
            
            currency = ticker_data_item.stats['currency']
            ax.set_ylabel(f'Stock price [{currency}]')
            ax.set_title(name + f'  ( {symbol} )', fontweight = 'bold', fontsize = 16) 
            
            
            # Bar plot (takes 1/7 of the height, aligned x-axis)
            ax2 = fig.add_subplot(gs[5, 0], sharex=ax)  # Use `sharex` to align the x-axis
            bar_positions1 = ticker_data_item.annual_dividends.index
            bar_data1      = ticker_data_item.annual_dividends.Dividends.values
            
            eps            = ticker_data_item.eps.dropna()
            bar_positions2 = bar_positions1[bar_positions1.year.isin(eps.index.year)]
            bar_data2      = eps.values
            
            ax2.bar(bar_positions1+ pd.Timedelta(days=50), bar_data1, width = 100, color='orange', label='Annual Dividends', alpha=0.7)
            ax2.bar(bar_positions2+ pd.Timedelta(days =170), bar_data2, width=100, color='green', label='Earnings per Share (4 years available)', alpha=0.7)
            
            # Add text for bar values
            offset1 = np.nanmean(bar_data1)*0.1
            offset2 = np.nanmean(bar_data2)*0.1
            for i, value in enumerate(bar_data1):
                ax2.text(bar_positions1[i] + pd.Timedelta(days=50), value+offset1, f'{value:.1f}', fontsize=10, ha='center')
            for i, value in enumerate(bar_data2):
                ax2.text(bar_positions2[i] + pd.Timedelta(days=170), value+offset2, f'{value:.1f}', fontsize=10, ha='center')

            ax2.set_ylabel("USD")
            ax2.grid(alpha=0.5)
            ax2.spines[['right', 'top']].set_visible(False)
            
            ax2.legend(loc='lower center', bbox_to_anchor=(0.5, -0.7), ncols=3, fontsize=12, frameon=False)
            
            fig.align_labels()
            plt.savefig(dst.joinpath(f'{symbol}_value_profile_stats_{Utils.get_date_today()}.svg'))
            plt.close()
            
            
