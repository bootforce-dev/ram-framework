#!/usr/bin/python

from pkg_resources import get_distribution, DistributionNotFound

try:
    __distrib__ = get_distribution('ram-framework')

    if not __file__.startswith(__distrib__.location):
        raise DistributionNotFound('ram-framework')

    __version__ = __distrib__.version

except DistributionNotFound:
    __version__ = '(dev)'
