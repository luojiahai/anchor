from __future__ import annotations
import typing

if (typing.TYPE_CHECKING):
    import anchor.ast as ast

import anchor.factory as factory


__all__: typing.List[str] = list([
    'Type', 'SymbolTable', 'Class', 'Function', 'Symbol',
])


class Symbol(object):

    def __init__(
        self, identifier: str, astnodes: typing.List[ast.ASTNode],
        symtable: SymbolTable, **kwargs
    ):
        self.__identifier: str = identifier
        self.__astnodes: typing.List[ast.ASTNode] = astnodes
        self.__symtable: SymbolTable = symtable
        self.__kwargs: typing.Dict[str, typing.Any] = kwargs

    @property
    def identifier(self) -> str:
        return self.__identifier

    @property
    def astnodes(self) -> typing.List[ast.ASTNode]:
        return self.__astnodes

    @property
    def astnode(self) -> ast.ASTNode:
        if len(self.__astnodes) != 1:
            # return latest defined astnode
            return self.__astnodes[-1]
        return self.__astnodes[0]

    @property
    def symtable(self) -> SymbolTable:
        return self.__symtable

    @property
    def kwargs(self) -> typing.Dict[str, typing.Any]:
        return self.__kwargs


class Type(object):
    MAIN = 'MAIN'
    CLASS = 'CLASS'
    FUNCTION = 'FUNCTION'


class SymbolTable(object):

    def __init__(self, identifier: str, parent = None) -> None:
        self._identifier: str = identifier
        self._type: Type = Type.MAIN
        self._symbols: typing.Dict[str, Symbol] = dict()
        self._parent: SymbolTable = parent

    @property
    def type(self) -> Type:
        return self._type

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def symbols(self) -> typing.Dict[str, Symbol]:
        return self._symbols
    
    def insert(
        self, identifier: str, astnodes: typing.List[ast.ASTNode], **kwargs
    ) -> None:
        symbol: Symbol = self.lookup(identifier)
        if (identifier in self.symbols):
            oldsymbol = self.symbols[identifier]
            symbol = Symbol(
                identifier, oldsymbol.astnodes + astnodes, self,
                **(oldsymbol.kwargs | kwargs)
            )
        else:
            symbol = Symbol(identifier, astnodes, self, **kwargs)
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

    __methods: typing.List[Symbol] = None

    def __init__(self, identifier: str, parent: SymbolTable = None) -> None:
        super().__init__(identifier, parent=parent)
        self._type: Type = Type.CLASS

    @property
    def methods(self) -> typing.List[Symbol]:
        return self.__methods


class Function(SymbolTable):

    __parameters: typing.List[Symbol] = None

    def __init__(self, identifier: str, parent: SymbolTable=None) -> None:
        super().__init__(identifier, parent=parent)
        self._type: Type = Type.FUNCTION

    @property
    def parameters(self) -> typing.List[Symbol]:
        return self.__parameters


factory.SYMTABLE = factory.SymbolTableFactory(declarations=list([
    (Type.MAIN, SymbolTable,),
    (Type.CLASS, Class,),
    (Type.FUNCTION, Function,),
]))
