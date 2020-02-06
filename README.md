# apq

`apq` provides different kinds of addressable priority queue data structures
usable in any Python 3 project.

All priority queues provided by `apq` are backed by a C++ binary heap
implementation. The priority queue types exposed to Python are implemented in
Cython. Type stubs are installed along with the package so that mypy can fully
check dependent code.

## Priority Queue Types

 * `KeyedPQ` - This priority queue allows lookup of entries through a string
   key. That means it combines an addressable priority queue with a
   dictionary creating a `str` to item mapping (**almost** implementing
   `typing.Mapping[str, Item]`). `KeyedPQ` is recommended whenever individual
   entries are looked up using a key.

## Quickstart

Installation:

```shell
$ pip install apq
```

Usage:

```python
>>> from apq import KeyedPQ
>>> pq: KeyedPQ[None] = KeyedPQ()
>>> pq.add('my_first_key', 34.0, None)
<apq.Item object at 0x7f506884bd70>
>>> pq.add('my_second_key', 36.0, None)
<apq.Item object at 0x7f506884bcb0>
>>> pq.change_value('my_second_key', 12.0)
<apq.Item object at 0x7f50663604f0>
>>> print(pq.pop())
('my_second_key', 12.0, None)
```
