from .trade import Trade
from .bond import Bond
from .future import Future
from .special_bond import SpecialBond


print('It is possible to iterate over Trade subclasses like this:')
for trade_cls in Trade:
    print(trade_cls)


print('It is also possible to get a Trade subclass by name like this:')
bond_cls = Trade['BOND']
print(bond_cls)


print('However it is not possible to iterate over the subclass object')
try:
    iter(bond_cls)
except TypeError as err:
    print(err)