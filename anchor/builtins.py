from re import S
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


# Python builtin type name to Anchor builtin type
TYPE = {
    'bool': Boolean,
    'NoneType': Null,
    'int': Integer,
    'float': Float,
    'complex': Complex,
    'str': String,
    'tuple': Tuple,
    'list': List,
    'dict': Dict,
}


# Anchor stream name to Python stream
STREAM = {
    'stdin': sys.stdin,
    'stdout': sys.stdout,
    'stderr': sys.stderr,
}


def builtin_print(value, file='stdout'):
    stream = None
    if (file in STREAM):
        stream = STREAM[file]
    else:
        stream = open(file, 'w')
    assert (stream != None)
    return print(value, file=stream)


# Anchor builtin function name to Python function pointer
FUNCTION = {
    'print': builtin_print,
}
