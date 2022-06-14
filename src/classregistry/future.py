from .trade import Trade


class Future(Trade):
    trade_type = 'FUTURE'

    def func(self) -> str:
        return 'Future here'
