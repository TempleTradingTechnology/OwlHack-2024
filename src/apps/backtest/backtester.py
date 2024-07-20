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
        
    def run(self, strategy_list):  
        for strategy in strategy_list:
            strategy.validate()
            strategy.run_strategy()
            print(f"Saving results to {self.pref.output_dir}")
            strategy.save_to_csv(self.pref.output_dir)
        

def _test():
    '''unit test
    '''
    pref = preference.Preference()

if __name__ == '__main__':
    _test()
        


    
