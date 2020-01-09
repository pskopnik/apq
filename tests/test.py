import heapq
import itertools
import math
import random
import typing
import unittest

from apq import KeyedPQ, Item


class KeyTest(unittest.TestCase):
	def setUp(self) -> None:
		self.pq: KeyedPQ[None] = KeyedPQ()

	def test_existing_str_key(self) -> None:
		self.pq.add('a', 0.0, None)

		self.assertTrue('a' in self.pq)
		self.assertEqual(self.pq['a'].key, 'a')

	def test_unknown_str_key(self) -> None:
		self.assertFalse('b' in self.pq)
		with self.assertRaises(KeyError):
			item = self.pq['a']

	def test_removed_str_key(self) -> None:
		self.pq.add('a', 0.0, None)
		del self.pq['a']

		self.assertFalse('a' in self.pq)
		with self.assertRaises(KeyError):
			item = self.pq['a']

		self.pq.add('b', 0.0, None)
		self.pq.pop()

		self.assertFalse('b' in self.pq)
		with self.assertRaises(KeyError):
			item = self.pq['b']

	def test_existing_item_key(self) -> None:
		item = self.pq.add('a', 0.0, None)

		self.assertTrue(item in self.pq)
		self.assertEqual(self.pq[item].key, 'a')

	def test_unknown_item_key(self) -> None:
		item: Item[None] = Item()

		self.assertFalse(item in self.pq)
		with self.assertRaises(KeyError):
			item = self.pq[item]

	def test_others_item_key(self) -> None:
		pq2: KeyedPQ[None] = KeyedPQ()
		item2 = pq2.add('a', 0.0, None)

		self.assertFalse(item2 in self.pq)
		with self.assertRaises(KeyError):
			item = self.pq[item2]

		self.pq.add('a', 0.0, None)

		self.assertFalse(item2 in self.pq)
		with self.assertRaises(KeyError):
			item = self.pq[item2]

	def test_removed_item_key(self) -> None:
		item_a = self.pq.add('a', 0.0, None)
		del self.pq['a']

		self.assertFalse(item_a in self.pq)
		with self.assertRaises(KeyError):
			item = self.pq[item_a]

		item_b = self.pq.add('b', 0.0, None)
		self.pq.pop()

		self.assertFalse(item_b in self.pq)
		with self.assertRaises(KeyError):
			item = self.pq[item_b]

	def test_add_duplicate_str_key(self) -> None:
		self.pq.add('a', 0.0, None)

		with self.assertRaises(KeyError):
			self.pq.add('a', 3.0, None)


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


class InvariantTest(unittest.TestCase):
	NUMBER_OF_ENTRIES = 10000

	def setUp(self) -> None:
		self.pq: KeyedPQ[None] = KeyedPQ()

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


# class MaxHeapInvariantTest(InvariantTest):
# 	def setUp(self) -> None:
# 		self.pq: KeyedPQ[None] = KeyedPQ(max_heap=True)


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
		self._sort_l: typing.Callable[[], None] = lambda: self.l.sort()

	def test_pop(self) -> None:
		# Setup

		for i in range(10000):
			val = random.random()
			self.pq.add(str(i), val, None)
			self.l.append(val)

		self._sort_l()

		# Test

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

		for i, val in enumerate(addressable_pq_pop_all(self.pq)):
			self.assertEqual(val, self.l[i])


# class MaxHeapEndToEndTest(EndToEndTest):
# 	def setUp(self) -> None:
# 		self.l: typing.List[float] = []
# 		self.pq: KeyedPQ[None] = KeyedPQ(max_heap=True)
# 		self._sort_l: typing.Callable[[], None] = lambda: self.l.sort(reverse=True)


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
