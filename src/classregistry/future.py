from .trade import Trade


class Future(Trade):
    trade_type = 'FUTURE'

    def func(self) -> str:
        return 'Future here'


# Uncomment the lines below to see the error in import time
# class Future2(Trade):
#     trade_type = 'FUTURE'  # already registered
#
#     def func(self):
#         return 'Back to the Future'