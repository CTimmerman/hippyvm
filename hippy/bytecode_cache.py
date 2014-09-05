
import os, sys, time
from hippy.phpcompiler import compile_php
from hippy.rpath import abspath

TIMEOUT = 1.0

class BytecodeCache(object):
    def __init__(self, timeout=TIMEOUT):
        self.cached_files = {}
        self.timeout = timeout

    # again, abs_filename is None for stdin
    def _really_compile(self, space, abs_fname):

        if abs_fname is None:
            f = sys.stdin
        else:
            f = open(abs_fname)

        data = f.read(-1)

        # probably don't want to close stdin
        if abs_fname is not None:
            f.close()

        if abs_fname is not None:
            tstamp = os.stat(abs_fname).st_mtime
        else:
            tstamp = time.time()

        bc = compile_php(abs_fname, data, space)
        self.cached_files[abs_fname] = (bc, tstamp)
        return bc

    # pass fname as None for stdin
    def compile_file(self, fname, space):
        now = time.time()

        if fname is None: # you can't cache stdin
            return self._really_compile(space, fname)

        # otherwise this really is a filename
        absname = abspath(fname)
        try:
            bc, tstamp = self.cached_files[absname]
            if now - tstamp >= self.timeout:
                mtime = os.stat(absname).st_mtime
                if mtime > tstamp:
                    raise KeyError
            return bc
        except KeyError:
            return self._really_compile(space, fname)
