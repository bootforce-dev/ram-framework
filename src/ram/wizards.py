#!/usr/bin/python

import ram.process

from ram.watches import press_key

from traceback import print_exc


class Unit(object):
    def __init__(self, *steps, **kwargs):
        self.kwargs = kwargs
        self.steps = tuple(steps)

    def __call__(self, *args, **kwargs):
        local = kwargs.pop('local', {}).copy()
        local.update(**self.kwargs)
        local.update(**kwargs)

        debug = local.pop('debug', None)
        debug = int(debug) if debug is not None else -1

        pause = local.pop('pause', None)
        pause = int(pause) if pause is not None else -1

        fatal = local.pop('fatal', False)

        delay = local.pop('delay', None)
        delay = int(delay) if delay is not None else 0

        shell = local.pop('shell', False)
        shell = (
            shell if isinstance(shell, basestring) else
            '/bin/sh' if shell else None
        )

        label = local.pop('label', None)
        title = local.pop('title', None)

        e = None
        try:
            for _step in self.steps:
                _step()
        except Exception as e:
            print
            print_exc()

        if not debug:
            point = None
        elif not e and debug < 0:
            point = None
        elif not e:
            point = ".... Debug"
        elif not fatal:
            point = ":::: Error"
        else:
            point = "!!!! Fatal"

        if point:
            print
            print "%s at:" % point
            if title is not None:
                print "\ttitle: %s" % title
            if label is not None:
                print "\tlabel: %s" % label
            print

        if (pause and e) or (pause > 0):
            try:
                press_key(timeout=abs(delay))
            except OverflowError:
                if delay > 0:
                    pass
                else:
                    raise
            except KeyboardInterrupt:
                if shell:
                    ram.process.launch(shell)
                else:
                    raise

        if (fatal and e):
            raise e

    def run(self, *args, **kwargs):
        return self(*args, **kwargs)
