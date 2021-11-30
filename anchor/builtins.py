import sys
import abc
import typing


# Anchor stream name to Python stream
STREAM: dict[str, typing.TextIO] = {
    'stdin': sys.stdin,
    'stdout': sys.stdout,
    'stderr': sys.stderr,
}


class AnchorType(abc.ABC):
    
    def __init__(self, typename: str, **flags):
        self.__typename: str = typename
        self.__flags: dict[str, typing.Any] = flags

    @property
    def typename(self) -> str:
        return self.__typename

    @property
    def flags(self) -> dict[str, typing.Any]:
        return self.__flags


class Boolean(AnchorType, int):

    def __init__(self, value: int, **flags):
        AnchorType.__init__(self, 'Boolean', **flags)
        self.__value: int = value

    @property
    def value(self) -> int:
        return self.__value


class Null(AnchorType):

    def __init__(self, value: str, **flags):
        AnchorType.__init__(self, 'NullType', **flags)
        self.__value: str = value

    @property
    def value(self) -> str:
        return self.__value


class Integer(AnchorType, int):
    
    def __init__(self, value: int, **flags):
        AnchorType.__init__(self, 'Integer', **flags)
        self.__value: int = value

    @property
    def value(self) -> int:
        return self.__value


class Float(AnchorType, float):

    def __init__(self, value: float, **flags):
        AnchorType.__init__(self, 'Float', **flags)
        self.__value: float = value

    @property
    def value(self) -> float:
        return self.__value


class Complex(AnchorType, complex):
    
    def __init__(self, value: complex, **flags):
        AnchorType.__init__(self, 'Complex', **flags)
        self.__value: complex = value

    @property
    def value(self) -> complex:
        return self.__value


class String(AnchorType, str):
    
    def __init__(self, value: str, **flags):
        AnchorType.__init__(self, 'String', **flags)
        self.__value: str = value

    @property
    def value(self) -> str:
        return self.__value


class Tuple(AnchorType, tuple): 
    
    def __init__(self, value: tuple, **flags):
        AnchorType.__init__(self, 'Tuple', **flags)

    def __new__(self, value):
        return tuple.__new__(self, value)


class List(AnchorType, list):

    def __init__(self, value: list, **flags):
        AnchorType.__init__(self, 'List', **flags)
        self.extend(value)


class Dict(AnchorType, dict):

    def __init__(self, value: dict, **flags):
        AnchorType.__init__(self, 'Dict', **flags)
        self.update(value)


class Function(AnchorType):

    def __init__(self, **flags):
        AnchorType.__init__(self, 'Function', **flags)


class Class(AnchorType):

    def __init__(self, **flags):
        AnchorType.__init__(self, 'Class', **flags)


class Object(AnchorType, object):

    def __init__(self, classname: str, **flags):
        AnchorType.__init__(self, classname, **flags)


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
