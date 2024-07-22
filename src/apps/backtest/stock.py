'''
Class to model stock
'''


import os
import pandas as pd
import numpy as np

import datetime
import preference
import talib as ta
import common as cm
from loader import DataLoader

class Stock(object):

    '''
    Stock class for getting financial pricing as well as fundamental data. 
    It uses pandas DataFrame

    '''

    def __init__(self, loader, ticker):
        self.loader = loader
        self.ticker = ticker
        self.ohlcv_df = None
        

    def get_daily_hist_price(self, start_date = None, end_date = None):
        self.ohlcv_df = self.loader.get_daily_hist_price(self.ticker, start_date, end_date)
        self._calc_daily_basic()
        return(self)
    
    def _calc_daily_basic(self):
        '''
        '''
        for period in [10, 20, 50, 200]:
            self.ohlcv_df[f"SMA_{period}"] = ta.SMA(self.ohlcv_df[cm.DataField.close], timeperiod = period)

        c = self.ohlcv_df[cm.DataField.close]
        self.ohlcv_df['daily_returns'] = (c - c.shift(1))/c.shift(1)
        self.ohlcv_df['weekly_returns'] = (c - c.shift(5))/c.shift(1)
        self.ohlcv_df['monthly_returns'] = (c - c.shift(20))/c.shift(1)                

        
    def grab_fields(self, fields):
        '''
        grab a subset of fields and add the ticker
        '''
        output_df = pd.DataFrame(index = self.ohlcv_df.index)
        for fld in fields:
            output_df[f"{self.ticker}_{fld}"] = self.ohlcv_df[fld]
        return(output_df)
                    
    


def _test1():

    parser = preference.get_default_parser()
    args = parser.parse_args()

    pref = preference.Preference(cli_args = args)

    if pref.data_dir is not None:
        data_dir = pref.data_dir
    else:
        data_dir = os.path.join(pref.data_root_dir, "train")
        
    print(f"Loading from data dir: {data_dir}")
    
    loader = DataLoader(pref, data_dir = data_dir)

    start_date = datetime.date(2010, 1, 1)
    end_date = datetime.date(2022, 1, 1)
    
    tickers = ['AWO', 'MOD', 'OCT', 'SPY']
    for ticker in tickers:
        stock = Stock(loader, ticker)
        stock.get_daily_hist_price(start_date, end_date)
        print(ticker)
        
        print(stock.ohlcv_df.tail())

    fields = [cm.DataField.open, cm.DataField.close, cm.DataField.volume]
    print(stock.grab_fields(fields))
    
def _test():
    _test1()
    
if __name__ == '__main__':
    _test()
    
