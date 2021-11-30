import anchor.symtable as symtable


class Factory(object):

    def __init__(self):
        self._builders = {}

    def _registerbuilder(self, key, builder):
        self._builders[key] = builder

    def new(self, key, **kwargs):
        builder = self._builders.get(key)
        if (not builder):
            raise ValueError(key)
        return builder(**kwargs)


class SymbolTableFactory(object):

    class __SymbolTableFactory(Factory):

        def __init__(self):
            super().__init__()
            self._registerbuilder('Main', symtable.SymbolTable)
            self._registerbuilder('Function', symtable.Function)
            self._registerbuilder('Class', symtable.Class)

    __instance: __SymbolTableFactory = None

    def __new__(cls):
        if (not SymbolTableFactory.__instance):
            SymbolTableFactory.__instance = \
                SymbolTableFactory.__SymbolTableFactory()
        return SymbolTableFactory.__instance
