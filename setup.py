from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize

extensions = [
	Extension("apq", ["apq.pyx"],
		extra_compile_args = ["-std=c++11"],
		extra_link_args = ["-std=c++11"],
	),
]

setup(
	name = "apq",
	version = "0.1",
	author = "Paul Skopnik",
	author_email = "paul@skopnik.me",
	description = "An addressable priority queue",
	ext_modules = cythonize(
		extensions,
		# annotate = True,
		# gdb_debug = True,
		compiler_directives = {
			'embedsignature': True,
			'language_level': '3',
		}
	),
)
