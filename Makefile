test:
	pipenv run cython -a --cplus -Wextra apq.pyx
	pipenv install -e .
	pipenv run mypy --strict tests
	pipenv run python -m unittest tests/test.py

bench-basic:
	pipenv run mypy --strict bench
	pipenv run python -m bench.basic

build-dist:
	pipenv run python setup.py sdist bdist_wheel

clean:
	rm -f apq.cpp apq.html
	rm -rf build apq.egg-info
	rm -f apq.*.so

.PHONY: test bench-basic build-dist clean
