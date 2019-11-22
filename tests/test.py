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

	def test_add(self):
		# Setup

		pq: AddressablePQ = AddressablePQ()

		# Test

		self.assertTrue(pq._verify_invariants())
		self.assertEqual(len(pq), 0)

		for i in range(self.NUMBER_OF_ENTRIES):
			val = random.random()
			pq.add(str(i), val, None)
			self.assertTrue(pq._verify_invariants())
			self.assertEqual(len(pq), i + 1)

	def test_pop(self):
		# Setup

		pq: AddressablePQ = AddressablePQ()

		for i in range(self.NUMBER_OF_ENTRIES):
			val = random.random()
			pq.add(str(i), val, None)

		# Test

		self.assertTrue(pq._verify_invariants())
		self.assertEqual(len(pq), self.NUMBER_OF_ENTRIES)

		for i in range(self.NUMBER_OF_ENTRIES):
			_, _, _ = pq.pop()
			self.assertTrue(pq._verify_invariants())
			self.assertEqual(len(pq), self.NUMBER_OF_ENTRIES - i - 1)

	def test_change_value(self):
		# Setup

		pq: AddressablePQ = AddressablePQ()

		for i in range(self.NUMBER_OF_ENTRIES):
			val = random.random()
			pq.add(str(i), val, None)

		# Test

		self.assertTrue(pq._verify_invariants())
		self.assertEqual(len(pq), self.NUMBER_OF_ENTRIES)

		for i in range(self.NUMBER_OF_ENTRIES):
			val = random.random()
			pq.change_value(str(i), val)
			self.assertTrue(pq._verify_invariants())

	def test_delete(self):
		# Setup

		pq: AddressablePQ = AddressablePQ()

		for i in range(self.NUMBER_OF_ENTRIES):
			val = random.random()
			pq.add(str(i), val, None)

		# Test

		self.assertTrue(pq._verify_invariants())
		self.assertEqual(len(pq), self.NUMBER_OF_ENTRIES)

		for i in range(self.NUMBER_OF_ENTRIES):
			del pq[str(i)]
			self.assertTrue(pq._verify_invariants())
			self.assertEqual(len(pq), self.NUMBER_OF_ENTRIES - i - 1)


class HeapCompareTest(unittest.TestCase):
	def test_incremental_push_small(self):
		for n in itertools.chain.from_iterable(itertools.repeat(i, 1000) for i in range(10)):
			# Setup

			pq: AddressablePQ = AddressablePQ()
			heap: typing.List[float] = []

			# Test

			for i in range(n):
				val = random.random()
				pq.add(str(i), val, None)
				heapq.heappush(heap, val)
				self.assertEqual(pq._export(), heap)

	def test_incremental_push(self):
		for n in range(1000):
			# Setup

			pq: AddressablePQ = AddressablePQ()
			heap: typing.List[float] = []

			# Test

			for i in range(n):
				val = random.random()
				pq.add(str(i), val, None)
				heapq.heappush(heap, val)
				self.assertEqual(pq._export(), heap)

	def test_incremental_pop_small(self):
		for n in itertools.chain.from_iterable(itertools.repeat(i, 1000) for i in range(10)):
			# Setup

			pq: AddressablePQ = AddressablePQ()
			heap: typing.List[float] = []

			for i in range(n):
				val = random.random()
				pq.add(str(i), val, None)
				heapq.heappush(heap, val)

			# Test

			for _ in range(n):
				self.assertEqual(pq.pop()[0], heapq.heappop(heap))
				self.assertEqual(pq._export(), heap)

	def test_incremental_pop(self):
		for n in range(1000):
			# Setup

			pq: AddressablePQ = AddressablePQ()
			heap: typing.List[float] = []

			for i in range(n):
				val = random.random()
				pq.add(str(i), val, None)
				heapq.heappush(heap, val)

			# Test

			for _ in range(n):
				self.assertEqual(pq.pop()[0], heapq.heappop(heap))
				self.assertEqual(pq._export(), heap)

	def test_incremental_change_value(self):
		# Setup

		pq: AddressablePQ = AddressablePQ()
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

	def test_change_value(self):
		# Setup

		pq: AddressablePQ = AddressablePQ()
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
	def test_pop(self):
		# Setup

		l: typing.List[float] = []
		pq: AddressablePQ = AddressablePQ()

		for i in range(10000):
			val = random.random()
			pq.add(str(i), val, None)
			l.append(val)

		l.sort()

		# Test

		for i, val in enumerate(addressable_pq_pop_all(pq)):
			self.assertEqual(val, l[i])

	def test_change_value(self):
		# Setup

		l: typing.List[float] = []
		pq: AddressablePQ = AddressablePQ()

		for i in range(10000):
			val = random.random()
			pq.add(str(i), val, None)

		for i in range(10000):
			val = random.random()
			pq.change_value(str(i), val)
			l.append(val)

		l.sort()

		# Test

		for i, val in enumerate(addressable_pq_pop_all(pq)):
			self.assertEqual(val, l[i])


def list_pop_all(l: typing.List[float]) -> typing.Iterator[float]:
	return iter(l)

def heap_pop_all(heap: typing.List[float]) -> typing.Iterator[float]:
	while True:
		try:
			yield heapq.heappop(heap)
		except IndexError:
			break

def addressable_pq_pop_all(pq: AddressablePQ) -> typing.Iterator[float]:
	while True:
		try:
			val, _, _ = pq.pop()
			yield val
		except IndexError:
			break
