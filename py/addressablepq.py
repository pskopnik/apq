from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union
import heapq
import math


KeyType = TypeVar('KeyType')
DataType = TypeVar('DataType')
KeyTypeInner = TypeVar('KeyTypeInner')
DataTypeInner = TypeVar('DataTypeInner')


class AddressablePQ(Generic[KeyType, DataType]):
	"""Basic implementation of an addressable priority queue.

	Changing the value of an entry requires a linear search within the data
	structure. This makes processing hits very expensive. The index of each
	_Entry must be tracked within the _Entry to alleviate this.
	A simple workaround could be to perform a heap-aware search instead of a
	linear one.
	"""

	@dataclass(order=True)
	class _Entry(Generic[KeyTypeInner, DataTypeInner]):
		value: float = field(init=True, compare=True)
		change_index: int = field(init=True, compare=True)
		key: KeyTypeInner = field(init=True, compare=False)
		data: DataTypeInner = field(init=True, compare=False)


	class Item(Generic[KeyTypeInner, DataTypeInner]):
		def __init__(self, entry: 'AddressablePQ._Entry[KeyTypeInner, DataTypeInner]') -> None:
			self._entry: AddressablePQ._Entry[KeyTypeInner, DataTypeInner] = entry

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
		self._heap: List[AddressablePQ._Entry[KeyType, DataType]] = []
		self._change_index = 1
		self._lookup_dict: Dict[KeyType, AddressablePQ._Entry[KeyType, DataType]] = {}

	def _entry_from_identifier(self, identifier: Union[KeyType, 'AddressablePQ.Item[KeyType, DataType]']) -> 'AddressablePQ._Entry[KeyType, DataType]':
		if isinstance(identifier, AddressablePQ.Item):
			return identifier._entry
		else:
			return self._lookup_dict[identifier]

	def __len__(self) -> int:
		return len(self._heap)

	def __contains__(self, key: KeyType) -> bool:
		return key in self._lookup_dict

	def __getitem__(self, key: KeyType) -> 'AddressablePQ.Item[KeyType, DataType]':
		entry = self._lookup_dict[key]
		return AddressablePQ.Item(entry)

	def __delitem__(self, identifier: Union[KeyType, 'AddressablePQ.Item[KeyType, DataType]']) -> None:
		entry = self._entry_from_identifier(identifier)
		entry.value, entry.change_index = -math.inf, 0
		# impl A
		# heapq.heapify(self._heap)

		# impl B
		ind = self._heap.index(entry)
		_siftup(self._heap, ind)

		heapq.heappop(self._heap)
		del self._lookup_dict[entry.key]

	def add(self, key: KeyType, value: float, data: DataType) -> 'AddressablePQ.Item[KeyType, DataType]':
		entry = AddressablePQ._Entry(value, self._change_index, key, data)
		self._change_index += 1
		heapq.heappush(self._heap, entry)
		self._lookup_dict[key] = entry
		return AddressablePQ.Item(entry)

	def change_value(self, identifier: Union[KeyType, 'AddressablePQ.Item[KeyType, DataType]'], value: float) -> None:
		entry = self._entry_from_identifier(identifier)
		self._change_value(entry, value)

	def _change_value(self, entry: 'AddressablePQ._Entry[KeyType, DataType]', value: float) -> None:
		entry.value, entry.change_index = value, self._change_index
		self._change_index += 1
		# impl A
		# heapq.heapify(self._heap)

		# impl B
		ind = self._heap.index(entry)
		_siftup(self._heap, ind)

	def add_or_change(self, key: KeyType, value: float, data: DataType) -> 'AddressablePQ.Item[KeyType, DataType]':
		try:
			entry = self._lookup_dict[key]
			self._change_value(entry, value)
			return AddressablePQ.Item(entry)
		except KeyError:
			return self.add(key, value, data)

	def peek(self) -> 'AddressablePQ.Item[KeyType, DataType]':
		entry = self._heap[0]
		return AddressablePQ.Item(entry)

	def pop(self) -> Tuple[KeyType, float, DataType]:
		entry = heapq.heappop(self._heap)
		del self._lookup_dict[entry.key]
		return entry.key, entry.value, entry.data


def _siftup(heap: List[Any], pos: int) -> None:
	# From Python 3.8
	# https://github.com/python/cpython/blob/3.8/Lib/heapq.py
	# The only thing changed is passing 0 as startpos to heapq._siftdown().

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
		pos = childpos
		childpos = 2*pos + 1
	# The leaf at pos is empty now.  Put newitem there, and bubble it up
	# to its final resting place (by sifting its parents down).
	heap[pos] = newitem
	heapq._siftdown(heap, 0, pos)
