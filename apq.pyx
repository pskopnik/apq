# distutils: language = c++
# cython: language_level = 3

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map
from libcpp.limits cimport numeric_limits

from cython.operator cimport dereference, preincrement


cdef extern from "src/binheap.hpp" nogil:
	cdef cppclass BinHeap[T, Container=*, Compare=*, SetIndex=*]:
		ctypedef T value_type
		ctypedef Container container_type
		ctypedef Compare value_compare
		ctypedef SetIndex value_set_index

	cdef cppclass AnyBinHeap[T]:
		ctypedef T value_type

		# note adapted from vector.pxd:
		# these should really be container_type.size_type, ...
		# but cython doesn't support deferred access on template arguments

		ctypedef size_t size_type
		ctypedef ptrdiff_t difference_type

		ctypedef vector[value_type].iterator iterator
		ctypedef vector[value_type].const_iterator const_iterator

		cppclass ordered_iterator:
			T& operator*()
			ordered_iterator operator++()
			bint operator==(ordered_iterator)
			bint operator!=(ordered_iterator)
		cppclass const_ordered_iterator(ordered_iterator):
			pass

		cppclass ordered_iterable:
			ordered_iterator begin()
			ordered_iterator end()
			const_ordered_iterator cbegin()
			const_ordered_iterator cend()
		cppclass const_ordered_iterable:
			const_ordered_iterator begin()
			const_ordered_iterator end()
			const_ordered_iterator cbegin()
			const_ordered_iterator cend()

		AnyBinHeap() except +
		AnyBinHeap(BinHeap[T]) except +
		AnyBinHeap& operator=(BinHeap[T]) except +

		void push(value_type&) except +
		void fix(size_type)
		void fix(iterator)
		void fix(const_iterator)
		void remove(size_type)
		void remove(iterator)
		void remove(const_iterator)
		void pop()
		bint empty()
		size_type size()
		value_type& top()
		T& operator[](size_type)
		iterator begin()
		iterator end()
		const_iterator const_begin "begin"()
		const_iterator const_end "end"()
		const_iterator cbegin()
		const_iterator cend()
		ordered_iterable orderedIterable()
		const_ordered_iterable const_orderedIterable "orderedIterable"()

	cdef cppclass MinHeapCompare[T]:
		pass

	cdef cppclass MaxHeapCompare[T]:
		pass

	cdef cppclass MinBinHeap[T, Container=*, SetIndex=*](BinHeap[T, Container, MinHeapCompare[T], SetIndex]):
		MinBinHeap()

	cdef cppclass MaxBinHeap[T, Container=*, SetIndex=*](BinHeap[T, Container, MaxHeapCompare[T], SetIndex]):
		MaxBinHeap()

	cdef cppclass StandardEntry[T, V=*, ChangeTSTracking=*, SetIndex=*]:
		ctypedef double value_type
		ctypedef T data_type
		ctypedef size_t ts_type
		ctypedef StandardEntry entry_type

		StandardEntry()
		StandardEntry(value_type, data_type&, ts_type)

		void set(value_type, data_type&, ts_type)
		value_type getValue()
		void setValue(value_type)
		void setValue(value_type, ts_type)
		ts_type getChangeTS()
		void setChangeTS(ts_type)
		data_type& getData()
		void setData(data_type&)
		void setData(data_type&, ts_type)
		bint minHeapCompare(entry_type&)
		bint maxHeapCompare(entry_type&)

cdef extern from "src/_apq_helpers.cpp" nogil:
	cdef cppclass APQPayload[T]:
		size_t index
		string key
		T data


cdef cppclass PyObjectWrapper:
	# PyObjectWrapper wraps an owned reference to a Python object.
	#
	# Reference counting operations are performed on construction, assigment
	# and destruction. This makes PyObjectWrapper useful for storing Python
	# objects in C++ containers.
	object obj


ctypedef APQPayload[PyObjectWrapper] Entry
ctypedef StandardEntry[Entry*] HeapEntry


cdef class Item:
	cdef AnyBinHeap[HeapEntry]* _heap
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
		return dereference(self._heap)[self._e.index].getValue()

	@property
	def data(self):
		return self._e.data.obj

	def __eq__(self, Item other):
		return self._heap == other._heap and self._e == other._e

	def __ne__(self, Item other):
		return not self.__eq__(other)

	@staticmethod
	cdef from_pointer(AnyBinHeap[HeapEntry]* heap, Entry* e):
		i = Item()
		i._heap = heap
		i._e = e
		return i


cdef class KeyedPQ:
	cdef AnyBinHeap[HeapEntry] _heap
	cdef unordered_map[string, Entry] _lookup_map
	cdef unsigned long long int _ts
	cdef bint _max_heap

	def __cinit__(self, bint max_heap=False):
		self._max_heap = max_heap
		if max_heap:
			self._heap = MaxBinHeap[HeapEntry]()
		else:
			self._heap = MinBinHeap[HeapEntry]()

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
		return Item.from_pointer(&self._heap, e)

	def __delitem__(self, object identifier):
		cdef Entry* e = self._entry_from_identifier(identifier)
		self._heap.remove(e.index)
		self._lookup_map.erase(e.key)

	def add(self, object key, double value, object data):
		cdef Entry e
		e.key = stringify(key)

		if self._lookup_map.count(e.key) > 0:
			raise KeyError("Duplicate key: key already exists in PQ")

		e.data.obj = data

		self._lookup_map[e.key] = e
		cdef Entry* e_pointer = &self._lookup_map[e.key]

		self._heap.push(HeapEntry(
			value,
			e_pointer,
			preincrement(self._ts),
		))

		return Item.from_pointer(&self._heap, e_pointer)

	def change_value(self, object identifier, double value):
		cdef Entry* e = self._entry_from_identifier(identifier)
		self._heap[e.index].setValue(value, preincrement(self._ts))
		self._heap.fix(e.index)
		return Item.from_pointer(&self._heap, e)

	def add_or_change_value(self, object key, double value, object data):
		cdef string string_key = stringify(key)
		cdef Entry* e
		try:
			e = self._lookup(string_key)
			self._heap[e.index].setValue(value, preincrement(self._ts))
			self._heap.fix(e.index)
			return Item.from_pointer(&self._heap, e)
		except KeyError:
			return self.add(key, value, data)

	def peek(self):
		if self._heap.size() == 0:
			raise IndexError("PQ is empty")

		return Item.from_pointer(&self._heap, self._heap.top().getData())

	def pop(self):
		if self._heap.size() == 0:
			raise IndexError("PQ is empty")

		cdef HeapEntry heapEntry = self._heap.top()
		cdef Entry* e = heapEntry.getData()

		cdef double value = heapEntry.getValue()
		cdef string key = e.key
		cdef object data = e.data.obj

		self._heap.pop()
		self._lookup_map.erase(key)

		return key.decode('utf8'), value, data

	def ordered_iter(self):
		cdef AnyBinHeap[HeapEntry].ordered_iterable iterable = self._heap.orderedIterable()
		cdef HeapEntry entry
		for entry in iterable:
			yield Item.from_pointer(&self._heap, entry.getData())

	cdef Entry* _lookup(self, string key) except +KeyError:
		return &self._lookup_map.at(key)

	cdef Entry* _entry_from_identifier(self, object identifier) except *:
		cdef Entry* e
		if type(identifier) is Item:
			if (<Item>identifier)._e is NULL:
				raise KeyError("Passed identifier (of type Item) does not reference a PQ entry")
			e = (<Item>identifier)._e
			if e.index >= self._heap.size() or self._heap[e.index].getData() != e:
				raise KeyError("Passed identifier (of type Item) is not known to the PQ")
			return e

		cdef string key = stringify(identifier)
		return self._lookup(key)

	def _export(self):
		l = []

		cdef HeapEntry entry
		for entry in self._heap:
			l.append(entry.getValue())

		return l

	def _verify_invariants(self):
		if self._heap.size() != self._lookup_map.size():
			# heap and lookup map don't have the same size
			return False

		cdef Entry* e
		cdef AnyBinHeap[HeapEntry].size_type i, left_child_ind, right_child_ind
		cdef AnyBinHeap[HeapEntry].iterator begin_it, end_it, it

		begin_it = self._heap.begin()
		end_it = self._heap.end()
		it = begin_it
		while it != end_it:
			e = dereference(it).getData()
			i = it - begin_it
			if e.index != i:
				# wrong index is stored in the entry
				return False

			if &self._lookup_map[e.key] != e:
				# key is not mapped to entry
				return False

			left_child_ind = 2 * i + 1
			right_child_ind = left_child_ind + 1
			if left_child_ind < self._heap.size() and self._compare(self._heap[left_child_ind], dereference(it)):
					# left child is less than parent
					return False
			if right_child_ind < self._heap.size() and self._compare(self._heap[left_child_ind], dereference(it)):
					# right child is less than parent
					return False

			preincrement(it)

		return True

	cdef bint _compare(self, HeapEntry& lhs, HeapEntry& rhs):
		if self._max_heap:
			return lhs.maxHeapCompare(rhs)
		else:
			return lhs.minHeapCompare(rhs)


cdef string stringify(object s) except *:
	if isinstance(s, unicode):
		return <string>(<unicode>s).encode('utf8')

	return <string?>(s)
