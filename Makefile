PIPENV := $(shell which pipenv)
ifneq ($(PIPENV),)
	PYTHON := $(shell $(PIPENV) --py)
else
	PYTHON := $(shell which python)
endif

SRC_DIRS := ./pyx_src
CYTHON_SRCS := $(shell find $(SRC_DIRS) -name "*.pyx")
CYTHON_CPPS := $(CYTHON_SRCS:.pyx=.cpp)
CYTHON_HTMLS := $(CYTHON_SRCS:.pyx=.html)

EXTENSION_SUFFIX := $(shell $(PYTHON) -c 'import importlib.machinery; print(importlib.machinery.EXTENSION_SUFFIXES[0])')
# BUILD_SUFFIX is $(OS)-$(MACHINE)-$(MAJOR_PYTHON_VERSION), e.g. linux-x86_64-3.7
BUILD_SUFFIX := $(shell $(PYTHON) -c 'import platform; print(platform.system().lower(), platform.machine().lower(), ".".join(platform.python_version_tuple()[0:2]), sep="-")')
LIB_DIR := ./build/lib.$(BUILD_SUFFIX)
EXTENSION_LIBRARY := apq$(EXTENSION_SUFFIX)

ifneq ($(TEST_PATTERN),)
	TEST_FLAGS := -k $(TEST_PATTERN)
endif

$(SRC_DIRS)/%.cpp $(SRC_DIRS)/%.html: $(SRC_DIRS)/%.pyx
	# Does not generate the same file as setup.py build_ext does: Cython meta data is missing.
	$(PIPENV) run cython -a --cplus -Werror -Wextra $<

$(LIB_DIR)/apq$(EXTENSION_SUFFIX): $(CYTHON_CPPS) $(SRC_DIRS)/cpp/binheap.hpp
	$(PIPENV) run python setup.py build_ext --transpile-cython

$(EXTENSION_LIBRARY): $(LIB_DIR)/$(EXTENSION_LIBRARY)
	cp $< $@

build-dev: $(EXTENSION_LIBRARY)

all: $(EXTENSION_LIBRARY)

test: $(EXTENSION_LIBRARY)
ifeq ($(NO_MYPY),)
		$(PIPENV) run mypy tests
endif
	$(PIPENV) run pytest tests $(TEST_FLAGS)

bench-basic: $(EXTENSION_LIBRARY)
ifeq ($(NO_MYPY),)
		$(PIPENV) run mypy bench
endif
	$(PIPENV) run python -m bench.basic

build-dist:
	$(PIPENV) run python setup.py sdist bdist_wheel --transpile-cython

clean:
	$(RM) -f $(CYTHON_CPPS) $(CYTHON_HTMLS)
	$(RM) -rf build py_src/apq.egg-info cython_debug
	$(RM) -f apq.*.so

.PHONY: test build-dev bench-basic build-dist clean
