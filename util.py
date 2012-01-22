import math
import functools 
import re

STRINGRE = r'[a-zA-Z0-9_-]+'
STRINGPROG = re.compile(STRINGRE)

class UnsafeFormatError(Exception):
    pass

def verify_string(s):
    if( STRINGPROG.match(s) ):
        return True
    return False

def check_string_input(fn):
    # Lookup the @distutils.wraps or whateer it's called
    @functools.wraps(fn)
    def wrap(*args, **kwargs):  
        try:
            for s in args:
                if not verify_string(s):
                    raise UnsafeFormatError(
                            "The string {string} is invalid. Valid " + \
                            "characters are alphanumeric, '_', and '-'".format(string=s)
                            )
            ret = fn(*args, **kwargs)
            return ret
        except UnsafeFormatError, e:
            raise
    wrap.__doc__ = fn.__doc__
    return wrap

def price_to_int(price):
    return int(math.floor(price.strip('$')))

def percent_to_int(pct):
    return int(math.floor(pct.strip("%")))

def tofloat(num):
    return float(''.join(num.split(',')))

def format_number(string):
    try:
        s = string.strip('$')
        s = s.strip('%')
        return tofloat(s)
    except:
        return None
