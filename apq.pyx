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

		# note adapted from vector.pxd:
		# these should really be container_type.size_type, ...
		# but cython doesn't support deferred access on template arguments

		ctypedef size_t size_type
		ctypedef ptrdiff_t difference_type

		ctypedef vector[value_type].iterator iterator
		ctypedef vector[value_type].const_iterator const_iterator

		BinHeap() except +

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
		iterator begin()
		iterator end()
		const_iterator const_begin "begin"()
		const_iterator const_end "end"()
		const_iterator cbegin()
		const_iterator cend()

	cdef cppclass MinHeapCompare[T]:
		pass

	cdef cppclass MaxHeapCompare[T]:
		pass

	cdef cppclass MinBinHeap[T, Container=*, SetIndex=*](BinHeap[T, Container, MinHeapCompare[T], SetIndex]):
		ctypedef T value_type
		ctypedef Container container_type
		ctypedef MinHeapCompare[T] Compare
		ctypedef SetIndex value_set_index

		# note adapted from vector.pxd:
		# these should really be container_type.size_type, ...
		# but cython doesn't support deferred access on template arguments

		ctypedef size_t size_type
		ctypedef ptrdiff_t difference_type

		ctypedef vector[value_type].iterator iterator
		ctypedef vector[value_type].const_iterator const_iterator

	cdef cppclass MaxBinHeap[T, Container=*, SetIndex=*](BinHeap[T, Container, MaxHeapCompare[T], SetIndex]):
		ctypedef T value_type
		ctypedef Container container_type
		ctypedef MaxHeapCompare[T] Compare
		ctypedef SetIndex value_set_index

		# note adapted from vector.pxd:
		# these should really be container_type.size_type, ...
		# but cython doesn't support deferred access on template arguments

		ctypedef size_t size_type
		ctypedef ptrdiff_t difference_type

		ctypedef vector[value_type].iterator iterator
		ctypedef vector[value_type].const_iterator const_iterator


cdef extern from "src/_apq_helpers.cpp" nogil:
	cdef cppclass APQEntry[T]:
		size_t index
		string key
		double value
		size_t change_ts
		T data

		APQEntry()
		APQEntry(size_t, string, double, size_t, T)

		bint minHeapCompare(APQEntry[T]&)
		bint maxHeapCompare(APQEntry[T]&)

	cdef cppclass PointerWrapper[T]:
		PointerWrapper(T*)
		PointerWrapper(T&)
		T* get()
		T& operator*()

# TODO: figure out how properly do this: templates cannot be instantiated with "object"
cdef cppclass PyObjectWrapper:
	object obj


ctypedef APQEntry[PyObjectWrapper] Entry
ctypedef PointerWrapper[APQEntry[PyObjectWrapper]] WrappedEntry


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
		return self._e.data.obj

	@staticmethod
	cdef from_pointer(Entry* e):
		i = Item()
		i._e = e
		return i


cdef class KeyedPQ:
	cdef MinBinHeap[WrappedEntry] _heap
	cdef unordered_map[string, Entry] _lookup_map
	cdef unsigned long long int _ts

	def __cinit__(self, bint max_heap=False):
		if max_heap:
			raise NotImplementedError("KeyedPQ only supports min_heap")

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
		self._heap.remove(e.index)
		self._lookup_map.erase(e.key)

	def add(self, object key, double value, object data):
		cdef Entry e
		e.key = stringify(key)

		if self._lookup_map.count(e.key) > 0:
			raise KeyError("Duplicate key: key already exists in PQ")

		e.value = value
		e.change_ts = preincrement(self._ts)
		e.data.obj = data

		self._lookup_map[e.key] = e
		cdef Entry* e_pointer = &self._lookup_map[e.key]

		self._heap.push(WrappedEntry(e_pointer))

		return Item.from_pointer(e_pointer)

	def change_value(self, object identifier, double value):
		cdef Entry* e = self._entry_from_identifier(identifier)
		e.value = value
		e.change_ts = preincrement(self._ts)
		self._heap.fix(e.index)
		return Item.from_pointer(e)

	def add_or_change_value(self, object key, double value, object data):
		cdef string string_key = stringify(key)
		cdef Entry* e
		try:
			e = self._lookup(string_key)
			e.value = value
			e.change_ts = preincrement(self._ts)
			self._heap.fix(e.index)
			return Item.from_pointer(e)
		except KeyError:
			return self.add(key, value, data)

	def peek(self):
		if self._heap.size() == 0:
			raise IndexError("PQ is empty")

		return Item.from_pointer(self._heap.top().get())

	def pop(self):
		if self._heap.size() == 0:
			raise IndexError("PQ is empty")

		cdef Entry* e = self._heap.top().get()

		cdef double value = e.value
		cdef string key = e.key
		cdef object data = e.data.obj

		self._heap.pop()
		self._lookup_map.erase(key)

		return key.decode('utf8'), value, data

	cdef Entry* _lookup(self, string key) except +KeyError:
		return &self._lookup_map.at(key)

	cdef Entry* _entry_from_identifier(self, object identifier) except *:
		cdef Entry* e
		if type(identifier) is Item:
			if (<Item>identifier)._e is NULL:
				raise KeyError("Passed identifier (of type Item) does not reference a PQ entry")
			e = (<Item>identifier)._e
			if e.index >= self._heap.size() or dereference(self._heap.begin() + e.index).get() != e:
				raise KeyError("Passed identifier (of type Item) is not known to the PQ")
			return e

		cdef string key = stringify(identifier)
		return self._lookup(key)

	def _export(self):
		l = []

		cdef MinBinHeap[WrappedEntry].iterator begin_it, end_it, it

		begin_it = self._heap.begin()
		end_it = self._heap.end()
		it = begin_it
		while it != end_it:
			l.append(dereference(it).get().value)
			preincrement(it)

		return l

	def _verify_invariants(self):
		if self._heap.size() != self._lookup_map.size():
			# heap and lookup map don't have the same size
			return False

		cdef Entry* e
		cdef MinBinHeap[WrappedEntry].size_type i, left_child_ind, right_child_ind
		cdef MinBinHeap[WrappedEntry].iterator begin_it, end_it, it

		begin_it = self._heap.begin()
		end_it = self._heap.end()
		it = begin_it
		while it != end_it:
			e = dereference(it).get()
			i = it - begin_it
			if e.index != i:
				# wrong index is stored in the entry
				return False

			if &self._lookup_map[e.key] != e:
				# key is not mapped to entry
				return False

			left_child_ind = 2 * i + 1
			right_child_ind = left_child_ind + 1
			if left_child_ind < self._heap.size() and dereference(begin_it + left_child_ind).get().minHeapCompare(dereference(e)):
					# left child is less than parent
					return False
			if right_child_ind < self._heap.size() and dereference(begin_it + right_child_ind).get().minHeapCompare(dereference(e)):
					# right child is less than parent
					return False

			preincrement(it)

		return True


cdef string stringify(object s):
	if isinstance(s, unicode):
		return <string>(<unicode>s).encode('utf8')

	return <string>(s)
