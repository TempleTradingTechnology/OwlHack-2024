'''
Class to model an Equity Portfolio
'''

import enum
import datetime
import copy
from collections import deque
from datetime import date
import common as cm


class Position(object):
    '''
    Closed or Open position by ticker
    '''
    class Type(enum.Enum):
        OPEN = "open"
        CLOSED = "closed"

    def __init__(self, ticker, entry_date, shares_with_sign, entry_price, exit_date = None, exit_price = None, type = Type.OPEN):
        self.ticker = ticker
        
        self.entry_date = entry_date
        # negative shares means it is a short position
        self.shares_with_sign = shares_with_sign
            
        self.entry_price = entry_price
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.type = type

        self.update()
        
    def update(self):
        if self.exit_price is not None:
            self.pnl = self.shares_with_sign * (self.exit_price - self.entry_price)
        else:
            self.pnl = None

    def __str__(self):
        txt = f"{self.ticker}: {self.type.value} position: entry_date: {self.entry_date}, entry_price: {self.entry_price} "
        txt += f"shares: {self.shares_with_sign}, exit_date: {self.exit_date}, exit_price: {self.exit_price}, pnl: {self.pnl}"
        return (txt)
    
        
class Portfolio(object):
    '''
    class to model a portfoilo. It has a dict from ticker to a list of closed position to that ticker for storing
    historical trades. It also has a queue to manage current open positions, whose disposal method can be either FIFO or LIFO

    TODO: implement LIFO
    '''
    def __init__(self, name, disposal_method = cm.DisposalMethod.FIFO):
        self.name = name
        self.disposal_method = disposal_method
        # dict from ticker to a list of positions
        self._positions_by_ticker = {}

        if disposal_method == cm.DisposalMethod.LIFO:
            raise Exception(f"{disposal_method} is not currently supported, only FIFO is supported")

    def get_open_long_positions(self, ticker):
        return [x for x in self._positions_by_ticker[ticker] if x.shares_with_sign > 0 and x.type == Position.Type.OPEN]

    def get_open_short_positions(self, ticker):
        return [x for x in self._positions_by_ticker[ticker] if x.shares_with_sign < 0 and x.type == Position.Type.OPEN]
    
    def get_closed_positions(self, ticker):
        return [x for x in self._positions_by_ticker[ticker] if x.type == Position.Type.CLOSED]
    

    def get_positions_by_ticker(self, ticker):
        return self.get_closed_positions(ticker) + self.get_open_long_positions(ticker) + self.get_open_short_positions(ticker) 
    
    def get_all_positions(self):
        result = []
        for ticker in self._positions_by_ticker.keys():
            result += self.get_positions_by_ticker(ticker)
        return result


    def _handle_buy(self, ticker, trade_action, trade_date, trade_price, trade_shares):
        '''
        Close all short lots, if need to buy more, create open positions
        '''
        outstanding_shares = trade_shares
        # try closing with full lots first
        for pos in self.get_open_short_positions(ticker):
            if outstanding_shares >= abs(pos.shares_with_sign):
                pos.type = Position.Type.CLOSED
                pos.exit_date = trade_date
                pos.exit_price = trade_price
                pos.update()
                outstanding_shares -= abs(pos.shares_with_sign)

        # after closing as much as possible and there is still some outstanding shares
        # then get the remaining open short positions
        if outstanding_shares > 0:
            for pos in self.get_open_short_positions(ticker):
                # close partial
                if outstanding_shares < abs(pos.shares_with_sign):
                    partial_closed = copy.deepcopy(pos)
                    partial_closed.type = Position.Type.CLOSED
                    partial_closed.shares_with_sign = -1 * outstanding_shares
                    
                    # reduce the lot size of the existing open lot
                    pos.shares_with_sign = pos.shares_with_sign + outstanding_shares
                    
                    # add the partial closed position to the trade record
                    partial_closed.exit_date = trade_date
                    partial_closed.exit_price = trade_price
                    partial_closed.update()
                    self._positions_by_ticker[ticker].append(partial_closed)

                    outstanding_shares = 0
                    break
                
            # if there is still some outstanding_shares, add new long position
            if outstanding_shares > 0:
                self._positions_by_ticker[ticker].append(Position(ticker, trade_date, outstanding_shares, trade_price))
            
            

    def _handle_sell(self, ticker, trade_action, trade_date, trade_price, trade_shares):
        '''
        Close all long lots, if need to sell more, create open positions
        '''
        outstanding_shares = trade_shares
        # try closing with full lots first
        for pos in self.get_open_long_positions(ticker):
            if outstanding_shares >= abs(pos.shares_with_sign):
                pos.type = Position.Type.CLOSED
                pos.exit_date = trade_date
                pos.exit_price = trade_price
                pos.update()
                outstanding_shares -= abs(pos.shares_with_sign)

        # after closing as much as possible and there is still some outstanding shares left to sell
        # then get the remaining open long positions
        if outstanding_shares > 0:
            for pos in self.get_open_long_positions(ticker):
                # close partial lot
                if outstanding_shares < abs(pos.shares_with_sign):
                    partial_closed = copy.deepcopy(pos)
                    partial_closed.type = Position.Type.CLOSED
                    partial_closed.shares_with_sign = outstanding_shares
                    
                    # reduce the lot size of the existing open lot
                    pos.shares_with_sign = pos.shares_with_sign - outstanding_shares
                    
                    # add the partial closed position to the trade record
                    partial_closed.exit_date = trade_date
                    partial_closed.exit_price = trade_price
                    partial_closed.update()
                    self._positions_by_ticker[ticker].append(partial_closed)

                    outstanding_shares = 0
                    break
                
            # if there is still some outstanding_shares, add new short position
            if outstanding_shares > 0:
                self._positions_by_ticker[ticker].append(Position(ticker, trade_date, -1 * outstanding_shares, trade_price))
                
        
        
    def add_trade(self, ticker, trade_action, trade_date, trade_price, trade_shares):
        '''
        When a trade happens, close existing lots with opposite direction as much as possible
        If there is shares left to buy or sell, add new lots
        '''

        if trade_shares is not None and trade_shares < 0:
            raise Exception(f"Expect trade shares to be a positive numbers, received {trade_shares} instead.")
        
        if ticker not in self._positions_by_ticker.keys():
            self._positions_by_ticker[ticker] = []

        total_short_shares = sum([abs(x.shares_with_sign) for x in self.get_open_short_positions(ticker)])
        total_long_shares = sum([abs(x.shares_with_sign) for x in self.get_open_long_positions(ticker)])
        
        # overwrite trade shares if it is a closing trade
        if trade_shares is None:
            if trade_action == cm.TradeAction.BUY_TO_CLOSE_ALL:
                trade_shares = total_short_shares
            elif trade_action == cm.TradeAction.SELL_TO_CLOSE_ALL:
                trade_shares = total_long_shares
            elif trade_action == cm.TradeAction.BUY_TO_CLOSE_50:
                trade_shares = total_short_shares/2
            elif trade_action == cm.TradeAction.BUY_TO_CLOSE_25:
                trade_shares = total_short_shares/4
            elif trade_action == cm.TradeAction.SELL_TO_CLOSE_50:
                trade_shares = total_long_shares/2
            elif trade_action == cm.TradeAction.SELL_TO_CLOSE_25:
                trade_shares = total_long_shares/4


        #print(ticker, trade_shares, trade_action)

        if trade_action in [cm.TradeAction.BUY, cm.TradeAction.BUY_TO_CLOSE_ALL, cm.TradeAction.BUY_TO_CLOSE_50,
                            cm.TradeAction.BUY_TO_CLOSE_25]:
            
            self._handle_buy(ticker, trade_action, trade_date, trade_price, trade_shares)
            
        elif trade_action in [cm.TradeAction.SELL, cm.TradeAction.SELL_TO_CLOSE_ALL, cm.TradeAction.SELL_TO_CLOSE_50,
                              cm.TradeAction.SELL_TO_CLOSE_25]:
                    
            self._handle_sell(ticker, trade_action, trade_date, trade_price, trade_shares)
            
        else:
            raise Exception(f"Unsupported Trade Action: {trade_action}")
            

    def summary(self):
        '''
        '''
        pass

def _test1():
    d1 = datetime.date(2020, 1, 1)
    d2 = datetime.date(2020, 2, 1)
    d3 = datetime.date(2020, 3, 1)
    d4 = datetime.date(2020, 4, 1)
    d5 = datetime.date(2020, 5, 1)
    d6 = datetime.date(2020, 6, 1)
    d7 = datetime.date(2020, 7, 1)
    d8 = datetime.date(2020, 8, 1)
    d9 = datetime.date(2020, 9, 1)                
    
    trades1 = [ \
                ('AAPL', cm.TradeAction.BUY, d3, 105, 500),
                ('AAPL', cm.TradeAction.SELL_TO_CLOSE_ALL, d4, 108, None),

                ('AAPL', cm.TradeAction.BUY, d5, 100, 1000),
                ('AAPL', cm.TradeAction.SELL_TO_CLOSE_50, d6, 110, None),
                ('AAPL', cm.TradeAction.SELL_TO_CLOSE_ALL, d7, 120, None),                                
                
               ]

    trades2 = [ \
                ('NVDA', cm.TradeAction.SELL, d3, 105, 500),
                ('NVDA', cm.TradeAction.BUY_TO_CLOSE_ALL, d4, 108, None),

                ('NVDA', cm.TradeAction.SELL, d5, 100, 1000),
                ('NVDA', cm.TradeAction.BUY_TO_CLOSE_50, d6, 110, None),
                ('NVDA', cm.TradeAction.BUY, d7, 110, 100),
#                ('NVDA', cm.TradeAction.BUY_TO_CLOSE_ALL, d8, 120, None),                                
                
        
               ]


    port = Portfolio('test')
    
    for trade in trades1:
        port.add_trade(trade[0], trade[1], trade[2], trade[3], trade[4])

    for trade in trades2:
        port.add_trade(trade[0], trade[1], trade[2], trade[3], trade[4])

        for pos in port._positions_by_ticker['NVDA']:
            print(pos.type, pos.shares_with_sign)

        for pos in port.get_open_short_positions('NVDA'):
            print(pos.type, pos.shares_with_sign)
            
    for pos in port.get_all_positions():
        print(pos)

        

    

def _test():
    _test1()


if __name__ == "__main__":
    _test1()
        
