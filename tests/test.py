import itertools
import unittest
import random
import typing
import heapq

from apq import AddressablePQ


class EdgeCaseTest(unittest.TestCase):
	# Should raise exception when empty, ...
	pass


class InvariantTest(unittest.TestCase):
	NUMBER_OF_ENTRIES = 10000

	def setUp(self) -> None:
		self.pq: AddressablePQ[None] = AddressablePQ()

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
		self.pq: AddressablePQ[None] = AddressablePQ(max_heap=True)


class HeapCompareTest(unittest.TestCase):
	def test_incremental_push_small(self) -> None:
		for n in itertools.chain.from_iterable(itertools.repeat(i, 1000) for i in range(10)):
			# Setup

			pq: AddressablePQ[None] = AddressablePQ()
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

			pq: AddressablePQ[None] = AddressablePQ()
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

			pq: AddressablePQ[None] = AddressablePQ()
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

			pq: AddressablePQ[None] = AddressablePQ()
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

		pq: AddressablePQ[None] = AddressablePQ()
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

		pq: AddressablePQ[None] = AddressablePQ()
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
		self.pq: AddressablePQ[None] = AddressablePQ()
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


class MaxHeapEndToEndTest(EndToEndTest):
	def setUp(self) -> None:
		self.l: typing.List[float] = []
		self.pq: AddressablePQ[None] = AddressablePQ(max_heap=True)
		self._sort_l: typing.Callable[[], None] = lambda: self.l.sort(reverse=True)


def list_pop_all(l: typing.List[float]) -> typing.Iterator[float]:
	return iter(l)

def heap_pop_all(heap: typing.List[float]) -> typing.Iterator[float]:
	while True:
		try:
			yield heapq.heappop(heap)
		except IndexError:
			break

def addressable_pq_pop_all(pq: 'AddressablePQ[None]') -> typing.Iterator[float]:
	while True:
		try:
			_, val, _ = pq.pop()
			yield val
		except IndexError:
			break
