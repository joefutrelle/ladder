import os
import sys
import time
from functools import wraps
from types import GeneratorType

def coalesce(*args):
    """return first non-None arg or None if none"""
    for arg in args:
        if arg is not None:
            return arg
    return None

def search_path(pathname_suffix):
    """search the python path for a pathname relative to it"""
    cands = [os.path.join(d,pathname_suffix) for d in sys.path]
    try:
        return filter(os.path.exists, cands)[0]
    except IndexError:
        return None

# from http://stackoverflow.com/questions/653368/how-to-create-a-python-decorator-that-can-be-used-either-with-or-without-paramet
def doublewrap(f):
    '''
    a decorator decorator, allowing the decorator to be used as:
    @decorator(with, arguments, and=kwargs)
    or
    @decorator
    '''
    @wraps(f)
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # actual decorated function
            return f(args[0])
        else:
            # decorator arguments
            return lambda realf: f(realf, *args, **kwargs)
    return new_dec

@doublewrap
def memoize(fn,ttl=31557600,ignore_exceptions=False,key=None):
    """decorator to memoize a function by its args,
    with an expiration time. use this to wrap an idempotent
    or otherwise cacheable getter or transformation function.
    the function args must be hashable.
    ignore exceptions means not to expire values in the case
    that the function to generate them raises an exception.
    if a generator is received, silently applies list() to it.
    be very careful about memoizing generator functions as this
    may not be desired"""
    cache = {}
    exp = {}
    @wraps(fn)
    def inner(*args,**kw):
        now = time.time()
        if key is not None:
            args_key = key(args)
        else:
            args_key = args
        if args_key not in exp or now > exp[args_key] or args_key not in cache:
            try:
                new_value = fn(*args,**kw)
            except:
                if ignore_exceptions and args_key in cache:
                    new_value = cache[args_key]
                else:
                    raise
            # we've got a value to cache, but it's a generator; freeze it
            if isinstance(new_value, GeneratorType):
                new_value = list(new_value)
            cache[args_key] = new_value
            exp[args_key] = now + ttl
        return cache[args_key]
    return inner
