ifneq ($(TEST_PATTERN),)
	TEST_FLAGS := -k $(TEST_PATTERN)
endif

test:
	pipenv run cython -a --cplus -Werror -Wextra apq.pyx
	pipenv install -e .
	pipenv run mypy --strict tests
	pipenv run python -m unittest tests/test.py $(TEST_FLAGS)

bench-basic:
	pipenv run mypy --strict bench
	pipenv run python -m bench.basic

build-dist:
	pipenv run python setup.py sdist bdist_wheel

clean:
	rm -f apq.cpp apq.html
	rm -rf build apq.egg-info cython_debug
	rm -f apq.*.so

.PHONY: test bench-basic build-dist clean
