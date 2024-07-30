'''
Classes for Buy and Hold
'''

import enum
import datetime
import pandas as pd

import random

import common as cm
from strategy import Strategy
from datamatrix import DataMatrix, DataMatrixLoader

class RandomStrategy(Strategy):

    ''' Simple Strategy based on Random
    1. Entry rule: long when Random < 30, short when Random > 70
    2. Exit rule: Close in a week or earn a target gain percentage or sell at a max loss percentage
    3. Capital Allocation: 1% of the capital

    '''
    def __init__(self, pref, input_datamatrix: DataMatrix, initial_capital: float, price_choice = cm.DataField.close, 
                 lower_bound = 20, upper_bound = 80, target_gain_percentage = 1.0, max_loss_percentage = -1.0, risk_allocation_percentage = 10):
        super().__init__(pref, 'RandomStrategy', input_datamatrix, initial_capital, price_choice)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.target_gain_percentage = target_gain_percentage
        self.max_loss_percentage = max_loss_percentage
        self.risk_allocation_percentage = risk_allocation_percentage

        # set random seed
        if pref.random_seed is not None:
            random.sedd(pref.random_seed)

    def validate(self):
        '''
        validate if the input_dm has everything the strategy needs
        '''
        columns = self.input_dm.columns
        for ticker in self.universe:
            col = f"{ticker}_{self.price_choice}"
            if col not in columns:
                raise Exception(f"Cannot found {col} for {ticker}")

            # check if Random is in the input datamatrix
            col = f"{ticker}_{self.price_choice}"
            if col not in columns:
                raise Exception(f"Cannot found {col} for {ticker}")
            

    def run_model(self, model = None):
        '''
        No external prediction model needed
        return a trade signal and its corresponding shares
        '''
        
        # when RSI is above 80, trade signal is sell, when RSI is below 20, trade signal is buy
        nrow, ncol   = self.pricing_matrix.shape
        
        taction = self.pricing_matrix.copy()
        tsignal = self.pricing_matrix.copy()
        # shares on trade execution
        shares = self.pricing_matrix.copy()

        # existing shares with sign 
        current_shares_with_sign = self.pricing_matrix.copy()
        dollar_exposure = self.initial_capital * self.risk_allocation_percentage/100

        taction = taction.applymap(lambda x: cm.TradeAction.NONE.value)
        tsignal *= 0
        shares  *= 0
        current_shares_with_sign *= 0
        
        # remember the price and the date index when a trade was put on by ticker
        entry_day_index = {}
        entry_price = {}
        
        for j in range(ncol):
            ticker = self.pricing_matrix.columns[j]
            for i in range(1, nrow):
                
                current_price = self.pricing_matrix.iloc[i, j]
                # propagate the previous current_shares to the current period
                current_shares_with_sign.iloc[i, j] = current_shares_with_sign.iloc[i-1, j]

                rnd = random.random()
                
                if self.pref.verbose:
                    print(i, j, entry_price, entry_day_index, rnd)
                    
                # a position exists already, check if one can exit the current position
                if current_shares_with_sign.iloc[i-1, j] != 0:
                    # randomly decide whether to close it or not
                    if rnd > 0.8 or rnd < 0.2:
                        TBD

                
                # go long if random > 0.8
                elif rnd > 0.8 and current_shares_with_sign.iloc[i-1, j] == 0:
                    
                    tsignal.iloc[i, j] = 1
                    taction.iloc[i, j] = cm.TradeAction.BUY.value
                    shares.iloc[i, j] = int(dollar_exposure/current_price)
                    current_shares_with_sign.iloc[i, j] = shares.iloc[i, j]
                    
                    entry_day_index[ticker] = i
                    entry_price[ticker] = self.pricing_matrix.iloc[i, j]
                    
                elif rnd < 0.2 and current_shares_with_sign.iloc[i-1, j] == 0:
                    
                    tsignal.iloc[i, j] = -1
                    taction.iloc[i, j] = cm.TradeAction.SELL.value
                    shares.iloc[i, j] = int(dollar_exposure/current_price)
                    current_shares_with_sign.iloc[i, j] = -1* shares.iloc[i, j] 
                    
                    entry_day_index[ticker] = i
                    entry_price[ticker] = self.pricing_matrix.iloc[i, j]

                else:
                    # no trade (new or closing trades), do nothing except copying previous current shares
                    pass
                
        return(tsignal, taction, shares)
    
        

def _test1():

    from preference import Preference

    pref = Preference()
    pref.random_seed = 1001
    
    # pick some random name
#    universe = ['AWO', 'BDJ', 'BDTC']
    universe = ['AWO', 'BDJ']
    start_date = datetime.date(2013, 1, 1)
    end_date = datetime.date(2023, 1, 1)

    name = 'test'
    loader = DataMatrixLoader(pref, name, universe, start_date, end_date)
    dm = loader.get_daily_datamatrix()

    RSI = RSIStrategy(pref, dm, cm.OneMillion, target_gain_percentage = 1.5, max_loss_percentage = -0.5)
    RSI.validate()
    tradesignal, tradeaction, shares = RSI.run_model()

    #print(tradeaction.head())
    #print(shares)
    
    RSI.run_strategy()
    print(RSI.performance)

    print(f"Saving output to {pref.test_output_dir}")
    RSI.save_to_csv(pref.test_output_dir)
    
def _test():
    _test1()


if __name__ == "__main__":
    _test()