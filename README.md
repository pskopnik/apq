# apq

[![PyPI](https://img.shields.io/pypi/v/apq)][pypi-apq]
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/apq)][pypi-apq]
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/apq)][pypi-apq]
[![PyPI - License](https://img.shields.io/pypi/l/apq)](https://github.com/pskopnik/apq/blob/master/LICENSE)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pskopnik/apq/Test/master)](https://github.com/pskopnik/apq/actions?query=workflow%3ATest)

`apq` implements different variants of addressable priority queue data
structures importable from Python 3 projects.

The project aims to provide run-time efficient implementations of priority
queues whilst remaining practical in use and maintaining a legible code base.

 * All priority queues provided by `apq` are backed by a C++ binary heap
   implementation. The priority queue types exposed to Python are implemented
   in Cython.

 * `apq` has no installation or runtime dependencies on all common platforms.
   **Note:** A compiler and basic C++ headers are required on platforms for
   which no binary distribution of `apq` is available.

 * Type stubs are installed along with the package so that mypy can fully
   check dependent code.

[pypi-apq]: https://pypi.org/project/apq/

## Priority Queue Types

These priority queues use 64 bit floating point as priority values (`value`)
and FIFO semantic for entries with the same `value`. **Note:** 64 bit floats
can represent 54 bit signed integers.

 * `AddressablePQ` - **Not implemented.** This priority queue exposes
   persistent references in the form of `Item` its entries. Through `Item`,
   the `value` of entries can be changed and arbitrary entries can be removed
   from the PQ.

 * `KeyedPQ` - This priority queue allows lookup of entries through a string
   key. That means it combines an addressable priority queue with a
   dictionary, creating a `str` to item mapping (**almost** implementing
   `typing.Mapping[str, KeyedItem]`). `KeyedPQ` is recommended whenever
   individual entries are looked up using a key.

 * `SimplePQ` - **Not implemented.** This priority queue is a non-addressable
   variant of AddressablePQ. `SimplePQ` is recommended when a fast PQ is
   required which is only modified via `add()` and `pop()`.

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

## Releases and Compatibility

`apq` uses [semantic versioning][semver] to derive the version identifier of
releases. Code using the documented public API of `apq` will continue to work
with all future releases of `apq` which are API compatible. API compatibility
is indicated through the major component of the version identifier.

`apq` is currently under active development / in beta. Breaking changes of the
public interface will occur. Beta releases are indicated through a `0` in the
major component of the version identifier, e.g. `0.10.0`.

To encourage use during beta, `apq` extends semantic versioning to beta
releases as follows: From `0.10.0` onwards, API compatibility is guaranteed
for all future releases with the same `MINOR // 10` value. E.g. `0.17.3` is
API compatible with `0.10.1`.

Depending packages should use this semantic for specifying version
constraints, e.g. `apq >= 0.11.1, < 0.20.0` (c.f. [PEP 508][pep-508]). Pinning
is still recommended for applications, e.g. using [Poetry][poetry] or
[Pipenv][pipenv].

`apq` aims to fully work on all active versions of Python. **Python 3.5 is not
supported at the moment.** Information on the state of Python releases is
described in the [Python Developer's Guide][python-devguide] with further
details on the [Development Cycle][python-devguide-devcycle] page.

[semver]: https://semver.org/
[pep-508]: https://www.python.org/dev/peps/pep-0508/
[poetry]: https://python-poetry.org/
[pipenv]: https://pipenv.readthedocs.io/en/latest/
[python-devguide]: https://devguide.python.org/
[python-devguide-devcycle]: https://devguide.python.org/devcycle/

## Distribution

`apq` is distributed through [PyPi][pypi]. The [PyPi `apq` Project][pypi-apq]
contains a source distribution for each release. Additionally, pre-built
binary distribution in the form of wheels are available for common platforms.
`pip install apq` will automatically detect the most appropriate distribution.

TODO: Table of machine platform and OS, Python implementation and version for
which wheels are built.

[pypi]: https://pypi.org/
