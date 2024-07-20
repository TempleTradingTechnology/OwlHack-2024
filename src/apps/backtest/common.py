'''
Misc utilites
'''

import os
import datetime
import enum
import numpy as np
import pandas as pd

OneThousand = 1000.0
OneHundredThousand = 100000.0
OneMillion = 1000000.0

# should not depend on other library

class TimeFrame(enum.Enum):

    DAILY = 'Daily'
    ONEMIN = '1-min'
    FIVEMIN = '5-min'
    WEEKLY = 'Weekly'
    MONTHLY = 'Monthly'

class DataField(str, enum.Enum):
    open = 'Open'
    high = 'High'
    low = 'Low'
    close = 'Close'
    volume = 'Volume'

    SMA_10 = 'SMA_10'
    SMA_20 = 'SMA_20'
    SMA_50 = 'SMA_50'
    SMA_200 = 'SMA_200'

    daily_returns = 'daily_returns'
    weekly_returns = 'weekly_returns'
    monthly_returns = 'monthly_returns'
    fifty_two_high = '52_weeks_high'
    fifty_two_low = '52_weeks_low'    
    
    capitalization = 'Capitalization'

    
class TradeAction(enum.Enum):
    NONE              = ""
    BUY               = "BUY"                   # Buy shares
    SELL              = "SELL"                  # Sell shares
    BUY_TO_CLOSE_ALL  = "BUY_TO_CLOSE_ALL"      # Buy back all short positions
    SELL_TO_CLOSE_ALL = "SELL_TO_CLOSE_ALL"     # Sell all long positions

    # the following are more for options
    BUY_TO_OPEN       = "BUY_TO_OPEN"           # buy new lots
    SELL_TO_OPEN      = "SELL_TO_OPEN"          # sell new lots
    BUY_TO_CLOSE      = "BUY_TO_CLOSE"          # buy to close all existing lots
    SELL_TO_CLOSE     = "SELL_TO_CLOSE"         # sell all existing long position
    
    # the following are for buying and selling shares without specifying the number of shares
    BUY_TO_CLOSE_50   = "BUY_TO_CLOSE_50"       # buy to close half
    BUY_TO_CLOSE_25   = "BUY_TO_CLOSE_25"       # buy to close a quarter
    SELL_TO_CLOSE_50  = "SELL_TO_CLOSE_50"      # sell 50 percent
    SELL_TO_CLOSE_25  = "SELL_TO_CLOSE_25"      # sell quarter position

class TradeSignal(enum.Enum):
    SHORT = -1
    HOLD = 0
    LONG = 1

class WeighingScheme(enum.Enum):
    EqualShares = "EQL_SHARE"
    EqualDollarExposure = "EQL_DOLLAR"
    MarketCapitalization = "MKT_CAP"

class RiskAllocation(enum.Enum):
    FIXED_PERCENT_PORT = "FIXED_PERCENT"
    FIXED_DOLLAR = "FIXED_DOLLAR"
    EQUAL_RISK = "EQUAL_RISK"
    

class DisposalMethod(enum.Enum):
    FIFO = "FIFO"
    LIFO = "LIFO"
    
def get_index():
    return ['S&P 500', 'NASDAQ 100', 'DJIA', 'RUSSELL 2000', 'OwlHack 2024 Universe']

def get_ETF_by_index(index):
    _map = {'S&P 500': 'SPY', 'NASDAQ 100': 'QQQ', 'DJIA': 'DIA', 'RUSSELL 2000': 'IWM',
            'OwlHack 2024 Universe': 'SPY'}
    return _map[index]

    
def get_sector():
    return ['Basic Materials', 'Communication Services', 'Consumer Cyclical',
            'Consumer Defensive', 'Energy', 'Financial', 'Healthcare', 'Industrials',
            'Real Estate', 'Technology', 'Utilities', 'Others']

def get_industry():
    # to be determined
    return []

def get_index_components(index, meta_data_dir):
    fname = os.path.join(meta_data_dir, index.replace(' ', '') + '.txt')
    df = pd.read_csv(fname)
    return(df['Ticker'].tolist())

def parse_date_str(txt):
    try:
        dt = datetime.datetime.strptime(txt, "%Y-%m-%d").date()
    except:
        dt = datetime.datetime.strptime(txt, "%m/%d/%Y").date()
    return(dt)

def calculate_sharpe_ratio(daily_returns, risk_free_rate):
    # Calculate average daily return
    avg_daily_return = np.mean(daily_returns)
    
    # Calculate daily standard deviation
    daily_std_dev = np.std(daily_returns, ddof=1)
    
    # Annualize the figures
    annualized_return = (1 + avg_daily_return) ** 252 - 1
    annualized_std_dev = daily_std_dev * np.sqrt(252)
    
    # Convert annual risk-free rate to daily
    daily_risk_free = (1 + risk_free_rate) ** (1/252) - 1
    annualized_risk_free = (1 + daily_risk_free) ** 252 - 1
    
    # Calculate Sharpe ratio
    sharpe_ratio = (annualized_return - annualized_risk_free) / annualized_std_dev
    
    return sharpe_ratio

def calculate_max_drawdown(equity_values):
    # Calculate the running maximum
    running_max = np.maximum.accumulate(equity_values)
    
    # Calculate drawdowns
    drawdowns = (equity_values - running_max) / running_max
    
    # Find the maximum drawdown
    max_drawdown = np.min(drawdowns)
    return max_drawdown


def _test():
    # various unit tests
    equity_values = [100, 110, 105, 95, 100, 90, 100, 110]
    max_dd = calculate_max_drawdown(equity_values)
    print(f"Maximum Drawdown: {max_dd:.2%}")

if __name__ == "__main__":
    _test()
