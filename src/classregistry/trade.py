from abc import ABC, abstractmethod

_trade_registry = {}


class Trade(ABC):

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


def iter_trade_types() -> Trade:  # TODO: typevar covariant
    yield from _trade_registry.values()


def get_trade_type_by_name(name: str) -> Trade:
    return _trade_registry[name]
