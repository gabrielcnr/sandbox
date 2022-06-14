from .bond import Bond


class SpecialBond(Bond):
    trade_type = 'SPECIAL_BOND'

    def func(self):
        return 'SpecialBond here'
