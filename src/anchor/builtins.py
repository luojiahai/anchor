import sys
import abc
import typing


__all__: list[str] = [
    'STREAM', 'CLASS', 'FUNCTION',
    'Boolean', 'Null', 'Integer', 'Float', 'Complex', 'String', 
    'Tuple', 'List', 'Dict', 'Function', 
    'Annotation', 'Class', 'Property', 'Method', 'Instance',
]


# Anchor stream name to Python stream
STREAM: dict[str, typing.TextIO] = {
    'stdin': sys.stdin,
    'stdout': sys.stdout,
    'stderr': sys.stderr,
}


class Type(abc.ABC):
    
    def __init__(self, typename: str, **kwargs):
        self.__typename: str = typename
        self.__kwargs: dict[str, typing.Any] = kwargs

    @property
    def typename(self) -> str:
        return self.__typename

    @property
    def kwargs(self) -> dict[str, typing.Any]:
        return self.__kwargs


class Boolean(Type, int):

    def __init__(self, value: int, **kwargs):
        Type.__init__(self, 'Boolean', **kwargs)
        self.__value: int = value

    @property
    def value(self) -> int:
        return self.__value


class Null(Type):

    def __init__(self, value: str, **kwargs):
        Type.__init__(self, 'Null', **kwargs)
        self.__value: str = value

    @property
    def value(self) -> str:
        return self.__value

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value


class Integer(Type, int):
    
    def __init__(self, value: int, **kwargs):
        Type.__init__(self, 'Integer', **kwargs)
        self.__value: int = value

    @property
    def value(self) -> int:
        return self.__value


class Float(Type, float):

    def __init__(self, value: float, **kwargs):
        Type.__init__(self, 'Float', **kwargs)
        self.__value: float = value

    @property
    def value(self) -> float:
        return self.__value


class Complex(Type, complex):
    
    def __init__(self, value: complex, **kwargs):
        Type.__init__(self, 'Complex', **kwargs)
        self.__value: complex = value

    @property
    def value(self) -> complex:
        return self.__value


class String(Type, str):
    
    def __init__(self, value: str, **kwargs):
        Type.__init__(self, 'String', **kwargs)
        self.__value: str = value

    @property
    def value(self) -> str:
        return self.__value


class Tuple(Type, tuple): 
    
    def __init__(self, value: tuple, **kwargs):
        Type.__init__(self, 'Tuple', **kwargs)

    def __new__(self, value):
        return tuple.__new__(self, value)


class List(Type, list):

    def __init__(self, value: list, **kwargs):
        Type.__init__(self, 'List', **kwargs)
        self.extend(value)


class Dict(Type, dict):

    def __init__(self, value: dict, **kwargs):
        Type.__init__(self, 'Dict', **kwargs)
        self.update(value)


class Function(Type):

    def __init__(self, **kwargs):
        Type.__init__(self, 'Function', **kwargs)


class Annotation(Type):

    def __init__(self, value: str, **kwargs):
        super().__init__('Annotation', **kwargs)
        self.__value: str = value

    @property
    def value(self) -> str:
        return self.__value


class Class(Type):

    def __init__(self, **kwargs):
        Type.__init__(self, 'Class', **kwargs)


class Property(Type):

    def __init__(self, **kwargs):
        Type.__init__(self, 'Property', **kwargs)


class Method(Type):

    def __init__(self, **kwargs):
        Type.__init__(self, 'Method', **kwargs)


class Instance(Type, object):

    def __init__(self, cls: Class, **kwargs):
        Type.__init__(self, cls.typename, **kwargs)


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
