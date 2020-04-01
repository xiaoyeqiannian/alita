#coding: utf-8

import os
import sys
import importlib
import logging
import time
import flask_script

logger = logging.getLogger(__name__)

class IntervalRun(flask_script.Command):
    capture_all_args = True
    '''run function some times
    Usage:
    interval mua.admin uploadgif 60 100
    '''
    def run(self, arg):
        module, function, interval, count = arg[:4]
        def fp2mod(filename):
            # filepath to model
            # It is a module -- insert its dir into sys.path and try to
            # import it. If it is part of a package, that possibly
            # won't work because of package imports.
            dirname, filename = os.path.split(filename)
            np = os.path.join(dirname, filename[:-3])
            return np.replace('/', '.')

        FORMAT = '%(asctime)s [%(levelname)s] %(process)d/%(thread)d %(name)s %(filename)s:%(funcName)s:%(lineno)d - %(message)s'
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(FORMAT)
        logging.getLogger().addHandler(ch)

        print('enter interval mode')

        if module.endswith(".py"):
            module = fp2mod(module)

        mod = importlib.import_module(module)
        print('load module', module, mod)

        f = getattr(mod, function)

        interval = int(interval)
        count = int(count)
        args = arg[4:]
        while count:
            print('run once')
            r = f(*args)

            if not r:
                print('failed')
                break

            print('succeeded')

            count = count - 1
            if count > 0:
                time.sleep(interval * 60)

        return True


# @manager.option('-m', '--module', help='run doctest of the module')
# @manager.command
class RunDocTest(flask_script.Command):
    capture_all_args = True
    def run(self, arg):
        module = arg[0]
        """run doctest with module(not file), usage:
        test mars.sixty
        """

        logger.info("doctest %s start", module)

        def fp2mod(filename):
            # filepath to model
            # It is a module -- insert its dir into sys.path and try to
            # import it. If it is part of a package, that possibly
            # won't work because of package imports.
            dirname, filename = os.path.split(filename)
            np = os.path.join(dirname, filename[:-3])
            return np.replace('/', '.')

        if module.endswith(".py"):
            module = fp2mod(module)

        mod = importlib.import_module(module)

        import doctest
        ret = doctest.testmod(mod, verbose=False, report=True)
        if ret:
            return 1
        return 0


class RunModule(flask_script.Command):
    capture_all_args = True
    def run(self, arg):
        module = arg[0]
        def fp2mod(filename):
            # filepath to model
            # It is a module -- insert its dir into sys.path and try to
            # import it. If it is part of a package, that possibly
            # won't work because of package imports.
            dirname, filename = os.path.split(filename)
            np = os.path.join(dirname, filename[:-3])
            return np.replace('/', '.')

        if module.endswith(".py"):
            module = fp2mod(module)

        mod = importlib.import_module(module)

        f = getattr(mod, 'main')
        if not f:
            raise ImportError('not found main()')

        return f()

