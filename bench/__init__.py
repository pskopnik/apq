import functools
import time
import itertools
import gc
import sys
import csv
from typing import Any, Callable, cast, Iterable, Iterator, List, Optional, Tuple, Union


def _double(start: int=1) -> Iterator[int]:
	current = start
	while True:
		yield current
		current *= 2

def _double_human(start: int=1) -> Iterator[int]:
	if start != 1:
		# Workaround for different start values
		yield start

		o = _double_human()

		for n in o:
			if n >= start:
				yield n
				break

		for n in o:
			yield n

		return

	current = 1
	while True:
		for fact in 1, 2, 5:
			yield fact * current
		current *= 10


class BenchTimer(object):
	class Timeable(object):
		def __init__(self, instance: 'BenchTimer') -> None:
			self._instance: BenchTimer = instance
			self._start_time: Optional[float] = None
			self._end_time: Optional[float] = None
			self._gc_enabled: Optional[bool] = None

		def __enter__(self) -> 'BenchTimer.Timeable':
			self._gc_enabled = gc.isenabled()
			gc.disable()

			self._start_time = self._instance._timer()

			return self

		def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
			self._end_time = self._instance._timer()

			if self._gc_enabled is not None and self._gc_enabled:
				gc.enable()

		@property
		def n(self) -> int:
			return self._instance._n

		def __iter__(self) -> Iterator[None]:
			return self.n_it()

		def n_it(self) -> Iterator[None]:
			return itertools.repeat(None, self._instance._n)

		def __call__(self, f: Callable[[], None]) -> None:
			self.do(f)

		def do(self, f: Callable[[], None]) -> None:
			with self as t:
				for _ in t:
					f()

		def timing(self)-> float:
			if self._start_time is None or self._end_time is None:
				raise Exception('no timing information available') # TODO

			return self._end_time - self._start_time


	class Timing(object):
		__slots__ = ['_n', '_primary', '_offset']

		def __init__(self, n: int, primary: float, offset: Optional[float]) -> None:
			self._n: int = n
			self._primary: float = primary
			self._offset: Optional[float] = offset

		def __add__(self, other: 'BenchTimer.Timing') -> 'BenchTimer.Timing':
			return BenchTimer.Timing(
				self._n + other._n,
				self._primary + other._primary,
				self.offset + other.offset, # non existing offset is converted to 0.0
			)

		def __sub__(self, other: 'BenchTimer.Timing') -> 'BenchTimer.Timing':
			return BenchTimer.Timing(
				self._n - other._n,
				self._primary - other._primary,
				self.offset - other.offset, # non existing offset is converted to 0.0
			)

		@property
		def n(self) -> int:
			return self._n

		@property
		def primary(self) -> float:
			return self._primary

		@property
		def primary_per_execution(self) -> float:
			return self.primary / self.n

		@property
		def offset_available(self) -> float:
			return self._offset is not None

		@property
		def offset(self) -> float:
			if self._offset is None:
				return 0.0
			return self._offset

		@property
		def offset_per_execution(self) -> float:
			return self.offset / self.n

		@property
		def duration(self) -> float:
			return self.primary - self.offset

		@property
		def duration_per_execution(self) -> float:
			return self.duration / self.n


	def __init__(self, n: int, timer: Callable[[], float]) -> None:
		self._n: int = n
		self._timer: Callable[[], float] = timer
		self._primary: Optional[BenchTimer.Timeable] = None
		self._offset: Optional[BenchTimer.Timeable] = None

	@property
	def n(self) -> int:
		return self._n

	def time(self) -> 'BenchTimer.Timeable':
		if self._primary is not None:
			raise Exception('primary has already been defined') # TODO
		self._primary = BenchTimer.Timeable(self)
		return self._primary

	def offset(self) -> 'BenchTimer.Timeable':
		if self._offset is not None:
			raise Exception('offset has already been defined') # TODO
		self._offset = BenchTimer.Timeable(self)
		return self._offset

	def collect_timing(self) -> 'BenchTimer.Timing':
		if self._primary is None:
			raise Exception('no primary timeable initialised') # TODO

		primary_timing: float = self._primary.timing()
		offset_timing: Optional[float] = None
		if self._offset is not None:
			try:
				offset_timing = self._offset.timing()
			except: # TODO
				pass

		return BenchTimer.Timing(
			self._n,
			primary_timing,
			offset_timing,
		)


BenchmarkFunction = Callable[[BenchTimer], None]


class BenchmarkSpecification(object):
	def __init__(self,
		name: str,
		function: BenchmarkFunction,
		min_n: int = 1,
		max_n: int = 0,
		min_repeats: int = 1,
	) -> None:
		self._name = name
		self._function: BenchmarkFunction = function
		self._min_n: int = min_n
		self._max_n: int = max_n
		self._min_repeats: int = min_repeats

	@property
	def name(self) -> str:
		return self._name

	@property
	def function(self) -> BenchmarkFunction:
		return self._function

	@property
	def min_n(self) -> int:
		return self._min_n

	@property
	def max_n(self) -> int:
		return self._max_n

	@property
	def min_repeats(self) -> int:
		return self._min_repeats


class BenchmarkRegistry(object):
	def __init__(self) -> None:
		self._specifications: List[BenchmarkSpecification] = []
		self._only_active: bool = False

	def __iter__(self) -> Iterator[BenchmarkSpecification]:
		return iter(self._specifications)

	def add(self, spec: BenchmarkSpecification, only: bool=False) -> None:
		if only and self._only_active:
			raise Exception(
				"multiple benchmark functions marked as only function",
				self._specifications[0].name,
				spec.name,
			)

		if only:
			self._specifications = [spec]
			self._only_active = True
		elif not self._only_active:
			self._specifications.append(spec)


class BenchDecorator(object):
	def __init__(self, default_registry: BenchmarkRegistry) -> None:
		self._default_registry: BenchmarkRegistry = default_registry

	def __call__(
		self,
		name: Optional[str] = None,
		registry: Optional[BenchmarkRegistry] = None,
		min_n: int = 1,
		max_n: int = 0,
		min_repeats: int = 1,
	) -> Callable[[BenchmarkFunction], BenchmarkFunction]:
		def inner(f: BenchmarkFunction) -> BenchmarkFunction:
			name_i = name or f.__name__
			registry_i = registry or self._default_registry

			registry_i.add(
				BenchmarkSpecification(name_i, f, min_n=min_n, max_n=max_n, min_repeats=min_repeats),
			)

			return f

		return inner

	def only(
		self,
		name: Optional[str] = None,
		registry: Optional[BenchmarkRegistry] = None,
		min_n: int = 1,
		max_n: int = 0,
		min_repeats: int = 1,
	) -> Callable[[BenchmarkFunction], BenchmarkFunction]:
		def inner(f: BenchmarkFunction) -> BenchmarkFunction:
			name_i = name or f.__name__
			registry_i = registry or self._default_registry

			registry_i.add(
				BenchmarkSpecification(name_i, f, min_n=min_n, max_n=max_n, min_repeats=min_repeats),
				only=True,
			)

			return f

		return inner

	def skip(
		self,
		name: Optional[str]=None,
		registry: Optional[BenchmarkRegistry]=None
	) -> Callable[[BenchmarkFunction], BenchmarkFunction]:
		return lambda f: f


class Benchmarker(object):
	def auto_bench(self, spec: BenchmarkSpecification) -> Iterable[BenchTimer.Timing]:
		n, _ = self._find_suitable_n(spec)
		# TODO pass in already known timing
		return self._full_eval(spec, n)

	def _find_suitable_n(self, spec: BenchmarkSpecification) -> Tuple[int, BenchTimer.Timing]:
		for n in _double_human(start=spec.min_n):
			timing = self._bench_spec_n(spec, n)
			if timing.duration > 0.2:
				return n, timing

		raise Exception("no suitable n found") # TODO

	def _full_eval(self, spec: BenchmarkSpecification, n: int) -> Iterable[BenchTimer.Timing]:
		for _ in range(spec.min_repeats):
			yield self._bench_spec_n(spec, n)

	def _bench_spec_n(self, spec: BenchmarkSpecification, n: int) -> BenchTimer.Timing:
		k_it: Iterator[int] = itertools.repeat(n, 1)
		if spec.max_n > 0 and n > spec.max_n:
			k_it = itertools.repeat(spec.max_n, n // spec.max_n)
			if n % spec.max_n > spec.min_n:
				k_it = itertools.chain(k_it, itertools.repeat(n % spec.max_n, 1))

		return sum(map(functools.partial(self._bench_func, spec.function), k_it), BenchTimer.Timing(0, 0.0, 0.0))

	def _bench_func(self, function: BenchmarkFunction, n: int) -> BenchTimer.Timing:
		b = BenchTimer(n, time.perf_counter)
		gc.collect()
		function(b)
		gc.collect()
		return b.collect_timing()


default_registry = BenchmarkRegistry()
bench = BenchDecorator(default_registry)

def main_bench_registered() -> None:
	b = Benchmarker()

	res: List[Tuple[str, BenchTimer.Timing]] = []

	w = csv.writer(sys.stdout)
	w.writerow([
		'name',
		'n',
		'duration',
		'primary',
		'offset',
		'duration_per_execution',
		'primary_per_execution',
		'offset_per_execution',
	])

	for spec in default_registry:
		for timing in b.auto_bench(spec):
			res.append((spec.name, timing))

			print("{0} dur={1.duration_per_execution} n={1.n} total={1.primary} off={1.offset}".format(spec.name, timing), file=sys.stderr)
			w.writerow([
				spec.name,
				timing.n,
				timing.duration,
				timing.primary,
				timing.offset,
				timing.duration_per_execution,
				timing.primary_per_execution,
				timing.offset_per_execution,
			])

# if __name__ == '__main__':
# 	main()
