from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize

extensions = [
	Extension("apq", ["apq.pyx"],
		extra_compile_args = ["-std=c++14"],
		extra_link_args = ["-std=c++14"],
	),
]

setup(
	name = "apq",
	version = "0.5",
	author = "Paul Skopnik",
	author_email = "paul@skopnik.me",
	description = "An addressable priority queue",
	packages = ["apq"],
	package_data = {"apq": ["*.pyi", "py.typed"]},
	zip_safe = False,
	ext_modules = cythonize(
		extensions,
		annotate = True,
		# gdb_debug = True,
		compiler_directives = {
			'embedsignature': True,
		}
	),
)
