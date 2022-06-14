from .trade import Trade


class Bond(Trade):
    trade_type = 'BOND'

    def func(self):
        return 'Bond here'
