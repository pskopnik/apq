import functools
import time
import itertools
import gc
from typing import Any, Callable, Iterator, List, Optional, Tuple, Union


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


class Benchmarker(object):
	def auto_bench_func(self, f: 'BenchmarkFunction') -> 'BenchTimer.Timing':
		for n in _double_human():
			timing = self._bench_func(f, n)
			if timing.duration > 0.2:
				return timing

		return BenchTimer.Timing(0, 0.0, 0.0)

	def _bench_func(self, f: 'BenchmarkFunction', n: int) -> 'BenchTimer.Timing':
		b = BenchTimer(n, time.perf_counter)
		gc.collect()
		f(b)
		gc.collect()
		return b.collect_timing()


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

benchmark_functions: List[BenchmarkFunction] = []
benchmark_functions_only: bool = False

def bench() -> Callable[[BenchmarkFunction], BenchmarkFunction]:
	def inner(f: BenchmarkFunction) -> BenchmarkFunction:
		global benchmark_functions, benchmark_functions_only
		if not benchmark_functions_only:
			benchmark_functions.append(f)
		return f

	return inner


def _bench_only() -> Callable[[BenchmarkFunction], BenchmarkFunction]:
	def inner(f: BenchmarkFunction) -> BenchmarkFunction:
		global benchmark_functions, benchmark_functions_only
		if benchmark_functions_only:
			raise Exception(
				"multiple benchmark functions marked as only function",
				benchmark_functions[0].__name__,
				benchmark_functions[0].__name__,
			)
		benchmark_functions = [f]
		benchmark_functions_only = True
		return f

	return inner

bench.only = _bench_only

def _bench_skip() -> Callable[[BenchmarkFunction], BenchmarkFunction]:
	return lambda f: f

bench.skip = _bench_skip

def main_bench_registered() -> None:
	b = Benchmarker()

	res: List[Tuple[str, BenchTimer.Timing]] = []

	for f in benchmark_functions:
		timing = b.auto_bench_func(f)
		res.append((f.__name__, (timing)))

		print("{0} dur={1.duration_per_execution} n={1.n} total={1.primary} off={1.offset}".format(f.__name__, timing))
		# print(*res[-1])

# if __name__ == '__main__':
# 	main()
