'''
Class to model user preferences
'''


import os
import getpass
import argparse
from pprint import pprint 


class Preference(object):

    '''
    Storing user preference as attribute.
    '''

    _file_dir = os.path.dirname(os.path.realpath(__file__))

    _default_option = { 'environ': 'dev', 'verbose': False,
                        'start_date': None, 'end_date': None, 
                        'data_root_dir': os.path.join(_file_dir, '../../../data'),
                        'train_data_dir': os.path.join(_file_dir, '../../../data/train'),
                        'test_data_dir': os.path.join(_file_dir, '../../../data/test'),                        
                        'test_output_dir': os.path.join(_file_dir, '../../tests/output'),
                        'tickers': None, 'port_name': None,
                       }

    def __init__(self, name = None, user = None, cli_args = None):

        self.name = name
        self.user = user

        # set defaults
        for k, v in Preference._default_option.items():
            setattr(self, k, v)

        # set from CLI
        if cli_args is not None:
            for k, v in vars(cli_args).items():
                setattr(self, k, v)

        if self.name is None:
            self.name = 'standard'
            
        if self.user is None:
            self.user = getpass.getuser()

            


def get_default_parser():
    #
    parser = argparse.ArgumentParser()
    parser.add_argument('--environ', dest='environ', default='dev', help='runtime environment')
    parser.add_argument('--verbose', action='store_true', dest='verbose', default=False, help='verbose')
    parser.add_argument('--user', dest='user', default=None, help='user name')        

    parser.add_argument('--start_date', dest='start_date', default="2001-01-01", help='start date (YYYY-MM-DD)')
    parser.add_argument('--end_date', dest='end_date', default="2020-01-01", help='end date (YYYY-MM-DD)')
    parser.add_argument('--tickers', dest='tickers', default=None, help='Tickers with | separator')

    parser.add_argument('--data_dir', dest = 'data_dir', default=None, help='data dir')
    parser.add_argument('--output_dir', dest = 'output_dir', default=None, help='output dir')    
    
    return(parser)

            
def _test1():
    # test default
    pref = Preference()
    pprint(vars(pref))

    pref = Preference(name = "yahoo applicaiton",  user = "John Doe")
    pprint(vars(pref))

    parser = get_default_parser()
    parser.add_argument('--foo', dest='foo', default = 'whatever', help='a parameter')
    parser.add_argument('--apikey', dest='api_key_file', help='a parameter')        
    args = parser.parse_args()
    
    pref = Preference(name = "from cli", cli_args = args)
    pprint(vars(pref))

def _test():
    _test1()
    
    

if __name__ == "__main__":
    _test()
