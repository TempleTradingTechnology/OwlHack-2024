'''
Main script to run the backtester
'''

# import native libraries
import os
import sys
import datetime
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

# append the lib directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
os.environ["ROOT_DATA_DIR"] = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir ,'data')


# import the internal libraries
import preference
import common as cm
import backtester
from datamatrix import DataMatrix, DataMatrixLoader

# import the strategies
from strategy.buyandhold_strategy import BuyAndHoldStrategy
from strategy.RSI_strategy import RSIStrategy

def create_strategy_list(pref, datamatrix_loader):
    result = []
    fields = [cm.DataField.close, cm.DataField.volume, cm.DataField.SMA_200, cm.DataField.daily_returns]

    print("Creating datamatrix")
    dm = datamatrix_loader.get_daily_datamatrix()


    buyandhold = BuyAndHoldStrategy(pref, dm, pref.initial_capital/2)
    result.append(buyandhold)

    rsi = RSIStrategy(pref, dm, pref.initial_capital/2)
    result.append(rsi)

    return(result)

def run():

    parser = preference.get_default_parser()
    parser.add_argument('--universe_name',   dest='universe_name', default = 'OwlHack 2024 Universe', help='Name of the Universe')
    parser.add_argument('--initial_capital', dest='initial_capital', default = cm.OneMillion, help='Initial Capital')

    args = parser.parse_args()
    args = parser.parse_args()
    pref = preference.Preference(cli_args = args)

    if pref.output_dir is None:
        pref.output_dir = pref.test_output_dir

    driver = backtester.Driver(pref)
    strategy_list = create_strategy_list(pref, driver.datamatrix_loader)

    driver.run(strategy_list)
    driver.summary()

if __name__ == "__main__":
    run()
