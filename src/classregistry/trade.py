from abc import ABC, abstractmethod, ABCMeta

_trade_registry = {}

class TradeMeta(ABCMeta):
    def __iter__(cls):
        if cls is not Trade:
            raise TypeError(f'{cls.__name__!r} object is not iterable')
        yield from _trade_registry.values()

    def __getitem__(cls, item):
        if cls is not Trade:
            raise TypeError(f'{cls.__name__!r} object is not subscriptable')
        return _trade_registry[item]


class Trade(metaclass=TradeMeta):

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        trade_type = getattr(cls, 'trade_type', undefined := object())
        if trade_type is undefined:
            raise TypeError('Trade subclasses must define trade_type class attribute.')
        if cls.trade_type in _trade_registry:
            raise RuntimeError(f'Invalid attempt to register the same '
                               f'trade type twice: {cls.trade_type}')
        _trade_registry[cls.trade_type] = cls

    @abstractmethod
    def func(self) -> str:
        ...
