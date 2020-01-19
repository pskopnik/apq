import heapq
import itertools
import math
import random
import typing
import unittest

from apq import KeyedPQ, Item


class DummyClass(object):
	pass


class InitialisationTest(unittest.TestCase):
	def test_correct(self) -> None:
		self.assertEqual(len(KeyedPQ()), 0)
		self.assertEqual(len(KeyedPQ([])), 0)

		dummy = DummyClass()
		pq: KeyedPQ[DummyClass] = KeyedPQ([('a', 1.0, dummy)])
		self.assertEqual(len(pq), 1)
		item = pq.peek()
		self.assertEqual(item.key, 'a')
		self.assertEqual(item.value, 1.0)
		self.assertIs(item.data, dummy)

	def test_incorrect(self) -> None:
		with self.assertRaises(TypeError):
			typing.cast(typing.Any, KeyedPQ)([], [])

		with self.assertRaises(ValueError):
			KeyedPQ(typing.cast(typing.Any, [tuple()]))
		with self.assertRaises(ValueError):
			KeyedPQ(typing.cast(typing.Any, [('a',)]))
		with self.assertRaises(ValueError):
			KeyedPQ(typing.cast(typing.Any, [('a', 1.0)]))

		with self.assertRaises(TypeError):
			KeyedPQ(typing.cast(typing.Any, [(1.0, 1.0, None)]))
		with self.assertRaises(TypeError):
			KeyedPQ(typing.cast(typing.Any, [('a', 'a', None)]))

	def test_duplicate_key(self) -> None:
		with self.assertRaises(KeyError):
			KeyedPQ([
				('a', 1.0, None),
				('a', 3.0, None),
			])


class KeyTest(unittest.TestCase):
	def setUp(self) -> None:
		self.pq: KeyedPQ[None] = KeyedPQ()

	def _assert_contained(self, identifier: "typing.Union[str, Item[None]]", key: "typing.Optional[str]"=None) -> None:
		key_str: str
		if key is not None:
			key_str = key
		else:
			if isinstance(identifier, str):
				key_str = identifier
			else:
				raise ValueError("Argument key required if identifier is not a string")

		self.assertTrue(identifier in self.pq)
		self.assertEqual(self.pq[identifier].key, key_str)
		item = self.pq.get(identifier)
		self.assertIsNotNone(item)
		self.assertEqual(typing.cast("Item[None]", item).key, key_str)

	def _assert_not_contained(self, identifier: "typing.Union[str, Item[None]]") -> None:
		self.assertFalse(identifier in self.pq)
		with self.assertRaises(KeyError):
			item = self.pq[identifier]
		self.assertIsNone(self.pq.get(identifier))

	def test_existing_str_key(self) -> None:
		self.pq.add('a', 0.0, None)

		self._assert_contained('a')

	def test_unknown_str_key(self) -> None:
		self._assert_not_contained('a')

	def test_removed_str_key(self) -> None:
		self.pq.add('a', 0.0, None)
		del self.pq['a']

		self._assert_not_contained('a')

		self.pq.add('b', 0.0, None)
		self.pq.pop()

		self._assert_not_contained('b')

	def test_existing_item_key(self) -> None:
		item = self.pq.add('a', 0.0, None)

		self._assert_contained(item, key='a')

	def test_unknown_item_key(self) -> None:
		item: Item[None] = Item()

		self._assert_not_contained(item)

	def test_others_item_key(self) -> None:
		pq2: KeyedPQ[None] = KeyedPQ()
		item2 = pq2.add('a', 0.0, None)

		self._assert_not_contained(item2)

		self.pq.add('a', 0.0, None)

		self._assert_not_contained(item2)

	def test_removed_item_key(self) -> None:
		item_a = self.pq.add('a', 0.0, None)
		del self.pq['a']

		self._assert_not_contained(item_a)

		item_b = self.pq.add('b', 0.0, None)
		self.pq.pop()

		self._assert_not_contained(item_b)

	def test_add_duplicate_str_key(self) -> None:
		self.pq.add('a', 0.0, None)

		with self.assertRaises(KeyError):
			self.pq.add('a', 3.0, None)

	def test_invalid_key_type(self) -> None:
		self.pq.add('a', 0.0, None)

		with self.assertRaises(TypeError):
			self.pq[typing.cast(typing.Any, None)]

		with self.assertRaises(TypeError):
			self.pq[typing.cast(typing.Any, 4)]

		with self.assertRaises(TypeError):
			self.pq[typing.cast(typing.Any, 4.5)]

		with self.assertRaises(TypeError):
			self.pq[typing.cast(typing.Any, DummyClass())]

		with self.assertRaises(TypeError):
			self.pq[typing.cast(typing.Any, (4,))]

		with self.assertRaises(TypeError):
			self.pq[typing.cast(typing.Any, lambda x: x)]

		with self.assertRaises(TypeError):
			self.pq[typing.cast(typing.Any, [4])]


class ValueTest(unittest.TestCase):
	def setUp(self) -> None:
		self.pq: KeyedPQ[None] = KeyedPQ()

	def test_change_value(self) -> None:
		item_added = self.pq.add('a', 0.0, None)

		item_changed = self.pq.change_value('a', 5.0)

		self.assertEqual(item_added.value, item_changed.value)
		self.assertEqual(item_changed.value, 5.0)
		self.assertEqual(len(self.pq), 1)
		self.assertTrue(item_added in self.pq)

	def test_add_or_change_value_change(self) -> None:
		item_added = self.pq.add('a', 0.0, None)

		item_changed = self.pq.add_or_change_value('a', 5.0, None)

		self.assertEqual(item_added.value, item_changed.value)
		self.assertEqual(item_changed.value, 5.0)
		self.assertEqual(len(self.pq), 1)
		self.assertTrue(item_added in self.pq)

	def test_add_or_change_value_add(self) -> None:
		item_added = self.pq.add('a', 0.0, None)

		item_changed = self.pq.add_or_change_value('b', 5.0, None)

		self.assertEqual(item_changed.key, 'b')
		self.assertEqual(item_changed.value, 5.0)
		self.assertEqual(len(self.pq), 2)
		self.assertTrue(item_added in self.pq)
		self.assertTrue(item_changed in self.pq)

	def test_add_infinity(self) -> None:
		self.pq.add('a', math.inf, None)
		self.pq.add('b', 3000.0, None)

		key_first, _, _ = self.pq.pop()
		self.assertEqual(key_first, 'b')
		key_second, _, _ = self.pq.pop()
		self.assertEqual(key_second, 'a')

	def test_change_to_infinity(self) -> None:
		self.pq.add('a', 3.0, None)
		self.pq.add('b', 3000.0, None)

		self.pq.change_value('a', math.inf)

		key_first, _, _ = self.pq.pop()
		self.assertEqual(key_first, 'b')
		key_second, _, _ = self.pq.pop()
		self.assertEqual(key_second, 'a')


class MappingStyleInterfaceTest(unittest.TestCase):
	def setUp(self) -> None:
		self.pq: KeyedPQ[DummyClass] = KeyedPQ()

	def test_equality(self) -> None:
		self.assertTrue(self.pq == self.pq)
		self.assertFalse(self.pq != self.pq)

	def test_non_equality(self) -> None:
		pq2: KeyedPQ[None] = KeyedPQ()

		self.assertTrue(self.pq != pq2)
		self.assertFalse(self.pq == pq2)

		self.assertTrue(self.pq != None)
		self.assertFalse(self.pq == None)

		self.assertTrue(self.pq != 4.0)
		self.assertFalse(self.pq == 4.0)

	def test_get_item_default_non_existing(self) -> None:
		self.assertIsNone(self.pq.get('a'))
		self.assertIsNone(self.pq.get('a', default=None))
		self.assertEqual(self.pq.get('a', default=4.0), 4.0)

	def test_get_item_default_existing(self) -> None:
		dummy = DummyClass()
		self.pq.add('a', 1.0, dummy)

		item1 = self.pq.get('a')
		self.assertIsNotNone(item1)
		self.assertIsInstance(item1, Item) # Item[DummyClass]
		self.assertIs(typing.cast("Item[DummyClass]", item1).data, dummy)

		item2 = self.pq.get('a', default=None)
		self.assertIsNotNone(item2)
		self.assertIsInstance(item2, Item) # Item[DummyClass]
		self.assertIs(typing.cast("Item[DummyClass]", item2).data, dummy)

		item3 = self.pq.get('a', default=4.0)
		self.assertNotEqual(item3, 4.0)
		self.assertIsInstance(item3, Item) # Item[DummyClass]
		self.assertIs(typing.cast("Item[DummyClass]", item3).data, dummy)

	def test_collection_property(self) -> None:
		# Setup

		s: typing.Set[typing.Tuple[str, float, DummyClass]] = set()

		for i in range(1000):
			val = random.random()
			add_tuple = (str(i), val, DummyClass())
			self.pq.add(*add_tuple)
			s.add(add_tuple)

		# Test

		for key, value in self.pq.items():
			self.assertTrue(key in self.pq)
			self.assertTrue(value in self.pq)
			self.assertEqual(key, value.key)
			self.assertTrue((key, value.value, value.data) in s)
			s.remove((key, value.value, value.data))

		self.assertEqual(len(s), 0)

	def test_iterable_order(self,) -> None:
		# Setup

		for i in range(1000):
			val = random.random()
			self.pq.add(str(i), val, DummyClass())

		# Test

		zipped = itertools.zip_longest(
			self.pq.keys(),
			self.pq.values(),
			self.pq.items(),
			iter(self.pq),
		)

		for key, value, (item_key, item_value), iter_value in zipped:
			self.assertTrue(key in self.pq)

			self.assertEqual(key, value.key)
			self.assertEqual(key, item_key)
			self.assertEqual(key, item_value.key)
			self.assertEqual(key, iter_value.key)

			self.assertEqual(value.value, self.pq[key].value)
			self.assertEqual(value.value, item_value.value)
			self.assertEqual(value.value, iter_value.value)

			self.assertIs(value.data, self.pq[key].data)
			self.assertIs(value.data, item_value.data)
			self.assertIs(value.data, iter_value.data)


class ItemTest(unittest.TestCase):
	def setUp(self) -> None:
		self.pq: KeyedPQ[None] = KeyedPQ()

	def _assert_equal(self, a: typing.Any, b: typing.Any) -> None:
		self.assertTrue(a == b)
		self.assertFalse(a != b)

	def _assert_not_equal(self, a: typing.Any, b: typing.Any) -> None:
		self.assertTrue(a != b)
		self.assertFalse(a == b)

	def test_equality(self) -> None:
		item_added = self.pq.add('a', 0.0, None)
		item_changed = self.pq.change_value('a', 5.0)
		item_keyed = self.pq['a']
		item_top = self.pq.peek()

		self._assert_equal(item_added, item_changed)
		self._assert_equal(item_added, item_keyed)
		self._assert_equal(item_added, item_top)

		self._assert_equal(item_changed, item_keyed)
		self._assert_equal(item_changed, item_top)

		self._assert_equal(item_keyed, item_top)

	def test_non_equality(self) -> None:
		item_a = self.pq.add('a', 0.0, None)
		item_b = self.pq.add('b', 0.0, None)

		self._assert_not_equal(item_a, item_b)

	def test_different_heaps(self) -> None:
		pq2: KeyedPQ[None] = KeyedPQ()

		item_a = self.pq.add('a', 0.0, None)
		item_b = pq2.add('a', 0.0, None)

		self._assert_not_equal(item_a, item_b)

	def test_different_type(self) -> None:
		item_a = self.pq.add('a', 0.0, None)

		self._assert_not_equal(item_a, 'a')
		self._assert_not_equal(item_a, 0.0)
		self._assert_not_equal(item_a, None)

		self._assert_not_equal(item_a, self)
		self._assert_not_equal(item_a, self.pq)


class InvariantTest(unittest.TestCase):
	NUMBER_OF_ENTRIES = 10000

	def setUp(self) -> None:
		self.pq: KeyedPQ[None] = KeyedPQ()

	def _set_pq_from_iterable(self, iterable: typing.Iterable[typing.Tuple[str, float, None]]) -> None:
		self.pq = KeyedPQ(iterable)

	def test_build_heap_small(self) -> None:
		# Setup

		# Test

		for entry_num in range(100):
			self._set_pq_from_iterable(
				(str(i), random.random(), None) for i in range(entry_num)
			)

			self.assertTrue(self.pq._verify_invariants())
			self.assertEqual(len(self.pq), entry_num)

	def test_build_heap(self) -> None:
		# Setup

		# Test

		self._set_pq_from_iterable(
			(str(i), random.random(), None) for i in range(self.NUMBER_OF_ENTRIES)
		)

		self.assertTrue(self.pq._verify_invariants())
		self.assertEqual(len(self.pq), self.NUMBER_OF_ENTRIES)

	def test_add(self) -> None:
		# Setup

		# Test

		self.assertTrue(self.pq._verify_invariants())
		self.assertEqual(len(self.pq), 0)

		for i in range(self.NUMBER_OF_ENTRIES):
			val = random.random()
			self.pq.add(str(i), val, None)
			self.assertTrue(self.pq._verify_invariants())
			self.assertEqual(len(self.pq), i + 1)

	def test_pop(self) -> None:
		# Setup

		for i in range(self.NUMBER_OF_ENTRIES):
			val = random.random()
			self.pq.add(str(i), val, None)

		# Test

		self.assertTrue(self.pq._verify_invariants())
		self.assertEqual(len(self.pq), self.NUMBER_OF_ENTRIES)

		for i in range(self.NUMBER_OF_ENTRIES):
			_, _, _ = self.pq.pop()
			self.assertTrue(self.pq._verify_invariants())
			self.assertEqual(len(self.pq), self.NUMBER_OF_ENTRIES - i - 1)

	def test_change_value(self) -> None:
		# Setup

		for i in range(self.NUMBER_OF_ENTRIES):
			val = random.random()
			self.pq.add(str(i), val, None)

		# Test

		self.assertTrue(self.pq._verify_invariants())
		self.assertEqual(len(self.pq), self.NUMBER_OF_ENTRIES)

		for i in range(self.NUMBER_OF_ENTRIES):
			val = random.random()
			self.pq.change_value(str(i), val)
			self.assertTrue(self.pq._verify_invariants())

	def test_delete(self) -> None:
		# Setup

		for i in range(self.NUMBER_OF_ENTRIES):
			val = random.random()
			self.pq.add(str(i), val, None)

		# Test

		self.assertTrue(self.pq._verify_invariants())
		self.assertEqual(len(self.pq), self.NUMBER_OF_ENTRIES)

		for i in range(self.NUMBER_OF_ENTRIES):
			del self.pq[str(i)]
			self.assertTrue(self.pq._verify_invariants())
			self.assertEqual(len(self.pq), self.NUMBER_OF_ENTRIES - i - 1)


class MaxHeapInvariantTest(InvariantTest):
	def setUp(self) -> None:
		self.pq: KeyedPQ[None] = KeyedPQ(max_heap=True)

	def _set_pq_from_iterable(self, iterable: typing.Iterable[typing.Tuple[str, float, None]]) -> None:
		self.pq = KeyedPQ(iterable, max_heap=True)


class HeapCompareTest(unittest.TestCase):
	def test_incremental_push_small(self) -> None:
		for n in itertools.chain.from_iterable(itertools.repeat(i, 1000) for i in range(10)):
			# Setup

			pq: KeyedPQ[None] = KeyedPQ()
			heap: typing.List[float] = []

			# Test

			for i in range(n):
				val = random.random()
				pq.add(str(i), val, None)
				heapq.heappush(heap, val)
				self.assertEqual(pq._export(), heap)

	def test_incremental_push(self) -> None:
		for n in range(1000):
			# Setup

			pq: KeyedPQ[None] = KeyedPQ()
			heap: typing.List[float] = []

			# Test

			for i in range(n):
				val = random.random()
				pq.add(str(i), val, None)
				heapq.heappush(heap, val)
				self.assertEqual(pq._export(), heap)

	def test_incremental_pop_small(self) -> None:
		for n in itertools.chain.from_iterable(itertools.repeat(i, 1000) for i in range(10)):
			# Setup

			pq: KeyedPQ[None] = KeyedPQ()
			heap: typing.List[float] = []

			for i in range(n):
				val = random.random()
				pq.add(str(i), val, None)
				heapq.heappush(heap, val)

			# Test

			for _ in range(n):
				self.assertEqual(pq.pop()[1], heapq.heappop(heap))
				self.assertEqual(pq._export(), heap)

	def test_incremental_pop(self) -> None:
		for n in range(1000):
			# Setup

			pq: KeyedPQ[None] = KeyedPQ()
			heap: typing.List[float] = []

			for i in range(n):
				val = random.random()
				pq.add(str(i), val, None)
				heapq.heappush(heap, val)

			# Test

			for _ in range(n):
				self.assertEqual(pq.pop()[1], heapq.heappop(heap))
				self.assertEqual(pq._export(), heap)

	def test_incremental_change_value(self) -> None:
		# Setup

		pq: KeyedPQ[None] = KeyedPQ()
		heap: typing.List[typing.List[float]] = []
		heap_lookup_dict: typing.Dict[str, typing.List[float]] = {}

		for i in range(1000):
			val = random.random()
			key = str(i)
			pq.add(key, val, None)
			heap_entry = [val]
			heap_lookup_dict[key] = heap_entry
			heapq.heappush(heap, heap_entry)

		# Test

		for i in range(1000):
			val = random.random()
			key = str(i)
			pq.change_value(key, val)
			heap_lookup_dict[key][0] = val
			heapq.heapify(heap)
			self.assertEqual(pq._export(), [e[0] for e in heap])

	def test_change_value(self) -> None:
		# Setup

		pq: KeyedPQ[None] = KeyedPQ()
		heap: typing.List[typing.List[float]] = []
		heap_lookup_dict: typing.Dict[str, typing.List[float]] = {}

		for i in range(10000):
			val = random.random()
			key = str(i)
			pq.add(key, val, None)
			heap_entry = [val]
			heap_lookup_dict[key] = heap_entry
			heapq.heappush(heap, heap_entry)

		for i in range(10000):
			val = random.random()
			key = str(i)
			pq.change_value(key, val)
			heap_lookup_dict[key][0] = val
			heapq.heapify(heap)

		# Test

		self.assertEqual(pq._export(), [e[0] for e in heap])


class EndToEndTest(unittest.TestCase):
	def setUp(self) -> None:
		self.l: typing.List[float] = []
		self.pq: KeyedPQ[None] = KeyedPQ()

	def _sort_l(self) -> None:
		self.l.sort()

	def _set_pq_from_iterable(self, iterable: typing.Iterable[typing.Tuple[str, float, None]]) -> None:
		self.pq = KeyedPQ(iterable)

	def test_build_heap(self) -> None:
		# Setup

		def iterable() -> typing.Iterable[typing.Tuple[str, float, None]]:
			for i in range(10000):
				val = random.random()
				self.l.append(val)
				yield (str(i), val, None)

		self._set_pq_from_iterable(iterable())

		self._sort_l()

		# Test

		self.assertEqual(len(self.pq), len(self.l))

		for i, val in enumerate(addressable_pq_pop_all(self.pq)):
			self.assertEqual(val, self.l[i])

	def test_pop(self) -> None:
		# Setup

		for i in range(10000):
			val = random.random()
			self.pq.add(str(i), val, None)
			self.l.append(val)

		self._sort_l()

		# Test

		self.assertEqual(len(self.pq), len(self.l))

		for i, val in enumerate(addressable_pq_pop_all(self.pq)):
			self.assertEqual(val, self.l[i])

	def test_change_value(self) -> None:
		# Setup

		for i in range(10000):
			val = random.random()
			self.pq.add(str(i), val, None)

		for i in range(10000):
			val = random.random()
			self.pq.change_value(str(i), val)
			self.l.append(val)

		self._sort_l()

		# Test

		self.assertEqual(len(self.pq), len(self.l))

		for i, val in enumerate(addressable_pq_pop_all(self.pq)):
			self.assertEqual(val, self.l[i])

	def test_ordered_iter(self) -> None:
		# Setup

		for i in range(10000):
			val = random.random()
			self.pq.add(str(i), val, None)
			self.l.append(val)

		self._sort_l()

		# Test

		self.assertEqual(len(self.pq), len(self.l))

		for i, it in enumerate(self.pq.ordered_iter()):
			self.assertEqual(it.value, self.l[i])

		self.assertEqual(len(self.pq), len(self.l))


class MaxHeapEndToEndTest(EndToEndTest):
	def setUp(self) -> None:
		self.l: typing.List[float] = []
		self.pq: KeyedPQ[None] = KeyedPQ(max_heap=True)

	def _sort_l(self) -> None:
		self.l.sort(reverse=True)

	def _set_pq_from_iterable(self, iterable: typing.Iterable[typing.Tuple[str, float, None]]) -> None:
		self.pq = KeyedPQ(iterable, max_heap=True)


def list_pop_all(l: typing.List[float]) -> typing.Iterator[float]:
	return iter(l)

def heap_pop_all(heap: typing.List[float]) -> typing.Iterator[float]:
	while True:
		try:
			yield heapq.heappop(heap)
		except IndexError:
			break

def addressable_pq_pop_all(pq: 'KeyedPQ[None]') -> typing.Iterator[float]:
	while True:
		try:
			_, val, _ = pq.pop()
			yield val
		except IndexError:
			break
