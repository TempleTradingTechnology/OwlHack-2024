'''
Class to model a strategy
'''

import pandas as pd
import common as cm
from datamatrix import DataMatrix

class Strategy(object):

    '''
    Strategy uses DataMatrix as both the input as well as the output
    1. The output is a DataMatrix with columns as the trade signal for each ticker
         positive shares means buy, negative shares means sell, 0 means hold
    2. Each strategy requires an input DataMatrix expected by the strategy
    3. Strategy can be rules based such as buy when SMA_10 cross above SMA_20
       or it has a internal model that makes a certain forecast and the strategy will make its recommendation
       based on the model output. It works with 3 datamtrix
     
       a. input_datamatrix with everything needed for generating a trade signal. 
       b. trade signal datamatrix which is the output of the strategy, long or short
       c. trade action datamatrix which buy to open, buy to close or sell to open or sell to close
       d. shares_datamatrix which is how many shares for each trade, it is always positive

       From the two output matrix, one can generate the following datamatrix
       d. current holding
       e. realized PandL
       f. unrealized PandL

    4. On each period, a strategy should maintained the following quantities in a dataframe
       a. current_cash
       b. total realized PandL
       c. total unrealized PandL
       
    '''

    def __init__(self, name, input_datamatrix: DataMatrix, initial_capital: float, price_choice = cm.DataField.close,
                 slippage = 0.0, risk_free_rate = 0.04):
        self.name = name
        self.input_dm = input_datamatrix
        self.universe = self.input_dm.universe
        self.initial_capital = initial_capital
        self.price_choice = price_choice
        self.slippage = slippage
        self.risk_free_rate = risk_free_rate

        # set up property based on the input datamatrix
        self.num_period = self.input_dm.shape[0]
        # days between periods
        self.timeframe = self.input_dm.timeframe
        self.pnl_column = f"{self.timeframe.value} pnl"

        if self.timeframe == cm.TimeFrame.DAILY:
            self.days_between_periods = 1
        elif self.timeframe == cm.WEEKLY:
            self.days_between_periods = 7
        elif self.timeframe == cm.MONTHLY:
            self.days_between_periods = 30
        else:
            raise Exception(f"{self.timeframe} timeframe is currently not supported")

        
        # state variables of the strategy
        self.cash = pd.Series(index = input_datamatrix.index)
        self.equity = pd.Series(index = input_datamatrix.index)
        

        # output of the strategy
        self.pnl = pd.DataFrame(index = input_datamatrix.index)
        self.performance = {'Cumulative Returns': -999,
                            'Maximum Drawdown': -999,
                            'Sharpe Ratio': -999}
        
        
    def validate(self, input_datamatrix):
        '''
        validate to see if it has everything first
        '''
        pass


    def run_model(self, model):
        '''
        Run any model underlying the strategy, generate a trading signal, a trading action and the shares datamatrix
        Trading signal has either long (1), sell (-1) or hold (0)
        Shares indicate how many shares to buy or sell
        '''
        pass
    
        
    def run_strategy(self):
        '''
        Call the run_model, then run the strategy.
        Calculate the state of the strategy period by period.
        '''
        self.tsignal, self.taction, self.shares = self.run_model()

        self.current_holding = (self.shares * self.tsignal).cumsum()
        self.equity = (self.current_holding * self.pricing_matrix).sum(axis = 1)
        
        nrow, ncol = self.pricing_matrix.shape
        cash = self.initial_capital
        
        for i in range(nrow):
            for j in range(ncol):
                # executing trades
                trade_amt = self.shares.iloc[i, j] * self.tsignal.iloc[i, j] * self.pricing_matrix.iloc[i, j]
                cash = cash - trade_amt

            # assume cash grow with risk free rate
            cash = cash * (1 + self.risk_free_rate * self.days_between_periods/365)
            self.cash[i] = cash

        self.pnl = pd.DataFrame(data = {'cash': self.cash, 'equity': self.equity,
                                        'total_value': self.cash + self.equity,}
                                  )
        self.pnl['cumulative pnl'] = self.pnl['total_value'] - self.initial_capital
        self.pnl[self.pnl_column] = self.pnl['cumulative pnl'].diff(periods = 1) / self.pnl['total_value']
                                  
        # calculate basic performance matrix
        if self.timeframe == cm.TimeFrame.DAILY:
            self._calc_daily_stat()

            
    def _calc_daily_stat(self):
        '''
        Calculate performance stat for daily timeframe
        '''
        pnl = self.pnl[self.pnl_column]
        self.performance['Cumulative Returns'] = 100 * self.pnl['cumulative pnl'][-1] / self.initial_capital
        self.performance['Maximum Drawdown'] = cm.calculate_max_drawdown(self.pnl['total_value'])
        self.performance['Sharpe Ratio'] = cm.calculate_sharpe_ratio(pnl, self.risk_free_rate)
        
        
    def finalize(self):
        '''
        Finalize any remaining calculation
        '''
        pass
    

    def save_to_csv(self, filename_root):
        '''
        Save strategy output to csv file
        '''
        self.input_dm.to_csv(filename_root + "_data.csv")
        self.pricing_matrix.to_csv(filename_root + "_prices.csv")    
    
        self.taction.to_csv(filename_root + "_taction.csv")
        self.tsignal.to_csv(filename_root + "_tsignal.csv")    
        self.shares.to_csv(filename_root + "_shares.csv")
        self.current_holding.to_csv(filename_root + "_holding.csv")
        
        self.pnl.to_csv(filename_root + "_pnl.csv")
    
