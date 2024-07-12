'''
Class to model an Equity Portfolio
'''

import datetime
from datetime import date

import common
import trades

class Holding(object):

    def __init__(self, ticker: str, shares: float, buy_date: date, purcahse_price: float):
        self.ticker = ticker
        self.shares = shares
        self.buy_date = date
        self.purchase_price = purchase_date

class Portfolio(object):

    def __init__(self, name: str, holdings: list):
        self.name = name
        self.current_holding = holdings


    

        
