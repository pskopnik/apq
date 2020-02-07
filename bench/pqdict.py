from . import bench, BenchTimer, main_bench_registered
from .utils import StringSource
from pqdict import pqdict
from random import random as random_01


@bench()
def bench_add(b: BenchTimer) -> None:
    s = StringSource()
    s_offset = StringSource()
    pq: pqdict[str, float] = pqdict()

    for _ in range(10000):
        pq.additem(next(s), random_01())
        next(s_offset)

    with b.time() as t:
        for _ in t:
            pq.additem(next(s), random_01())

    with b.offset() as t:
        for _ in t:
            next(s_offset)
            random_01()

@bench()
def bench_pop(b: BenchTimer) -> None:
    s = StringSource()
    pq: pqdict[str, float] = pqdict()

    for _ in range(b.n + 10000):
        pq.additem(next(s), random_01())

    with b.time() as t:
        for _ in t:
            pq.popitem()

    with b.offset() as t:
        for _ in t:
            pass

@bench()
def bench_pop_add(b: BenchTimer) -> None:
    s = StringSource()
    s_offset = StringSource()
    pq: pqdict[str, float] = pqdict()

    for _ in range(10000):
        pq.additem(next(s), random_01())
        next(s_offset)

    with b.time() as t:
        for _ in t:
            pq.popitem()
            pq.additem(next(s), random_01())

    with b.offset() as t:
        for _ in t:
            next(s_offset)
            random_01()

@bench()
def bench_change_value(b: BenchTimer) -> None:
    s = StringSource()
    pq: pqdict[str, float] = pqdict()

    for _ in range(10000):
        pq.additem(next(s), random_01())

    with b.time() as t:
        for _ in t:
            key = s.rand_existing()
            pq.updateitem(key, random_01())

    with b.offset() as t:
        for _ in t:
            key = s.rand_existing()
            random_01()

@bench()
def bench_remove(b: BenchTimer) -> None:
    s = StringSource()
    s_remove = StringSource()
    s_offset = StringSource()
    pq: pqdict[str, float] = pqdict()

    for _ in range(b.n + 10000):
        pq.additem(next(s), random_01())
        next(s_offset)

    with b.time() as t:
        for _ in t:
            key = next(s_remove)
            del pq[key]

    with b.offset() as t:
        for _ in t:
            key = next(s_offset)

if __name__ == '__main__':
    main_bench_registered()
