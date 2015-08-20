import json

# factory method
# internal, does not interpret strings as JSON
def __struct_wrap(item):
    if isinstance(item,basestring):
        return item
    try: # assume dict
        return Struct(item)
    except:
        pass
    try: # assume sequence
        return map(__struct_wrap,item)
    except TypeError:
        return item

# external, accepts JSON strings, sequences, dicts, and keyword args
def structs(item=None,**kv):
    if item is None:
        return __struct_wrap(kv)
    try:
        return __struct_wrap(json.loads(item))
    except:
        pass
    return __struct_wrap(item)
        
def destructs(item):
    if isinstance(item,basestring):
        return item
    try:
        return item.destruct
    except:
        pass
    try:
        return dict([(k,destructs(v)) for k,v in item.iteritems()])
    except:
        pass
    try:
        return map(destructs,item)
    except:
        pass
    return item

# external, accepts Structs, sequences, or primitive values
def jsons(item):
    return json.dumps(destructs(item))

class Struct():
    @property
    def destruct(self):
        result = {}
        for k,v in self.__dict__.iteritems():
            try:
                result[k] = v.destruct
            except AttributeError:
                # handle lists and tuples separately, so no duck typing
                if isinstance(v,list):
                    result[k] = map(lambda e: e.destruct if isinstance(e,Struct) else e, v)
                elif isinstance(v,tuple):
                    result[k] = tuple(map(lambda e: e.destruct if isinstance(e,Struct) else e,v))
                else:
                    result[k] = v
        return result
    
    @property
    def json(self):
        return json.dumps(self.destruct)
    
    def __repr__(self):
        return self.json
    
    def __init__(self, d={}):
        for k,v in d.items():
            self.__dict__[k] = structs(v)
