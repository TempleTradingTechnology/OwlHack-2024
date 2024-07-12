'''
Main driver class for helping to build a ML model

'''

import datetime

import common as cm

from loader import DataLoader
from datamatrix import DataMatrix

class ModelBuilder(self):

    def __init__(self, pref, universe: list, start_date: datetime.date, end_date: datetime.date,
                 timeframe = cm.TimeFrame.DAILY):

        self.pref = pref
        self.universe = universe
        self.start_date = start_date
        self.end_date = end_date

        self.loader = DataLoader(pref, pref.data_dir)

    def gen_model_data(self):
        '''

        '''
        pass


def _test():
    '''unit test
    '''


if __name__ == '__main__':
    _test()
        


    
