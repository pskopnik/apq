# distutils: language = c++
# cython: language_level = 3

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map
from libcpp.limits cimport numeric_limits

from cython.operator cimport dereference, preincrement


cdef cppclass Entry:
	unsigned long long int index
	string key
	double value
	unsigned long long int change_ts
	object data


cdef class Item:
	cdef Entry* _e
	cdef unicode _cached_key
	cdef bint _cached_key_set

	@property
	def key(self):
		if not self._cached_key_set:
			self._cached_key = self._e.key.decode('utf8')

		return self._cached_key

	@property
	def value(self):
		return self._e.value

	@property
	def data(self):
		return self._e.data

	@staticmethod
	cdef from_pointer(Entry* e):
		i = Item()
		i._e = e
		return i


cdef class KeyedPQ:
	cdef vector[Entry*] _heap
	cdef unordered_map[string, Entry] _lookup_map
	cdef unsigned long long int _ts
	cdef bint _max_heap

	def __cinit__(self, bint max_heap=False):
		self._max_heap = max_heap

	def __len__(self):
		return self._heap.size()

	def __contains__(self, object identifier):
		try:
			self._entry_from_identifier(identifier)
		except:
			return False
		else:
			return True

	def __getitem__(self, object identifier):
		cdef Entry* e = self._entry_from_identifier(identifier)
		return Item.from_pointer(e)

	def __delitem__(self, object identifier):
		cdef Entry* e = self._entry_from_identifier(identifier)
		# TODO siftdown only?
		self._change_value(e, self._lowest_value(), 0)
		self._pop_heap()
		self._lookup_map.erase(e.key)

	def add(self, object key, double value, object data):
		cdef Entry e
		e.key = stringify(key)

		if self._lookup_map.count(e.key) > 0:
			raise KeyError("Duplicate key: key already exists in PQ")

		e.index = self._heap.size()
		e.value = value
		e.change_ts = preincrement(self._ts)
		e.data = data

		self._lookup_map[e.key] = e
		cdef Entry* e_pointer = &self._lookup_map[e.key]

		self._heap.push_back(e_pointer)
		self._siftdown(0, e.index)

		return Item.from_pointer(e_pointer)

	def change_value(self, object identifier, double value):
		cdef Entry* e = self._entry_from_identifier(identifier)
		self._change_value(e, value, preincrement(self._ts))
		return Item.from_pointer(e)

	def add_or_change_value(self, object key, double value, object data):
		cdef string string_key = stringify(key)
		cdef Entry* e
		try:
			e = self._lookup(string_key)
			self._change_value(e, value, preincrement(self._ts))
			return Item.from_pointer(e)
		except KeyError:
			return self.add(key, value, data)

	def peek(self):
		if self._heap.size() == 0:
			raise IndexError("PQ is empty")

		return Item.from_pointer(self._heap[0])

	def pop(self):
		if self._heap.size() == 0:
			raise IndexError("PQ is empty")

		cdef Entry* e = self._pop_heap()

		cdef double value = e.value
		cdef string key = e.key
		cdef object data = e.data

		self._lookup_map.erase(key)

		return key.decode('utf8'), value, data

	def _export(self):
		l = []
		for i in range(self._heap.size()):
			l.append(self._heap[i].value)
		return l

	def _verify_invariants(self):
		if self._heap.size() != self._lookup_map.size():
			# heap and lookup map don't have the same size
			return False

		cdef Entry* e
		cdef unsigned long long i, leftchildpos, rightchildpos
		cdef vector[Entry*].iterator begin_it, it

		begin_it = self._heap.begin()
		it = begin_it
		while it != self._heap.end():
			e = dereference(it)
			i = it - begin_it
			if e.index != i:
				# wrong index is stored in the entry
				return False

			if &self._lookup_map[e.key] != e:
				# key is not mapped to entry
				return False

			leftchildpos = 2 * i + 1
			rightchildpos = leftchildpos + 1
			if leftchildpos < self._heap.size() and self._compare(leftchildpos, i):
					# left child is less than parent
					return False
			if rightchildpos < self._heap.size() and self._compare(rightchildpos, i):
					# right child is less than parent
					return False

			preincrement(it)

		return True

	cdef Entry* _pop_heap(self):
		# Asserts that there is at least one element on the heap
		cdef Entry* e = self._heap[0]
		if self._heap.size() > 1:
			self._swap(0, self._heap.size() - 1)
		self._heap.pop_back()
		self._siftup(0)
		return e

	cdef void _change_value(self, Entry* e, double value, unsigned long long int change_ts):
		e.value = value
		e.change_ts = change_ts

		self._siftup(e.index)

	cdef void _swap(self, unsigned long long int a, unsigned long long int b):
		cdef Entry* a_entry = self._heap[a]
		cdef Entry* b_entry = self._heap[b]
		self._heap[a] = b_entry
		self._heap[b] = a_entry
		b_entry.index = a
		a_entry.index = b

	cdef bint _compare(self, unsigned long long int a, unsigned long long int b):
		cdef Entry* a_entry = self._heap[a]
		cdef Entry* b_entry = self._heap[b]
		if a_entry.value < b_entry.value:
			# a < b. Return True if min_heap, return False if max_heap
			return not self._max_heap
		if a_entry.value == b_entry.value and a_entry.change_ts < b_entry.change_ts:
			# a --happened before-> b
			return True
		return self._max_heap


	cdef double _lowest_value(self):
		if self._max_heap:
			return numeric_limits[double].infinity()
		else:
			return -numeric_limits[double].infinity()

	cdef int _siftdown(self, unsigned long long int startpos, unsigned long long int pos):

		# 'self._heap' is a heap at all indices >= startpos, except possibly
		# for pos. pos is the index of a leaf with a possibly out-of-order
		# value. Restore the heap invariant.

		# Asserts that startpos and pos are valid positions in the heap,
		# startpos < pos (or no work is done)

		# From
		# https://github.com/python/cpython/blob/3.8/Lib/heapq.py
		# https://github.com/python/cpython/blob/3.8/Modules/_heapqmodule.c

		cdef unsigned long long int parentpos

		while pos > startpos:
			parentpos = (pos - 1) >> 1
			if not self._compare(pos, parentpos):
				# parentpos <= pos
				break

			self._swap(pos, parentpos)
			pos = parentpos

		return 0

	cdef int _siftup(self, unsigned long long int pos):

		# 'self._heap' is a heap at all indices of the sub-tree (transitive
		# children) of pos except possibly at pos. Bubble the smaller child of
		# pos up (recursively until reaching a leave), then use siftdown to
		# move the entry originally at pos to the right place.

		# Asserts that pos is a valid position in the heap

		# From
		# https://github.com/python/cpython/blob/3.8/Lib/heapq.py
		# https://github.com/python/cpython/blob/3.8/Modules/_heapqmodule.c

		# See note at the end of this method
		# cdef unsigned long long int startpos

		cdef unsigned long long int endpos, childpos, limit

		endpos = self._heap.size()

		# See note at the end of this method
		# startpos = pos

		limit = endpos >> 1
		while pos < limit:
			childpos = 2 * pos + 1
			rightchildpos = childpos + 1
			if rightchildpos < endpos:
				if not self._compare(childpos, rightchildpos):
					# rightchildpos <= childpos
					childpos = rightchildpos
			self._swap(childpos, pos)
			pos = childpos

		# This is the original line from Python 3.8. "startpos" leads to issues when
		# siftup is called on an arbitrary "pos". This never occurs in standard
		# library, as siftup is always called with pos = 0.
		# return self._siftdown(startpos, pos)

		return self._siftdown(0, pos)

	cdef Entry* _lookup(self, string key) except +KeyError:
		return &self._lookup_map.at(key)

	cdef Entry* _entry_from_identifier(self, object identifier) except *:
		cdef Entry* e
		if type(identifier) is Item:
			if (<Item>identifier)._e is NULL:
				raise KeyError("Passed identifier (of type Item) does not reference a PQ entry")
			e = (<Item>identifier)._e
			if e.index >= self._heap.size() or self._heap.at(e.index) != e:
				raise KeyError("Passed identifier (of type Item) is not known to the PQ")
			return e

		cdef string key = stringify(identifier)
		return self._lookup(key)


cdef string stringify(object s):
	if isinstance(s, unicode):
		return <string>(<unicode>s).encode('utf8')

	return <string>(s)
