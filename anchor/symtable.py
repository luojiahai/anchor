import typing


__all__ = [
    'SymbolTableType', 'SymbolTable', 'Class', 'Function', 'Symbol',
]


class Symbol(object):

    def __init__(self, identifier: str, namespaces: list, **flags):
        self.__identifier: str = identifier
        self.__namespaces: list = namespaces
        self.__flags: dict[str, typing.Any] = flags

    @property
    def identifier(self) -> str:
        return self.__identifier

    @property
    def namespaces(self) -> list:
        return self.__namespaces

    @property
    def namespace(self) -> typing.Any:
        if len(self.__namespaces) != 1:
            # return latest defined namespace
            return self.__namespaces[-1]
        return self.__namespaces[0]

    @property
    def flags(self) -> dict[str, typing.Any]:
        return self.__flags


class SymbolTableType(object):
    MAIN = 'MAIN'
    CLASS = 'CLASS'
    FUNCTION = 'FUNCTION'


class SymbolTable(object):

    def __init__(self, identifier: str, parent=None):
        self._identifier: str = identifier
        self._type: SymbolTableType = SymbolTableType.MAIN
        self._symbols: dict = dict()
        if (parent):
            for _, symbol in parent.symbols.items():
                self.insert(
                    symbol.identifier, symbol.namespaces, **symbol.flags,
                )

    @property
    def type(self) -> SymbolTableType:
        return self._type

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def symbols(self) -> dict:
        return self._symbols
    
    def insert(self, identifier: str, namespaces: list, **flags) -> None:
        symbol: Symbol = None
        if (identifier in self.symbols):
            symbol = Symbol(
                identifier, self.symbols[identifier].namespaces + namespaces, 
                **flags,
            )
        else:
            symbol = Symbol(identifier, namespaces, **flags,)
        assert (symbol != None)
        self.symbols[identifier] = symbol

    def lookup(self, identifier: str) -> Symbol:
        if (identifier not in self.symbols):
            return None
        return self.symbols[identifier]


class Class(SymbolTable):

    __methods: list = None

    def __init__(self, identifier: str, parent: SymbolTable = None):
        super().__init__(identifier, parent=parent)
        self._type: SymbolTableType = SymbolTableType.CLASS

    @property
    def methods(self) -> list:
        return self.__methods


class Function(SymbolTable):

    __parameters: list = None

    def __init__(self, identifier: str, parent: SymbolTable=None):
        super().__init__(identifier, parent=parent)
        self._type: SymbolTableType = SymbolTableType.FUNCTION

    @property
    def parameters(self) -> list:
        return self.__parameters

    