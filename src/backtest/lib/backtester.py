'''
Main driver class for the backtester

'''

import datetime

import preference
import common as cm
import portfolio

from datamatrix import DataMatrixLoader

class Driver(object):

    def __init__(self, pref):
        self.pref = pref
        self.start_date = pref.start_date
        self.end_date = pref.end_date
        self.universe_name = pref.universe_name
        self.initial_capital = pref.initial_capital
        self.universe = cm.get_index_components(pref.universe_name, pref.meta_data_dir)
        self.datamatrix_loader = DataMatrixLoader(pref, pref.universe_name, self.universe, pref.start_date, pref.end_date)
        self.strategy_list = []
        self.run_date = None
        
    def get_info(self):
        '''
        Return all the settings for this backtest
        '''
        info = self.pref.describe()
        info += f"\nRun date: {self.run_date}"
        
        return(info)
        
    def run(self, strategy_list):
        self.run_date = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        self.strategy_list = strategy_list
        
        for strategy in strategy_list:
            strategy.validate()
            strategy.run_strategy()
            print(f"Saving results to {self.pref.output_dir}")
            strategy.save_to_csv(self.pref.output_dir)
        
    def summary(self):
        '''
        print out summary of the result
        '''
        for strategy in self.strategy_list:
            print(f"\n{strategy.name} performance: {strategy.performance}")
            
def _test():
    '''unit test
    '''
    pref = preference.Preference()

    driver = Driver(pref)

    
if __name__ == '__main__':
    _test()
        


    
