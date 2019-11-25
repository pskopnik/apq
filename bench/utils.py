import itertools
from typing import Iterable, Iterator
import random


class StringSource(object):
	def __init__(self) -> None:
		self._next: int = 0

	def __iter__(self) -> Iterator[str]:
		return self

	def __next__(self) -> str:
		el = str(self._next)
		self._next += 1
		return el

	def take(self, n: int) -> Iterable[str]:
		start = self._next
		self._next += n
		return (str(i) for _, i in zip(range(n), itertools.count(start)))

	def rand_existing(self) -> str:
		if self._next == 0:
			raise Exception("StringSource has not yet generated any elements")

		return str(random.randrange(self._next))
