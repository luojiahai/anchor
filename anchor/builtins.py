import sys
import abc


# Anchor stream name to Python stream
STREAM = {
    'stdin': sys.stdin,
    'stdout': sys.stdout,
    'stderr': sys.stderr,
}


class AnchorType(abc.ABC):
    
    def __init__(self, type_name, **flags):
        self.__type = type_name
        self.__flags = flags

    @property
    def type(self):
        return self.__type

    @property
    def flags(self):
        return self.__flags


class Boolean(AnchorType, int):

    def __init__(self, value, **flags):
        AnchorType.__init__(self, 'Boolean', **flags)
        self.__value = value

    @property
    def value(self):
        return self.__value


class Null(AnchorType):

    def __init__(self, value, **flags):
        AnchorType.__init__(self, 'NullType', **flags)
        self.__value = value

    @property
    def value(self):
        return self.__value


class Integer(AnchorType, int):
    
    def __init__(self, value, **flags):
        AnchorType.__init__(self, 'Integer', **flags)
        self.__value = value

    @property
    def value(self):
        return self.__value

    def Anchor_init(self, value):
        self.__init__(value)

    def Anchor_plus(self, other):
        value = self.__add__(other)
        return TYPE[type(value)](value)


class Float(AnchorType, float):

    def __init__(self, value, **flags):
        AnchorType.__init__(self, 'Float', **flags)
        self.__value = value

    @property
    def value(self):
        return self.__value


class Complex(AnchorType, complex):
    
    def __init__(self, value, **flags):
        AnchorType.__init__(self, 'Complex', **flags)
        self.__value = value

    @property
    def value(self):
        return self.__value


class String(AnchorType, str):
    
    def __init__(self, value, **flags):
        AnchorType.__init__(self, 'String', **flags)
        self.__value = value

    @property
    def value(self):
        return self.__value


class Tuple(AnchorType, tuple): 
    
    def __init__(self, value, **flags):
        AnchorType.__init__(self, 'Tuple', **flags)

    def __new__(self, value):
        return tuple.__new__(self, value)


class List(AnchorType, list):

    def __init__(self, value, **flags):
        AnchorType.__init__(self, 'List', **flags)
        self.extend(value)


class Dict(AnchorType, dict):

    def __init__(self, value, **flags):
        AnchorType.__init__(self, 'Dict', **flags)
        self.update(value)


class Function(AnchorType):

    def __init__(self, name, parameters, body, **flags):
        AnchorType.__init__(self, 'Function', **flags)
        self.__name = name
        self.__parameters = parameters
        self.__body = body
    
    @property
    def name(self):
        return self.__name

    @property
    def parameters(self):
        return self.__parameters

    @property
    def body(self):
        return self.__body


class Class(AnchorType):

    def __init__(self, name, superclasses, properties, methods, **flags):
        AnchorType.__init__(self, 'Class', **flags)
        self.__name = name
        self.__superclasses = superclasses
        self.__properties = properties
        self.__methods = methods
    
    @property
    def name(self):
        return self.__name

    @property
    def superclasses(self):
        return self.__superclasses

    @property
    def properties(self):
        return self.__properties

    @property
    def methods(self):
        return self.__methods


class Object(AnchorType):

    def __init__(self, classname, symtable, **flags):
        AnchorType.__init__(self, classname, **flags)
        self.__symtable = symtable
    
    @property
    def symtable(self):
        return self.__symtable


TYPE = {
    bool: Boolean,
    type(None): Null,
    int: Integer,
    float: Float,
    complex: Complex,
    str: String,
    tuple: Tuple,
    list: List,
    dict: Dict,
}

CLASS = {
    'Boolean': Boolean,
    'Null': Null,
    'Integer': Integer,
    'Float': Float,
    'Complex': Complex,
    'String': String,
    'Tuple': Tuple,
    'List': List,
    'Dict': Dict,
}


def builtin_print(value):
    return print(value, file=STREAM['stdout'])


# Anchor builtin function name to Python function pointer
FUNCTION = {
    'print': builtin_print,
}
