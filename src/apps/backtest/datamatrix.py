'''
Class to manage data set for a list of stocks and for a time period
'''

import datetime
import pandas as pd

import preference
import common as cm

from loader import DataLoader
from stock import Stock

import common as cm

class DataMatrix(pd.DataFrame):

    '''
    DataMatrix is a pandad dataframe where the row is index by datetime with a certain fixed Timeframe.
    The columns are index by keys encoded usng {ticker}_{field}
    where field can be open, high, low, close, volume and calculated Technical indicators or fundamental quantities
    such as capitalization
    '''

    def __init__(self, *args, **kwargs):
        _name = kwargs.pop('name', None)
        _universe = kwargs.pop('universe', None)
        _timeframe = kwargs.pop('timeframe', cm.TimeFrame.DAILY)
        super().__init__(*args, **kwargs)
        self._name = _name
        self._universe = _universe
        self._timeframe = _timeframe

    @property
    def timeframe(self):
        return self._timeframe

    @timeframe.setter
    def timeframe(self, value):
        self._timeframe = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        
    @property
    def universe(self):
        return self._universe

    @universe.setter
    def universe(self, value):
        self._universe = value
    
    def get_info(self):
        info = f"Name: {self._name}, Universe: {self._universe}"
        return(info)
        

    def extract_price_matrix(self, price_choice = cm.DataField.close):
        '''
        return a datamatrix that has only the ticker_close columns
        '''
        result = self[[f"{ticker}_{price_choice}" for ticker in self.universe]]
        # keep only the ticker as column label
        result.columns = [f"{col.split('_')[0]}" for col in result.columns]
        return(result)

        
    def validate(self):
        '''
        TBD
        '''
        result = True
        return result

    def analyse(self):
        '''
        TBD

        '''
        print(f"running analyse in DataMatrix")
        


class DataMatrixLoader(DataLoader):
    ''' 
    class responsible for loading data from files or database into DataMatrix which is a derived class from pandas DataFrame
    '''

    _standard_fields = [ cm.DataField.open, cm.DataField.high, cm.DataField.low, cm.DataField.close, cm.DataField.volume
                         ]
    
    def __init__(self, pref, name, universe, start_date, end_date, data_src = DataLoader.DataSource.CSV,
                 data_dir = None, db_connection = None):

        super().__init__(pref, data_src, data_dir, db_connection)
        self.name = name
        self.universe = universe
        self.start_date = start_date
        self.end_date = end_date


    def get_daily_datamatrix(self, fields = _standard_fields):
        '''
        create datamatrix with columns as {ticker_field}
        '''
        self.fields = fields
        df = Stock(self, self.universe[0]).get_daily_hist_price(self.start_date,
                                                                self.end_date).grab_fields(fields)

        for ticker in self.universe[1:]:
            tdf = Stock(self, ticker).get_daily_hist_price(self.start_date,
                                                           self.end_date).grab_fields(fields)
            for col in tdf.columns:
                df[col] = tdf[col]
                
        return(DataMatrix(df, name = self.name, universe = self.universe, timeframe = cm.TimeFrame.DAILY))
        


def _test1():

    fname = "C:/test/daily/AAPL_daily.csv"
    df = pd.read_csv(fname)

    dm = DataMatrix(df, name = 'test', universe = ['AAPL', 'COST'])
    print(dm.get_info())
    print(dm.head())

    dm = DataMatrix(data = {'A': [1,2,3]})
    print(dm.get_info())
    
    print(dm.head())
    

def _test2():

    print('Running test2')
    parser = preference.get_default_parser()
    args = parser.parse_args()

    pref = preference.Preference(cli_args = args)

    universe = ['AAPL', 'COST', 'NVDA']
    start_date = datetime.date(2010, 1, 1)
    end_date = datetime.date(2022, 1, 1)

    name = 'test'
    fields = [cm.DataField.close, cm.DataField.volume, cm.DataField.SMA_200, cm.DataField.daily_returns]

    loader = DataMatrixLoader(pref, name, universe, start_date, end_date)
    dm = loader.get_daily_datamatrix(fields)
    print(dm.get_info())

    print(dm.extract_price_matrix('Close'))
    
    output_fname = f"C:/test/model_data/{name}.csv"
    dm.to_csv(output_fname)
    
def _test():
    _test1()
    _test2()
    
if __name__ == "__main__":
    _test()

    
