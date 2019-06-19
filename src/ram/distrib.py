#!/usr/bin/python

from setuptools import setup, find_packages
from setuptools import Distribution, Command

import os

class build_ram(Command):
    def initialize_options(self):
        self.build_base = None
        self.executable = None
        self.compile = None
        self.optimize = None

    def finalize_options(self):
        self.set_undefined_options('build',
            ('build_base', 'build_base'),
        )

        self.set_undefined_options('build_scripts',
            ('executable', 'executable'),
        )

        self.set_undefined_options('build_py',
            ('compile', 'compile'),
            ('optimize', 'optimize'),
        )

        for (_dst, _src), _dist in self.distribution.ram_dists.items():
            _build = _dist.reinitialize_command('build', reinit_subcommands=True)
            _build.build_base = os.path.join(self.build_base, 'ram', _src, '__pybuild__')

            _build_scripts = _dist.reinitialize_command('build_scripts')
            _build_scripts.executable = self.executable

            _build_py = _dist.reinitialize_command('build_py')
            _build_py.compile = self.compile
            _build_py.optimize = self.optimize


    def run(self):
        for (_dst, _src), _dist in self.distribution.ram_dists.items():
            _dist.run_command('build')


class install_ram(Command):
    def initialize_options(self):
        self.root = None
        self.compile = None
        self.optimize = None

    def finalize_options(self):
        self.set_undefined_options('install',
            ('root', 'root'),
        )

        self.set_undefined_options('install_lib',
            ('compile', 'compile'),
            ('optimize', 'optimize'),
        )

        for (_dst, _src), _dist in self.distribution.ram_dists.items():
            _install = _dist.reinitialize_command('install', reinit_subcommands=True)
            _install.root = self.root

            _install.install_scripts = os.path.join('$base', _dst)
            _install.install_lib = os.path.join('$base', _dst)

            _install_scripts = _dist.reinitialize_command('install_scripts')

            _install_lib = _dist.reinitialize_command('install_lib')
            _install_lib.compile = self.compile
            _install_lib.optimize = self.optimize


    def get_outputs(self):
        return sum(
            (_dist.get_command_obj('install', create=0).get_outputs()
            for _, _dist in self.distribution.ram_dists.items()
            ), []
        )

    def run(self):
        for (_dst, _src), _dist in self.distribution.ram_dists.items():
            _dist.run_command('install')


class DummyCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        pass

    def get_outputs(self): return []


class RamDistribution(Distribution):
    def __init__(self, attrs=None):
        self.ram_units = None

        Distribution.__init__(self, attrs)

        self.cmdclass.setdefault('build_ram', build_ram)
        self.cmdclass.setdefault('install_ram', install_ram)

        self.ram_dists = {}

        for ram_dst, ram_src in self.ram_units or list():
            for srcpath, dirs, files in os.walk(ram_src):
                dstpath = os.path.normpath(
                    os.path.join(ram_dst, os.path.relpath(srcpath, ram_src))
                )

                scripts = []
                modules = []
                various = []

                for _ in files:
                    _name, _ext = os.path.splitext(_)
                    _path = os.path.join(srcpath, _)
                    if os.path.isfile(_path) and os.access(_path, os.X_OK):
                        scripts.append(_path)
                    elif _ext == '.py':
                        modules.append(_name)
                    else:
                        various.append(_)

                self.ram_dists[dstpath, srcpath] = Distribution(dict(
                    scripts=scripts,
                    package_dir={'': srcpath},
                    packages=[''],
                    package_data={'': various},
                    options=dict(
                        install_scripts={
                            'no_ep': True,
                        },
                    ),
                    cmdclass={
                        'egg_info': DummyCommand,
                        'install_egg_info': DummyCommand,
                    },
                    script_name=self.script_name,
                    script_args=self.script_args,
                ))

    def get_command_class(self, command):
        klass = Distribution.get_command_class(self, command)

        if command in ['build', 'install']:
            class klass(klass):
                sub_commands = klass.sub_commands + [
                    ('%s_ram' % command, lambda self: True),
                ]

            klass.__name__ = command

        return klass


if __name__ == '__main__':
    try:
        from setuptools.command import build_py
    except ImportError:
        from distutils.command import build_py

    class _build_py(build_py.build_py):
        def run(self):
            build_py.build_py.run(self)

            if not self.dry_run:
                _data_of = 'ram'
                for _package, _, _builddir, _ in self.data_files:
                    if _package == _data_of:
                        break
                else:
                    raise KeyError(_data_of)
                version_path = os.path.join(_builddir, 'VERSION')
                with open(version_path, 'w') as version_file:
                    version_file.write(self.distribution.get_version())

    from pbr.version import VersionInfo

    __project__ = 'ram-framework'
    __version__ = VersionInfo(__project__).release_string()

    setup(
        name=__project__,
        version=__version__,
        description='Framework to manage product state and configuration',
        long_description=open('./README.md').read(),
        long_description_content_type='text/markdown',
        author='Roman Valov',
        author_email='roman.valov@gmail.com',
        url='https://ram-framework.readthedocs.io/en/latest/',
        license='MIT',
        package_dir={'': 'src'},
        packages=find_packages(where='src', exclude=['tests', 'tests.*']),
        package_data={'': ['VERSION']},
        ram_units=[
            ('lib/ram', 'lib/ram'),
        ],
        data_files=[
            ('share/ram', ['share/ram/srv.functions', 'share/ram/ram.functions']),
            ('/etc/bash_completion.d', ['etc/bash_completion.d/ram']),
        ],
        distclass=RamDistribution,
        cmdclass={
            'build_py': _build_py,
        },
        scripts=['bin/ram', 'bin/ram-symbols'],
        classifiers=(
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Environment :: Console :: Newt',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
            'Topic :: System :: Installation/Setup',
            'Topic :: System :: Systems Administration',
            'Topic :: Utilities',
        ),
    )
