PIPENV := $(shell which pipenv)
ifneq ($(PIPENV),)
	PYTHON := $(shell $(PIPENV) --py)
else
	PYTHON := $(shell which python)
endif

SRC_DIRS := ./
CYTHON_SRCS := $(shell find $(SRC_DIRS) -name "*.pyx")
CYTHON_CPPS := $(OBJS:.pyx=.cpp)
CYTHON_HTMLS := $(OBJS:.pyx=.html)

EXTENSION_SUFFIX := $(shell $(PYTHON) -c 'import importlib.machinery; print(importlib.machinery.EXTENSION_SUFFIXES[0])')
# BUILD_SUFFIX is $(OS)-$(MACHINE)-$(MAJOR_PYTHON_VERSION), e.g. linux-x86_64-3.7
BUILD_SUFFIX := $(shell $(PYTHON) -c 'import platform; print(platform.system().lower(), platform.machine().lower(), ".".join(platform.python_version_tuple()[0:2]), sep="-")')
LIB_DIR := ./build/lib.$(BUILD_SUFFIX)
EXTENSION_LIBRARY := apq$(EXTENSION_SUFFIX)

ifneq ($(TEST_PATTERN),)
	TEST_FLAGS := -k $(TEST_PATTERN)
endif

./%.cpp ./%.html: ./%.pyx
	# Does not generate the same file as setup.py build_ext does: Cython meta data is missing.
	$(PIPENV) run cython -a --cplus -Werror -Wextra $<

$(LIB_DIR)/apq$(EXTENSION_SUFFIX): apq.cpp src/binheap.hpp
	$(PIPENV) run python setup.py build_ext

$(EXTENSION_LIBRARY): $(LIB_DIR)/$(EXTENSION_LIBRARY)
	cp $< $@

build-dev: $(EXTENSION_LIBRARY)

all: $(EXTENSION_LIBRARY)

test: $(EXTENSION_LIBRARY)
ifeq ($(NO_MYPY),)
		$(PIPENV) run mypy --strict tests
endif
	$(PIPENV) run pytest tests $(TEST_FLAGS)

bench-basic: $(EXTENSION_LIBRARY)
ifeq ($(NO_MYPY),)
		$(PIPENV) run mypy --strict bench
endif
	$(PIPENV) run python -m bench.basic

build-dist:
	$(PIPENV) run python setup.py sdist bdist_wheel

clean:
	$(RM) -f apq.cpp apq.html
	$(RM) -rf build apq.egg-info cython_debug
	$(RM) -f apq.*.so

.PHONY: test build-dev bench-basic build-dist clean
