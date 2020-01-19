PIPENV := $(shell which pipenv)
PYTHON := $(shell $(PIPENV) --py)

EXTENSION_SUFFIX := $(shell $(PYTHON) -c 'import importlib.machinery; print(importlib.machinery.EXTENSION_SUFFIXES[0])')
# BUILD_SUFFIX is $(OS)-$(MACHINE)-$(MAJOR_PYTHON_VERSION), e.g. linux-x86_64-3.7
BUILD_SUFFIX := $(shell $(PYTHON) -c 'import platform; print(platform.system().lower(), platform.machine().lower(), ".".join(platform.python_version_tuple()[0:2]), sep="-")')
LIB_DIR := build/lib.$(BUILD_SUFFIX)
EXTENSION_LIBRARY := apq$(EXTENSION_SUFFIX)

ifneq ($(TEST_PATTERN),)
	TEST_FLAGS := -k $(TEST_PATTERN)
endif

apq.cpp apq.html: apq.pyx
	$(PIPENV) run cython -a --cplus -Werror -Wextra apq.pyx

$(LIB_DIR)/apq$(EXTENSION_SUFFIX): apq.cpp src/_apq_helpers.cpp src/binheap.hpp
	$(PIPENV) run python setup.py build_ext

$(EXTENSION_LIBRARY): $(LIB_DIR)/$(EXTENSION_LIBRARY)
	cp $< $@

build-dev: $(EXTENSION_LIBRARY)

test: $(EXTENSION_LIBRARY)
	$(PIPENV) run mypy --strict tests
	$(PIPENV) run python -m unittest tests/test.py $(TEST_FLAGS)

bench-basic: $(EXTENSION_LIBRARY)
	$(PIPENV) run mypy --strict bench
	$(PIPENV) run python -m bench.basic

build-dist:
	$(PIPENV) run python setup.py sdist bdist_wheel

clean:
	$(RM) -f apq.cpp apq.html
	$(RM) -rf build apq.egg-info cython_debug
	$(RM) -f apq.*.so

.PHONY: test build-dev bench-basic build-dist clean
