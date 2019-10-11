#!/usr/bin/python


import ram.console


class __api__(object):
    def __call__(self, *args, **kwargs):
        return ram.console.capture(*args, **kwargs)
