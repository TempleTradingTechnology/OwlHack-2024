'''
Class to model user preferences
'''


import os
import getpass
import argparse


class Preference(object):

    '''
    Storing user preference as attribute.
    '''
    _default_option = { 'environ': 'dev', 'verbose': False,
                        'start_date': None, 'end_date': None, 
                        'data_dir': "C:/test/daily",
                        'user': getpass.getuser(),
                        'tickers': None, 'port_name': None,
                       }

    def __init__(self, name = None, user = None, cli_args = None):

        self.name = name
        self.user = user
        self.cli_args = cli_args
        self.cli_dict = vars(cli_args) if cli_args is not None else {}
        
        # set defaults
        for k, v in Preference._default_option.items():
            setattr(self, k, v)

        for k, v in self.cli_dict.items():
            print(k, v)
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

    parser.add_argument('--data_dir', dest = 'data_dir', default="C:/test/daily", help='data dir')
    
    return(parser)
            
def _test():

    parser = get_default_parser()
    parser.add_argument('--foo', dest='foo', default = 'whatever', help='a parameter')
    parser.add_argument('--apikey', dest='api_key_file', help='a parameter')        

    args = parser.parse_args()
    
    pref = Preference(cli_args = args)
    print (pref.name, pref.user, pref.force, pref.start_date, pref.foo, pref.api_key_file)

    
    pref = Preference()
    print (pref.name, pref.user, pref.force, pref.start_date, pref.tickers)

    pref = Preference(name = "yahoo applicaiton",  user = "John Doe")
    print (pref.name, pref.user, pref.force, pref.start_date, pref.tickers)
    
    

if __name__ == "__main__":
    _test()
