from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union
import heapq
import math


KeyType = TypeVar('KeyType')
DataType = TypeVar('DataType')
KeyTypeInner = TypeVar('KeyTypeInner')
DataTypeInner = TypeVar('DataTypeInner')


class PyKeyedPQC(Generic[KeyType, DataType]):

	@dataclass(order=True)
	class _Entry(Generic[KeyTypeInner, DataTypeInner]):
		value: float = field(init=True, compare=True)
		change_index: int = field(init=True, compare=True)
		index: int = field(init=True, compare=False)
		key: KeyTypeInner = field(init=True, compare=False)
		data: DataTypeInner = field(init=True, compare=False)


	class Item(Generic[KeyTypeInner, DataTypeInner]):
		def __init__(self, entry: 'PyKeyedPQC._Entry[KeyTypeInner, DataTypeInner]') -> None:
			self._entry: PyKeyedPQC._Entry[KeyTypeInner, DataTypeInner] = entry

		@property
		def key(self) -> KeyTypeInner:
			return self._entry.key

		@property
		def value(self) -> float:
			return self._entry.value

		@property
		def data(self) -> DataTypeInner:
			return self._entry.data

	def __init__(self) -> None:
		self._heap: List[PyKeyedPQC._Entry[KeyType, DataType]] = []
		self._change_index = 1
		self._lookup_dict: Dict[KeyType, PyKeyedPQC._Entry[KeyType, DataType]] = {}

	def _entry_from_identifier(self, identifier: Union[KeyType, 'PyKeyedPQC.Item[KeyType, DataType]']) -> 'PyKeyedPQC._Entry[KeyType, DataType]':
		if isinstance(identifier, PyKeyedPQC.Item):
			return identifier._entry
		else:
			return self._lookup_dict[identifier]

	def __len__(self) -> int:
		return len(self._heap)

	def __contains__(self, key: KeyType) -> bool:
		return key in self._lookup_dict

	def __getitem__(self, key: KeyType) -> 'PyKeyedPQC.Item[KeyType, DataType]':
		entry = self._lookup_dict[key]
		return PyKeyedPQC.Item(entry)

	def __delitem__(self, identifier: Union[KeyType, 'PyKeyedPQC.Item[KeyType, DataType]']) -> None:
		entry = self._entry_from_identifier(identifier)
		entry.value, entry.change_index = -math.inf, 0
		# impl C
		ind = entry.index
		_siftup(self._heap, ind)

		heappop(self._heap)
		del self._lookup_dict[entry.key]

	def add(self, key: KeyType, value: float, data: DataType) -> 'PyKeyedPQC.Item[KeyType, DataType]':
		entry = PyKeyedPQC._Entry(value, self._change_index, len(self._heap), key, data)
		self._change_index += 1
		heappush(self._heap, entry)
		self._lookup_dict[key] = entry
		return PyKeyedPQC.Item(entry)

	def change_value(self, identifier: Union[KeyType, 'PyKeyedPQC.Item[KeyType, DataType]'], value: float) -> None:
		entry = self._entry_from_identifier(identifier)
		self._change_value(entry, value)

	def _change_value(self, entry: 'PyKeyedPQC._Entry[KeyType, DataType]', value: float) -> None:
		entry.value, entry.change_index = value, self._change_index
		self._change_index += 1
		# impl C
		ind = entry.index
		_siftup(self._heap, ind)

	def add_or_change(self, key: KeyType, value: float, data: DataType) -> 'PyKeyedPQC.Item[KeyType, DataType]':
		try:
			entry = self._lookup_dict[key]
			self._change_value(entry, value)
			return PyKeyedPQC.Item(entry)
		except KeyError:
			return self.add(key, value, data)

	def peek(self) -> 'PyKeyedPQC.Item[KeyType, DataType]':
		entry = self._heap[0]
		return PyKeyedPQC.Item(entry)

	def pop(self) -> Tuple[KeyType, float, DataType]:
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
