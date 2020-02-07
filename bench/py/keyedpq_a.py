from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union
import heapq
import math


_KT = TypeVar('_KT') # key type
_DT = TypeVar('_DT') # data type
_KT_inner = TypeVar('_KT_inner') # alternative key type for inner definitions
_DT_inner = TypeVar('_DT_inner') # alternative data type for inner definitions


class PyKeyedPQA(Generic[_KT, _DT]):

    @dataclass(order=True)
    class _Entry(Generic[_KT_inner, _DT_inner]):
        value: float = field(init=True, compare=True)
        change_index: int = field(init=True, compare=True)
        key: _KT_inner = field(init=True, compare=False)
        data: _DT_inner = field(init=True, compare=False)


    class Item(Generic[_KT_inner, _DT_inner]):
        def __init__(self, entry: 'PyKeyedPQA._Entry[_KT_inner, _DT_inner]') -> None:
            self._entry: PyKeyedPQA._Entry[_KT_inner, _DT_inner] = entry

        @property
        def key(self) -> _KT_inner:
            return self._entry.key

        @property
        def value(self) -> float:
            return self._entry.value

        @property
        def data(self) -> _DT_inner:
            return self._entry.data

    def __init__(self) -> None:
        self._heap: List[PyKeyedPQA._Entry[_KT, _DT]] = []
        self._change_index = 1
        self._lookup_dict: Dict[_KT, PyKeyedPQA._Entry[_KT, _DT]] = {}

    def _entry_from_identifier(self, identifier: Union[_KT, 'PyKeyedPQA.Item[_KT, _DT]']) -> 'PyKeyedPQA._Entry[_KT, _DT]':
        if isinstance(identifier, PyKeyedPQA.Item):
            return identifier._entry
        else:
            return self._lookup_dict[identifier]

    def __len__(self) -> int:
        return len(self._heap)

    def __contains__(self, key: _KT) -> bool:
        return key in self._lookup_dict

    def __getitem__(self, key: _KT) -> 'PyKeyedPQA.Item[_KT, _DT]':
        entry = self._lookup_dict[key]
        return PyKeyedPQA.Item(entry)

    def __delitem__(self, identifier: Union[_KT, 'PyKeyedPQA.Item[_KT, _DT]']) -> None:
        entry = self._entry_from_identifier(identifier)
        entry.value, entry.change_index = -math.inf, 0
        # impl A
        heapq.heapify(self._heap)

        heapq.heappop(self._heap)
        del self._lookup_dict[entry.key]

    def add(self, key: _KT, value: float, data: _DT) -> 'PyKeyedPQA.Item[_KT, _DT]':
        entry = PyKeyedPQA._Entry(value, self._change_index, key, data)
        self._change_index += 1
        heapq.heappush(self._heap, entry)
        self._lookup_dict[key] = entry
        return PyKeyedPQA.Item(entry)

    def change_value(self, identifier: Union[_KT, 'PyKeyedPQA.Item[_KT, _DT]'], value: float) -> None:
        entry = self._entry_from_identifier(identifier)
        self._change_value(entry, value)

    def _change_value(self, entry: 'PyKeyedPQA._Entry[_KT, _DT]', value: float) -> None:
        entry.value, entry.change_index = value, self._change_index
        self._change_index += 1
        # impl A
        heapq.heapify(self._heap)

    def add_or_change(self, key: _KT, value: float, data: _DT) -> 'PyKeyedPQA.Item[_KT, _DT]':
        try:
            entry = self._lookup_dict[key]
            self._change_value(entry, value)
            return PyKeyedPQA.Item(entry)
        except KeyError:
            return self.add(key, value, data)

    def peek(self) -> 'PyKeyedPQA.Item[_KT, _DT]':
        entry = self._heap[0]
        return PyKeyedPQA.Item(entry)

    def pop(self) -> Tuple[_KT, float, _DT]:
        entry = heapq.heappop(self._heap)
        del self._lookup_dict[entry.key]
        return entry.key, entry.value, entry.data
