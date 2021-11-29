import sys
import abc


class AnchorType(abc.ABC):
    
    def __init__(self, type_name):
        self._type = type_name

    @property
    def type(self):
        return self._type


class Boolean(AnchorType, int):

    def __init__(self, value):
        AnchorType.__init__(self, 'Boolean')
        self.__value = value

    @property
    def value(self):
        return self.__value


class Null(AnchorType):

    def __init__(self, value):
        AnchorType.__init__(self, 'NullType')
        self.__value = value

    @property
    def value(self):
        return self.__value


class Integer(AnchorType, int):
    
    def __init__(self, value):
        AnchorType.__init__(self, 'Integer')
        self.__value = value

    @property
    def value(self):
        return self.__value


class Float(AnchorType, float):

    def __init__(self, value):
        AnchorType.__init__(self, 'Float')
        self.__value = value

    @property
    def value(self):
        return self.__value


class Complex(AnchorType, complex):
    
    def __init__(self, value):
        AnchorType.__init__(self, 'Complex')
        self.__value = value

    @property
    def value(self):
        return self.__value


class String(AnchorType, str):
    
    def __init__(self, value):
        AnchorType.__init__(self, 'String')
        self.__value = value

    @property
    def value(self):
        return self.__value


class Tuple(AnchorType, tuple): 
    
    def __init__(self, value):
        AnchorType.__init__(self, 'Tuple')

    def __new__(self, value):
        return tuple.__new__(self, value)


class List(AnchorType, list):

    def __init__(self, value):
        AnchorType.__init__(self, 'List')
        self.extend(value)


class Dict(AnchorType, dict):

    def __init__(self, value):
        AnchorType.__init__(self, 'Dict')
        self.update(value)


class Function(AnchorType):

    def __init__(self, name, parameters, body, **flags):
        AnchorType.__init__(self, 'Function')
        self.__name = name
        self.__parameters = parameters
        self.__body = body
        self.__flags = flags
    
    @property
    def name(self):
        return self.__name

    @property
    def parameters(self):
        return self.__parameters

    @property
    def body(self):
        return self.__body

    @property
    def flags(self):
        return self.__flags


class Class(AnchorType):

    def __init__(self, name, superclasses, properties, methods, **flags):
        AnchorType.__init__(self, 'Class')
        self.__name = name
        self.__superclasses = superclasses
        self.__properties = properties
        self.__methods = methods
        self.__flags = flags
    
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

    @property
    def flags(self):
        return self.__flags


class Object(AnchorType):

    def __init__(self, classname, symtable):
        AnchorType.__init__(self, classname)
        self.__symtable = symtable
    
    @property
    def symtable(self):
        return self.__symtable


# Anchor stream name to Python stream
STREAM = {
    'stdin': sys.stdin,
    'stdout': sys.stdout,
    'stderr': sys.stderr,
}


def builtin_print(value):
    return print(value, file=STREAM['stdout'])


# Anchor builtin function name to Python function pointer
FUNCTION = {
    'print': builtin_print,
}
