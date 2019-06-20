#!/usr/bin/python

from setuptools import setup, find_packages

from pbr.version import VersionInfo

try:
    from setuptools.command.install import install as _install
except ImportError:
    from distutils.command.install import install as _install

try:
    from setuptools.command.build import build as _build
except ImportError:
    from distutils.command.build import build as _build

try:
    from setuptools.cmd import Command
except ImportError:
    from distutils.cmd import Command

try:
    from setuptools.dist import Distribution
except ImportError:
    from distutils.dist import Distribution

import os


__project__ = 'ram-framework'
__version__ = VersionInfo(__project__).release_string()


class build(_build):
    def __init__(self, dist):
        self.default = None

        _build.__init__(self, dist)

    def initialize_options(self):
        if self.default is None:
            already = self.__dict__

        _build.initialize_options(self)

        if self.default is None:
            self.default = dict((k, v) for k, v in self.__dict__.items() if not k in already)

    def finalize_options(self):
        if self.default is None:
            raise RuntimeError('no defaults')

        for key in self.default:
            self.default[key] = getattr(self, key)

        _build.finalize_options(self)

    def run(self):
        _build.run(self)

        for (_dst, _src), _dist in self.distribution.ram_dists.items():
            __build = _dist.reinitialize_command('build', reinit_subcommands=1)

            __build.build_base = os.path.join(self.build_base, 'ram', _src, '__pybuild__')

            _dist.run_command('build')
            

class install(_install):
    def __init__(self, dist):
        self.default = None

        _install.__init__(self, dist)

    def initialize_options(self):
        if self.default is None:
            already = self.__dict__

        _install.initialize_options(self)

        if self.default is None:
            self.default = dict((k, v) for k, v in self.__dict__.items() if not k in already)

    def finalize_options(self):
        if self.default is None:
            raise RuntimeError('no defaults')

        for key in self.default:
            self.default[key] = getattr(self, key)

        _install.finalize_options(self)

    def get_outputs(self):
        return sum(
            (_dist.get_command_obj('install').get_outputs()
            for _, _dist in self.distribution.ram_dists.items()
            ), []
        )

    def run(self):
        _install.run(self)

        for (_dst, _src), _dist in self.distribution.ram_dists.items():
            __install = _dist.reinitialize_command('install', reinit_subcommands=1)

            __install.root = self.root

            __install.install_scripts = os.path.join('$base', _dst)
            __install.install_lib = os.path.join('$base', _dst)

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

        self.ram_dists = {}

        for ram_dst, ram_src in self.ram_units:
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
                self.ram_dists[dstpath, srcpath].command_options = self.command_options
                self.ram_dists[dstpath, srcpath].command_options.setdefault('install_scripts', {})['no_ep'] = ('', True)


if __name__ == '__main__':
    setup(
        name=__project__,
        version=__version__,
        description='Framework to manage product state and configuration',
        long_description=open('./README.md').read(),
        long_description_content_type="text/markdown",
        author='Roman Valov',
        author_email='roman.valov@gmail.com',
        url='https://ram-framework.readthedocs.io/en/latest/',
        license='MIT',
        package_dir={'': 'src'},
        packages=find_packages(where='src', exclude=['tests', 'tests.*']),
        ram_units=[
            ('lib/ram', 'lib/ram'),
        ],
        data_files=[
            ('share/ram', ['share/ram/srv.functions', 'share/ram/ram.functions']),
            ('/etc/bash_completion.d', ['share/bash-completion/ram']),
        ],
        distclass=RamDistribution,
        cmdclass={
            'build': build,
            'install': install,
        },
        scripts=['src/bin/ram', 'src/bin/ram-symbols'],
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
