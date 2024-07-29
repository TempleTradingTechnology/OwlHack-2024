'''
Classes for basic strategies
'''


from strategy import Strategy

class RandomStrategy(Strategy):
    
    def __init__(self, *args, **kwargs):
        super(BuyAndHold, self).__init__(*args, **kwargs)
