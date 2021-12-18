import sys
import typing
import abc


__all__: typing.List[str] = list([
    'STREAM', 'CLASS', 'FUNCTION',
    'Boolean', 'Null', 'Integer', 'Float', 'Complex', 'String', 
    'Tuple', 'List', 'Dict', 'Function', 
    'Annotation', 'Class', 'Property', 'Method', 'Instance',
])


# Anchor stream name to Python stream
STREAM: typing.Dict[str, typing.TextIO] = dict({
    'stdin': sys.stdin,
    'stdout': sys.stdout,
    'stderr': sys.stderr,
})


class Type(abc.ABC):
    
    def __init__(self, typename: str, **kwargs) -> None:
        self.__typename: str = typename
        self.__kwargs: typing.Dict[str, typing.Any] = kwargs

    @property
    def typename(self) -> str:
        return self.__typename

    @property
    def kwargs(self) -> typing.Dict[str, typing.Any]:
        return self.__kwargs


class Boolean(Type, int):

    def __init__(self, value: int, **kwargs) -> None:
        Type.__init__(self, 'Boolean', **kwargs)
        self.__value: int = value

    @property
    def value(self) -> int:
        return self.__value


class Null(Type):

    def __init__(self, value: str, **kwargs) -> None:
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
    
    def __init__(self, value: int, **kwargs) -> None:
        Type.__init__(self, 'Integer', **kwargs)
        self.__value: int = value

    @property
    def value(self) -> int:
        return self.__value


class Float(Type, float):

    def __init__(self, value: float, **kwargs) -> None:
        Type.__init__(self, 'Float', **kwargs)
        self.__value: float = value

    @property
    def value(self) -> float:
        return self.__value


class Complex(Type, complex):
    
    def __init__(self, value: complex, **kwargs) -> None:
        Type.__init__(self, 'Complex', **kwargs)
        self.__value: complex = value

    @property
    def value(self) -> complex:
        return self.__value


class String(Type, str):
    
    def __init__(self, value: str, **kwargs) -> None:
        Type.__init__(self, 'String', **kwargs)
        self.__value: str = value

    @property
    def value(self) -> str:
        return self.__value


class Tuple(Type, tuple): 
    
    def __init__(self, value: typing.Tuple, **kwargs) -> None:
        Type.__init__(self, 'Tuple', **kwargs)

    def __new__(self, value):
        return tuple.__new__(self, value)


class List(Type, list):

    def __init__(self, value: typing.List, **kwargs) -> None:
        Type.__init__(self, 'List', **kwargs)
        self.extend(value)


class Dict(Type, dict):

    def __init__(self, value: typing.Dict, **kwargs) -> None:
        Type.__init__(self, 'Dict', **kwargs)
        self.update(value)


class Function(Type):

    def __init__(self, **kwargs) -> None:
        Type.__init__(self, 'Function', **kwargs)


class Annotation(Type):

    def __init__(self, value: str, **kwargs) -> None:
        super().__init__('Annotation', **kwargs)
        self.__value: str = value

    @property
    def value(self) -> str:
        return self.__value


class Class(Type):

    def __init__(self, **kwargs) -> None:
        Type.__init__(self, 'Class', **kwargs)


class Property(Type):

    def __init__(self, **kwargs) -> None:
        Type.__init__(self, 'Property', **kwargs)


class Method(Type):

    def __init__(self, **kwargs) -> None:
        Type.__init__(self, 'Method', **kwargs)


class Instance(Type, object):

    def __init__(self, cls: Class, **kwargs) -> None:
        Type.__init__(self, cls.typename, **kwargs)


CLASS: typing.Dict[str, Type] = dict({
    'Boolean': Boolean,
    'Null': Null,
    'Integer': Integer,
    'Float': Float,
    'Complex': Complex,
    'String': String,
    'Tuple': Tuple,
    'List': List,
    'Dict': Dict,
})


def builtin_print(value):
    return print(value, file=STREAM['stdout'])


# Anchor builtin function name to Python function pointer
FUNCTION: typing.Dict[str, typing.Callable] = dict({
    'print': builtin_print,
})
