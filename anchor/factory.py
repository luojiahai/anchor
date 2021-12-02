import abc
import typing


__all__: list[str] = ['AST', 'SYMTABLE',]


class Factory(abc.ABC):

    def __init__(self):
        self._builders: dict[str, typing.Any] = {}

    def _registerbuilder(self, key: str, builder: typing.Any) -> None:
        self._builders[key] = builder

    def new(self, key, **kwargs) -> typing.Any:
        builder: typing.Any = self._builders.get(key)
        if (not builder):
            raise ValueError(key)
        return builder(**kwargs)


class ASTNodeFactory(object):

    class __ASTNodeFactory(Factory):

        __astnodename: dict[typing.Type, str] = dict({
            bool: 'Boolean',
            type(None): 'Null',
            int: 'Integer',
            float: 'Float',
            complex: 'Complex',
            str: 'String',
            tuple: 'Tuple',
            list: 'List',
            dict: 'Dict',
        })

        def __init__(self, declarations: list[tuple[str, typing.Type]]):
            super().__init__()
            for key, builder in declarations:
                self._registerbuilder(key, builder)
        
        def new(self, literal: typing.Any) -> typing.Any:
            key = self.__astnodename[type(literal)]
            kwargs = dict({'literal': literal})
            return super().new(key, **kwargs)

    __instance: __ASTNodeFactory = None

    def __new__(cls, declarations: list[tuple[str, typing.Type]]):
        if (not ASTNodeFactory.__instance):
            ASTNodeFactory.__instance = \
                ASTNodeFactory.__ASTNodeFactory(declarations)
        return ASTNodeFactory.__instance


class SymbolTableFactory(object):

    class __SymbolTableFactory(Factory):

        def __init__(self, declarations: list[tuple[str, typing.Type]]):
            super().__init__()
            for key, builder in declarations:
                self._registerbuilder(key, builder)

    __instance: __SymbolTableFactory = None

    def __new__(cls, declarations: list[tuple[str, typing.Type]]):
        if (not SymbolTableFactory.__instance):
            SymbolTableFactory.__instance = \
                SymbolTableFactory.__SymbolTableFactory(declarations)
        return SymbolTableFactory.__instance


AST: ASTNodeFactory = None
SYMTABLE: SymbolTableFactory = None
