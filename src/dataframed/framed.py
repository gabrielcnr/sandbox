import pandas as pd

# TODO: how about the order of the columns? What if one wants/needs to enforce order?
import typing

import pytest
from pandas._typing import Axes, Dtype


class DataFramed(pd.DataFrame):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Schema = getattr(cls, 'Schema', None)
        if Schema is not None and isinstance(Schema, type):
            # look at annotations
            type_hints = typing.get_type_hints(Schema)
        else:
            type_hints = {}

        cls._type_hints = type_hints


    def __init__(
        self,
        data=None,
        index: Axes | None = None,
        columns: Axes | None = None,
        dtype: Dtype | None = None,
        copy: bool | None = None,
    ):
        if columns is None:
            columns = list(self._type_hints)
            # if dtype is None:
            #     dtype = list(self._type_hints.values())  # TODO; wrong
        elif missing := set(self._type_hints) - set(columns):
                raise ValueError(f'{type(self).__name__} is missing required columns: {missing}')
        super().__init__(data=data, index=index, columns=columns, dtype=dtype, copy=copy)

    def __setitem__(self, key, value):
        if isinstance(key, str): # only strings
            if key in self._type_hints:
                type_ = self._type_hints[key]

                try:
                    iter(value)
                except TypeError:
                    # object is not iterable ...
                    if not isinstance(value, type_):   # TODO: do we want to be strict? do we want to coerce?
                        raise TypeError(f'{type(self).__name__} requires values for column: {key}'
                                        f' to be {type_} - got: {type(value).__name__}')
                else:
                    # it is iterable
                    if isinstance(value, str):
                        # TODO: TBC ... (I stopped here) ...

    def __delitem__(self, key):
        if key in self._type_hints:
            raise RuntimeError(f'Cannot drop column: {key} which is part of '
                               f'the schema for {type(self).__name__}')
        else:
            return super().__delitem__(key)



def test_simple_creation():

    class MyDataFrame(DataFramed):
        class Schema:
            name: str
            age: int

    df = MyDataFrame()
    assert list(df.columns) == ['name', 'age']
    assert len(df) == 0


def test_assert_isinstance():
    class MyDataFrame(DataFramed):
        class Schema:
            name: str

    assert isinstance(MyDataFrame(), pd.DataFrame)


def test_cannot_delete_or_drop_columns_that_belong_to_schema():
    class MyDataFrame(DataFramed):
        class Schema:
            name: str

    df = MyDataFrame(data=[{'name': 'joe'}, {'name': 'jane'}])

    with pytest.raises(RuntimeError):
        del df['name']

    # TODO: this fails... it doesn't call __delitem__ under the hood...
    with pytest.raises(RuntimeError):
        df.drop(columns=['name'])
