from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union
import heapq
import math


_KT = TypeVar('_KT') # key type
_DT = TypeVar('_DT') # data type
_KT_inner = TypeVar('_KT_inner') # alternative key type for inner definitions
_DT_inner = TypeVar('_DT_inner') # alternative data type for inner definitions


class PyKeyedPQC(Generic[_KT, _DT]):

	@dataclass(order=True)
	class _Entry(Generic[_KT_inner, _DT_inner]):
		value: float = field(init=True, compare=True)
		change_index: int = field(init=True, compare=True)
		index: int = field(init=True, compare=False)
		key: _KT_inner = field(init=True, compare=False)
		data: _DT_inner = field(init=True, compare=False)


	class Item(Generic[_KT_inner, _DT_inner]):
		def __init__(self, entry: 'PyKeyedPQC._Entry[_KT_inner, _DT_inner]') -> None:
			self._entry: PyKeyedPQC._Entry[_KT_inner, _DT_inner] = entry

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
		self._heap: List[PyKeyedPQC._Entry[_KT, _DT]] = []
		self._change_index = 1
		self._lookup_dict: Dict[_KT, PyKeyedPQC._Entry[_KT, _DT]] = {}

	def _entry_from_identifier(self, identifier: Union[_KT, 'PyKeyedPQC.Item[_KT, _DT]']) -> 'PyKeyedPQC._Entry[_KT, _DT]':
		if isinstance(identifier, PyKeyedPQC.Item):
			return identifier._entry
		else:
			return self._lookup_dict[identifier]

	def __len__(self) -> int:
		return len(self._heap)

	def __contains__(self, key: _KT) -> bool:
		return key in self._lookup_dict

	def __getitem__(self, key: _KT) -> 'PyKeyedPQC.Item[_KT, _DT]':
		entry = self._lookup_dict[key]
		return PyKeyedPQC.Item(entry)

	def __delitem__(self, identifier: Union[_KT, 'PyKeyedPQC.Item[_KT, _DT]']) -> None:
		entry = self._entry_from_identifier(identifier)
		entry.value, entry.change_index = -math.inf, 0
		# impl C
		ind = entry.index
		_siftup(self._heap, ind)

		heappop(self._heap)
		del self._lookup_dict[entry.key]

	def add(self, key: _KT, value: float, data: _DT) -> 'PyKeyedPQC.Item[_KT, _DT]':
		entry = PyKeyedPQC._Entry(value, self._change_index, len(self._heap), key, data)
		self._change_index += 1
		heappush(self._heap, entry)
		self._lookup_dict[key] = entry
		return PyKeyedPQC.Item(entry)

	def change_value(self, identifier: Union[_KT, 'PyKeyedPQC.Item[_KT, _DT]'], value: float) -> None:
		entry = self._entry_from_identifier(identifier)
		self._change_value(entry, value)

	def _change_value(self, entry: 'PyKeyedPQC._Entry[_KT, _DT]', value: float) -> None:
		entry.value, entry.change_index = value, self._change_index
		self._change_index += 1
		# impl C
		ind = entry.index
		_siftup(self._heap, ind)

	def add_or_change(self, key: _KT, value: float, data: _DT) -> 'PyKeyedPQC.Item[_KT, _DT]':
		try:
			entry = self._lookup_dict[key]
			self._change_value(entry, value)
			return PyKeyedPQC.Item(entry)
		except KeyError:
			return self.add(key, value, data)

	def peek(self) -> 'PyKeyedPQC.Item[_KT, _DT]':
		entry = self._heap[0]
		return PyKeyedPQC.Item(entry)

	def pop(self) -> Tuple[_KT, float, _DT]:
		entry = heappop(self._heap)
		del self._lookup_dict[entry.key]
		return entry.key, entry.value, entry.data


def _siftup(heap: List[Any], pos: int) -> None:
	# From Python 3.8
	# https://github.com/python/cpython/blob/3.8/Lib/heapq.py
	# Changes:
	#  * Do not accept pass a startpos to _siftdown
	#  * Set index field when moving entries

	endpos = len(heap)
	newitem = heap[pos]
	# Bubble up the smaller child until hitting a leaf.
	childpos = 2*pos + 1    # leftmost child position
	while childpos < endpos:
		# Set childpos to index of smaller child.
		rightpos = childpos + 1
		if rightpos < endpos and not heap[childpos] < heap[rightpos]:
		    childpos = rightpos
		# Move the smaller child up.
		heap[pos] = heap[childpos]
		heap[pos].index = pos
		pos = childpos
		childpos = 2*pos + 1
	# The leaf at pos is empty now.  Put newitem there, and bubble it up
	# to its final resting place (by sifting its parents down).
	heap[pos] = newitem
	heap[pos].index = pos
	_siftdown(heap, pos)

def _siftdown(heap: List[Any], pos: int) -> None:
	# From Python 3.8
	# https://github.com/python/cpython/blob/3.8/Lib/heapq.py
	# Changes:
	#  * Do not accept startpos, always use 0
	#  * Set index field when moving entries

    newitem = heap[pos]
    # Follow the path to the root, moving parents down until finding a place
    # newitem fits.
    while pos > 0:
        parentpos = (pos - 1) >> 1
        parent = heap[parentpos]
        if newitem < parent:
            heap[pos] = parent
            heap[pos].index = pos
            pos = parentpos
            continue
        break
    heap[pos] = newitem
    heap[pos].index = pos

def heappop(heap: List[Any]) -> Any:
	# From Python 3.8
	# https://github.com/python/cpython/blob/3.8/Lib/heapq.py

    """Pop the smallest item off the heap, maintaining the heap invariant."""
    lastelt = heap.pop()    # raises appropriate IndexError if heap is empty
    if heap:
        returnitem = heap[0]
        heap[0] = lastelt
        _siftup(heap, 0)
        return returnitem
    return lastelt

def heappush(heap: List[Any], item: Any) -> None:
	# From Python 3.8
	# https://github.com/python/cpython/blob/3.8/Lib/heapq.py
	# Changes:
	#  * Do not accept pass a startpos to _siftdown

    """Push item onto heap, maintaining the heap invariant."""
    heap.append(item)
    _siftdown(heap, len(heap)-1)
