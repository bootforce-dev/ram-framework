#!/usr/bin/python

from setuptools import setup, find_packages

from pbr.version import VersionInfo

__project__ = 'ram-framework'
__version__ = VersionInfo(__project__).release_string()

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
        ],
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
