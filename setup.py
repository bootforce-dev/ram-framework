#!/usr/bin/python

from setuptools import setup, find_packages

from pbr.version import VersionInfo

try:
    from setuptools.command.install_data import install_data
except ImportError:
    from distutils.command.install_data import install_data

from setuptools.command.easy_install import is_python_script, get_script_header

import os


__project__ = 'ram-framework'
__version__ = VersionInfo(__project__).release_string()


def list_units(install, dirroot):
    for dirpath, dirs, files in os.walk(dirroot):
        filelst = [os.path.join(dirpath, _) for _ in files]
        if filelst:
            yield (os.path.join(install, dirpath), filelst)

class _install_data(install_data):
    def run(self):
        install_data.run(self)
        for _file in self.outfiles:
            if not os.path.isfile(_file):
                continue

            if not os.access(_file, os.X_OK):
                continue

            with open(_file, 'r') as _:
                _exec = _.readline()
                _text = _.read()

            if not _exec.startswith('#!'):
                continue

            try:
                compile(_text, _file, 'exec')
            except SyntaxError:
                continue

            _exec = get_script_header(_exec)

            with open(_file, 'w') as _:
                _.write(_exec)
                _.write(_text)


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
        data_files=[
            ('share/ram', ['share/ram/srv.functions', 'share/ram/ram.functions']),
            ('/etc/bash_completion.d', ['etc/bash_completion.d/ram']),
        ] + list(list_units('', 'lib')),
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
