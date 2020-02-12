from distutils.core import Command
import functools
from os import environ, stat
from os.path import isfile, splitext, join as pathjoin
from setuptools import setup
from setuptools.command.sdist import sdist as sdist_
from setuptools.extension import Extension
import sys

import versioneer

cmdclass=versioneer.get_cmdclass()

try:
    from Cython.Build import cythonize
    cython_installed = True
except ImportError:
    cythonize = lambda x, *args, **kwargs: x
    cython_installed = False

if cython_installed:
    # Cython is installed.
    # A clear error message will be emitted if new_built_ext has been renamed.
    from Cython.Distutils.build_ext import new_build_ext as build_ext_
else:
    from setuptools.command.build_ext import build_ext as build_ext_

cpp_missing_msg = ' '.join((
    '{cpp_path!r} is missing.',
    'Run the transpile_cython command to generate.',
))

cpp_outdated_msg = ' '.join((
    '{path!r} has been modified after its dependent {cpp_path!r}.',
    'Run the transpile_cython command to regenerate.',
    'Set pass --force-outdated-sources to disable this check.',
))

cython_missing_msg = ' '.join((
    'Cython is required to perform this operation.',
    'Either install Cython or disable do not run commands which require',
    'Cython, such as transpile_cython.',
))

def decythonize(extensions, **kwargs):
    # TODO: use create_extension_list if available

    wrapped_extensions = ExtensionList(options=kwargs)
    for extension in extensions:
        extension = WrappedExtension.from_extension(extension)
        wrapped_extensions.append(extension)
        sources = []
        for path in extension.sources:
            base, ext = splitext(path)
            if ext in ('.pyx'):
                # TODO: glob search

                language = kwargs.get('language')
                if language is None:
                    language = extension.language
                if language is None:
                    language = 'c++' # TODO: hard-coded here
                # TODO: detect language from file directive

                ext = '.cpp' if language == 'c++' else '.c'
                path = base + ext

                extension.language = language

                # TODO: fail if multiple files .pyx are part of the extension.

            sources.append(path)

        extension.sources = sources

    return wrapped_extensions


class BuildError(RuntimeError):
    pass


class ExtensionList(list):
    def __init__(self, *args, options=None, **kwargs):
        super(ExtensionList, self).__init__(*args, **kwargs)
        self.options = options


class WrappedExtension(Extension):
    @classmethod
    def from_extension(cls, extension):
        instance = cls('', [])
        instance.__dict__ = extension.__dict__.copy()
        instance.original_extension = extension
        return instance


class transpile_cython(Command):
    description = "transpiles Cython sources (.pyx) to .c / .cpp outputs"
    user_options = [
        ('force', 'f', "forcibly build everything (ignore file timestamps)"),
        ('parallel', 'j', "number of parallel build jobs"),
    ]

    def initialize_options(self):
        self.force = 0
        self.parallel = None

    def finalize_options(self):
        self.nthreads = int(self.parallel) if self.parallel is not None else 0

    def run(self):
        if not cython_installed:
            raise BuildError(cython_missing_msg)

        if len(self.distribution.ext_modules) == 0:
            return

        if isinstance(self.distribution.ext_modules, ExtensionList):
            kwargs = self.distribution.ext_modules.options
        else:
            kwargs = dict()

        extensions = [
                extension.original_extension
                if isinstance(extension, WrappedExtension) else extension
                for extension in self.distribution.ext_modules
            ]

        kwargs['nthreads'] = self.nthreads
        kwargs['force'] = bool(self.force)

        self.distribution.ext_modules[:] = cythonize(extensions, **kwargs)


class CheckOutdatedMixin(object):
    checking_stuff_user_options = [
        (
            'force-outdated-sources',
            None,
            "Force the operation to continue although outdated sources " +
            "have been detected",
        )
    ]
    checking_stuff_boolean_options = [
        'force-outdated-sources'
    ]

    def initialize_options(self):
        super(CheckOutdatedMixin, self).initialize_options()
        self.force_outdated_sources = 0

    def check_cythonized_extensions(self):
        options = self.distribution.ext_modules.options

        if 'include_path' not in options:
            options['include_path'] = ['.']

        from Cython.Build.Dependency import create_extension_list
        from Cython.Compiler.Main import Context
        from Cython.Compiler.Options import CompilationOptions

        c_options = CompilationOptions(**options)
        ctx = Context.from_options(c_options)
        options = c_options

        module_list, _ = create_extension_list(
            self.distribution.ext_modules,
            ctx = ctx,
            **options,
        )

        # can now retrieve the complete list of dependents?

        # Should have parsed language!

        # TODO

    def check_extensions(self):
        for extension in self.distribution.ext_modules:
            wrapped = None
            if isinstance(extension, WrappedExtension):
                wrapped = extension
                extension = extension.original_extension

            for path in extension.sources:
                base, ext = splitext(path)
                if ext in ('.pyx'):
                    language = wrapped.language if wrapped is not None else None
                    ext = '.cpp' if language == 'c++' else '.c'

                    cpp_path = base + ext

                    if not isfile(cpp_path):
                        raise BuildError(
                            cpp_missing_msg.format(path=path, cpp_path=cpp_path),
                        )

                    # TODO: is there any way of detecting that this is being run on a package
                    # (sdist)?

                    is_outdated = stat(path).st_mtime > stat(cpp_path).st_mtime
                    if not self.force_outdated_sources and is_outdated:
                        raise BuildError(
                            cpp_outdated_msg.format(path=path, cpp_path=cpp_path),
                        )


if 'build_ext' in cmdclass:
    build_ext_ = cmdclass['build_ext']


class build_ext(CheckOutdatedMixin, build_ext_):
    user_options = build_ext_.user_options + \
        CheckOutdatedMixin.checking_stuff_user_options
    boolean_options = build_ext_.boolean_options + \
        CheckOutdatedMixin.checking_stuff_boolean_options

    def run(self):
        self.check_extensions()
        super(build_ext, self).run()


if 'sdist' in cmdclass:
    sdist_ = cmdclass['sdist']


class sdist(CheckOutdatedMixin, sdist_):
    user_options = sdist_.user_options + \
        CheckOutdatedMixin.checking_stuff_user_options
    boolean_options = sdist_.boolean_options + \
        CheckOutdatedMixin.checking_stuff_boolean_options

    def run(self):
        self.check_extensions()
        super(sdist, self).run()

    def make_release_tree(self, base_dir, files):
        import toml

        super(sdist, self).make_release_tree(base_dir, files)

        pyproject_path = pathjoin(base_dir, 'pyproject.toml')
        if isfile(pyproject_path):
            with open(pyproject_path) as f:
                config = toml.load(f)

            if (
                not 'build-system' in config or
                not 'requires' in config['build-system']
            ):
                return

            config['build-system']['requires'] = filter(
                lambda s: s.lower() not in ('cython', 'toml'),
                config['build-system']['requires'],
            )

            with open(pyproject_path, 'w') as f:
                toml.dump(config, f)

cmdclass.update({
    'transpile_cython': transpile_cython,
    'build_ext': build_ext,
    'sdist': sdist,
})

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
    version = versioneer.get_version(),
    license = 'MIT',
    author = 'Paul Skopnik',
    author_email = 'paul@skopnik.me',
    url = 'https://github.com/pskopnik/apq',
    description = (
        'Fast addressable priority queues supporting advanced operations'
    ),
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    keywords = (
        'addressable priority queue heap priorityqueue ' +
        'datastructures min max mapping'
    ),
    packages = ['apq'],
    package_dir = {'': 'py_src'},
    package_data = {'apq': ['*.pyi', 'py.typed']},
    zip_safe = False,
    python_requires = ">=3.6, <4",
    cmdclass = cmdclass,
    ext_modules = decythonize(
        extensions,
        annotate = True,
        # gdb_debug = True,
    ),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
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
