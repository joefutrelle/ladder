import sys
import re

from ladder import Resolver

# pretty-print bindings
def pprint(bindings,header=''):
    if len(bindings) == 0:
        print '%s {}' % header
        return
    if len(bindings) == 1:
        print '%s %s' % (header, bindings)
        return
    # remove integer bindings (groups from the most recent regex match)
    for var in bindings.keys():
        try:
            int(var)
            del bindings[var]
        except ValueError:
            pass
    # colon-align
    width = max(len(var) for var in bindings)
    print '%s {' % header
    for var in sorted(bindings):
        print '%s%s: "%s"' % (' ' * (width-len(var)),var,bindings[var])
    print '}'

if __name__=='__main__':
    """usage example
    python ladder foo.xml:bar.xml some.resolver.name var1=val1 var2=val2 ...
    """
    path, name = sys.argv[1:3]
    xml_files = re.split(':',path)
    bindings = dict(re.split('=',kw) for kw in sys.argv[3:])

    resolver = Resolver(*xml_files)
    n = 0
    for result in resolver.invoke(name,**bindings):
        n += 1
        pprint(result,'Solution %d' % n)
