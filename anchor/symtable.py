__all__ = [
    'SymbolTableType', 'SymbolTable', 'Class', 'Function', 'Symbol',
]


class SymbolTableType(object):
    MAIN = 'MAIN'
    CLASS = 'CLASS'
    FUNCTION = 'FUNCTION'


class SymbolTable(object):

    def __init__(self, identifier, parent=None):
        self._identifier = identifier
        self._type = SymbolTableType.MAIN
        self._symbols = dict()
        if (parent):
            for _, symbol in parent.symbols.items():
                self.insert(
                    symbol.identifier, symbol.namespaces, **symbol.flags,
                )

    @property
    def type(self):
        return self._type

    @property
    def identifier(self):
        return self._identifier

    @property
    def symbols(self):
        return self._symbols
    
    def insert(self, identifier, namespaces, **flags):
        symbol = None
        if (identifier in self.symbols):
            symbol = Symbol(
                identifier, self.symbols[identifier].namespaces + namespaces, 
                **flags,
            )
        else:
            symbol = Symbol(identifier, namespaces, **flags,)
        assert (symbol != None)
        self.symbols[identifier] = symbol

    def lookup(self, identifier):
        if (identifier not in self.symbols):
            return None
        return self.symbols[identifier]


class Class(SymbolTable):

    __methods = None

    def __init__(self, identifier, parent=None):
        super().__init__(identifier, parent=parent)
        self._type = SymbolTableType.CLASS

    @property
    def methods(self):
        return self.__methods


class Function(SymbolTable):

    __parameters = None

    def __init__(self, identifier, parent=None):
        super().__init__(identifier, parent=parent)
        self._type = SymbolTableType.FUNCTION

    @property
    def parameters(self):
        return self.__parameters


class Symbol(object):

    def __init__(self, identifier, namespaces, **flags):
        self.__identifier = identifier
        self.__namespaces = namespaces
        self.__flags = flags

    @property
    def identifier(self):
        return self.__identifier

    @property
    def namespaces(self):
        return self.__namespaces

    @property
    def namespace(self):
        if len(self.__namespaces) != 1:
            # return latest defined namespace
            return self.__namespaces[-1]
        return self.__namespaces[0]

    @property
    def flags(self):
        return self.__flags
    