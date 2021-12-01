from __future__ import annotations
import typing

if (typing.TYPE_CHECKING):
    import anchor.ast as ast

import anchor.factory as factory


__all__: list[str] = [
    'SymbolTableType', 'SymbolTable', 'Class', 'Function', 'Symbol',
]


class Symbol(object):

    def __init__(self, identifier: str, astnodes: list[ast.ASTNode], **flags):
        self.__identifier: str = identifier
        self.__astnodes: list[ast.ASTNode] = astnodes
        self.__flags: dict[str, typing.Any] = flags

    @property
    def identifier(self) -> str:
        return self.__identifier

    @property
    def astnodes(self) -> list[ast.ASTNode]:
        return self.__astnodes

    @property
    def astnode(self) -> ast.ASTNode:
        if len(self.__astnodes) != 1:
            # return latest defined astnode
            return self.__astnodes[-1]
        return self.__astnodes[0]

    @property
    def flags(self) -> dict[str, typing.Any]:
        return self.__flags


class SymbolTableType(object):
    MAIN = 'MAIN'
    CLASS = 'CLASS'
    FUNCTION = 'FUNCTION'


class SymbolTable(object):

    def __init__(self, identifier: str, parent = None):
        self._identifier: str = identifier
        self._type: SymbolTableType = SymbolTableType.MAIN
        self._symbols: dict[str, Symbol] = dict()
        self._parent: SymbolTable = parent

    @property
    def type(self) -> SymbolTableType:
        return self._type

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def symbols(self) -> dict[str, Symbol]:
        return self._symbols
    
    def insert(
        self, identifier: str, astnodes: list[ast.ASTNode], **flags
    ) -> None:
        symbol: Symbol = None
        if (identifier in self.symbols):
            symbol = Symbol(
                identifier, self.symbols[identifier].astnodes + astnodes, 
                **flags,
            )
        else:
            symbol = Symbol(identifier, astnodes, **flags,)
        assert (symbol != None)
        self.symbols[identifier] = symbol

    def lookup(self, identifier: str) -> Symbol:
        if (identifier in self.symbols):
            return self.symbols[identifier]
        elif (self._parent): 
            return self._parent.lookup(identifier)
        else:
            return None


class Class(SymbolTable):

    __methods: list[Symbol] = None

    def __init__(self, identifier: str, parent: SymbolTable = None):
        super().__init__(identifier, parent=parent)
        self._type: SymbolTableType = SymbolTableType.CLASS

    @property
    def methods(self) -> list[Symbol]:
        return self.__methods


class Function(SymbolTable):

    __parameters: list[Symbol] = None

    def __init__(self, identifier: str, parent: SymbolTable=None):
        super().__init__(identifier, parent=parent)
        self._type: SymbolTableType = SymbolTableType.FUNCTION

    @property
    def parameters(self) -> list[Symbol]:
        return self.__parameters


factory.SYMTABLE = factory.SymbolTableFactory(declarations=list([
    ('Main', SymbolTable,),
    ('Class', Class,),
    ('Function', Function,),
]))
