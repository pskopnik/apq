import functools
from os import environ, stat
from os.path import isfile, splitext
from setuptools import setup
from setuptools.extension import Extension
import sys

try:
	from Cython.Build import cythonize
	cython_installed = True
except ImportError:
	cythonize = lambda x, *args, **kwargs: x
	cython_installed = False

cpp_missing_msg = ' '.join((
	'{cpp_path!r} is missing.',
	'Set env APQ_TRANSPILE_CYTHON or pass --transpile-cython to regenerate.',
))

cpp_outdated_msg = ' '.join((
	'{path!r} has been modified after its dependent {cpp_path!r}.',
	'Set env APQ_TRANSPILE_CYTHON or pass --transpile-cython to regenerate.',
	'Set env APQ_FORCE_OUTDATED_SOURCE or pass --force-outdated-source to',
	'disable this check.',
))

cython_missing_msg = ' '.join((
	'Cython is required to perform this operation.',
	'Either install Cython or disable any options which require Cython,',
	'such as env APQ_TRANSPILE_CYTHON or argument --transpile-cython.',
))

def decythonize(extensions):
	for extension in extensions:
		sources = []
		for path in extension.sources:
			base, ext = splitext(path)
			if ext in ('.pyx'):
				ext = '.cpp'

				cpp_path = base + ext

				if not isfile(cpp_path):
					raise Exception(
						cpp_missing_msg.format(path=path, cpp_path=cpp_path),
					)

				is_outdated = stat(path).st_mtime > stat(cpp_path).st_mtime
				if not force_outdated_source and is_outdated:
					raise Exception(
						cpp_outdated_msg.format(path=path, cpp_path=cpp_path),
					)

				path = cpp_path

			sources.append(path)

		extension.sources[:] = sources

	return extensions

# Parsing of additional options in the form of environment variables and CLI
# arguments.

transpile_cython = environ.get('APQ_TRANSPILE_CYTHON', False)
if '--transpile-cython' in sys.argv:
	transpile_cython = True
	sys.argv.remove('--transpile-cython')

force_outdated_source = environ.get('APQ_FORCE_OUTDATED_SOURCE', False)
if '--force-outdated-source' in sys.argv:
	force_outdated_source = True
	sys.argv.remove('--force-outdated-source')

if transpile_cython:
	if not cython_installed:
		raise Exception(cython_missing_msg)

	prepare_extensions = functools.partial(
		cythonize,
		annotate = True,
		# gdb_debug = True,
	)
else:
	prepare_extensions = decythonize

extensions = [
	Extension('apq', ['pyx_src/apq.pyx'],
		extra_compile_args = ['-std=c++14'],
		extra_link_args = ['-std=c++14'],
	),
]

with open('README.md') as file:
	long_description = file.read()

setup(
	name = 'apq',
	version = '0.6.1',
	license = 'MIT',
	author = 'Paul Skopnik',
	author_email = 'paul@skopnik.me',
	url = 'https://github.com/pskopnik/apq',
	description = 'Addressable priority queue data structures',
	long_description = long_description,
	long_description_content_type = 'text/markdown',
	keywords = 'queue priorityqueue addressable datastructures mapping',
	packages = ['apq'],
	package_dir={'': 'py_src'},
	package_data = {'apq': ['*.pyi', 'py.typed']},
	zip_safe = False,
	python_requires=">=3.6, <4",
	ext_modules = prepare_extensions(extensions),
	classifiers = [
		'Development Status :: 4 - Beta',
		'Target Audience :: Developers',
		'Target Audience :: Science/Research',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Cython',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: Implementation :: CPython',
		'Programming Language :: Python :: Implementation :: PyPy',
		'Operating System :: MacOS',
		'Operating System :: POSIX :: Linux',
		'Topic :: Scientific/Engineering',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Typing :: Typed',
	]
)
