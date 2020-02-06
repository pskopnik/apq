from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize

extensions = [
	Extension('apq', ['apq.pyx'],
		extra_compile_args = ['-std=c++14'],
		extra_link_args = ['-std=c++14'],
	),
]

with open('README.md') as file:
	long_description = file.read()

setup(
	name = 'apq',
	version = '0.6.1dev0',
	license = 'MIT',
	author = 'Paul Skopnik',
	author_email = 'paul@skopnik.me',
	url = 'https://github.com/pskopnik/apq',
	description = 'Addressable priority queue data structures',
	long_description = long_description,
	long_description_content_type = 'text/markdown',
	keywords = 'queue priorityqueue addressable datastructures mapping',
	packages = ['apq'],
	package_data = {'apq': ['*.pyi', 'py.typed']},
	zip_safe = False,
	python_requires=">=3.6, <4",
	ext_modules = cythonize(
		extensions,
		annotate = True,
		# gdb_debug = True,
	),
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
