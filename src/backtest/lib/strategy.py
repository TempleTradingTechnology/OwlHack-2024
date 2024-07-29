'''
Class to model a strategy
'''
import os
import pandas as pd
import common as cm
from datamatrix import DataMatrix

from portfolio import Position, Portfolio

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

    def __init__(self, pref, name, input_datamatrix: DataMatrix, initial_capital: float, price_choice = cm.DataField.close):
        self.pref = pref
        self.name = name
        self.input_dm = input_datamatrix
        self.universe = self.input_dm.universe
        self.initial_capital = initial_capital
        self.price_choice = price_choice

        self.pricing_matrix = self.input_dm.extract_price_matrix().copy()

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
        Shares indicate how many shares to buy or sell and are positive
        '''
        raise Exception("Should not be calling the Strategy Base class run_model method")


    def run_strategy(self):
        '''
        Call the run_model, then run the strategy.
        Calculate the state of the strategy period by period.
        '''
        self.tsignal, self.taction, self.shares = self.run_model()

        nrow, ncol   = self.pricing_matrix.shape
        nrow1, ncol1 = self.tsignal.shape
        nrow2, ncol2 = self.taction.shape
        nrow3, ncol3 = self.shares.shape

        print(ncol1, ncol2, ncol3)

        if nrow != nrow1 or ncol != ncol1:
            raise Exception(f"Pricing Matrix size don't matter in generate trade history")

        if nrow1 != nrow2 or nrow2 != nrow3:
            raise Exception(f"Number of row don't matter in generate trade history")
        if ncol1 != ncol2 or ncol2 != ncol3:
            raise Exception(f"Number of column don't matter in generate trade history")

        self.current_holding = (self.shares * self.tsignal).cumsum()
        self.equity = (self.current_holding * self.pricing_matrix).sum(axis = 1)

        cash = self.initial_capital

        for i in range(nrow):
            for j in range(ncol):
                # executing trades
                trade_amt = self.shares.iloc[i, j] * self.tsignal.iloc[i, j] * self.pricing_matrix.iloc[i, j]
                cash = cash - trade_amt

            # assume cash grow with risk free rate
            cash = cash * (1 + self.pref.risk_free_rate * self.days_between_periods/365)
            self.cash[i] = cash

        self.pnl = pd.DataFrame(data = {'cash': self.cash, 'equity': self.equity,
                                        'total_value': self.cash + self.equity,}
                                  )
        self.pnl['cumulative pnl'] = self.pnl['total_value'] - self.initial_capital
        self.pnl[self.pnl_column] = self.pnl['cumulative pnl'].diff(periods = 1) / self.pnl['total_value']

        # calculate basic performance matrix
        if self.timeframe == cm.TimeFrame.DAILY:
            self._calc_daily_stat()


    def generate_trade_history(self, output_fname):
        '''
        '''
        port = Portfolio(self.name)
<<<<<<< HEAD:src/apps/backtest/strategy.py
        nrow, ncol = self.pricing_matrix.shapeg
        
=======
        nrow, ncol = self.pricing_matrix.shape

>>>>>>> 8a624fe579fae357cfa3b5d777f50d45e1d7f095:src/backtest/lib/strategy.py
        for i in range(nrow):
            trade_date = self.pricing_matrix.index[i]
            for j in range(ncol):
                ticker = self.tsignal.columns[j]
                action = self.taction.iloc[i, j]
                shares = self.shares.iloc[i, j]
                price = self.pricing_matrix.iloc[i, j]

                port.add_trade(ticker, action, trade_date, price, shares)

        port.save_trade_history(output_fname)


    def _calc_daily_stat(self):
        '''
        Calculate performance stat for daily timeframe
        '''
        pnl = self.pnl[self.pnl_column]
        self.performance['Cumulative Returns'] = 100 * self.pnl['cumulative pnl'][-1] / self.initial_capital
        self.performance['Maximum Drawdown'] = cm.calculate_max_drawdown(self.pnl['total_value'])
<<<<<<< HEAD:src/apps/backtest/strategy.py
        self.performance['Sharpe Ratio'] = cm.calculate_sharpe_ratio(pnl, self.pref.risk_free_rate)
        
        
=======
        self.performance['Sharpe Ratio'] = cm.calculate_sharpe_ratio(pnl, self.risk_free_rate)


>>>>>>> 8a624fe579fae357cfa3b5d777f50d45e1d7f095:src/backtest/lib/strategy.py
    def finalize(self):
        '''
        Finalize any remaining calculation
        '''
        pass


    def save_to_csv(self, output_dir):
        '''
        Save strategy output to csv file
        '''
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        fname = self.name.replace(' ', '')
        self.input_dm.to_csv(os.path.join(output_dir, f"{fname}_data.csv"))
        self.pricing_matrix.to_csv(os.path.join(output_dir, f"{fname}_prices.csv"))
        self.taction.to_csv(os.path.join(output_dir,  f"{fname}_taction.csv"))
        self.tsignal.to_csv(os.path.join(output_dir, f"{fname}_tsignal.csv"))
        self.shares.to_csv(os.path.join(output_dir, f"{fname}_shares.csv"))
        self.current_holding.to_csv(os.path.join(output_dir, f"{fname}_holding.csv"))

        self.pnl.to_csv(os.path.join(output_dir, f"{fname}_pnl.csv"))

        self.generate_trade_history(os.path.join(output_dir, f"{fname}_trade_history.csv"))


def _test():
    pass


if __name__ == "__main__":
    _test()





