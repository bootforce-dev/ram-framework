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
    from setuptools.command.build_scripts import build_scripts as _build_scripts
except ImportError:
    from distutils.command.build_scripts import build_scripts as _build_scripts

try:
    from setuptools.command.build_py import build_py as _build_py
except ImportError:
    from distutils.comman.build_py import build_py as _build_py

try:
    from setuptools.cmd import Command
except ImportError:
    from distutils.cmd import Command

import os


__project__ = 'ram-framework'
__version__ = VersionInfo(__project__).release_string()


class build(_build):
    sub_commands = _build.sub_commands + [
        ('build_ram', lambda self: True),
    ]


class install(_install):
    sub_commands = _install.sub_commands + [
        ('install_ram', lambda self: True),
    ]


class build_ram(Command):
    def initialize_options(self):
        self.lib_root = None
        self.build_dir = None

    def finalize_options(self):
        if self.build_dir is None:
            build_base = self.get_finalized_command('build').build_base
            self.build_dir = os.path.join(build_base, 'ram')

        if self.lib_root is None:
            self.lib_root = 'lib'

    def run(self):
        for dirpath, dirs, files in os.walk(self.lib_root):

            scripts = []
            modules = []
            various = []

            for _ in files:
                _name, _ext = os.path.splitext(_)
                _path = os.path.join(dirpath, _)
                if os.path.isfile(_path) and os.access(_path, os.X_OK):
                    scripts.append(_path)
                elif _ext == '.py':
                    modules.append(_name)
                else:
                    various.append(_)

            if scripts:
                build_scripts = _build_scripts(self.distribution)
                build_scripts.ensure_finalized()

                build_scripts.build_dir = os.path.join(self.build_dir, dirpath)
                build_scripts.scripts = scripts

                build_scripts.run()

            if modules or various:
                build_py = _build_py(self.distribution)
                build_py.ensure_finalized()

                build_py.build_lib = os.path.join(self.build_dir, dirpath)
                build_py.py_modules = []
                build_py.package_dir = {'': dirpath}
                build_py.packages = ['']

                build_py.package_data = {}

                build_py.data_files = [('', dirpath, build_py.build_lib, various)]

                build_py.run()


class install_ram(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        pass


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
            ('/etc/bash_completion.d', ['etc/bash_completion.d/ram']),
        ],# + list(list_units('', 'lib')),
        cmdclass={
            'build': build,
            'build_ram': build_ram,
            'install': install,
            'install_ram': install_ram,
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
        )
    )
