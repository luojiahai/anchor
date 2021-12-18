import typing
import abc
import anchor.builtins as builtins


__all__: typing.List[str] = list(['AST', 'SYMTABLE',])


class Factory(abc.ABC):

    def __init__(self) -> None:
        self._builders: typing.Dict[str, typing.Any] = {}

    def _registerbuilder(self, key: str, builder: typing.Any) -> None:
        self._builders[key] = builder

    def new(self, key, **kwargs) -> typing.Any:
        builder: typing.Any = self._builders.get(key)
        if (not builder):
            raise ValueError(key)
        return builder(**kwargs)


class ASTNodeFactory(object):

    class __ASTNodeFactory(Factory):

        __astnodename: typing.Dict[typing.Type, str] = dict({
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

        def __init__(
            self, declarations: typing.List[typing.Tuple[str, typing.Type]]
        ) -> None:
            super().__init__()
            for key, builder in declarations:
                self._registerbuilder(key, builder)
        
        def new(self, value: typing.Any) -> typing.Any:
            if (isinstance(value, builtins.Type)):
                return super().new(value.typename, value=value)
            key = self.__astnodename[type(value)]
            return super().new(key, value=value)

    __instance: __ASTNodeFactory = None

    def __new__(
        cls, declarations: typing.List[typing.Tuple[str, typing.Type]]
    ) -> __ASTNodeFactory:
        if (not ASTNodeFactory.__instance):
            ASTNodeFactory.__instance = \
                ASTNodeFactory.__ASTNodeFactory(declarations)
        return ASTNodeFactory.__instance

    def new(self, value: typing.Any) -> typing.Any:
        return ASTNodeFactory().new(value)


class SymbolTableFactory(object):

    class __SymbolTableFactory(Factory):

        def __init__(
            self, declarations: typing.List[typing.Tuple[str, typing.Type]]
        ) -> None:
            super().__init__()
            for key, builder in declarations:
                self._registerbuilder(key, builder)

    __instance: __SymbolTableFactory = None

    def __new__(
        cls, declarations: typing.List[typing.Tuple[str, typing.Type]]
    ) -> __SymbolTableFactory:
        if (not SymbolTableFactory.__instance):
            SymbolTableFactory.__instance = \
                SymbolTableFactory.__SymbolTableFactory(declarations)
        return SymbolTableFactory.__instance

    def new(self, key: str, **kwargs) -> typing.Any:
        return SymbolTableFactory().new(key, **kwargs)


AST: ASTNodeFactory = None
SYMTABLE: SymbolTableFactory = None
